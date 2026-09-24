from fastapi.testclient import TestClient


def test_register_user(client: TestClient):
    response = client.post(
        "/auth/register",
        json={
            "first_name": "Nikki",
            "last_name": "Wanjiku",
            "username": "nikki_auth",
            "password": "SecurePassword123!",
            "user_email": "nikki_auth@example.com",
            "role": "cashier",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "nikki_auth"
    assert data["user_email"] == "nikki_auth@example.com"
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_username(client: TestClient):
    user_data = {
        "first_name": "Nikki",
        "last_name": "Wanjiku",
        "username": "duplicate_user",
        "password": "SecurePassword123!",
        "user_email": "duplicate1@example.com",
        "role": "cashier",
    }

    first_response = client.post("/auth/register", json=user_data)
    second_response = client.post("/auth/register", json=user_data)

    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Username already exists"


def test_login_success(client: TestClient):
    user_data = {
        "first_name": "Nikki",
        "last_name": "Wanjiku",
        "username": "login_user",
        "password": "SecurePassword123!",
        "user_email": "login@example.com",
        "role": "cashier",
    }

    register_response = client.post("/auth/register", json=user_data)
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "username": "login_user",
            "password": "SecurePassword123!",
        },
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)


def test_login_wrong_password(client: TestClient):
    user_data = {
        "first_name": "Nikki",
        "last_name": "Wanjiku",
        "username": "wrong_password_user",
        "password": "CorrectPassword123!",
        "user_email": "wrong_password@example.com",
        "role": "cashier",
    }

    register_response = client.post("/auth/register", json=user_data)
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "username": "wrong_password_user",
            "password": "WrongPassword123!",
        },
    )

    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Incorrect username or password"


def test_login_nonexistent_user(client: TestClient):
    response = client.post(
        "/auth/login",
        json={
            "username": "does_not_exist",
            "password": "SomePassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"
