import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production-use-only-32chars")
os.environ.setdefault("SSN_ENCRYPTION_KEY", "test-ssn-encryption-key-not-for-prod-32chars")

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.core.security import get_password_hash
from app.core.rate_limit import limiter
from app.models.user import User
from app.models.study import Study
from app.models.user_study import UserStudy

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    raise RuntimeError(
        "TEST_DATABASE_URL is not set. This suite always runs against a real Postgres "
        "instance, never SQLite: SQLite silently accepts things Postgres rejects (e.g. it "
        "can't even create the schema — migration_events.detail is a JSONB column, which "
        "has no SQLite equivalent) and that kind of divergence hides real bugs instead of "
        "catching them. Point this at a disposable database, e.g.:\n"
        "  scripts/run-backend-tests.sh          # starts a throwaway postgres:15 container for you\n"
        "  # or manually:\n"
        "  docker run -d --rm --name recruit_test_postgres -e POSTGRES_PASSWORD=postgres "
        "-e POSTGRES_DB=recruit_test -p 55432:5432 postgres:15\n"
        "  TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:55432/recruit_test pytest"
    )

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def _schema():
    """Real Postgres, so the full model set (including migration_events' JSONB column)
    creates cleanly with no per-dialect exclusions needed."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Login rate limiting is a per-process in-memory counter (see app/core/rate_limit.py),
    shared across every TestClient in this test run since they all hit the same Limiter
    instance. Without resetting it, tests would start tripping the real 5/minute login
    limit purely from unrelated tests logging in via fixtures."""
    limiter.reset()
    yield


@pytest.fixture
def db_session():
    """One test = one outer transaction, rolled back at teardown. Route code that calls
    db.commit() lands on a SAVEPOINT (nested transaction) instead of the real outer one,
    via the standard SQLAlchemy 'join a session into an external transaction' recipe —
    so the rollback below always undoes everything the test touched, however many commits
    happened along the way."""
    connection = engine.connect()
    outer_transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _restart_savepoint(sess, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    try:
        yield session
    finally:
        session.close()
        outer_transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(get_db, None)


def _make_user(db_session, *, email, password, role, is_superuser=False, is_active=True):
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        full_name=email.split("@")[0],
        role=role,
        is_superuser=is_superuser,
        is_active=is_active,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session):
    return _make_user(db_session, email="admin@example.com", password="AdminPass123!", role="admin", is_superuser=True)


@pytest.fixture
def researcher_user(db_session):
    return _make_user(db_session, email="researcher@example.com", password="ResearchPass123!", role="researcher")


@pytest.fixture
def viewer_user(db_session):
    return _make_user(db_session, email="viewer@example.com", password="ViewerPass123!", role="viewer")


@pytest.fixture
def study(db_session):
    s = Study(name="Test Study", status="active")
    db_session.add(s)
    db_session.commit()
    db_session.refresh(s)
    return s


def _login(client, email, password):
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def auth_headers(client, email, password):
    token = _login(client, email, password)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, admin_user):
    return auth_headers(client, "admin@example.com", "AdminPass123!")


@pytest.fixture
def researcher_headers(client, researcher_user):
    return auth_headers(client, "researcher@example.com", "ResearchPass123!")


@pytest.fixture
def viewer_headers(client, viewer_user):
    return auth_headers(client, "viewer@example.com", "ViewerPass123!")


@pytest.fixture
def researcher_with_study_access(db_session, researcher_user, study):
    link = UserStudy(user_id=researcher_user.id, study_id=study.id, study_role="researcher")
    db_session.add(link)
    db_session.commit()
    return researcher_user
