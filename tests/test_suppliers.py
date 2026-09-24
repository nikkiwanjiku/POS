def supplier_payload():
    return {
        "supplier_name": "Tech Supplies Ltd",
        "supplier_email": "supplier@example.com",
        "phone_number": "+254712345678",
        "address": "Nairobi, Kenya",
    }


def create_supplier(client):
    response = client.post(
        "/suppliers/",
        json=supplier_payload(),
    )

    assert response.status_code == 201
    return response.json()


def test_create_supplier(client):
    payload = supplier_payload()

    response = client.post("/suppliers/", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["supplier_name"] == payload["supplier_name"]
    assert data["supplier_email"] == payload["supplier_email"]
    assert data["phone_number"] == payload["phone_number"]
    assert data["address"] == payload["address"]
    assert "supplier_id" in data


def test_create_supplier_without_optional_fields(client):
    payload = {
        "supplier_name": "Basic Supplier",
        "supplier_email": "basic@example.com",
    }

    response = client.post("/suppliers/", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["supplier_name"] == "Basic Supplier"
    assert data["supplier_email"] == "basic@example.com"
    assert data["phone_number"] is None
    assert data["address"] is None


def test_create_supplier_without_required_name(client):
    payload = {
        "supplier_email": "supplier@example.com",
        "phone_number": "+254712345678",
        "address": "Nairobi, Kenya",
    }

    response = client.post("/suppliers/", json=payload)

    assert response.status_code == 422


def test_create_supplier_without_required_email(client):
    payload = {
        "supplier_name": "Missing Email Supplier",
        "phone_number": "+254712345678",
        "address": "Nairobi, Kenya",
    }

    response = client.post("/suppliers/", json=payload)

    assert response.status_code == 422


def test_create_supplier_with_invalid_email(client):
    payload = {
        "supplier_name": "Invalid Email Supplier",
        "supplier_email": "invalid-email",
        "phone_number": "+254712345678",
        "address": "Nairobi, Kenya",
    }

    response = client.post("/suppliers/", json=payload)

    assert response.status_code == 422


def test_list_suppliers(client):
    first_supplier = create_supplier(client)

    second_payload = {
        "supplier_name": "Second Supplier",
        "supplier_email": "second@example.com",
    }

    second_response = client.post(
        "/suppliers/",
        json=second_payload,
    )

    assert second_response.status_code == 201

    response = client.get("/suppliers/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["supplier_id"] == first_supplier["supplier_id"]
    assert data[1]["supplier_name"] == "Second Supplier"


def test_get_supplier(client):
    created_supplier = create_supplier(client)
    supplier_id = created_supplier["supplier_id"]

    response = client.get(f"/suppliers/{supplier_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["supplier_id"] == supplier_id
    assert data["supplier_name"] == "Tech Supplies Ltd"


def test_get_missing_supplier(client):
    missing_supplier_id = "00000000-0000-0000-0000-000000000001"

    response = client.get(f"/suppliers/{missing_supplier_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Supplier not found"


def test_get_supplier_with_invalid_uuid(client):
    response = client.get("/suppliers/not-a-valid-uuid")

    assert response.status_code == 422


def test_update_supplier(client):
    created_supplier = create_supplier(client)
    supplier_id = created_supplier["supplier_id"]

    update_payload = {
        "supplier_name": "Updated Tech Supplies",
        "supplier_email": "updated@example.com",
        "phone_number": "+254799999999",
        "address": "Mombasa, Kenya",
    }

    response = client.put(
        f"/suppliers/{supplier_id}",
        json=update_payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["supplier_id"] == supplier_id
    assert data["supplier_name"] == "Updated Tech Supplies"
    assert data["supplier_email"] == "updated@example.com"
    assert data["phone_number"] == "+254799999999"
    assert data["address"] == "Mombasa, Kenya"


def test_update_supplier_partially(client):
    created_supplier = create_supplier(client)
    supplier_id = created_supplier["supplier_id"]

    update_payload = {
        "supplier_name": "Partially Updated Supplier",
    }

    response = client.put(
        f"/suppliers/{supplier_id}",
        json=update_payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["supplier_name"] == "Partially Updated Supplier"
    assert data["supplier_email"] == "supplier@example.com"
    assert data["phone_number"] == "+254712345678"
    assert data["address"] == "Nairobi, Kenya"


def test_update_supplier_with_invalid_email(client):
    created_supplier = create_supplier(client)
    supplier_id = created_supplier["supplier_id"]

    update_payload = {
        "supplier_email": "invalid-email",
    }

    response = client.put(
        f"/suppliers/{supplier_id}",
        json=update_payload,
    )

    assert response.status_code == 422


def test_update_missing_supplier(client):
    missing_supplier_id = "00000000-0000-0000-0000-000000000002"

    update_payload = {
        "supplier_name": "Updated Missing Supplier",
    }

    response = client.put(
        f"/suppliers/{missing_supplier_id}",
        json=update_payload,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Supplier not found"


def test_delete_supplier(client):
    created_supplier = create_supplier(client)
    supplier_id = created_supplier["supplier_id"]

    response = client.delete(f"/suppliers/{supplier_id}")

    assert response.status_code == 204

    get_response = client.get(f"/suppliers/{supplier_id}")

    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Supplier not found"


def test_delete_missing_supplier(client):
    missing_supplier_id = "00000000-0000-0000-0000-000000000003"

    response = client.delete(f"/suppliers/{missing_supplier_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Supplier not found"


def test_delete_supplier_with_invalid_uuid(client):
    response = client.delete("/suppliers/not-a-valid-uuid")

    assert response.status_code == 422
