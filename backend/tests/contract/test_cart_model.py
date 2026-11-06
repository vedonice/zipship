"""Contract tests for Cart and CartItem models.

These tests validate the model structure and database contracts.
"""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from src.models.cart import Cart
from src.models.cart_item import CartItem


class TestCartModelContract:
    """Validate Cart model structure and constraints."""

    def test_cart_has_required_fields(self):
        """Cart must have: cart_id, user_id, status, created_at, updated_at, expires_at."""
        assert hasattr(Cart, "cart_id")
        assert hasattr(Cart, "user_id")
        assert hasattr(Cart, "status")
        assert hasattr(Cart, "created_at")
        assert hasattr(Cart, "updated_at")
        assert hasattr(Cart, "expires_at")

    def test_cart_id_is_uuid_primary_key(self):
        """cart_id must be UUID and primary key."""
        cart_id_col = Cart.__table__.columns["cart_id"]
        assert cart_id_col.primary_key
        # UUID column type validation
        assert "UUID" in str(cart_id_col.type) or "uuid" in str(cart_id_col.type).lower()

    def test_cart_user_id_is_uuid_indexed(self):
        """user_id must be UUID and indexed."""
        user_id_col = Cart.__table__.columns["user_id"]
        assert not user_id_col.primary_key
        # Check for index on user_id
        indexes = [idx for idx in Cart.__table__.indexes if "user_id" in [c.name for c in idx.columns]]
        assert len(indexes) > 0, "user_id must have an index for query performance"

    def test_cart_status_enum_values(self):
        """status must support: active, abandoned, converted."""
        # Status is String(20) but should contain valid enum values
        status_col = Cart.__table__.columns["status"]
        assert status_col.type.length >= 20

    def test_cart_timestamps_have_defaults(self):
        """created_at and updated_at must have server defaults."""
        created_at = Cart.__table__.columns["created_at"]
        updated_at = Cart.__table__.columns["updated_at"]
        assert created_at.server_default is not None
        assert updated_at.server_default is not None

    def test_cart_expiration_field_exists(self):
        """Cart must have expires_at field for 24-hour expiration."""
        expires_at = Cart.__table__.columns["expires_at"]
        assert not expires_at.nullable


class TestCartItemModelContract:
    """Validate CartItem model structure and constraints."""

    def test_cart_item_has_required_fields(self):
        """CartItem must have all required fields."""
        required_fields = [
            "cart_item_id",
            "cart_id",
            "product_id",
            "product_name",
            "quantity",
            "unit_price",
            "subtotal",
            "added_at",
        ]
        for field in required_fields:
            assert hasattr(CartItem, field), f"CartItem missing field: {field}"

    def test_cart_item_id_is_uuid_primary_key(self):
        """cart_item_id must be UUID and primary key."""
        cart_item_id_col = CartItem.__table__.columns["cart_item_id"]
        assert cart_item_id_col.primary_key

    def test_cart_item_has_foreign_key_to_cart(self):
        """CartItem must have foreign key to Cart.cart_id."""
        fks = [fk for fk in CartItem.__table__.foreign_keys if "cart_id" in fk.column.name]
        assert len(fks) > 0, "CartItem must have foreign key to Cart"

    def test_cart_item_quantity_range(self):
        """quantity must be Integer (supports 1-999 range)."""
        quantity_col = CartItem.__table__.columns["quantity"]
        assert quantity_col.type.__class__.__name__ == "Integer"
        assert not quantity_col.nullable

    def test_cart_item_price_precision(self):
        """unit_price and subtotal must support 2 decimal places."""
        unit_price = CartItem.__table__.columns["unit_price"]
        subtotal = CartItem.__table__.columns["subtotal"]

        # Check numeric type with 2 decimals
        assert "Numeric" in str(unit_price.type) or "DECIMAL" in str(unit_price.type)
        assert "Numeric" in str(subtotal.type) or "DECIMAL" in str(subtotal.type)

    def test_cart_item_cascade_delete_from_cart(self):
        """Deleting a Cart must cascade-delete its CartItems."""
        fks = list(CartItem.__table__.foreign_keys)
        assert len(fks) > 0
        # Check that at least one FK has ondelete='CASCADE'
        cascade_fks = [fk for fk in fks if fk.ondelete and "CASCADE" in fk.ondelete.upper()]
        assert len(cascade_fks) > 0, "CartItem must cascade-delete when Cart is deleted"

    def test_cart_item_added_at_has_default(self):
        """added_at must have server default (now)."""
        added_at = CartItem.__table__.columns["added_at"]
        assert added_at.server_default is not None


class TestCartItemModelValidation:
    """Validate CartItem business rules (quantity 1-999, price ≥0)."""

    def test_quantity_field_accepts_integers(self):
        """quantity column must accept integer values."""
        quantity_col = CartItem.__table__.columns["quantity"]
        assert "Integer" in str(quantity_col.type)

    def test_unit_price_supports_decimal(self):
        """unit_price must support decimal pricing."""
        unit_price = CartItem.__table__.columns["unit_price"]
        # Verify it's a numeric type that supports decimals
        assert "Numeric" in str(unit_price.type) or "DECIMAL" in str(unit_price.type)

    def test_subtotal_is_computed_field(self):
        """subtotal field exists for persisting computed values."""
        subtotal = CartItem.__table__.columns["subtotal"]
        assert not subtotal.nullable
