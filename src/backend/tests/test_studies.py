def test_create_study_requires_researcher_role(client, viewer_headers):
    resp = client.post("/api/v1/studies", json={"name": "New Study"}, headers=viewer_headers)
    assert resp.status_code == 403


def test_create_and_get_study(client, admin_headers):
    resp = client.post("/api/v1/studies", json={"name": "Alpha Study"}, headers=admin_headers)
    assert resp.status_code == 201, resp.text
    study_id = resp.json()["id"]

    resp = client.get(f"/api/v1/studies/{study_id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Alpha Study"


def test_duplicate_study_name_rejected(client, admin_headers):
    client.post("/api/v1/studies", json={"name": "Dup Study"}, headers=admin_headers)
    resp = client.post("/api/v1/studies", json={"name": "Dup Study"}, headers=admin_headers)
    assert resp.status_code == 400


def test_update_study_requires_manage_access(client, admin_headers, researcher_headers, study):
    resp = client.put(
        f"/api/v1/studies/{study.id}",
        json={"description": "updated"},
        headers=researcher_headers,
    )
    assert resp.status_code == 403

    resp = client.put(
        f"/api/v1/studies/{study.id}",
        json={"description": "updated"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["description"] == "updated"


def test_delete_study_requires_admin(client, researcher_headers, admin_headers, study):
    resp = client.delete(f"/api/v1/studies/{study.id}", headers=researcher_headers)
    assert resp.status_code == 403

    resp = client.delete(f"/api/v1/studies/{study.id}", headers=admin_headers)
    assert resp.status_code == 204


def test_non_admin_only_sees_accessible_studies(
    client, researcher_headers, admin_headers, study, researcher_with_study_access
):
    # A second study the researcher has no membership in should stay invisible to them.
    client.post("/api/v1/studies", json={"name": "Other Study"}, headers=admin_headers)

    resp = client.get("/api/v1/studies", headers=researcher_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == study.id

    resp = client.get("/api/v1/studies", headers=admin_headers)
    assert resp.json()["total"] == 2
