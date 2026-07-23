from app.models.audit_log import AuditLog


def _audit_rows(db_session, entity_type, entity_id, action=None):
    q = db_session.query(AuditLog).filter(
        AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id
    )
    if action:
        q = q.filter(AuditLog.action == action)
    return q.all()


def test_non_admin_cannot_manage_users(client, researcher_headers):
    resp = client.get("/api/v1/admin/users", headers=researcher_headers)
    assert resp.status_code == 403


def test_create_user_writes_audit_log(client, db_session, admin_headers):
    resp = client.post(
        "/api/v1/admin/users",
        json={"email": "created.user@example.com", "password": "SomePass123!", "role": "viewer"},
        headers=admin_headers,
    )
    assert resp.status_code == 201, resp.text
    user_id = resp.json()["id"]

    logs = _audit_rows(db_session, "user", user_id, action="CREATE")
    assert len(logs) == 1
    # The password must never be written to the audit trail.
    assert "SomePass123!" not in (logs[0].new_value or "")


def test_update_user_writes_audit_log_and_redacts_password(client, db_session, admin_headers):
    resp = client.post(
        "/api/v1/admin/users",
        json={"email": "target@example.com", "password": "InitialPass123!", "role": "viewer"},
        headers=admin_headers,
    )
    user_id = resp.json()["id"]

    resp = client.put(
        f"/api/v1/admin/users/{user_id}",
        json={"full_name": "New Name", "password": "NewPass456!"},
        headers=admin_headers,
    )
    assert resp.status_code == 200

    logs = _audit_rows(db_session, "user", user_id, action="UPDATE")
    assert len(logs) >= 2  # one row per changed field
    field_names = {log.field_name for log in logs}
    assert "full_name" in field_names
    assert "password" in field_names
    password_log = next(log for log in logs if log.field_name == "password")
    assert "NewPass456!" not in (password_log.new_value or "")
    assert "NewPass456!" not in (password_log.old_value or "")


def test_delete_user_writes_audit_log(client, db_session, admin_headers):
    resp = client.post(
        "/api/v1/admin/users",
        json={"email": "to.delete@example.com", "password": "SomePass123!", "role": "viewer"},
        headers=admin_headers,
    )
    user_id = resp.json()["id"]

    resp = client.delete(f"/api/v1/admin/users/{user_id}", headers=admin_headers)
    assert resp.status_code == 204

    logs = _audit_rows(db_session, "user", user_id, action="DELETE")
    assert len(logs) == 1


def test_admin_cannot_delete_self(client, admin_headers, admin_user):
    resp = client.delete(f"/api/v1/admin/users/{admin_user.id}", headers=admin_headers)
    assert resp.status_code == 400


def test_add_and_remove_user_study_writes_audit_log(client, db_session, admin_headers, researcher_user, study):
    resp = client.post(
        f"/api/v1/admin/users/{researcher_user.id}/studies",
        json=[study.id],
        headers=admin_headers,
    )
    assert resp.status_code == 200, resp.text
    grant_logs = _audit_rows(db_session, "user", researcher_user.id, action="UPDATE")
    assert any(log.field_name == "study_access" for log in grant_logs)

    resp = client.delete(
        f"/api/v1/admin/users/{researcher_user.id}/studies/{study.id}",
        headers=admin_headers,
    )
    assert resp.status_code == 204
    revoke_logs = [
        log for log in _audit_rows(db_session, "user", researcher_user.id, action="UPDATE")
        if log.field_name == "study_access" and log.new_value is None
    ]
    assert len(revoke_logs) == 1


def test_patch_user_study_role_writes_audit_log(client, db_session, admin_headers, researcher_with_study_access, study):
    resp = client.patch(
        f"/api/v1/admin/users/{researcher_with_study_access.id}/studies/{study.id}",
        json={"study_role": "admin"},
        headers=admin_headers,
    )
    assert resp.status_code == 200, resp.text
    logs = [
        log for log in _audit_rows(db_session, "user", researcher_with_study_access.id, action="UPDATE")
        if log.field_name and log.field_name.startswith("study_role:")
    ]
    assert len(logs) == 1
    # AuditService._serialize_value JSON-encodes even plain strings.
    assert logs[0].new_value == '"admin"'
