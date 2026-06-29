from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.menu_item import MenuItemCreate


def test_valid_item_with_price():
    """MenuItemCreate should accept a valid name and price."""
    item = MenuItemCreate(name="Margherita", price=Decimal("9.99"), category="Pizza")
    assert item.name == "Margherita"
    assert item.price == Decimal("9.99")
    assert item.category == "Pizza"


def test_valid_item_without_price():
    """MenuItemCreate should accept None price."""
    item = MenuItemCreate(name="House Salad", price=None)
    assert item.name == "House Salad"
    assert item.price is None
    assert item.category is None


def test_blank_name_fails():
    """MenuItemCreate should reject a name that is blank after stripping."""
    with pytest.raises(ValidationError) as exc_info:
        MenuItemCreate(name="   ", price=Decimal("5.00"))
    errors = exc_info.value.errors()
    assert any("name" in str(e["loc"]) for e in errors)


def test_negative_price_fails():
    """MenuItemCreate should reject a negative price."""
    with pytest.raises(ValidationError) as exc_info:
        MenuItemCreate(name="Espresso", price=Decimal("-1.00"))
    errors = exc_info.value.errors()
    assert any("price" in str(e["loc"]) for e in errors)


def test_non_numeric_price_fails():
    """MenuItemCreate should reject a non-numeric price string via Pydantic coercion."""
    with pytest.raises(ValidationError):
        MenuItemCreate(name="Espresso", price="not-a-number")  # type: ignore[arg-type]


def test_price_with_more_than_two_decimals_fails():
    """MenuItemCreate should reject prices with more than 2 decimal places."""
    with pytest.raises(ValidationError) as exc_info:
        MenuItemCreate(name="Espresso", price=Decimal("1.999"))
    errors = exc_info.value.errors()
    assert any("price" in str(e["loc"]) for e in errors)


def test_zero_price_fails():
    """MenuItemCreate should reject a price of exactly zero."""
    with pytest.raises(ValidationError):
        MenuItemCreate(name="Water", price=Decimal("0.00"))


def test_name_is_stripped():
    """MenuItemCreate should strip whitespace from the name."""
    item = MenuItemCreate(name="  Tiramisu  ")
    assert item.name == "Tiramisu"


def test_empty_name_fails():
    """MenuItemCreate should reject an empty name string."""
    with pytest.raises(ValidationError):
        MenuItemCreate(name="")
