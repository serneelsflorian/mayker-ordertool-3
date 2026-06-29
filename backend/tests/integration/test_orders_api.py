import uuid

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


async def test_create_order_returns_201(client: AsyncClient):
    """POST /api/orders should create an order and return 201."""
    response = await client.post("/api/orders")
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["status"] == "open"
    assert "restaurant_name" in data


async def test_get_order_returns_200(client: AsyncClient):
    """GET /api/orders/{id} should return the order when it exists."""
    create_response = await client.post("/api/orders")
    assert create_response.status_code == 201
    order_id = create_response.json()["id"]

    get_response = await client.get(f"/api/orders/{order_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == order_id
    assert data["status"] == "open"
    assert "menu_items" in data
    assert data["menu_items"] == []


async def test_get_order_not_found_returns_404(client: AsyncClient):
    """GET /api/orders/{id} should return 404 for a non-existent order."""
    missing_id = str(uuid.uuid4())
    response = await client.get(f"/api/orders/{missing_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "not_found"
