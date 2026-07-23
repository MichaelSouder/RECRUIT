def test_register_and_login(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "new.user@example.com", "password": "StrongPass123!", "full_name": "New User"},
    )
    assert resp.status_code == 201, resp.text

    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "new.user@example.com", "password": "StrongPass123!"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client, researcher_user):
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "researcher@example.com", "password": "wrong-password"},
    )
    assert resp.status_code == 401


def test_login_unknown_user(client):
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "whatever123"},
    )
    assert resp.status_code == 401


def test_login_inactive_user(client, db_session, researcher_user):
    researcher_user.is_active = False
    db_session.add(researcher_user)
    db_session.commit()

    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "researcher@example.com", "password": "ResearchPass123!"},
    )
    assert resp.status_code == 400


def test_login_piv_unregistered_certificate(client):
    resp = client.post("/api/v1/auth/login-piv", json={"certificate_id": "unknown-cert"})
    assert resp.status_code == 401


def test_login_piv_success(client, db_session, researcher_user):
    researcher_user.piv_certificate_id = "CN=test.user"
    db_session.add(researcher_user)
    db_session.commit()

    resp = client.post("/api/v1/auth/login-piv", json={"certificate_id": "CN=test.user"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_me_requires_auth(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_me_returns_current_user(client, researcher_headers):
    resp = client.get("/api/v1/auth/me", headers=researcher_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "researcher@example.com"


def test_logout_writes_audit_log(client, db_session, researcher_headers):
    from app.models.audit_log import AuditLog

    resp = client.post("/api/v1/auth/logout", headers=researcher_headers)
    assert resp.status_code == 204

    logs = db_session.query(AuditLog).filter(AuditLog.action == "LOGOUT").all()
    assert len(logs) == 1
    assert logs[0].user_email == "researcher@example.com"


def test_logout_requires_auth(client):
    resp = client.post("/api/v1/auth/logout")
    assert resp.status_code == 401


def test_login_rate_limited_after_five_attempts(client):
    for _ in range(5):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "whatever123"},
        )
        assert resp.status_code == 401

    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "whatever123"},
    )
    assert resp.status_code == 429


def test_login_piv_rate_limited_after_five_attempts(client):
    for _ in range(5):
        resp = client.post("/api/v1/auth/login-piv", json={"certificate_id": "unknown-cert"})
        assert resp.status_code == 401

    resp = client.post("/api/v1/auth/login-piv", json={"certificate_id": "unknown-cert"})
    assert resp.status_code == 429
