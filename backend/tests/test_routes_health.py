def test_health_is_always_200_and_light(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_ready_reports_status(client):
    resp = client.get("/ready")
    # 200 if db+redis reachable in this test env, 503 naming the failed dependency otherwise
    assert resp.status_code in (200, 503)
    body = resp.json()
    if resp.status_code == 503:
        assert "failed_dependencies" in body


def test_metrics_returns_prometheus_text_format(client):
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "civicpulse_up" in resp.text
