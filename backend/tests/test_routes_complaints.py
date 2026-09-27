def _create_complaint(client, text="Water is not coming since three days please check.", location="Street 5"):
    return client.post("/api/complaints", json={"text": text, "location": location})


def test_create_complaint_returns_201_with_full_shape(client):
    resp = _create_complaint(client)
    assert resp.status_code == 201
    body = resp.json()
    for field in ("id", "category", "priority", "ai_summary", "status", "triaged_by", "triage_latency_ms"):
        assert field in body
    assert body["status"] == "open"


def test_create_complaint_rejects_short_text(client):
    resp = client.post("/api/complaints", json={"text": "too short", "location": "X"})
    assert resp.status_code == 422  # field-level validation error


def test_get_complaint_by_id(client):
    created = _create_complaint(client).json()
    resp = client.get(f"/api/complaints/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_get_missing_complaint_returns_404(client):
    resp = client.get("/api/complaints/999999")
    assert resp.status_code == 404


def test_list_complaints_supports_pagination(client):
    for i in range(3):
        _create_complaint(client, text=f"Complaint number {i} about roads being bad here.")
    resp = client.get("/api/complaints?page=1&page_size=2")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 3
    assert len(body["items"]) == 2


def test_list_complaints_rejects_bad_page_size(client):
    resp = client.get("/api/complaints?page_size=500")
    assert resp.status_code == 422  # FastAPI/Pydantic validation error (>100)


def test_patch_status_valid_transition(client):
    created = _create_complaint(client).json()
    resp = client.patch(f"/api/complaints/{created['id']}/status", json={"status": "in_progress"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"


def test_patch_status_invalid_transition_returns_409_with_named_transition(client):
    created = _create_complaint(client).json()
    resp = client.patch(f"/api/complaints/{created['id']}/status", json={"status": "resolved"})
    assert resp.status_code == 409
    detail = resp.json()["detail"]
    assert "open" in detail
    assert "resolved" in detail


def test_patch_status_on_missing_complaint_returns_404(client):
    resp = client.patch("/api/complaints/999999/status", json={"status": "in_progress"})
    assert resp.status_code == 404
