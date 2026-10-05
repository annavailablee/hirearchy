import io

from tests._pdf_helper import make_minimal_pdf


_counter = [0]


def _unique_email():
    _counter[0] += 1
    return f"insights_test_{_counter[0]}@example.com"


def _token(client) -> str:
    email = _unique_email()
    client.post("/auth/register", json={"email": email, "password": "supersecret123"})
    resp = client.post("/auth/login", json={"email": email, "password": "supersecret123"})
    return resp.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _make_job(client, token, title, description) -> str:
    resp = client.post(
        "/jobs",
        headers=_auth(token),
        json={"title": title, "company": "X", "description": description},
    )
    return resp.json()["id"]


def _save(client, token, job_id):
    return client.post(f"/jobs/{job_id}/save", headers=_auth(token))


def _upload_resume(client, token, text):
    return client.post(
        "/resumes",
        headers=_auth(token),
        files={"file": ("r.pdf", io.BytesIO(make_minimal_pdf(text)), "application/pdf")},
        data={"name": "TestResume"},
    )


# ---------- Basic ----------

def test_no_jobs_returns_empty(client):
    token = _token(client)
    _upload_resume(client, token, "Python SQL")
    resp = client.get("/insights/skills", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["jobs_analyzed"] == 0
    assert body["skills"] == []


def test_single_saved_job_analyzed(client):
    token = _token(client)
    _upload_resume(client, token, "Python SQL")
    jid = _make_job(client, token, "Backend Intern", "Python FastAPI PostgreSQL")
    _save(client, token, jid)

    resp = client.get("/insights/skills", headers=_auth(token))
    body = resp.json()
    assert body["jobs_analyzed"] == 1
    canonicals = {s["canonical"] for s in body["skills"]}
    assert {"Python", "FastAPI", "PostgreSQL"} <= canonicals


# ---------- Strengths / gaps ----------

def test_strength_when_user_has_skill(client):
    token = _token(client)
    _upload_resume(client, token, "Python")
    jid = _make_job(client, token, "Job", "Python")
    _save(client, token, jid)

    body = client.get("/insights/skills", headers=_auth(token)).json()
    assert "Python" in body["strengths"]
    assert "Python" not in body["gaps"]


def test_gap_when_user_lacks_skill(client):
    token = _token(client)
    _upload_resume(client, token, "Python")  # user does NOT have Docker
    jid = _make_job(client, token, "Job", "Python and Docker required")
    _save(client, token, jid)

    body = client.get("/insights/skills", headers=_auth(token)).json()
    assert "Docker" in body["gaps"]
    assert "Docker" not in body["strengths"]


def test_low_frequency_skill_not_reported_as_gap(client):
    """Skill appearing in only 1 of 10 jobs should not be a 'gap'."""
    token = _token(client)
    _upload_resume(client, token, "Python")

    # 10 jobs total; only one mentions Docker
    for i in range(9):
        jid = _make_job(client, token, f"Python Job {i}", "Python SQL")
        _save(client, token, jid)
    rare_jid = _make_job(client, token, "Rare", "Docker")
    _save(client, token, rare_jid)

    body = client.get("/insights/skills", headers=_auth(token)).json()
    # Docker at 10% is below the 20% threshold
    assert "Docker" not in body["gaps"]
    # But it still shows in the raw skills list
    docker = next((s for s in body["skills"] if s["canonical"] == "Docker"), None)
    assert docker is not None
    assert docker["frequency_pct"] == 10.0


def test_significant_gap_is_reported(client):
    """Skill appearing in 4 of 5 jobs (80%) IS a gap if user lacks it."""
    token = _token(client)
    _upload_resume(client, token, "Python")

    for i in range(4):
        jid = _make_job(client, token, f"Python+Docker {i}", "Python Docker")
        _save(client, token, jid)
    jid = _make_job(client, token, "Python only", "Python")
    _save(client, token, jid)

    body = client.get("/insights/skills", headers=_auth(token)).json()
    assert "Docker" in body["gaps"]


# ---------- Frequency ----------

def test_frequency_pct_is_correct(client):
    token = _token(client)
    _upload_resume(client, token, "Python")

    # 4 jobs: 3 mention Python, 1 doesn't
    for i in range(3):
        jid = _make_job(client, token, f"P{i}", "Python")
        _save(client, token, jid)
    jid = _make_job(client, token, "JavaRole", "Java")
    _save(client, token, jid)

    body = client.get("/insights/skills", headers=_auth(token)).json()
    python = next(s for s in body["skills"] if s["canonical"] == "Python")
    assert python["frequency"] == 3
    assert python["frequency_pct"] == 75.0


# ---------- Rejected jobs excluded ----------

def test_rejected_applications_not_counted(client):
    token = _token(client)
    _upload_resume(client, token, "Python")

    jid1 = _make_job(client, token, "Keep", "Python")
    jid2 = _make_job(client, token, "Discard", "Docker")

    _save(client, token, jid1)
    _save(client, token, jid2)

    # Transition jid2's application to REJECTED via PATCH.
    # Need to find the application id first.
    apps = client.get("/applications", headers=_auth(token)).json()
    rejected_app = next(a for a in apps if a["job_id"] == jid2)
    client.patch(
        f"/applications/{rejected_app['id']}",
        headers=_auth(token),
        json={"to_status": "REJECTED"},
    )

    body = client.get("/insights/skills", headers=_auth(token)).json()
    assert body["jobs_analyzed"] == 1
    canonicals = {s["canonical"] for s in body["skills"]}
    assert "Python" in canonicals
    assert "Docker" not in canonicals


# ---------- Isolation ----------

def test_insights_isolated_between_users(client):
    alice = _token(client)
    bob = _token(client)

    _upload_resume(client, alice, "Python")
    _upload_resume(client, bob, "Java")

    ajid = _make_job(client, alice, "AliceJob", "Python")
    bjid = _make_job(client, bob, "BobJob", "Java")
    _save(client, alice, ajid)
    _save(client, bob, bjid)

    a_body = client.get("/insights/skills", headers=_auth(alice)).json()
    b_body = client.get("/insights/skills", headers=_auth(bob)).json()

    assert a_body["jobs_analyzed"] == 1
    assert b_body["jobs_analyzed"] == 1
    a_canonicals = {s["canonical"] for s in a_body["skills"]}
    b_canonicals = {s["canonical"] for s in b_body["skills"]}
    assert "Python" in a_canonicals and "Python" not in b_canonicals
    assert "Java" in b_canonicals and "Java" not in a_canonicals


# ---------- Applications insight ----------

def test_application_insights_empty(client):
    token = _token(client)
    resp = client.get("/insights/applications", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 0
    assert body["response_rate_pct"] == 0.0


def test_application_insights_counts_by_status(client):
    token = _token(client)
    j1 = _make_job(client, token, "J1", "Python")
    j2 = _make_job(client, token, "J2", "Python")
    _save(client, token, j1)
    _save(client, token, j2)

    apps = client.get("/applications", headers=_auth(token)).json()
    client.patch(
        f"/applications/{apps[0]['id']}",
        headers=_auth(token),
        json={"to_status": "APPLIED"},
    )

    resp = client.get("/insights/applications", headers=_auth(token)).json()
    assert resp["total"] == 2
    assert resp["by_status"].get("SAVED") == 1
    assert resp["by_status"].get("APPLIED") == 1