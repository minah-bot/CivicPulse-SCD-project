def test_providers_meta_returns_active_provider_and_list(client):
    resp = client.get("/api/meta/providers")
    assert resp.status_code == 200
    body = resp.json()
    assert "active_provider" in body
    assert isinstance(body["providers"], list)
    assert len(body["providers"]) >= 1
