from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import os

# pool_pre_ping avoids surfacing a stale/dropped connection (idle timeout, network blip,
# postgres restart) as a request-time OperationalError — SQLAlchemy checks and transparently
# recycles it instead. pool_size/max_overflow are explicit rather than left at the (small)
# SQLAlchemy defaults; revisit against real concurrency numbers as the deployment grows.
_POSTGRES_ENGINE_KWARGS = {"pool_pre_ping": True, "pool_size": 10, "max_overflow": 20}

# Use SQLite for development if PostgreSQL is not available
database_url = settings.database_url
if "postgresql" in database_url:
    # Try to use SQLite as fallback if PostgreSQL connection fails
    try:
        # Test connection
        test_engine = create_engine(database_url, connect_args={"connect_timeout": 2})
        with test_engine.connect() as conn:
            pass
        engine = create_engine(database_url, **_POSTGRES_ENGINE_KWARGS)
    except Exception:
        # Fallback to SQLite
        db_path = os.path.join(os.path.dirname(__file__), "..", "..", "recruit.db")
        database_url = f"sqlite:///{db_path}"
        engine = create_engine(database_url, connect_args={"check_same_thread": False})
else:
    # Non-Postgres URL configured directly (e.g. sqlite://) — the pool kwargs above are
    # Postgres/QueuePool-specific and would raise on a pool class that doesn't accept them.
    engine = create_engine(database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

