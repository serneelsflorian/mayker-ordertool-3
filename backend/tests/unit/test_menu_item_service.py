import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import NotFoundError
from app.models.menu_item import MenuItem
from app.models.order import Order
from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.menu_item import MenuItemCreate
from app.services.menu_item_service import MenuItemService


@pytest.fixture
def mock_order_repo():
    repo = MagicMock(spec=OrderRepository)
    repo.get_by_id = AsyncMock()
    return repo


@pytest.fixture
def mock_item_repo():
    repo = MagicMock(spec=MenuItemRepository)
    repo.add = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def service(mock_order_repo, mock_item_repo):
    return MenuItemService(
        order_repository=mock_order_repo,
        menu_item_repository=mock_item_repo,
    )


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def existing_order():
    order_id = uuid.uuid4()
    return Order(id=order_id, status="open")


async def test_add_item_happy_path_with_price(service, mock_order_repo, mock_item_repo, mock_session, existing_order):
    """add_item should create a MenuItem with all fields when price is provided."""
    payload = MenuItemCreate(name="Margherita", price=Decimal("9.99"), category="Pizza")
    created_item = MenuItem(
        id=uuid.uuid4(),
        order_id=existing_order.id,
        name="Margherita",
        price=Decimal("9.99"),
        category="Pizza",
    )
    mock_order_repo.get_by_id.return_value = existing_order
    mock_item_repo.add.return_value = created_item

    result = await service.add_item(mock_session, existing_order.id, payload)

    mock_item_repo.add.assert_called_once()
    assert result is created_item


async def test_add_item_with_null_price(service, mock_order_repo, mock_item_repo, mock_session, existing_order):
    """add_item should allow None price (price-less menu items)."""
    payload = MenuItemCreate(name="House Salad", price=None, category=None)
    created_item = MenuItem(
        id=uuid.uuid4(),
        order_id=existing_order.id,
        name="House Salad",
        price=None,
        category=None,
    )
    mock_order_repo.get_by_id.return_value = existing_order
    mock_item_repo.add.return_value = created_item

    result = await service.add_item(mock_session, existing_order.id, payload)

    assert result.price is None


async def test_add_item_blank_name_raises_validation_error(service, mock_session, existing_order):
    """add_item should raise when the schema validator rejects a blank name."""
    with pytest.raises(Exception):
        MenuItemCreate(name="   ", price=None, category=None)


async def test_add_item_missing_order_raises_not_found(service, mock_order_repo, mock_session):
    """add_item should raise NotFoundError when the target order does not exist."""
    mock_order_repo.get_by_id.return_value = None
    payload = MenuItemCreate(name="Tiramisu", price=Decimal("4.50"))

    with pytest.raises(NotFoundError) as exc_info:
        await service.add_item(mock_session, uuid.uuid4(), payload)

    assert exc_info.value.status_code == 404


async def test_add_item_negative_price_raises_validation_error(service, mock_session):
    """add_item should raise when the schema validator rejects a negative price."""
    with pytest.raises(Exception):
        MenuItemCreate(name="Espresso", price=Decimal("-1.00"))


async def test_remove_item_success(service, mock_order_repo, mock_item_repo, mock_session, existing_order):
    """remove_item should delete the item when it belongs to the given order."""
    item_id = uuid.uuid4()
    existing_item = MenuItem(id=item_id, order_id=existing_order.id, name="Bruschetta")
    mock_item_repo.get_by_id.return_value = existing_item

    await service.remove_item(mock_session, existing_order.id, item_id)

    mock_item_repo.delete.assert_called_once_with(mock_session, existing_item)


async def test_remove_item_not_found(service, mock_item_repo, mock_session):
    """remove_item should raise NotFoundError when the item does not exist."""
    mock_item_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError) as exc_info:
        await service.remove_item(mock_session, uuid.uuid4(), uuid.uuid4())

    assert exc_info.value.status_code == 404
