import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.menu_item import MenuItem
from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.menu_item import MenuItemCreate

logger = logging.getLogger(__name__)


class MenuItemService:
    def __init__(
        self,
        order_repository: OrderRepository | None = None,
        menu_item_repository: MenuItemRepository | None = None,
    ) -> None:
        self._order_repo = order_repository if order_repository is not None else OrderRepository()
        self._item_repo = menu_item_repository if menu_item_repository is not None else MenuItemRepository()

    async def add_item(
        self,
        session: AsyncSession,
        order_id: uuid.UUID,
        payload: MenuItemCreate,
    ) -> MenuItem:
        """Add a menu item to an existing order."""
        order = await self._order_repo.get_by_id(session, order_id)
        if order is None:
            raise NotFoundError(f"Order {order_id} not found")

        item = MenuItem(
            order_id=order_id,
            name=payload.name,
            price=payload.price,
            category=payload.category,
        )
        created = await self._item_repo.add(session, item)
        await session.commit()
        logger.info("Added menu item id=%s to order id=%s", created.id, order_id)
        return created

    async def remove_item(
        self,
        session: AsyncSession,
        order_id: uuid.UUID,
        item_id: uuid.UUID,
    ) -> None:
        """Remove a menu item from an order. Raises NotFoundError if not found."""
        item = await self._item_repo.get_by_id(session, item_id)
        if item is None or item.order_id != order_id:
            raise NotFoundError(f"Menu item {item_id} not found in order {order_id}")

        await self._item_repo.delete(session, item)
        await session.commit()
        logger.info("Removed menu item id=%s from order id=%s", item_id, order_id)
