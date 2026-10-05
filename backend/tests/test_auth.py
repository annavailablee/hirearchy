
VALID_USER = {
    "email": "alice@example.com",
    "password": "supersecret123",
    "full_name": "Alice Doe",
}


def register(client, **overrides):
    payload = {**VALID_USER, **overrides}
    return client.post("/auth/register", json=payload)


def login(client, email=None, password=None):
    return client.post(
        "/auth/login",
        json={
            "email": email or VALID_USER["email"],
            "password": password or VALID_USER["password"],
        },
    )


# ---------- Registration ----------

def test_register_creates_user(client):
    resp = register(client)
    assert resp.status_code == 201

    body = resp.json()
    assert body["email"] == "alice@example.com"
    assert body["full_name"] == "Alice Doe"
    assert body["is_active"] is True
    assert "id" in body
    assert "created_at" in body


def test_register_never_leaks_hashed_password(client):
    resp = register(client)
    assert resp.status_code == 201
    assert "hashed_password" not in resp.json()
    assert "password" not in resp.json()


def test_register_normalizes_email_to_lowercase(client):
    resp = register(client, email="ALICE@EXAMPLE.COM")
    assert resp.status_code == 201
    assert resp.json()["email"] == "alice@example.com"


def test_register_duplicate_email_returns_409(client):
    assert register(client).status_code == 201
    resp = register(client)
    assert resp.status_code == 409


def test_register_duplicate_email_is_case_insensitive(client):
    assert register(client, email="Alice@Example.com").status_code == 201
    resp = register(client, email="alice@example.com")
    assert resp.status_code == 409


def test_register_invalid_email_returns_422(client):
    resp = register(client, email="not-an-email")
    assert resp.status_code == 422


def test_register_short_password_returns_422(client):
    resp = register(client, password="short")
    assert resp.status_code == 422


def test_register_missing_fields_returns_422(client):
    resp = client.post("/auth/register", json={})
    assert resp.status_code == 422


# ---------- Login ----------

def test_login_returns_token(client):
    register(client)
    resp = login(client)
    assert resp.status_code == 200

    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password_returns_401(client):
    register(client)
    resp = login(client, password="wrongpassword")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"


def test_login_unknown_email_returns_401(client):
    resp = login(client, email="nobody@example.com")
    assert resp.status_code == 401


def test_login_unknown_email_and_wrong_password_have_identical_response(client):
    """
    User enumeration guard: the response must be indistinguishable
    whether the email doesn't exist or the password is wrong.
    """
    register(client)
    wrong_pw = login(client, password="wrongpassword")
    unknown  = login(client, email="nobody@example.com", password="wrongpassword")

    assert wrong_pw.status_code == unknown.status_code
    assert wrong_pw.json() == unknown.json()


# ---------- /auth/me ----------

def _auth_header(client) -> dict:
    register(client)
    token = login(client).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_me_with_valid_token_returns_user(client):
    headers = _auth_header(client)
    resp = client.get("/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == VALID_USER["email"]


def test_me_without_token_returns_401(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_me_with_garbage_token_returns_401(client):
    resp = client.get("/auth/me", headers={"Authorization": "Bearer garbage"})
    assert resp.status_code == 401


def test_me_with_malformed_header_returns_401(client):
    resp = client.get("/auth/me", headers={"Authorization": "NotBearer foo"})
    assert resp.status_code == 401


# ---------- Isolation ----------

def test_user_isolation_between_tests_a(client):
    """First half of an isolation check. Creates a user."""
    assert register(client).status_code == 201


def test_user_isolation_between_tests_b(client):
    """
    Second half. If isolation works, the previous test's user should
    NOT be present — the transaction was rolled back.
    """
    # Same email should be registerable again — proving the first test was rolled back.
    assert register(client).status_code == 201