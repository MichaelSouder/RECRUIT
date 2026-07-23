SUBJECT_PAYLOAD = {
    "first_name": "Jane",
    "last_name": "Doe",
    "sex": "female",
}


def test_create_subject_requires_researcher_role(client, viewer_headers):
    resp = client.post("/api/v1/subjects", json=SUBJECT_PAYLOAD, headers=viewer_headers)
    assert resp.status_code == 403


def test_create_and_get_subject(client, admin_headers):
    resp = client.post("/api/v1/subjects", json=SUBJECT_PAYLOAD, headers=admin_headers)
    assert resp.status_code == 201, resp.text
    subject_id = resp.json()["id"]

    resp = client.get(f"/api/v1/subjects/{subject_id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["last_name"] == "Doe"


def test_update_subject(client, admin_headers):
    resp = client.post("/api/v1/subjects", json=SUBJECT_PAYLOAD, headers=admin_headers)
    subject_id = resp.json()["id"]

    resp = client.put(
        f"/api/v1/subjects/{subject_id}",
        json={"last_name": "Smith"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["last_name"] == "Smith"


def test_delete_subject(client, admin_headers):
    """Regression test for the db_subject.gender -> .sex crash bug."""
    resp = client.post("/api/v1/subjects", json=SUBJECT_PAYLOAD, headers=admin_headers)
    subject_id = resp.json()["id"]

    resp = client.delete(f"/api/v1/subjects/{subject_id}", headers=admin_headers)
    assert resp.status_code == 204

    resp = client.get(f"/api/v1/subjects/{subject_id}", headers=admin_headers)
    assert resp.status_code == 404


def test_get_subject_not_found(client, admin_headers):
    resp = client.get("/api/v1/subjects/999999", headers=admin_headers)
    assert resp.status_code == 404


def test_subject_ssn_encrypted_at_rest(client, db_session, admin_headers):
    """SSN should round-trip through the API in plaintext, but never be stored as plaintext."""
    from sqlalchemy import text

    resp = client.post(
        "/api/v1/subjects",
        json={**SUBJECT_PAYLOAD, "ssn": "123-45-6789"},
        headers=admin_headers,
    )
    assert resp.status_code == 201, resp.text
    subject_id = resp.json()["id"]
    assert resp.json()["ssn"] == "123-45-6789"

    raw_ssn = db_session.execute(
        text("SELECT ssn FROM subjects WHERE id = :id"), {"id": subject_id}
    ).scalar_one()
    assert raw_ssn != "123-45-6789"
    assert "123-45-6789" not in raw_ssn

    resp = client.get(f"/api/v1/subjects/{subject_id}", headers=admin_headers)
    assert resp.json()["ssn"] == "123-45-6789"


def test_researcher_without_study_access_cannot_see_scoped_subject(
    client, researcher_headers, admin_headers, study
):
    resp = client.post(
        "/api/v1/subjects",
        json={**SUBJECT_PAYLOAD, "study_ids": [study.id]},
        headers=admin_headers,
    )
    subject_id = resp.json()["id"]

    resp = client.get(f"/api/v1/subjects/{subject_id}", headers=researcher_headers)
    assert resp.status_code == 403


def test_list_subjects_paginated(client, admin_headers):
    for i in range(3):
        client.post(
            "/api/v1/subjects",
            json={"first_name": f"Person{i}", "last_name": "Test", "sex": "male"},
            headers=admin_headers,
        )

    resp = client.get("/api/v1/subjects", headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 3
    assert "items" in body and "page" in body and "pages" in body
