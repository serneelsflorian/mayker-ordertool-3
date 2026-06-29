import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.menu_item import MenuItemCreate, MenuItemRead
from app.services.menu_item_service import MenuItemService

router = APIRouter(prefix="/api/orders", tags=["menu-items"])

_menu_item_service = MenuItemService()


@router.post(
    "/{order_id}/menu-items",
    response_model=MenuItemRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_menu_item(
    order_id: uuid.UUID,
    payload: MenuItemCreate,
    session: AsyncSession = Depends(get_db),
) -> MenuItemRead:
    """Add a menu item to an order."""
    item = await _menu_item_service.add_item(session, order_id, payload)
    await session.commit()
    return MenuItemRead.model_validate(item)


@router.delete(
    "/{order_id}/menu-items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_menu_item(
    order_id: uuid.UUID,
    item_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> None:
    """Remove a menu item from an order."""
    await _menu_item_service.remove_item(session, order_id, item_id)
    await session.commit()
