import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import NotFoundError
from app.models.order import Order
from app.repositories.order_repository import OrderRepository
from app.services.order_service import OrderService


@pytest.fixture
def mock_repo():
    repo = MagicMock(spec=OrderRepository)
    repo.add = AsyncMock()
    repo.get_by_id = AsyncMock()
    return repo


@pytest.fixture
def service(mock_repo):
    return OrderService(order_repository=mock_repo)


@pytest.fixture
def mock_session():
    return AsyncMock()


async def test_create_order_success(service, mock_repo, mock_session):
    """create_order should persist a new Order with status 'open' and return it."""
    new_order = Order(id=uuid.uuid4(), status="open")
    mock_repo.add.return_value = new_order

    result = await service.create_order(mock_session)

    mock_repo.add.assert_called_once()
    created_order_arg = mock_repo.add.call_args[0][1]
    assert created_order_arg.status == "open"
    assert result is new_order


async def test_get_order_success(service, mock_repo, mock_session):
    """get_order should return the order when it exists."""
    order_id = uuid.uuid4()
    existing_order = Order(id=order_id, status="open")
    mock_repo.get_by_id.return_value = existing_order

    result = await service.get_order(mock_session, order_id)

    mock_repo.get_by_id.assert_called_once_with(mock_session, order_id)
    assert result is existing_order


async def test_get_order_not_found(service, mock_repo, mock_session):
    """get_order should raise NotFoundError when the order does not exist."""
    order_id = uuid.uuid4()
    mock_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError) as exc_info:
        await service.get_order(mock_session, order_id)

    assert exc_info.value.status_code == 404
    assert str(order_id) in exc_info.value.message
