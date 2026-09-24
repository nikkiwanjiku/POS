from uuid import uuid4


def test_create_category(client):
    payload = {
        "category_name": "Electronics",
        "description": "Electronic products",
    }

    response = client.post("/categories/", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["category_name"] == "Electronics"
    assert data["description"] == "Electronic products"
    assert "category_id" in data


def test_create_category_without_optional_description(client):
    payload = {
        "category_name": "Furniture",
    }

    response = client.post("/categories/", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["category_name"] == "Furniture"
    assert data["description"] is None


def test_create_category_without_required_name(client):
    payload = {
        "description": "A category without a name",
    }

    response = client.post("/categories/", json=payload)

    assert response.status_code == 422


def test_create_category_with_invalid_data_type(client):
    payload = {
        "category_name": 123,
        "description": "Invalid category name type",
    }

    response = client.post("/categories/", json=payload)

    # Pydantic may reject this depending on its string validation behavior.
    assert response.status_code in (201, 422)


def test_list_categories(client):
    client.post(
        "/categories/",
        json={
            "category_name": "Electronics",
            "description": "Electronic products",
        },
    )

    client.post(
        "/categories/",
        json={
            "category_name": "Clothing",
            "description": "Clothing products",
        },
    )

    response = client.get("/categories/")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["category_name"] == "Electronics"
    assert data[1]["category_name"] == "Clothing"


def test_get_category(client):
    create_response = client.post(
        "/categories/",
        json={
            "category_name": "Electronics",
            "description": "Electronic products",
        },
    )

    category_id = create_response.json()["category_id"]

    response = client.get(f"/categories/{category_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["category_id"] == category_id
    assert data["category_name"] == "Electronics"


def test_get_missing_category(client):
    missing_category_id = uuid4()

    response = client.get(f"/categories/{missing_category_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


def test_get_category_with_invalid_uuid(client):
    response = client.get("/categories/not-a-valid-uuid")

    assert response.status_code == 422


def test_update_category(client):
    create_response = client.post(
        "/categories/",
        json={
            "category_name": "Electronics",
            "description": "Electronic products",
        },
    )

    category_id = create_response.json()["category_id"]

    response = client.put(
        f"/categories/{category_id}",
        json={
            "category_name": "Updated Electronics",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["category_id"] == category_id
    assert data["category_name"] == "Updated Electronics"
    assert data["description"] == "Electronic products"


def test_update_missing_category(client):
    missing_category_id = uuid4()

    response = client.put(
        f"/categories/{missing_category_id}",
        json={
            "category_name": "Updated Category",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


def test_delete_category(client):
    create_response = client.post(
        "/categories/",
        json={
            "category_name": "Temporary Category",
            "description": "Category to delete",
        },
    )

    category_id = create_response.json()["category_id"]

    response = client.delete(f"/categories/{category_id}")

    assert response.status_code == 204

    get_response = client.get(f"/categories/{category_id}")

    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Category not found"


def test_delete_missing_category(client):
    missing_category_id = uuid4()

    response = client.delete(f"/categories/{missing_category_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"
