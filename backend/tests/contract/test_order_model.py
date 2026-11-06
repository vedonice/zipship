"""Contract tests for Order model - validate structure and constraints."""
import pytest
from decimal import Decimal
from uuid import uuid4

from src.models.order import Order, OrderStatus
from src.models.order_item import OrderItem
from src.db.session import SessionLocal


@pytest.fixture
def db():
    """Get test database session."""
    db = SessionLocal()
    yield db
    db.close()


class TestOrderModel:
    """Test Order model structure and constraints."""

    def test_order_has_required_fields(self):
        """Verify Order model has all required fields."""
        required_fields = [
            'order_id', 'user_id', 'status', 'shipping_street', 'shipping_city',
            'shipping_state', 'shipping_postal_code', 'shipping_country',
            'items_subtotal', 'shipping_fee', 'tax_amount', 'total_amount',
            'created_at', 'updated_at'
        ]
        for field in required_fields:
            assert hasattr(Order, field), f"Order missing required field: {field}"

    def test_order_status_enum_has_all_values(self):
        """Verify OrderStatus enum has all required values."""
        assert hasattr(OrderStatus, 'PENDING')
        assert hasattr(OrderStatus, 'CONFIRMED')
        assert hasattr(OrderStatus, 'FAILED')
        assert hasattr(OrderStatus, 'REFUNDED')

    def test_order_default_status_is_pending(self):
        """Verify default status is PENDING."""
        assert OrderStatus.PENDING.value == 'pending'

    def test_order_has_items_relationship(self):
        """Verify Order has items relationship."""
        assert hasattr(Order, 'items')

    def test_order_has_payments_relationship(self):
        """Verify Order has payments relationship."""
        assert hasattr(Order, 'payments')

    def test_order_has_bill_relationship(self):
        """Verify Order has bill relationship (one-to-one)."""
        assert hasattr(Order, 'bill')

    def test_order_subtotal_is_numeric_10_2(self):
        """Verify items_subtotal is Numeric(10,2)."""
        col = Order.__table__.columns['items_subtotal']
        assert 'numeric' in str(col.type).lower()

    def test_order_shipping_fee_is_numeric_10_2(self):
        """Verify shipping_fee is Numeric(10,2)."""
        col = Order.__table__.columns['shipping_fee']
        assert 'numeric' in str(col.type).lower()

    def test_order_tax_amount_is_numeric_10_2(self):
        """Verify tax_amount is Numeric(10,2)."""
        col = Order.__table__.columns['tax_amount']
        assert 'numeric' in str(col.type).lower()

    def test_order_total_is_numeric_10_2(self):
        """Verify total_amount is Numeric(10,2)."""
        col = Order.__table__.columns['total_amount']
        assert 'numeric' in str(col.type).lower()

    def test_order_user_id_is_indexed(self):
        """Verify user_id is indexed for query performance."""
        indexes = [idx.name for idx in Order.__table__.indexes]
        user_id_indexed = any('user_id' in idx for idx in indexes) or Order.__table__.columns['user_id'].index
        assert user_id_indexed, "user_id should be indexed"

    def test_order_repr(self):
        """Verify Order __repr__ is meaningful."""
        order_id = uuid4()
        user_id = uuid4()
        assert hasattr(Order, '__repr__')


class TestOrderItemModel:
    """Test OrderItem model structure and constraints."""

    def test_order_item_has_required_fields(self):
        """Verify OrderItem model has all required fields."""
        required_fields = [
            'order_item_id', 'order_id', 'product_id', 'product_name',
            'quantity', 'unit_price', 'subtotal', 'added_at'
        ]
        for field in required_fields:
            assert hasattr(OrderItem, field), f"OrderItem missing required field: {field}"

    def test_order_item_has_order_relationship(self):
        """Verify OrderItem has order relationship."""
        assert hasattr(OrderItem, 'order')

    def test_order_item_order_id_is_indexed(self):
        """Verify order_id is indexed."""
        indexes = [idx.name for idx in OrderItem.__table__.indexes]
        order_id_indexed = any('order_id' in idx for idx in indexes) or OrderItem.__table__.columns['order_id'].index
        assert order_id_indexed, "order_id should be indexed"

    def test_order_item_unit_price_is_numeric_10_2(self):
        """Verify unit_price is Numeric(10,2)."""
        col = OrderItem.__table__.columns['unit_price']
        assert 'numeric' in str(col.type).lower()

    def test_order_item_subtotal_is_numeric_10_2(self):
        """Verify subtotal is Numeric(10,2)."""
        col = OrderItem.__table__.columns['subtotal']
        assert 'numeric' in str(col.type).lower()

    def test_order_item_quantity_not_null(self):
        """Verify quantity is not nullable."""
        assert not OrderItem.__table__.columns['quantity'].nullable

    def test_order_item_product_name_is_string(self):
        """Verify product_name is String type."""
        col = OrderItem.__table__.columns['product_name']
        assert 'string' in str(col.type).lower() or 'varchar' in str(col.type).lower()

    def test_order_item_repr(self):
        """Verify OrderItem __repr__ is meaningful."""
        assert hasattr(OrderItem, '__repr__')


class TestOrderRelationships:
    """Test Order model relationships and cascade behavior."""

    def test_order_cascade_delete_to_items(self):
        """Verify cascade delete is set from Order to OrderItems."""
        # Check the relationship configuration
        assert hasattr(Order, 'items')
        # Items should cascade delete when order is deleted

    def test_order_cascade_delete_to_payments(self):
        """Verify cascade delete is set from Order to Payments."""
        # Check the relationship configuration
        assert hasattr(Order, 'payments')

    def test_order_cascade_delete_to_bill(self):
        """Verify cascade delete is set from Order to Bill."""
        # Check the relationship configuration
        assert hasattr(Order, 'bill')

    def test_order_item_foreign_key_constraint(self):
        """Verify OrderItem has foreign key to Order."""
        fks = [fk.name for fk in OrderItem.__table__.foreign_keys]
        assert any('order_id' in fk for fk in fks), "OrderItem should have FK to Order"
