import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.order import Order
from app.repositories.order_repository import OrderRepository

logger = logging.getLogger(__name__)

_order_repository = OrderRepository()


class OrderService:
    def __init__(self, order_repository: OrderRepository | None = None) -> None:
        self._repo = order_repository or _order_repository

    async def create_order(self, session: AsyncSession) -> Order:
        """Create a new order with default 'open' status."""
        order = Order(status="open")
        created = await self._repo.add(session, order)
        logger.info("Created order id=%s", created.id)
        return created

    async def get_order(self, session: AsyncSession, order_id: uuid.UUID) -> Order:
        """Retrieve an order by id. Raises NotFoundError if it does not exist."""
        order = await self._repo.get_by_id(session, order_id)
        if order is None:
            raise NotFoundError(f"Order {order_id} not found")
        return order
