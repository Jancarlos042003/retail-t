import uuid

import pytest


@pytest.mark.asyncio
async def test_list_movement_types(client, movement_type_in, movement_type_out):
    response = await client.get("/stock/movement-types")
    assert response.status_code == 200
    codes = [mt["code"] for mt in response.json()]
    assert "ENTRADA" in codes
    assert "SALIDA" in codes


@pytest.mark.asyncio
async def test_get_stock_level(client, product):
    response = await client.get(f"/stock/{product.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 100


@pytest.mark.asyncio
async def test_get_stock_level_not_found(client):
    response = await client.get(f"/stock/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_register_movement_in(client, product, movement_type_in):
    response = await client.post(
        "/stock/movements",
        json={
            "product_id": str(product.id),
            "type_id": str(movement_type_in.id),
            "quantity": 10,
            "reason": "Reposición de inventario",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["quantity"] == 10

    stock_response = await client.get(f"/stock/{product.id}")
    assert stock_response.json()["quantity"] == 110


@pytest.mark.asyncio
async def test_register_movement_out(client, product, movement_type_out):
    response = await client.post(
        "/stock/movements",
        json={
            "product_id": str(product.id),
            "type_id": str(movement_type_out.id),
            "quantity": 20,
        },
    )
    assert response.status_code == 201

    stock_response = await client.get(f"/stock/{product.id}")
    assert stock_response.json()["quantity"] == 80


@pytest.mark.asyncio
async def test_register_movement_invalid_quantity(client, product, movement_type_in):
    response = await client.post(
        "/stock/movements",
        json={
            "product_id": str(product.id),
            "type_id": str(movement_type_in.id),
            "quantity": 0,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_movement_history(client, product, movement_type_in):
    await client.post(
        "/stock/movements",
        json={
            "product_id": str(product.id),
            "type_id": str(movement_type_in.id),
            "quantity": 5,
        },
    )
    response = await client.get(f"/stock/{product.id}/movements")
    assert response.status_code == 200
    assert len(response.json()) >= 1
