from uuid import uuid4


def user_payload(**overrides):
    payload = {
        "first_name": "Nikki",
        "last_name": "Wanjiku",
        "username": "nikki",
        "password": "SecurePassword123!",
        "user_email": "nikki@example.com",
        "role": "cashier",
    }
    payload.update(overrides)
    return payload


def create_user(client, **overrides):
    response = client.post(
        "/users/",
        json=user_payload(**overrides),
    )
    assert response.status_code == 201
    return response.json()


# ---------------------------------------------------------
# CREATE USER TESTS
# ---------------------------------------------------------


def test_create_user_successfully(client):
    response = client.post(
        "/users/",
        json=user_payload(),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["first_name"] == "Nikki"
    assert data["last_name"] == "Wanjiku"
    assert data["username"] == "nikki"
    assert data["user_email"] == "nikki@example.com"
    assert data["role"] == "cashier"
    assert data["is_active"] is True
    assert "user_id" in data

    # The password must not be returned in the response.
    assert "password" not in data
    assert "password_hash" not in data


def test_create_user_without_optional_email(client):
    response = client.post(
        "/users/",
        json=user_payload(user_email=None),
    )

    assert response.status_code == 201

    data = response.json()
    assert data["user_email"] is None


def test_create_user_missing_first_name(client):
    payload = user_payload()
    del payload["first_name"]

    response = client.post("/users/", json=payload)

    assert response.status_code == 422


def test_create_user_missing_last_name(client):
    payload = user_payload()
    del payload["last_name"]

    response = client.post("/users/", json=payload)

    assert response.status_code == 422


def test_create_user_missing_username(client):
    payload = user_payload()
    del payload["username"]

    response = client.post("/users/", json=payload)

    assert response.status_code == 422


def test_create_user_missing_password(client):
    payload = user_payload()
    del payload["password"]

    response = client.post("/users/", json=payload)

    assert response.status_code == 422


def test_create_user_missing_role(client):
    payload = user_payload()
    del payload["role"]

    response = client.post("/users/", json=payload)

    assert response.status_code == 422


def test_create_user_with_invalid_email(client):
    response = client.post(
        "/users/",
        json=user_payload(user_email="invalid-email"),
    )

    assert response.status_code == 422


def test_create_user_with_duplicate_username(client):
    create_user(client)

    response = client.post(
        "/users/",
        json=user_payload(
            user_email="another@example.com",
        ),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


# ---------------------------------------------------------
# GET USER TESTS
# ---------------------------------------------------------


def test_list_users(client):
    create_user(client)

    response = client.get("/users/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1


def test_list_users_when_empty(client):
    response = client.get("/users/")

    assert response.status_code == 200
    assert response.json() == []


def test_get_user_by_id(client):
    user = create_user(client)

    response = client.get(
        f"/users/{user['user_id']}",
    )

    assert response.status_code == 200

    data = response.json()
    assert data["user_id"] == user["user_id"]
    assert data["username"] == "nikki"


def test_get_missing_user(client):
    missing_id = uuid4()

    response = client.get(
        f"/users/{missing_id}",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_get_user_with_invalid_uuid(client):
    response = client.get("/users/not-a-valid-uuid")

    assert response.status_code == 422


# ---------------------------------------------------------
# UPDATE USER TESTS
# ---------------------------------------------------------


def test_update_user_successfully(client):
    user = create_user(client)

    response = client.put(
        f"/users/{user['user_id']}",
        json={
            "first_name": "Updated",
            "last_name": "User",
            "username": "updated_user",
            "user_email": "updated@example.com",
            "role": "manager",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["first_name"] == "Updated"
    assert data["last_name"] == "User"
    assert data["username"] == "updated_user"
    assert data["user_email"] == "updated@example.com"
    assert data["role"] == "manager"


def test_partial_update_user(client):
    user = create_user(client)

    response = client.put(
        f"/users/{user['user_id']}",
        json={
            "first_name": "PartiallyUpdated",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["first_name"] == "PartiallyUpdated"
    assert data["last_name"] == "Wanjiku"
    assert data["username"] == "nikki"


def test_update_user_password(client):
    user = create_user(client)

    response = client.put(
        f"/users/{user['user_id']}",
        json={
            "password": "NewSecurePassword456!",
        },
    )

    assert response.status_code == 200
    assert response.json()["username"] == "nikki"


def test_update_user_with_invalid_email(client):
    user = create_user(client)

    response = client.put(
        f"/users/{user['user_id']}",
        json={
            "user_email": "invalid-email",
        },
    )

    assert response.status_code == 422


def test_update_user_with_empty_payload(client):
    user = create_user(client)

    response = client.put(
        f"/users/{user['user_id']}",
        json={},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["first_name"] == "Nikki"
    assert data["last_name"] == "Wanjiku"


def test_update_missing_user(client):
    missing_id = uuid4()

    response = client.put(
        f"/users/{missing_id}",
        json={
            "first_name": "Updated",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_update_user_with_invalid_uuid(client):
    response = client.put(
        "/users/not-a-valid-uuid",
        json={
            "first_name": "Updated",
        },
    )

    assert response.status_code == 422


# ---------------------------------------------------------
# DELETE USER TESTS
# ---------------------------------------------------------


def test_delete_user_successfully(client):
    user = create_user(client)

    response = client.delete(
        f"/users/{user['user_id']}",
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/users/{user['user_id']}",
    )

    assert get_response.status_code == 404


def test_delete_missing_user(client):
    missing_id = uuid4()

    response = client.delete(
        f"/users/{missing_id}",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_delete_user_with_invalid_uuid(client):
    response = client.delete("/users/not-a-valid-uuid")

    assert response.status_code == 422
