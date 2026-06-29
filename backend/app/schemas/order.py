import uuid

from pydantic import BaseModel

from app.schemas.menu_item import MenuItemRead


class OrderCreateResponse(BaseModel):
    id: uuid.UUID
    status: str
    restaurant_name: str

    model_config = {"from_attributes": True}


class OrderRead(BaseModel):
    id: uuid.UUID
    status: str
    restaurant_name: str
    menu_items: list[MenuItemRead]

    model_config = {"from_attributes": True}
