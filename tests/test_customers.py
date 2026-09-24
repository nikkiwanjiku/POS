from uuid import uuid4


def customer_payload(**overrides):
    payload = {
        "first_name": "Nikki",
        "last_name": "Wanjiku",
        "email": "nikki@example.com",
        "phone_number": "0712345678",
    }
    payload.update(overrides)
    return payload


def create_customer(client, **overrides):
    response = client.post(
        "/customers/",
        json=customer_payload(**overrides),
    )
    assert response.status_code == 201
    return response.json()


# ---------------------------------------------------------
# CREATE CUSTOMER TESTS
# ---------------------------------------------------------


def test_create_customer_successfully(client):
    response = client.post(
        "/customers/",
        json=customer_payload(),
    )

    assert response.status_code == 201

    data = response.json()
    assert data["first_name"] == "Nikki"
    assert data["last_name"] == "Wanjiku"
    assert data["email"] == "nikki@example.com"
    assert data["phone_number"] == "0712345678"
    assert "customer_id" in data
    assert "created_at" in data


def test_create_customer_without_optional_fields(client):
    response = client.post(
        "/customers/",
        json={
            "first_name": "John",
            "last_name": "Doe",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["email"] is None
    assert data["phone_number"] is None


def test_create_customer_missing_first_name(client):
    response = client.post(
        "/customers/",
        json={
            "last_name": "Wanjiku",
            "email": "nikki@example.com",
        },
    )

    assert response.status_code == 422


def test_create_customer_missing_last_name(client):
    response = client.post(
        "/customers/",
        json={
            "first_name": "Nikki",
            "email": "nikki@example.com",
        },
    )

    assert response.status_code == 422


def test_create_customer_with_invalid_email(client):
    response = client.post(
        "/customers/",
        json=customer_payload(email="invalid-email"),
    )

    assert response.status_code == 422


def test_create_customer_with_invalid_phone_type(client):
    response = client.post(
        "/customers/",
        json=customer_payload(phone_number=123456789),
    )

    assert response.status_code == 422


# ---------------------------------------------------------
# GET CUSTOMER TESTS
# ---------------------------------------------------------


def test_list_customers(client):
    create_customer(client)

    response = client.get("/customers/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1


def test_list_customers_when_empty(client):
    response = client.get("/customers/")

    assert response.status_code == 200
    assert response.json() == []


def test_get_customer_by_id(client):
    customer = create_customer(client)

    response = client.get(f"/customers/{customer['customer_id']}")

    assert response.status_code == 200
    assert response.json()["customer_id"] == customer["customer_id"]
    assert response.json()["first_name"] == "Nikki"


def test_get_missing_customer(client):
    missing_id = uuid4()

    response = client.get(f"/customers/{missing_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"


def test_get_customer_with_invalid_uuid(client):
    response = client.get("/customers/not-a-valid-uuid")

    assert response.status_code == 422


# ---------------------------------------------------------
# UPDATE CUSTOMER TESTS
# ---------------------------------------------------------


def test_update_customer_successfully(client):
    customer = create_customer(client)

    response = client.put(
        f"/customers/{customer['customer_id']}",
        json={
            "first_name": "Updated",
            "last_name": "Customer",
            "email": "updated@example.com",
            "phone_number": "0798765432",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "Customer"
    assert data["email"] == "updated@example.com"
    assert data["phone_number"] == "0798765432"


def test_partial_update_customer(client):
    customer = create_customer(client)

    response = client.put(
        f"/customers/{customer['customer_id']}",
        json={
            "first_name": "PartiallyUpdated",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["first_name"] == "PartiallyUpdated"
    assert data["last_name"] == "Wanjiku"
    assert data["email"] == "nikki@example.com"
    assert data["phone_number"] == "0712345678"


def test_update_customer_email_with_invalid_value(client):
    customer = create_customer(client)

    response = client.put(
        f"/customers/{customer['customer_id']}",
        json={
            "email": "not-an-email",
        },
    )

    assert response.status_code == 422


def test_update_customer_with_empty_payload(client):
    customer = create_customer(client)

    response = client.put(
        f"/customers/{customer['customer_id']}",
        json={},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["first_name"] == "Nikki"
    assert data["last_name"] == "Wanjiku"


def test_update_missing_customer(client):
    missing_id = uuid4()

    response = client.put(
        f"/customers/{missing_id}",
        json={
            "first_name": "Updated",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"


def test_update_customer_with_invalid_uuid(client):
    response = client.put(
        "/customers/not-a-valid-uuid",
        json={
            "first_name": "Updated",
        },
    )

    assert response.status_code == 422


# ---------------------------------------------------------
# DELETE CUSTOMER TESTS
# ---------------------------------------------------------


def test_delete_customer_successfully(client):
    customer = create_customer(client)

    response = client.delete(
        f"/customers/{customer['customer_id']}",
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/customers/{customer['customer_id']}",
    )

    assert get_response.status_code == 404


def test_delete_missing_customer(client):
    missing_id = uuid4()

    response = client.delete(
        f"/customers/{missing_id}",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"


def test_delete_customer_with_invalid_uuid(client):
    response = client.delete("/customers/not-a-valid-uuid")

    assert response.status_code == 422
