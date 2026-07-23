from app.models.audit_log import AuditLog


def _create_subject(client, headers):
    resp = client.post(
        "/api/v1/subjects",
        json={"first_name": "Jane", "last_name": "Doe", "sex": "female"},
        headers=headers,
    )
    return resp.json()["id"]


def _audit_rows(db_session, entity_id, action):
    return (
        db_session.query(AuditLog)
        .filter(AuditLog.entity_type == "session_note", AuditLog.entity_id == entity_id, AuditLog.action == action)
        .all()
    )


def test_create_session_note_requires_researcher_role(client, viewer_headers, admin_headers):
    subject_id = _create_subject(client, admin_headers)
    resp = client.post(
        "/api/v1/session-notes",
        json={"subject_id": subject_id, "session_date": "2026-01-01", "notes": "hi"},
        headers=viewer_headers,
    )
    assert resp.status_code == 403


def test_create_update_delete_session_note(client, admin_headers):
    subject_id = _create_subject(client, admin_headers)
    resp = client.post(
        "/api/v1/session-notes",
        json={"subject_id": subject_id, "session_date": "2026-01-01", "notes": "initial"},
        headers=admin_headers,
    )
    assert resp.status_code == 201, resp.text
    note_id = resp.json()["id"]

    resp = client.put(
        f"/api/v1/session-notes/{note_id}",
        json={"notes": "updated"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["notes"] == "updated"

    resp = client.delete(f"/api/v1/session-notes/{note_id}", headers=admin_headers)
    assert resp.status_code == 204

    resp = client.get(f"/api/v1/session-notes/{note_id}", headers=admin_headers)
    assert resp.status_code == 404


def test_session_note_crud_writes_audit_log(client, db_session, admin_headers):
    subject_id = _create_subject(client, admin_headers)
    resp = client.post(
        "/api/v1/session-notes",
        json={"subject_id": subject_id, "session_date": "2026-01-01", "notes": "initial"},
        headers=admin_headers,
    )
    note_id = resp.json()["id"]
    assert len(_audit_rows(db_session, note_id, "CREATE")) == 1

    client.put(f"/api/v1/session-notes/{note_id}", json={"notes": "updated"}, headers=admin_headers)
    assert len(_audit_rows(db_session, note_id, "UPDATE")) == 1

    client.delete(f"/api/v1/session-notes/{note_id}", headers=admin_headers)
    assert len(_audit_rows(db_session, note_id, "DELETE")) == 1
