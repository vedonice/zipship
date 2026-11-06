"""Test fixtures and factories for Cart and CartItem models."""
import factory
from datetime import datetime, timedelta
from uuid import uuid4

from src.models.cart import Cart
from src.models.cart_item import CartItem


class CartFactory(factory.Factory):
    """Factory for creating test Cart instances."""

    class Meta:
        model = Cart

    cart_id = factory.LazyFunction(uuid4)
    user_id = factory.LazyFunction(uuid4)
    status = "active"
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)
    expires_at = factory.LazyFunction(lambda: datetime.now() + timedelta(hours=24))


class CartItemFactory(factory.Factory):
    """Factory for creating test CartItem instances."""

    class Meta:
        model = CartItem

    cart_item_id = factory.LazyFunction(uuid4)
    cart_id = factory.LazyFunction(uuid4)
    product_id = factory.LazyFunction(uuid4)
    product_name = factory.Faker("word")
    quantity = factory.Faker("random_int", min=1, max=999)
    unit_price = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    subtotal = factory.LazyAttribute(lambda o: o.unit_price * o.quantity if hasattr(o, "unit_price") and hasattr(o, "quantity") else 0)
    added_at = factory.LazyFunction(datetime.now)


def create_cart_with_items(user_id=None, item_count=3):
    """Create a Cart with associated CartItems.

    Args:
        user_id: User ID for the cart (generated if None)
        item_count: Number of items to add (default 3)

    Returns:
        Tuple of (Cart, List[CartItem])
    """
    cart = CartFactory(user_id=user_id or uuid4())
    items = [CartItemFactory(cart_id=cart.cart_id) for _ in range(item_count)]
    return cart, items


def create_expired_cart(user_id=None):
    """Create an expired Cart (expires_at in past).

    Args:
        user_id: User ID for the cart (generated if None)

    Returns:
        Cart with expires_at in the past
    """
    return CartFactory(
        user_id=user_id or uuid4(),
        expires_at=datetime.now() - timedelta(hours=1)
    )


def create_abandoned_cart(user_id=None):
    """Create a Cart with 'abandoned' status.

    Args:
        user_id: User ID for the cart (generated if None)

    Returns:
        Cart with status='abandoned'
    """
    return CartFactory(
        user_id=user_id or uuid4(),
        status="abandoned"
    )
