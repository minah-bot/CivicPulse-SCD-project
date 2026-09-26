def test_stats_returns_shape_and_cache_header(client):
    client.post("/api/complaints", json={"text": "Water is not coming since three days please check.", "location": "Street 5"})
    resp = client.get("/api/stats")
    assert resp.status_code == 200
    assert "X-Cache" in resp.headers
    assert resp.headers["X-Cache"] in ("HIT", "MISS")
    body = resp.json()
    for field in ("total", "by_category", "by_priority", "by_status"):
        assert field in body
    assert body["total"] >= 1
