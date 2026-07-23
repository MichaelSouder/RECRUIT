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
        .filter(AuditLog.entity_type == "assessment", AuditLog.entity_id == entity_id, AuditLog.action == action)
        .all()
    )


def test_create_assessment_requires_researcher_role(client, viewer_headers, admin_headers):
    subject_id = _create_subject(client, admin_headers)
    resp = client.post(
        "/api/v1/assessments",
        json={
            "subject_id": subject_id,
            "assessment_type": "moca",
            "assessment_date": "2026-01-01",
        },
        headers=viewer_headers,
    )
    assert resp.status_code == 403


def test_assessment_data_field_round_trips(client, admin_headers):
    """Regression test: Assessment.data was silently dropped before schemas/assessment.py
    declared the field, even though the frontend sends it (AssessmentForm.tsx)."""
    subject_id = _create_subject(client, admin_headers)
    payload = {
        "subject_id": subject_id,
        "assessment_type": "moca",
        "assessment_date": "2026-01-01",
        "data": {"q1": 3, "q2": "yes"},
    }
    resp = client.post("/api/v1/assessments", json=payload, headers=admin_headers)
    assert resp.status_code == 201, resp.text
    assessment_id = resp.json()["id"]
    assert resp.json()["data"] == {"q1": 3, "q2": "yes"}

    resp = client.get(f"/api/v1/assessments/{assessment_id}", headers=admin_headers)
    assert resp.json()["data"] == {"q1": 3, "q2": "yes"}

    resp = client.put(
        f"/api/v1/assessments/{assessment_id}",
        json={"data": {"q1": 5}},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["data"] == {"q1": 5}


def test_assessment_crud_writes_audit_log(client, db_session, admin_headers):
    subject_id = _create_subject(client, admin_headers)
    resp = client.post(
        "/api/v1/assessments",
        json={"subject_id": subject_id, "assessment_type": "moca", "assessment_date": "2026-01-01"},
        headers=admin_headers,
    )
    assessment_id = resp.json()["id"]
    assert len(_audit_rows(db_session, assessment_id, "CREATE")) == 1

    client.put(
        f"/api/v1/assessments/{assessment_id}",
        json={"total_score": 27},
        headers=admin_headers,
    )
    assert len(_audit_rows(db_session, assessment_id, "UPDATE")) == 1

    client.delete(f"/api/v1/assessments/{assessment_id}", headers=admin_headers)
    assert len(_audit_rows(db_session, assessment_id, "DELETE")) == 1


def test_delete_assessment(client, admin_headers):
    subject_id = _create_subject(client, admin_headers)
    resp = client.post(
        "/api/v1/assessments",
        json={"subject_id": subject_id, "assessment_type": "moca", "assessment_date": "2026-01-01"},
        headers=admin_headers,
    )
    assessment_id = resp.json()["id"]

    resp = client.delete(f"/api/v1/assessments/{assessment_id}", headers=admin_headers)
    assert resp.status_code == 204

    resp = client.get(f"/api/v1/assessments/{assessment_id}", headers=admin_headers)
    assert resp.status_code == 404
