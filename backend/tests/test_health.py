def test_liveness(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "alive"
    assert "version" in body


def test_readiness(client):
    resp = client.get("/ready")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ready"
    assert body["database"] == "connected"


def test_request_id_is_returned(client):
    resp = client.get("/health")
    assert "X-Request-ID" in resp.headers
    assert len(resp.headers["X-Request-ID"]) > 0


def test_incoming_request_id_is_echoed(client):
    resp = client.get("/health", headers={"X-Request-ID": "test-id-123"})
    assert resp.headers["X-Request-ID"] == "test-id-123"