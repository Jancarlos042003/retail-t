import uuid

import pytest


@pytest.mark.asyncio
async def test_create_sale(client, product, payment_method):
    response = await client.post(
        "/sales/",
        json={
            "payment_method_id": str(payment_method.id),
            "items": [{"product_id": str(product.id), "quantity": 2}],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 2
    assert float(data["total_amount"]) == pytest.approx(30.00)


@pytest.mark.asyncio
async def test_create_sale_no_items(client, payment_method):
    response = await client.post(
        "/sales/",
        json={
            "payment_method_id": str(payment_method.id),
            "items": [],
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_sale_invalid_product(client, payment_method):
    response = await client.post(
        "/sales/",
        json={
            "payment_method_id": str(payment_method.id),
            "items": [{"product_id": str(uuid.uuid4()), "quantity": 1}],
        },
    )
    assert response.status_code in (404, 422)


@pytest.mark.asyncio
async def test_get_sale(client, product, payment_method):
    create_response = await client.post(
        "/sales/",
        json={
            "payment_method_id": str(payment_method.id),
            "items": [{"product_id": str(product.id), "quantity": 1}],
        },
    )
    sale_id = create_response.json()["id"]

    response = await client.get(f"/sales/{sale_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sale_id
    assert data["items"][0]["unit_price"] == "15.00"


@pytest.mark.asyncio
async def test_list_sales(client, product, payment_method):
    await client.post(
        "/sales/",
        json={
            "payment_method_id": str(payment_method.id),
            "items": [{"product_id": str(product.id), "quantity": 1}],
        },
    )
    response = await client.get("/sales/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_update_sale_status(client, product, payment_method):
    create_response = await client.post(
        "/sales/",
        json={
            "payment_method_id": str(payment_method.id),
            "items": [{"product_id": str(product.id), "quantity": 1}],
        },
    )
    sale_id = create_response.json()["id"]

    response = await client.patch(f"/sales/{sale_id}/status", json={"status": "CANCELLED"})
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


@pytest.mark.asyncio
async def test_get_sale_not_found(client):
    response = await client.get(f"/sales/{uuid.uuid4()}")
    assert response.status_code == 404
