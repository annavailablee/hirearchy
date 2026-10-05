from datetime import datetime, timedelta, timezone


_counter = [0]


def _unique_email():
    _counter[0] += 1
    return f"dash_{_counter[0]}@example.com"


def _token(client) -> str:
    email = _unique_email()
    client.post("/auth/register", json={"email": email, "password": "supersecret123"})
    resp = client.post(
        "/auth/login", json={"email": email, "password": "supersecret123"}
    )
    return resp.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_job(client, token, title="Backend Intern", description="Python"):
    return client.post(
        "/jobs",
        headers=_auth(token),
        json={"title": title, "company": "Acme", "description": description},
    ).json()


def _save(client, token, job_id):
    return client.post(f"/jobs/{job_id}/save", headers=_auth(token)).json()


def _deadline(client, token, **overrides):
    payload = {
        "title": "Test",
        "kind": "custom",
        "due_at": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
    }
    payload.update(overrides)
    return client.post("/deadlines", headers=_auth(token), json=payload).json()


# ---------- Shape ----------

def test_dashboard_empty(client):
    token = _token(client)
    resp = client.get("/dashboard", headers=_auth(token))
    assert resp.status_code == 200

    body = resp.json()
    assert body["applications"]["total"] == 0
    assert body["attention"]["overdue_count"] == 0
    assert body["attention"]["urgent_count"] == 0
    assert body["upcoming"] == []
    assert body["top_skills"] == []
    assert body["gaps"] == []


def test_dashboard_requires_auth(client):
    assert client.get("/dashboard").status_code == 401


# ---------- Applications section ----------

def test_dashboard_counts_applications(client):
    token = _token(client)
    j1 = _create_job(client, token, "J1")
    j2 = _create_job(client, token, "J2")
    _save(client, token, j1["id"])
    _save(client, token, j2["id"])

    body = client.get("/dashboard", headers=_auth(token)).json()
    assert body["applications"]["total"] == 2
    assert body["applications"]["by_status"]["SAVED"] == 2


# ---------- Attention section ----------

def test_dashboard_reports_overdue_and_urgent(client):
    token = _token(client)
    # overdue
    _deadline(client, token, title="Overdue",
              due_at=(datetime.now(timezone.utc) - timedelta(hours=3)).isoformat())
    # urgent
    _deadline(client, token, title="Due soon",
              due_at=(datetime.now(timezone.utc) + timedelta(hours=10)).isoformat())

    body = client.get("/dashboard", headers=_auth(token)).json()
    assert body["attention"]["overdue_count"] == 1
    assert body["attention"]["urgent_count"] == 1
    assert len(body["attention"]["top_items"]) == 2


# ---------- Upcoming section ----------

def test_dashboard_upcoming_joins_job_info(client):
    token = _token(client)
    job = _create_job(client, token, title="QA Engineer", description="Python")
    app = _save(client, token, job["id"])

    _deadline(
        client, token,
        title="Online Assessment",
        kind="assessment",
        application_id=app["id"],
        due_at=(datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
    )

    body = client.get("/dashboard", headers=_auth(token)).json()
    assert len(body["upcoming"]) == 1
    item = body["upcoming"][0]
    assert item["title"] == "Online Assessment"
    assert item["job_title"] == "QA Engineer"
    assert item["company"] == "Acme"


def test_dashboard_upcoming_excludes_past(client):
    token = _token(client)
    _deadline(client, token, title="Past",
              due_at=(datetime.now(timezone.utc) - timedelta(hours=1)).isoformat())
    _deadline(client, token, title="Future",
              due_at=(datetime.now(timezone.utc) + timedelta(days=2)).isoformat())

    body = client.get("/dashboard", headers=_auth(token)).json()
    titles = {u["title"] for u in body["upcoming"]}
    assert "Future" in titles
    assert "Past" not in titles


def test_dashboard_upcoming_excludes_completed(client):
    token = _token(client)
    d = _deadline(client, token, title="Done",
                  due_at=(datetime.now(timezone.utc) + timedelta(days=2)).isoformat())
    client.patch(f"/deadlines/{d['id']}", headers=_auth(token), json={"completed": True})

    body = client.get("/dashboard", headers=_auth(token)).json()
    assert body["upcoming"] == []


# ---------- Skills section ----------

def test_dashboard_top_skills_populated(client):
    token = _token(client)
    for i in range(3):
        j = _create_job(client, token, f"J{i}", "Python FastAPI SQL")
        _save(client, token, j["id"])

    body = client.get("/dashboard", headers=_auth(token)).json()
    canonicals = {s["canonical"] for s in body["top_skills"]}
    assert "Python" in canonicals


def test_dashboard_gaps_populated(client):
    token = _token(client)
    for i in range(3):
        j = _create_job(client, token, f"J{i}", "Docker Kubernetes")
        _save(client, token, j["id"])

    # No resume uploaded → user has no skills → all significant skills are gaps
    body = client.get("/dashboard", headers=_auth(token)).json()
    assert "Docker" in body["gaps"]
    assert "Kubernetes" in body["gaps"]


# ---------- Isolation ----------

def test_dashboard_is_isolated(client):
    alice = _token(client)
    bob = _token(client)

    j = _create_job(client, alice, "Alice Job")
    _save(client, alice, j["id"])

    alice_dash = client.get("/dashboard", headers=_auth(alice)).json()
    bob_dash = client.get("/dashboard", headers=_auth(bob)).json()

    assert alice_dash["applications"]["total"] == 1
    assert bob_dash["applications"]["total"] == 0