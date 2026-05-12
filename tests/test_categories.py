import uuid

import pytest


@pytest.mark.asyncio
async def test_create_category(client):
    response = await client.post("/categories/", json={"name": "Lácteos"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Lácteos"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_categories(client, category):
    response = await client.get("/categories/")
    assert response.status_code == 200
    ids = [item["id"] for item in response.json()]
    assert str(category.id) in ids


@pytest.mark.asyncio
async def test_get_category(client, category):
    response = await client.get(f"/categories/{category.id}")
    assert response.status_code == 200
    assert response.json()["name"] == category.name


@pytest.mark.asyncio
async def test_get_category_not_found(client):
    response = await client.get(f"/categories/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_category(client, category):
    response = await client.patch(f"/categories/{category.id}", json={"name": "Refrescos"})
    assert response.status_code == 200
    assert response.json()["name"] == "Refrescos"


@pytest.mark.asyncio
async def test_delete_category(client, category):
    response = await client.delete(f"/categories/{category.id}")
    assert response.status_code == 204
