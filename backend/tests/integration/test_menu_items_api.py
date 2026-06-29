import uuid

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.usefixtures("run_migrations")


@pytest.fixture
async def order_id(client: AsyncClient) -> str:
    """Create a fresh order and return its id."""
    response = await client.post("/api/orders")
    assert response.status_code == 201
    return response.json()["id"]


async def test_add_menu_item_with_price_returns_201(client: AsyncClient, order_id: str):
    """POST /api/orders/{id}/menu-items should return 201 with price."""
    payload = {"name": "Margherita", "price": "9.99", "category": "Pizza"}
    response = await client.post(f"/api/orders/{order_id}/menu-items", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Margherita"
    assert data["price"] == "9.99"
    assert data["category"] == "Pizza"
    assert "id" in data


async def test_add_menu_item_without_price_returns_201(client: AsyncClient, order_id: str):
    """POST /api/orders/{id}/menu-items should return 201 with null price."""
    payload = {"name": "House Salad"}
    response = await client.post(f"/api/orders/{order_id}/menu-items", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "House Salad"
    assert data["price"] is None


async def test_add_menu_item_blank_name_returns_422(client: AsyncClient, order_id: str):
    """POST /api/orders/{id}/menu-items should return 422 for blank name."""
    payload = {"name": "   "}
    response = await client.post(f"/api/orders/{order_id}/menu-items", json=payload)
    assert response.status_code == 422


async def test_add_menu_item_negative_price_returns_422(client: AsyncClient, order_id: str):
    """POST /api/orders/{id}/menu-items should return 422 for negative price."""
    payload = {"name": "Espresso", "price": "-1.00"}
    response = await client.post(f"/api/orders/{order_id}/menu-items", json=payload)
    assert response.status_code == 422


async def test_add_menu_item_missing_order_returns_404(client: AsyncClient):
    """POST /api/orders/{id}/menu-items should return 404 for non-existent order."""
    missing_id = str(uuid.uuid4())
    payload = {"name": "Tiramisu"}
    response = await client.post(f"/api/orders/{missing_id}/menu-items", json=payload)
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "not_found"


async def test_remove_menu_item_returns_204(client: AsyncClient, order_id: str):
    """DELETE /api/orders/{id}/menu-items/{item_id} should return 204."""
    add_response = await client.post(
        f"/api/orders/{order_id}/menu-items",
        json={"name": "Bruschetta", "price": "5.50"},
    )
    assert add_response.status_code == 201
    item_id = add_response.json()["id"]

    delete_response = await client.delete(f"/api/orders/{order_id}/menu-items/{item_id}")
    assert delete_response.status_code == 204


async def test_remove_missing_menu_item_returns_404(client: AsyncClient, order_id: str):
    """DELETE /api/orders/{id}/menu-items/{item_id} should return 404 for missing item."""
    missing_item_id = str(uuid.uuid4())
    response = await client.delete(f"/api/orders/{order_id}/menu-items/{missing_item_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "not_found"
