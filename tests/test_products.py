from decimal import Decimal


def category_payload():
    return {
        "category_name": "Electronics",
        "description": "Electronic products",
    }


def supplier_payload():
    return {
        "supplier_name": "Tech Supplies Ltd",
        "supplier_email": "products@example.com",
        "phone_number": "+254712345678",
        "address": "Nairobi, Kenya",
    }


def product_payload(category_id, supplier_id=None):
    payload = {
        "category_id": category_id,
        "product_name": "Laptop",
        "cost_price": "50000.00",
        "selling_price": "65000.00",
        "quantity": 10,
        "barcode": "LAPTOP001",
    }

    if supplier_id is not None:
        payload["supplier_id"] = supplier_id

    return payload


def create_category(client):
    response = client.post(
        "/categories/",
        json=category_payload(),
    )

    assert response.status_code == 201
    return response.json()


def create_supplier(client):
    response = client.post(
        "/suppliers/",
        json=supplier_payload(),
    )

    assert response.status_code == 201
    return response.json()


def create_product(client, include_supplier=True):
    category = create_category(client)

    supplier_id = None

    if include_supplier:
        supplier = create_supplier(client)
        supplier_id = supplier["supplier_id"]

    response = client.post(
        "/products/",
        json=product_payload(
            category_id=category["category_id"],
            supplier_id=supplier_id,
        ),
    )

    assert response.status_code == 201
    return response.json()


def test_create_product(client):
    category = create_category(client)
    supplier = create_supplier(client)

    payload = product_payload(
        category_id=category["category_id"],
        supplier_id=supplier["supplier_id"],
    )

    response = client.post("/products/", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["category_id"] == category["category_id"]
    assert data["supplier_id"] == supplier["supplier_id"]
    assert data["product_name"] == "Laptop"
    assert Decimal(str(data["cost_price"])) == Decimal("50000.00")
    assert Decimal(str(data["selling_price"])) == Decimal("65000.00")
    assert data["quantity"] == 10
    assert data["barcode"] == "LAPTOP001"
    assert "product_id" in data
    assert "created_at" in data


def test_create_product_without_optional_supplier_and_barcode(client):
    category = create_category(client)

    payload = {
        "category_id": category["category_id"],
        "product_name": "Keyboard",
        "cost_price": "1500.00",
        "selling_price": "2500.00",
        "quantity": 20,
    }

    response = client.post("/products/", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["category_id"] == category["category_id"]
    assert data["supplier_id"] is None
    assert data["product_name"] == "Keyboard"
    assert data["barcode"] is None


def test_create_product_without_required_category_id(client):
    payload = {
        "product_name": "Mouse",
        "cost_price": "500.00",
        "selling_price": "1000.00",
        "quantity": 15,
        "barcode": "MOUSE001",
    }

    response = client.post("/products/", json=payload)

    assert response.status_code == 422


def test_create_product_without_required_product_name(client):
    category = create_category(client)

    payload = {
        "category_id": category["category_id"],
        "cost_price": "500.00",
        "selling_price": "1000.00",
        "quantity": 15,
    }

    response = client.post("/products/", json=payload)

    assert response.status_code == 422


def test_create_product_without_required_cost_price(client):
    category = create_category(client)

    payload = {
        "category_id": category["category_id"],
        "product_name": "Mouse",
        "selling_price": "1000.00",
        "quantity": 15,
    }

    response = client.post("/products/", json=payload)

    assert response.status_code == 422


def test_create_product_without_required_selling_price(client):
    category = create_category(client)

    payload = {
        "category_id": category["category_id"],
        "product_name": "Mouse",
        "cost_price": "500.00",
        "quantity": 15,
    }

    response = client.post("/products/", json=payload)

    assert response.status_code == 422


def test_create_product_without_required_quantity(client):
    category = create_category(client)

    payload = {
        "category_id": category["category_id"],
        "product_name": "Mouse",
        "cost_price": "500.00",
        "selling_price": "1000.00",
    }

    response = client.post("/products/", json=payload)

    assert response.status_code == 422


def test_create_product_with_invalid_category_uuid(client):
    payload = product_payload(
        category_id="not-a-valid-uuid",
    )

    response = client.post("/products/", json=payload)

    assert response.status_code == 422


def test_create_product_with_invalid_price_type(client):
    category = create_category(client)

    payload = {
        "category_id": category["category_id"],
        "product_name": "Invalid Price Product",
        "cost_price": "not-a-number",
        "selling_price": "1000.00",
        "quantity": 10,
    }

    response = client.post("/products/", json=payload)

    assert response.status_code == 422


def test_list_products(client):
    first_product = create_product(client)

    category = create_category(client)

    second_payload = product_payload(
        category_id=category["category_id"],
        supplier_id=None,
    )
    second_payload["product_name"] = "Monitor"
    second_payload["barcode"] = "MONITOR001"

    second_response = client.post(
        "/products/",
        json=second_payload,
    )

    assert second_response.status_code == 201

    response = client.get("/products/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["product_id"] == first_product["product_id"]
    assert data[1]["product_name"] == "Monitor"


def test_get_product(client):
    created_product = create_product(client)
    product_id = created_product["product_id"]

    response = client.get(f"/products/{product_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["product_id"] == product_id
    assert data["product_name"] == "Laptop"


def test_get_missing_product(client):
    missing_product_id = "00000000-0000-0000-0000-000000000001"

    response = client.get(f"/products/{missing_product_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_get_product_with_invalid_uuid(client):
    response = client.get("/products/not-a-valid-uuid")

    assert response.status_code == 422


def test_update_product(client):
    created_product = create_product(client)
    product_id = created_product["product_id"]

    new_category = create_category(client)
    new_supplier = create_supplier(client)

    update_payload = {
        "category_id": new_category["category_id"],
        "supplier_id": new_supplier["supplier_id"],
        "product_name": "Updated Laptop",
        "cost_price": "55000.00",
        "selling_price": "70000.00",
        "quantity": 25,
        "barcode": "UPDATED001",
    }

    response = client.put(
        f"/products/{product_id}",
        json=update_payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["product_id"] == product_id
    assert data["category_id"] == new_category["category_id"]
    assert data["supplier_id"] == new_supplier["supplier_id"]
    assert data["product_name"] == "Updated Laptop"
    assert Decimal(str(data["cost_price"])) == Decimal("55000.00")
    assert Decimal(str(data["selling_price"])) == Decimal("70000.00")
    assert data["quantity"] == 25
    assert data["barcode"] == "UPDATED001"


def test_update_product_partially(client):
    created_product = create_product(client)
    product_id = created_product["product_id"]

    update_payload = {
        "product_name": "Partially Updated Laptop",
        "quantity": 50,
    }

    response = client.put(
        f"/products/{product_id}",
        json=update_payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["product_name"] == "Partially Updated Laptop"
    assert data["quantity"] == 50
    assert Decimal(str(data["cost_price"])) == Decimal("50000.00")
    assert Decimal(str(data["selling_price"])) == Decimal("65000.00")


def test_update_product_with_invalid_price(client):
    created_product = create_product(client)
    product_id = created_product["product_id"]

    update_payload = {
        "cost_price": "invalid-price",
    }

    response = client.put(
        f"/products/{product_id}",
        json=update_payload,
    )

    assert response.status_code == 422


def test_update_missing_product(client):
    missing_product_id = "00000000-0000-0000-0000-000000000002"

    update_payload = {
        "product_name": "Updated Missing Product",
    }

    response = client.put(
        f"/products/{missing_product_id}",
        json=update_payload,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_delete_product(client):
    created_product = create_product(client)
    product_id = created_product["product_id"]

    response = client.delete(f"/products/{product_id}")

    assert response.status_code == 204

    get_response = client.get(f"/products/{product_id}")

    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Product not found"


def test_delete_missing_product(client):
    missing_product_id = "00000000-0000-0000-0000-000000000003"

    response = client.delete(f"/products/{missing_product_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_delete_product_with_invalid_uuid(client):
    response = client.delete("/products/not-a-valid-uuid")

    assert response.status_code == 422
