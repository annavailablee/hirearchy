def _token(client, email="alice@example.com") -> str:
    client.post("/auth/register", json={"email": email, "password": "supersecret123"})
    resp = client.post("/auth/login", json={"email": email, "password": "supersecret123"})
    return resp.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_job(client, token, **overrides):
    payload = {
        "title": "Backend Engineer Intern",
        "company": "Acme Corp",
        "description": "We need Python, FastAPI, PostgreSQL, Docker and AWS.",
        "location": "Bangalore",
        "remote_type": "hybrid",
        "employment_type": "internship",
    }
    payload.update(overrides)
    return client.post("/jobs", headers=_auth(token), json=payload)


# ---------- Create ----------

def test_create_job_succeeds(client):
    token = _token(client)
    resp = _create_job(client, token)
    assert resp.status_code == 201, resp.text

    body = resp.json()
    assert body["title"] == "Backend Engineer Intern"
    assert body["company"] == "Acme Corp"
    assert body["source"] == "manual"


def test_create_job_extracts_skills(client):
    token = _token(client)
    resp = _create_job(client, token)
    assert resp.status_code == 201

    canonicals = {s["canonical"] for s in resp.json()["skills"]}
    assert {"Python", "FastAPI", "PostgreSQL", "Docker", "AWS"} <= canonicals


def test_create_job_requires_auth(client):
    resp = client.post("/jobs", json={"title": "x", "company": "y"})
    assert resp.status_code == 401


def test_create_job_validates_required_fields(client):
    token = _token(client)
    resp = client.post("/jobs", headers=_auth(token), json={"title": "only title"})
    assert resp.status_code == 422


def test_create_job_duplicate_url_returns_409(client):
    token = _token(client)
    url = "https://example.com/jobs/123"
    assert _create_job(client, token, source_url=url).status_code == 201
    resp = _create_job(client, token, source_url=url)
    assert resp.status_code == 409


def test_create_job_no_url_allows_duplicates(client):
    """Two manual jobs without a source_url are allowed — no way to detect dupe."""
    token = _token(client)
    assert _create_job(client, token).status_code == 201
    assert _create_job(client, token).status_code == 201


# ---------- List ----------

def test_list_jobs_returns_both_jobs(client):
    token = _token(client)
    _create_job(client, token, title="TestAlpha", company="TestCoA")
    _create_job(client, token, title="TestBeta", company="TestCoB")

    body = client.get("/jobs", headers=_auth(token)).json()
    titles = {j["title"] for j in body}
    # Only assert about jobs we created.
    assert {"TestAlpha", "TestBeta"} <= titles


def test_list_jobs_filters_by_search(client):
    token = _token(client)
    _create_job(client, token, title="UniqueFrontendRole99", company="X")
    _create_job(client, token, title="UniqueBackendRole77", company="Y")

    # Search term is guaranteed unique — won't collide with any pre-existing data.
    body = client.get("/jobs?q=UniqueBackendRole77", headers=_auth(token)).json()
    assert len(body) == 1
    assert body[0]["title"] == "UniqueBackendRole77"


def test_list_jobs_filters_by_remote_type(client):
    token = _token(client)
    _create_job(client, token, title="TestRemoteOnly", remote_type="remote")
    _create_job(client, token, title="TestOnsiteOnly", remote_type="onsite")

    body = client.get("/jobs?remote_type=remote", headers=_auth(token)).json()
    titles = {j["title"] for j in body}
    assert "TestRemoteOnly" in titles
    assert "TestOnsiteOnly" not in titles


def test_list_jobs_pagination(client):
    token = _token(client)
    for i in range(5):
        _create_job(client, token, title=f"PaginationTest{i}", company="X")

    body = client.get("/jobs?limit=2&offset=0", headers=_auth(token)).json()
    # We asked for limit=2, so we get exactly 2 — regardless of total count.
    assert len(body) == 2


def test_list_jobs_requires_auth(client):
    assert client.get("/jobs").status_code == 401


# ---------- Detail ----------

def test_get_job_detail(client):
    token = _token(client)
    job_id = _create_job(client, token).json()["id"]

    resp = client.get(f"/jobs/{job_id}", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["description"] is not None
    assert isinstance(body["skills"], list)


def test_get_job_not_found(client):
    token = _token(client)
    resp = client.get("/jobs/00000000-0000-0000-0000-000000000000", headers=_auth(token))
    assert resp.status_code == 404


# ---------- Cross-user visibility ----------

def test_any_user_can_view_any_job(client):
    alice = _token(client, email="alice@example.com")
    bob = _token(client, email="bob@example.com")

    job_id = _create_job(client, alice).json()["id"]
    resp = client.get(f"/jobs/{job_id}", headers=_auth(bob))
    assert resp.status_code == 200


# ---------- Delete ----------

def test_creator_can_delete_own_job(client):
    token = _token(client)
    job_id = _create_job(client, token).json()["id"]
    assert client.delete(f"/jobs/{job_id}", headers=_auth(token)).status_code == 204
    assert client.get(f"/jobs/{job_id}", headers=_auth(token)).status_code == 404


def test_non_creator_cannot_delete(client):
    alice = _token(client, email="alice@example.com")
    bob = _token(client, email="bob@example.com")
    job_id = _create_job(client, alice).json()["id"]

    resp = client.delete(f"/jobs/{job_id}", headers=_auth(bob))
    assert resp.status_code == 403

    # And the job still exists for Alice
    assert client.get(f"/jobs/{job_id}", headers=_auth(alice)).status_code == 200