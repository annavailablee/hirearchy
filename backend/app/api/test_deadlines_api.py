from datetime import datetime, timedelta, timezone


_counter = [0]


def _unique_email():
    _counter[0] += 1
    return f"deadline_test_{_counter[0]}@example.com"


def _token(client) -> str:
    email = _unique_email()
    client.post("/auth/register", json={"email": email, "password": "supersecret123"})
    resp = client.post("/auth/login", json={"email": email, "password": "supersecret123"})
    return resp.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create(client, token, **overrides):
    payload = {
        "title": "Test deadline",
        "kind": "custom",
        "due_at": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
    }
    payload.update(overrides)
    return client.post("/deadlines", headers=_auth(token), json=payload)


def test_create_deadline(client):
    token = _token(client)
    resp = _create(client, token, title="Interview prep")
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["title"] == "Interview prep"
    assert body["completed_at"] is None


def test_create_requires_auth(client):
    resp = client.post(
        "/deadlines",
        json={"title": "x", "kind": "custom", "due_at": "2030-01-01T00:00:00Z"},
    )
    assert resp.status_code == 401


def test_create_invalid_kind_returns_422(client):
    token = _token(client)
    resp = _create(client, token, kind="not_a_real_kind")
    assert resp.status_code == 422


def test_list_excludes_completed_by_default(client):
    token = _token(client)
    a = _create(client, token, title="Keep me").json()["id"]
    b = _create(client, token, title="Complete me").json()["id"]

    client.patch(f"/deadlines/{b}", headers=_auth(token), json={"completed": True})

    listed = client.get("/deadlines", headers=_auth(token)).json()
    titles = {d["title"] for d in listed}
    assert "Keep me" in titles
    assert "Complete me" not in titles


def test_list_includes_completed_when_asked(client):
    token = _token(client)
    b = _create(client, token, title="Complete me").json()["id"]
    client.patch(f"/deadlines/{b}", headers=_auth(token), json={"completed": True})

    listed = client.get("/deadlines?include_completed=true", headers=_auth(token)).json()
    titles = {d["title"] for d in listed}
    assert "Complete me" in titles


def test_attention_queue_excludes_far_future(client):
    token = _token(client)
    _create(client, token, title="Far away",
            due_at=(datetime.now(timezone.utc) + timedelta(days=60)).isoformat())
    _create(client, token, title="Due soon",
            due_at=(datetime.now(timezone.utc) + timedelta(days=2)).isoformat())

    queue = client.get("/deadlines/attention", headers=_auth(token)).json()
    titles = {d["title"] for d in queue}
    assert "Due soon" in titles
    assert "Far away" not in titles


def test_attention_queue_sorts_overdue_first(client):
    token = _token(client)
    _create(client, token, title="Due in 3 days",
            due_at=(datetime.now(timezone.utc) + timedelta(days=3)).isoformat())
    _create(client, token, title="Overdue",
            due_at=(datetime.now(timezone.utc) - timedelta(hours=2)).isoformat())

    queue = client.get("/deadlines/attention", headers=_auth(token)).json()
    assert queue[0]["priority"] == "OVERDUE"
    assert queue[0]["title"] == "Overdue"


def test_mark_completed_then_undo(client):
    token = _token(client)
    d_id = _create(client, token).json()["id"]

    r = client.patch(f"/deadlines/{d_id}", headers=_auth(token), json={"completed": True})
    assert r.status_code == 200
    assert r.json()["completed_at"] is not None

    r = client.patch(f"/deadlines/{d_id}", headers=_auth(token), json={"completed": False})
    assert r.json()["completed_at"] is None


def test_isolation(client):
    alice = _token(client)
    bob = _token(client)

    d_id = _create(client, alice).json()["id"]
    assert client.get(f"/deadlines/{d_id}", headers=_auth(bob)).status_code == 404


def test_delete(client):
    token = _token(client)
    d_id = _create(client, token).json()["id"]
    assert client.delete(f"/deadlines/{d_id}", headers=_auth(token)).status_code == 204
    assert client.get(f"/deadlines/{d_id}", headers=_auth(token)).status_code == 404


def test_create_with_own_application(client):
    token = _token(client)
    job = client.post(
        "/jobs", headers=_auth(token),
        json={"title": "Intern", "company": "X", "description": "Python"},
    ).json()
    app_id = client.post(
        "/applications", headers=_auth(token), json={"job_id": job["id"]}
    ).json()["id"]

    resp = _create(client, token, title="Take-home", kind="assessment",
                   application_id=app_id)
    assert resp.status_code == 201
    assert resp.json()["application_id"] == app_id


def test_create_with_other_users_application_returns_404(client):
    alice = _token(client)
    bob = _token(client)

    job = client.post(
        "/jobs", headers=_auth(alice),
        json={"title": "Intern", "company": "X", "description": "Python"},
    ).json()
    app_id = client.post(
        "/applications", headers=_auth(alice), json={"job_id": job["id"]}
    ).json()["id"]

    resp = _create(client, bob, application_id=app_id)
    assert resp.status_code == 404