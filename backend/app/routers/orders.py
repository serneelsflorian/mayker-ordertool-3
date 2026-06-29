import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.order import OrderCreateResponse, OrderRead
from app.services.order_service import OrderService

router = APIRouter(prefix="/api/orders", tags=["orders"])

_order_service = OrderService()


@router.post("", response_model=OrderCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    session: AsyncSession = Depends(get_db),
) -> OrderCreateResponse:
    """Create a new group order."""
    order = await _order_service.create_order(session)
    await session.commit()
    return OrderCreateResponse(
        id=order.id,
        status=order.status,
        restaurant_name=get_settings().RESTAURANT_NAME,
    )


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> OrderRead:
    """Retrieve an order with its menu items."""
    order = await _order_service.get_order(session, order_id)
    return OrderRead(
        id=order.id,
        status=order.status,
        restaurant_name=get_settings().RESTAURANT_NAME,
        menu_items=order.menu_items,
    )
