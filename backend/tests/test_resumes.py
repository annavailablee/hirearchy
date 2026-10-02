import io

from tests._pdf_helper import make_minimal_pdf


def _token(client, email="alice@example.com") -> str:
    client.post("/auth/register", json={"email": email, "password": "supersecret123"})
    resp = client.post("/auth/login", json={"email": email, "password": "supersecret123"})
    return resp.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _upload(client, token, name="General", filename="resume.pdf", content=None):
    if content is None:
        content = make_minimal_pdf("Jane Doe Python SQL FastAPI")
    return client.post(
        "/resumes",
        headers=_auth(token),
        files={"file": (filename, io.BytesIO(content), "application/pdf")},
        data={"name": name},
    )


# ---------- Upload ----------

def test_upload_pdf_stores_and_extracts(client):
    token = _token(client)
    resp = _upload(client, token, name="General")
    assert resp.status_code == 201, resp.text

    body = resp.json()
    assert body["name"] == "General"
    assert body["extraction_status"] == "success"
    assert body["is_primary"] is True
    assert body["file_size"] > 0
    assert "Jane Doe" in (body["raw_text"] or "")


def test_upload_rejects_empty_file(client):
    token = _token(client)
    resp = _upload(client, token, content=b"")
    assert resp.status_code == 422


def test_upload_rejects_non_pdf(client):
    """A file that isn't a PDF should be rejected by magic bytes."""
    token = _token(client)
    resp = _upload(client, token, content=b"#!/bin/sh\necho hi")
    assert resp.status_code == 422
    assert "PDF" in resp.json()["detail"]


def test_upload_rejects_oversized_file(client, monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "max_resume_size_bytes", 100)

    token = _token(client)
    big = make_minimal_pdf("x" * 500)
    resp = _upload(client, token, content=big)
    assert resp.status_code == 413


def test_upload_rejects_duplicate_name(client):
    token = _token(client)
    assert _upload(client, token, name="Backend").status_code == 201
    resp = _upload(client, token, name="Backend")
    assert resp.status_code == 409


def test_upload_second_resume_is_not_primary(client):
    token = _token(client)
    _upload(client, token, name="General")
    resp = _upload(client, token, name="Backend")
    assert resp.json()["is_primary"] is False


# ---------- List / Detail ----------

def test_list_resumes_returns_only_own(client):
    alice = _token(client, email="alice@example.com")
    bob = _token(client, email="bob@example.com")

    _upload(client, alice, name="Alice Resume")
    _upload(client, bob, name="Bob Resume")

    alice_list = client.get("/resumes", headers=_auth(alice)).json()
    bob_list = client.get("/resumes", headers=_auth(bob)).json()

    assert len(alice_list) == 1
    assert alice_list[0]["name"] == "Alice Resume"
    assert bob_list[0]["name"] == "Bob Resume"


def test_list_does_not_expose_raw_text(client):
    token = _token(client)
    _upload(client, token)
    body = client.get("/resumes", headers=_auth(token)).json()
    assert "raw_text" not in body[0]


def test_detail_exposes_raw_text(client):
    token = _token(client)
    resume_id = _upload(client, token).json()["id"]
    resp = client.get(f"/resumes/{resume_id}", headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json()["raw_text"]


# ---------- Isolation ----------

def test_cannot_read_other_users_resume(client):
    alice = _token(client, email="alice@example.com")
    bob = _token(client, email="bob@example.com")

    resume_id = _upload(client, alice).json()["id"]

    # Bob tries to read Alice's resume. Must be 404, not 403.
    resp = client.get(f"/resumes/{resume_id}", headers=_auth(bob))
    assert resp.status_code == 404


def test_cannot_delete_other_users_resume(client):
    alice = _token(client, email="alice@example.com")
    bob = _token(client, email="bob@example.com")

    resume_id = _upload(client, alice).json()["id"]
    resp = client.delete(f"/resumes/{resume_id}", headers=_auth(bob))
    assert resp.status_code == 404

    # And the resume is still there for Alice.
    assert client.get(f"/resumes/{resume_id}", headers=_auth(alice)).status_code == 200


# ---------- Update ----------

def test_rename_resume(client):
    token = _token(client)
    resume_id = _upload(client, token, name="General").json()["id"]

    resp = client.patch(
        f"/resumes/{resume_id}",
        headers=_auth(token),
        json={"name": "Backend"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Backend"


def test_rename_conflict_with_existing(client):
    token = _token(client)
    _upload(client, token, name="General")
    backend_id = _upload(client, token, name="Backend").json()["id"]

    resp = client.patch(
        f"/resumes/{backend_id}",
        headers=_auth(token),
        json={"name": "General"},
    )
    assert resp.status_code == 409


def test_set_primary_demotes_others(client):
    token = _token(client)
    first = _upload(client, token, name="General").json()["id"]
    second = _upload(client, token, name="Backend").json()["id"]

    # Second is not primary yet
    assert client.get(f"/resumes/{second}", headers=_auth(token)).json()["is_primary"] is False

    # Make it primary
    client.patch(f"/resumes/{second}", headers=_auth(token), json={"is_primary": True})

    assert client.get(f"/resumes/{second}", headers=_auth(token)).json()["is_primary"] is True
    assert client.get(f"/resumes/{first}", headers=_auth(token)).json()["is_primary"] is False


# ---------- Delete ----------

def test_delete_removes_resume(client):
    token = _token(client)
    resume_id = _upload(client, token).json()["id"]

    assert client.delete(f"/resumes/{resume_id}", headers=_auth(token)).status_code == 204
    assert client.get(f"/resumes/{resume_id}", headers=_auth(token)).status_code == 404


# ---------- Auth ----------

def test_upload_requires_auth(client):
    resp = client.post(
        "/resumes",
        files={"file": ("r.pdf", io.BytesIO(make_minimal_pdf()), "application/pdf")},
        data={"name": "x"},
    )
    assert resp.status_code == 401