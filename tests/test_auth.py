def test_register_success(client):
    response = client.post(
        "/auth/register",
        json={"name": "New Student", "email": "new.student@example.com", "password": "SafePassword123!"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "new.student@example.com"
    assert "user_id" in response.json()


def test_register_invalid_email(client):
    response = client.post(
        "/auth/register",
        json={"name": "New Student", "email": "not-an-email", "password": "SafePassword123!"},
    )
    assert response.status_code == 422


def test_register_missing_required_field(client):
    response = client.post(
        "/auth/register",
        json={"name": "New Student", "email": "new.student@example.com"},
    )
    assert response.status_code == 422


def test_login_success_returns_bearer_token(client, test_user):
    response = client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "TestPassword123!"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"].lower() == "bearer"
    assert body["access_token"]


def test_login_wrong_password(client, test_user):
    response = client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_me_requires_authentication(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_with_valid_login_token(client, login_headers, test_user):
    response = client.get("/auth/me", headers=login_headers)
    assert response.status_code == 200
    assert response.json()["id"] == test_user.id


def test_me_rejects_malformed_token(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer not.a.valid.token"})
    assert response.status_code == 401
