"""Test fixtures for Order and OrderItem models using factory_boy."""
import factory
from decimal import Decimal
from uuid import uuid4

from src.models.order import Order, OrderStatus
from src.models.order_item import OrderItem
from src.db.session import SessionLocal


class OrderFactory(factory.Factory):
    """Factory for creating Order instances."""

    class Meta:
        model = Order

    order_id = factory.LazyFunction(uuid4)
    user_id = factory.LazyFunction(uuid4)
    cart_id = factory.LazyFunction(uuid4)
    status = OrderStatus.PENDING.value
    shipping_street = "123 Main Street"
    shipping_city = "Chicago"
    shipping_state = "IL"
    shipping_postal_code = "60601"
    shipping_country = "USA"
    items_subtotal = Decimal('100.00')
    shipping_fee = Decimal('5.00')
    tax_amount = Decimal('8.00')
    total_amount = Decimal('113.00')


class OrderItemFactory(factory.Factory):
    """Factory for creating OrderItem instances."""

    class Meta:
        model = OrderItem

    order_item_id = factory.LazyFunction(uuid4)
    order_id = factory.LazyFunction(uuid4)
    product_id = factory.LazyFunction(uuid4)
    product_name = "Test Product"
    quantity = 1
    unit_price = Decimal('50.00')
    subtotal = Decimal('50.00')


# Helper functions
def create_order_with_items(user_id=None, num_items=2, db=None):
    """Create an order with multiple items for testing.

    Args:
        user_id: User ID for the order (generated if not provided)
        num_items: Number of items to create
        db: Database session (uses default if not provided)

    Returns:
        Order instance with items persisted to database
    """
    if db is None:
        db = SessionLocal()

    if user_id is None:
        user_id = uuid4()

    order = OrderFactory(user_id=user_id)
    db.add(order)

    for i in range(num_items):
        item = OrderItemFactory(
            order_id=order.order_id,
            product_name=f"Product {i+1}",
            quantity=i + 1,
            unit_price=Decimal(f"{50 + i * 10}.00"),
            subtotal=Decimal(f"{(50 + i * 10) * (i + 1):.2f}")
        )
        order.items.append(item)

    db.commit()
    db.refresh(order)
    return order


def create_confirmed_order(user_id=None, db=None):
    """Create a confirmed order for payment testing.

    Args:
        user_id: User ID for the order
        db: Database session

    Returns:
        Confirmed Order instance
    """
    if db is None:
        db = SessionLocal()

    if user_id is None:
        user_id = uuid4()

    order = OrderFactory(
        user_id=user_id,
        status=OrderStatus.CONFIRMED.value
    )
    item = OrderItemFactory(order_id=order.order_id)
    order.items.append(item)

    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def create_pending_order(user_id=None, db=None):
    """Create a pending order for checkout testing.

    Args:
        user_id: User ID for the order
        db: Database session

    Returns:
        Pending Order instance
    """
    if db is None:
        db = SessionLocal()

    if user_id is None:
        user_id = uuid4()

    order = OrderFactory(
        user_id=user_id,
        status=OrderStatus.PENDING.value
    )
    item = OrderItemFactory(order_id=order.order_id)
    order.items.append(item)

    db.add(order)
    db.commit()
    db.refresh(order)
    return order
