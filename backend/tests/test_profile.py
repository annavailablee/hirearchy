

def _register_and_login(client, email="alice@example.com") -> str:
    client.post("/auth/register", json={"email": email, "password": "supersecret123"})
    resp = client.post("/auth/login", json={"email": email, "password": "supersecret123"})
    return resp.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_profile_is_created_on_registration(client):
    token = _register_and_login(client)
    resp = client.get("/profile", headers=_auth(token))
    assert resp.status_code == 200

    body = resp.json()
    # All array fields default to empty lists, not null.
    assert body["preferred_locations"] == []
    assert body["target_roles"] == []
    assert body["preferred_employment_types"] == []
    assert body["education"] is None


def test_get_profile_without_auth_returns_401(client):
    resp = client.get("/profile")
    assert resp.status_code == 401


def test_update_profile_single_field(client):
    token = _register_and_login(client)
    resp = client.put(
        "/profile",
        headers=_auth(token),
        json={"education": "B.Tech"},
    )
    assert resp.status_code == 200
    assert resp.json()["education"] == "B.Tech"


def test_update_profile_does_not_clear_unsent_fields(client):
    """PUT with partial body should not null out other fields."""
    token = _register_and_login(client)

    client.put(
        "/profile",
        headers=_auth(token),
        json={"education": "B.Tech", "current_location": "Bangalore"},
    )
    # Second update touches only education; location must survive.
    resp = client.put("/profile", headers=_auth(token), json={"education": "M.Tech"})

    body = resp.json()
    assert body["education"] == "M.Tech"
    assert body["current_location"] == "Bangalore"


def test_update_profile_explicit_null_clears_field(client):
    token = _register_and_login(client)
    client.put("/profile", headers=_auth(token), json={"education": "B.Tech"})
    resp = client.put("/profile", headers=_auth(token), json={"education": None})
    assert resp.status_code == 200
    assert resp.json()["education"] is None


def test_update_profile_arrays(client):
    token = _register_and_login(client)
    resp = client.put(
        "/profile",
        headers=_auth(token),
        json={
            "preferred_locations": ["Bangalore", "Remote"],
            "target_roles": ["Backend Engineer", "AI Engineer"],
            "preferred_employment_types": ["internship", "full-time"],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["preferred_locations"] == ["Bangalore", "Remote"]
    assert body["target_roles"] == ["Backend Engineer", "AI Engineer"]
    assert body["preferred_employment_types"] == ["internship", "full-time"]


def test_update_profile_invalid_enum_returns_422(client):
    token = _register_and_login(client)
    resp = client.put(
        "/profile",
        headers=_auth(token),
        json={"remote_preference": "mostly-remote-sometimes-not"},
    )
    assert resp.status_code == 422


def test_update_profile_invalid_graduation_year_returns_422(client):
    token = _register_and_login(client)
    resp = client.put("/profile", headers=_auth(token), json={"graduation_year": 1800})
    assert resp.status_code == 422


def test_profile_isolation_between_users(client):
    """
    Core isolation guarantee: two users, two tokens, each sees only their own profile.
    """
    alice_token = _register_and_login(client, email="alice@example.com")
    bob_token = _register_and_login(client, email="bob@example.com")

    client.put("/profile", headers=_auth(alice_token), json={"degree": "CS"})
    client.put("/profile", headers=_auth(bob_token), json={"degree": "EE"})

    alice_profile = client.get("/profile", headers=_auth(alice_token)).json()
    bob_profile = client.get("/profile", headers=_auth(bob_token)).json()

    assert alice_profile["degree"] == "CS"
    assert bob_profile["degree"] == "EE"
    # Crucially: different IDs
    assert alice_profile["id"] != bob_profile["id"]