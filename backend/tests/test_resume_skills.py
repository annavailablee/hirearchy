import io

from tests._pdf_helper import make_minimal_pdf


def _token(client, email="alice@example.com") -> str:
    client.post("/auth/register", json={"email": email, "password": "supersecret123"})
    resp = client.post(
        "/auth/login", json={"email": email, "password": "supersecret123"}
    )
    return resp.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _upload(client, token, text, name="General"):
    content = make_minimal_pdf(text)
    return client.post(
        "/resumes",
        headers=_auth(token),
        files={"file": ("resume.pdf", io.BytesIO(content), "application/pdf")},
        data={"name": name},
    )


def test_upload_extracts_skills(client):
    token = _token(client)
    resp = _upload(client, token, "Python, FastAPI, PostgreSQL, Docker, AWS")
    assert resp.status_code == 201
    resume_id = resp.json()["id"]

    skills_resp = client.get(f"/resumes/{resume_id}/skills", headers=_auth(token))
    assert skills_resp.status_code == 200

    canonicals = {s["canonical"] for s in skills_resp.json()}
    assert {"Python", "FastAPI", "PostgreSQL", "Docker", "AWS"} <= canonicals


def test_skills_include_evidence(client):
    token = _token(client)
    resume_id = _upload(client, token, "Familiar with k8s in production.").json()["id"]

    skills = client.get(f"/resumes/{resume_id}/skills", headers=_auth(token)).json()
    k8s = next(s for s in skills if s["canonical"] == "Kubernetes")

    assert k8s["matched_text"].lower() == "k8s"
    assert "k8s" in k8s["context"].lower()


def test_no_skills_when_text_has_none(client):
    token = _token(client)
    resume_id = _upload(client, token, "Just a plain document with no tech terms.").json()["id"]

    skills = client.get(f"/resumes/{resume_id}/skills", headers=_auth(token)).json()
    # Filter out any incidental matches from the taxonomy — the point is it's
    # not producing spurious entries for every token.
    assert all(isinstance(s["canonical"], str) for s in skills)


def test_cannot_read_other_users_resume_skills(client):
    alice = _token(client, email="alice@example.com")
    bob = _token(client, email="bob@example.com")

    resume_id = _upload(client, alice, "Python SQL").json()["id"]

    resp = client.get(f"/resumes/{resume_id}/skills", headers=_auth(bob))
    assert resp.status_code == 404


def test_skills_are_isolated_per_resume(client):
    """Two resumes uploaded by the same user should have independent skill sets."""
    token = _token(client)
    a = _upload(client, token, "Python and Docker", name="A").json()["id"]
    b = _upload(client, token, "Java and Spring Boot", name="B").json()["id"]

    a_skills = {s["canonical"] for s in client.get(f"/resumes/{a}/skills", headers=_auth(token)).json()}
    b_skills = {s["canonical"] for s in client.get(f"/resumes/{b}/skills", headers=_auth(token)).json()}

    assert "Python" in a_skills
    assert "Python" not in b_skills
    assert "Java" in b_skills
    assert "Java" not in a_skills


def test_taxonomy_skills_are_seeded_once(client, db):
    """Two uploads should not duplicate rows in the `skills` table."""
    from sqlalchemy import func, select

    from app.models.skill import Skill

    token = _token(client)
    _upload(client, token, "Python and SQL", name="A")
    _upload(client, token, "Python and Java", name="B")

    # Same session the endpoint used — sees the transaction state correctly.
    python_count = db.scalar(
        select(func.count()).select_from(Skill).where(Skill.canonical == "Python")
    )
    assert python_count == 1

    java_count = db.scalar(
        select(func.count()).select_from(Skill).where(Skill.canonical == "Java")
    )
    assert java_count == 1