def test_health_returns_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200

    body = resp.json()
    assert body["status"] == "healthy"
    assert body["database"] == "connected"
    assert "version" in body