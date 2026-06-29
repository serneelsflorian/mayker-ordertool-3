import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.menu_item import MenuItem


class MenuItemRepository:
    async def add(self, session: AsyncSession, item: MenuItem) -> MenuItem:
        """Persist a new menu item and return it with its generated id."""
        session.add(item)
        await session.flush()
        await session.refresh(item)
        return item

    async def get_by_id(self, session: AsyncSession, item_id: uuid.UUID) -> MenuItem | None:
        """Fetch a menu item by id."""
        result = await session.execute(
            select(MenuItem).where(MenuItem.id == item_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, session: AsyncSession, item: MenuItem) -> None:
        """Delete a menu item."""
        await session.delete(item)
        await session.flush()
