import uuid
from decimal import Decimal, InvalidOperation

from pydantic import BaseModel, field_validator


class MenuItemCreate(BaseModel):
    name: str
    price: Decimal | None = None
    category: str | None = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("name must not be blank")
        return stripped

    @field_validator("price")
    @classmethod
    def price_must_be_positive_with_max_two_decimals(cls, v: Decimal | None) -> Decimal | None:
        if v is None:
            return v
        if v <= 0:
            raise ValueError("price must be greater than 0")
        # Check that price has at most 2 decimal places
        try:
            quantized = v.quantize(Decimal("0.01"))
            if quantized != v:
                raise ValueError("price must have at most 2 decimal places")
        except InvalidOperation:
            raise ValueError("price is not a valid decimal number")
        return v


class MenuItemRead(BaseModel):
    id: uuid.UUID
    name: str
    price: Decimal | None
    category: str | None

    model_config = {"from_attributes": True}
