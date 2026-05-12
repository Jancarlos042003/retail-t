import uuid

import pytest


@pytest.mark.asyncio
async def test_create_product_without_image(client, category):
    response = await client.post(
        "/products/",
        data={
            "barcode": "1234567890123",
            "name": "Agua Mineral 500ml",
            "category_id": str(category.id),
            "min_stock": "0",
            "is_active": "true",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["barcode"] == "1234567890123"
    assert data["image_url"] is None


@pytest.mark.asyncio
async def test_create_product_with_image(client, category):
    response = await client.post(
        "/products/",
        data={
            "barcode": "9876543210987",
            "name": "Jugo de Naranja",
            "category_id": str(category.id),
        },
        files={"image": ("jugo.jpg", b"fake-image-bytes", "image/jpeg")},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["image_url"] is not None


@pytest.mark.asyncio
async def test_list_products(client, product):
    response = await client.get("/products/")
    assert response.status_code == 200
    ids = [p["id"] for p in response.json()]
    assert str(product.id) in ids


@pytest.mark.asyncio
async def test_list_products_filter_active(client, product):
    response = await client.get("/products/", params={"is_active": "true"})
    assert response.status_code == 200
    assert all(p["is_active"] for p in response.json())


@pytest.mark.asyncio
async def test_get_product(client, product):
    response = await client.get(f"/products/{product.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(product.id)
    assert "category" in data


@pytest.mark.asyncio
async def test_get_product_not_found(client):
    response = await client.get(f"/products/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_product(client, product):
    response = await client.patch(f"/products/{product.id}", json={"name": "Coca Cola 1L"})
    assert response.status_code == 200
    assert response.json()["name"] == "Coca Cola 1L"


@pytest.mark.asyncio
async def test_delete_product(client, product):
    response = await client.delete(f"/products/{product.id}")
    assert response.status_code == 204
