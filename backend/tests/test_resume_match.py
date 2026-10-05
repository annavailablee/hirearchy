import io

from tests._pdf_helper import make_minimal_pdf

_counter = [0]


def _unique_email():
    _counter[0] += 1
    return f"resmatch_{_counter[0]}@example.com"


def _token(client) -> str:
    email = _unique_email()
    client.post("/auth/register", json={"email": email, "password": "supersecret123"})
    resp = client.post(
        "/auth/login", json={"email": email, "password": "supersecret123"}
    )
    return resp.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _make_job(client, token, description) -> str:
    return client.post(
        "/jobs",
        headers=_auth(token),
        json={"title": "Engineer", "company": "X", "description": description},
    ).json()["id"]


def _upload(client, token, name, text):
    return client.post(
        "/resumes",
        headers=_auth(token),
        files={"file": ("r.pdf", io.BytesIO(make_minimal_pdf(text)), "application/pdf")},
        data={"name": name},
    ).json()


def _best_resume(client, token, job_id):
    return client.get(f"/jobs/{job_id}/best-resume", headers=_auth(token))


# ---------- Basics ----------

def test_best_resume_requires_job_to_exist(client):
    token = _token(client)
    _upload(client, token, "R", "Python")
    resp = _best_resume(client, token, "00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_best_resume_requires_at_least_one_resume(client):
    token = _token(client)
    job_id = _make_job(client, token, "Python")
    resp = _best_resume(client, token, job_id)
    assert resp.status_code == 400
    assert "No resumes" in resp.json()["detail"]


def test_single_resume_is_recommended(client):
    token = _token(client)
    r = _upload(client, token, "General", "Python FastAPI")
    job_id = _make_job(client, token, "We need Python and FastAPI.")

    body = _best_resume(client, token, job_id).json()
    assert len(body["resumes"]) == 1
    assert body["resumes"][0]["id"] == r["id"]
    assert body["resumes"][0]["is_recommended"] is True
    assert body["resumes"][0]["score"] > 0


# ---------- Ranking ----------

def test_higher_scoring_resume_is_recommended(client):
    token = _token(client)
    # Backend resume matches the job better than the general one
    _upload(client, token, "General", "Java Spring Angular")
    backend = _upload(client, token, "Backend", "Python FastAPI PostgreSQL Docker")
    job_id = _make_job(client, token, "Python FastAPI PostgreSQL Docker required.")

    body = _best_resume(client, token, job_id).json()
    assert body["resumes"][0]["id"] == backend["id"]
    assert body["resumes"][0]["is_recommended"] is True
    # Others not recommended
    assert all(not r["is_recommended"] for r in body["resumes"][1:])


def test_ranking_is_sorted_by_score_desc(client):
    token = _token(client)
    _upload(client, token, "Low", "Java")
    _upload(client, token, "High", "Python FastAPI SQL Docker AWS")
    _upload(client, token, "Mid", "Python FastAPI")
    job_id = _make_job(
        client, token, "Python FastAPI SQL Docker AWS required."
    )

    body = _best_resume(client, token, job_id).json()
    scores = [r["score"] for r in body["resumes"]]
    assert scores == sorted(scores, reverse=True)
    assert body["resumes"][0]["name"] == "High"


def test_primary_breaks_ties(client):
    token = _token(client)
    # Same skill content → same score. Second upload is not primary by default.
    _upload(client, token, "First", "Python")
    second = _upload(client, token, "Second", "Python")

    # Make second primary explicitly
    client.patch(f"/resumes/{second['id']}", headers=_auth(token), json={"is_primary": True})

    job_id = _make_job(client, token, "Python")
    body = _best_resume(client, token, job_id).json()
    # Ties broken by primary → Second should be first
    assert body["resumes"][0]["name"] == "Second"


# ---------- Matched / missing skills ----------

def test_matched_skills_are_reported(client):
    token = _token(client)
    _upload(client, token, "R", "Python FastAPI PostgreSQL")
    job_id = _make_job(client, token, "Python FastAPI PostgreSQL AWS Docker required.")

    body = _best_resume(client, token, job_id).json()
    summary = body["resumes"][0]
    assert set(summary["matched_skills"]) == {"Python", "FastAPI", "PostgreSQL"}
    assert set(summary["missing_skills"]) == {"AWS", "Docker"}


# ---------- Isolation ----------

def test_only_users_own_resumes_are_ranked(client):
    alice = _token(client)
    bob = _token(client)

    _upload(client, alice, "AliceResume", "Python")
    _upload(client, bob, "BobResume", "Java")

    # Job created by alice
    job_id = _make_job(client, alice, "Python required")

    body = _best_resume(client, alice, job_id).json()
    names = {r["name"] for r in body["resumes"]}
    assert names == {"AliceResume"}

    body_bob = _best_resume(client, bob, job_id).json()
    names_bob = {r["name"] for r in body_bob["resumes"]}
    assert names_bob == {"BobResume"}


def test_failed_extraction_resume_is_excluded_from_recommendation(client, db):
    """
    Force a resume with a failed extraction by uploading a valid PDF whose text
    we then clear in the DB — simulates a scanned resume.
    """
    from app.models.resume import Resume

    token = _token(client)
    good = _upload(client, token, "Good", "Python FastAPI")
    bad = _upload(client, token, "Bad", "Python FastAPI")

    # Force 'bad' to look like a failed extraction.
    r = db.get(Resume, bad["id"])
    r.extraction_status = "failed"
    r.raw_text = None
    db.commit()

    job_id = _make_job(client, token, "Python FastAPI required.")
    body = _best_resume(client, token, job_id).json()

    by_id = {str(r["id"]): r for r in body["resumes"]}
    assert by_id[str(good["id"])]["is_recommended"] is True
    assert by_id[str(bad["id"])]["is_recommended"] is False
    assert by_id[str(bad["id"])]["note"] is not None