def _token(client, email="alice@example.com") -> str:
    client.post("/auth/register", json={"email": email, "password": "supersecret123"})
    resp = client.post("/auth/login", json={"email": email, "password": "supersecret123"})
    return resp.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _make_job(client, token, title="Backend Intern") -> str:
    resp = client.post(
        "/jobs",
        headers=_auth(token),
        json={"title": title, "company": "Acme", "description": "Python FastAPI"},
    )
    return resp.json()["id"]


def _create_app(client, token, job_id, initial_status="SAVED"):
    return client.post(
        "/applications",
        headers=_auth(token),
        json={"job_id": job_id, "initial_status": initial_status},
    )


# ---------- Create ----------

def test_create_application(client):
    token = _token(client)
    job_id = _make_job(client, token)
    resp = _create_app(client, token, job_id)
    assert resp.status_code == 201, resp.text

    body = resp.json()
    assert body["current_status"] == "SAVED"
    assert body["job_id"] == job_id
    assert len(body["events"]) == 1
    assert body["events"][0]["from_status"] is None
    assert body["events"][0]["to_status"] == "SAVED"


def test_create_duplicate_returns_409(client):
    token = _token(client)
    job_id = _make_job(client, token)
    assert _create_app(client, token, job_id).status_code == 201
    assert _create_app(client, token, job_id).status_code == 409


def test_create_with_invalid_initial_status(client):
    token = _token(client)
    job_id = _make_job(client, token)
    resp = client.post(
        "/applications",
        headers=_auth(token),
        json={"job_id": job_id, "initial_status": "OFFER"},
    )
    assert resp.status_code == 422  # Pydantic pattern rejects


def test_create_for_missing_job_returns_404(client):
    token = _token(client)
    resp = _create_app(client, token, "00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


# ---------- Transitions ----------

def test_valid_transition(client):
    token = _token(client)
    job_id = _make_job(client, token)
    app_id = _create_app(client, token, job_id).json()["id"]

    resp = client.patch(
        f"/applications/{app_id}",
        headers=_auth(token),
        json={"to_status": "APPLIED"},
    )
    assert resp.status_code == 200
    assert resp.json()["current_status"] == "APPLIED"
    assert len(resp.json()["events"]) == 2


def test_invalid_transition_rejected(client):
    token = _token(client)
    job_id = _make_job(client, token)
    app_id = _create_app(client, token, job_id).json()["id"]

    # SAVED -> OFFER is not legal
    resp = client.patch(
        f"/applications/{app_id}",
        headers=_auth(token),
        json={"to_status": "OFFER"},
    )
    assert resp.status_code == 422


def test_full_happy_path(client):
    token = _token(client)
    job_id = _make_job(client, token)
    app_id = _create_app(client, token, job_id).json()["id"]

    for target in ["APPLIED", "ASSESSMENT", "INTERVIEW", "OFFER"]:
        r = client.patch(
            f"/applications/{app_id}", headers=_auth(token), json={"to_status": target}
        )
        assert r.status_code == 200, f"{target}: {r.text}"

    detail = client.get(f"/applications/{app_id}", headers=_auth(token)).json()
    assert detail["current_status"] == "OFFER"
    assert len(detail["events"]) == 5


def test_terminal_state_has_no_exits(client):
    token = _token(client)
    job_id = _make_job(client, token)
    app_id = _create_app(client, token, job_id).json()["id"]

    # Force to REJECTED
    client.patch(f"/applications/{app_id}", headers=_auth(token), json={"to_status": "REJECTED"})

    # Any further transition fails
    resp = client.patch(
        f"/applications/{app_id}", headers=_auth(token), json={"to_status": "INTERVIEW"}
    )
    assert resp.status_code == 422


def test_transition_with_notes(client):
    token = _token(client)
    job_id = _make_job(client, token)
    app_id = _create_app(client, token, job_id).json()["id"]

    resp = client.patch(
        f"/applications/{app_id}",
        headers=_auth(token),
        json={"to_status": "APPLIED", "notes": "Submitted via LinkedIn"},
    )
    assert resp.status_code == 200
    events = resp.json()["events"]
    assert events[-1]["notes"] == "Submitted via LinkedIn"


# ---------- Read ----------

def test_list_applications_filters_by_status(client):
    token = _token(client)
    job_a = _make_job(client, token, title="A")
    job_b = _make_job(client, token, title="B")

    app_a = _create_app(client, token, job_a).json()["id"]
    _create_app(client, token, job_b)

    client.patch(f"/applications/{app_a}", headers=_auth(token), json={"to_status": "APPLIED"})

    applied = client.get("/applications?status=APPLIED", headers=_auth(token)).json()
    saved = client.get("/applications?status=SAVED", headers=_auth(token)).json()

    assert len(applied) == 1
    assert len(saved) == 1


# ---------- Isolation ----------

def test_cannot_read_other_users_application(client):
    alice = _token(client, email="alice@example.com")
    bob = _token(client, email="bob@example.com")

    job_id = _make_job(client, alice)
    app_id = _create_app(client, alice, job_id).json()["id"]

    resp = client.get(f"/applications/{app_id}", headers=_auth(bob))
    assert resp.status_code == 404


def test_cannot_patch_other_users_application(client):
    alice = _token(client, email="alice@example.com")
    bob = _token(client, email="bob@example.com")

    job_id = _make_job(client, alice)
    app_id = _create_app(client, alice, job_id).json()["id"]

    resp = client.patch(
        f"/applications/{app_id}", headers=_auth(bob), json={"to_status": "APPLIED"}
    )
    assert resp.status_code == 404


# ---------- Save shortcut ----------

def test_save_job_creates_application(client):
    token = _token(client)
    job_id = _make_job(client, token)
    resp = client.post(f"/jobs/{job_id}/save", headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json()["current_status"] == "SAVED"


def test_save_job_is_idempotent(client):
    token = _token(client)
    job_id = _make_job(client, token)
    first = client.post(f"/jobs/{job_id}/save", headers=_auth(token)).json()
    second = client.post(f"/jobs/{job_id}/save", headers=_auth(token)).json()
    assert first["id"] == second["id"]


# ---------- Delete ----------

def test_delete_application(client):
    token = _token(client)
    job_id = _make_job(client, token)
    app_id = _create_app(client, token, job_id).json()["id"]

    assert client.delete(f"/applications/{app_id}", headers=_auth(token)).status_code == 204
    assert client.get(f"/applications/{app_id}", headers=_auth(token)).status_code == 404