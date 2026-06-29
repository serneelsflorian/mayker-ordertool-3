import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order


class OrderRepository:
    async def add(self, session: AsyncSession, order: Order) -> Order:
        """Persist a new order and return it with its generated id."""
        session.add(order)
        await session.flush()
        await session.refresh(order)
        return order

    async def get_by_id(self, session: AsyncSession, order_id: uuid.UUID) -> Order | None:
        """Fetch an order by id, eagerly loading its menu items."""
        result = await session.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.menu_items))
        )
        return result.scalar_one_or_none()
