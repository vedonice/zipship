"""Integration tests for bill generation flow."""
import pytest
import json
import re
from decimal import Decimal
from uuid import uuid4

from src.db.session import SessionLocal
from src.models.order import Order
from src.models.order_item import OrderItem
from src.models.bill import Bill
from src.services.bill_service import BillService, BillNumberGenerator
from src.utils.errors import ValidationError, NotFoundError


@pytest.fixture
def db():
    """Get test database session."""
    db = SessionLocal()
    yield db
    db.close()


class TestBillFlow:
    """Test bill generation flow."""

    def test_bill_generation_creates_bill(self, db):
        """Verify bill generation creates Bill record."""
        user_id = uuid4()
        order = Order(
            user_id=user_id,
            cart_id=uuid4(),
            shipping_street="123 Main St",
            shipping_city="Chicago",
            shipping_state="IL",
            shipping_postal_code="60601",
            shipping_country="USA",
            items_subtotal=Decimal('100.00'),
            shipping_fee=Decimal('5.00'),
            tax_amount=Decimal('8.00'),
            total_amount=Decimal('113.00')
        )
        item = OrderItem(
            order_id=None,
            product_id=uuid4(),
            product_name="Test Product",
            quantity=2,
            unit_price=Decimal('50.00'),
            subtotal=Decimal('100.00')
        )
        order.items.append(item)
        db.add(order)
        db.commit()

        bill_service = BillService(db)
        bill_data = bill_service.generate_bill(order.order_id, user_id)

        assert bill_data['bill_id']
        assert bill_data['bill_number']
        assert bill_data['status'] == 'generated'
        assert bill_data['total'] == 113.00

    def test_bill_number_format(self, db):
        """Verify bill number is in INV-YYYY-XXXXXX format."""
        order_id = uuid4()
        bill_number = BillNumberGenerator.generate(order_id)

        # Pattern: INV-YYYY-XXXXXX (6 hex chars)
        pattern = r'^INV-\d{4}-[a-fA-F0-9]{6}$'
        assert re.match(pattern, bill_number), f"Bill number {bill_number} doesn't match expected format"

    def test_bill_includes_order_items(self, db):
        """Verify bill includes serialized order items."""
        user_id = uuid4()
        order = Order(
            user_id=user_id,
            cart_id=uuid4(),
            shipping_street="123 Main St",
            shipping_city="Chicago",
            shipping_state="IL",
            shipping_postal_code="60601",
            shipping_country="USA",
            items_subtotal=Decimal('100.00'),
            shipping_fee=Decimal('5.00'),
            tax_amount=Decimal('8.00'),
            total_amount=Decimal('113.00')
        )
        item = OrderItem(
            order_id=None,
            product_id=uuid4(),
            product_name="Test Product",
            quantity=2,
            unit_price=Decimal('50.00'),
            subtotal=Decimal('100.00')
        )
        order.items.append(item)
        db.add(order)
        db.commit()

        bill_service = BillService(db)
        bill_data = bill_service.generate_bill(order.order_id, user_id)

        assert len(bill_data['items']) == 1
        assert bill_data['items'][0]['product_name'] == "Test Product"
        assert bill_data['items'][0]['quantity'] == 2

    def test_bill_includes_all_costs(self, db):
        """Verify bill includes subtotal, shipping, tax, and total."""
        user_id = uuid4()
        order = Order(
            user_id=user_id,
            cart_id=uuid4(),
            shipping_street="123 Main St",
            shipping_city="Chicago",
            shipping_state="IL",
            shipping_postal_code="60601",
            shipping_country="USA",
            items_subtotal=Decimal('100.00'),
            shipping_fee=Decimal('5.00'),
            tax_amount=Decimal('8.00'),
            total_amount=Decimal('113.00')
        )
        item = OrderItem(
            order_id=None,
            product_id=uuid4(),
            product_name="Test Product",
            quantity=1,
            unit_price=Decimal('100.00'),
            subtotal=Decimal('100.00')
        )
        order.items.append(item)
        db.add(order)
        db.commit()

        bill_service = BillService(db)
        bill_data = bill_service.generate_bill(order.order_id, user_id)

        assert bill_data['subtotal'] == 100.00
        assert bill_data['shipping_fee'] == 5.00
        assert bill_data['tax_amount'] == 8.00
        assert bill_data['total'] == 113.00

    def test_bill_prevents_duplicates(self, db):
        """Verify bill generation is idempotent (one bill per order)."""
        user_id = uuid4()
        order = Order(
            user_id=user_id,
            cart_id=uuid4(),
            shipping_street="123 Main St",
            shipping_city="Chicago",
            shipping_state="IL",
            shipping_postal_code="60601",
            shipping_country="USA",
            items_subtotal=Decimal('100.00'),
            shipping_fee=Decimal('5.00'),
            tax_amount=Decimal('8.00'),
            total_amount=Decimal('113.00')
        )
        item = OrderItem(
            order_id=None,
            product_id=uuid4(),
            product_name="Test Product",
            quantity=1,
            unit_price=Decimal('100.00'),
            subtotal=Decimal('100.00')
        )
        order.items.append(item)
        db.add(order)
        db.commit()

        bill_service = BillService(db)

        # Generate bill twice
        bill_data_1 = bill_service.generate_bill(order.order_id, user_id)
        bill_data_2 = bill_service.generate_bill(order.order_id, user_id)

        # Should return same bill
        assert bill_data_1['bill_id'] == bill_data_2['bill_id']

    def test_bill_validates_ownership(self, db):
        """Verify user can only access their own bills."""
        user_id_1 = uuid4()
        user_id_2 = uuid4()

        order = Order(
            user_id=user_id_1,
            cart_id=uuid4(),
            shipping_street="123 Main St",
            shipping_city="Chicago",
            shipping_state="IL",
            shipping_postal_code="60601",
            shipping_country="USA",
            items_subtotal=Decimal('100.00'),
            shipping_fee=Decimal('5.00'),
            tax_amount=Decimal('8.00'),
            total_amount=Decimal('113.00')
        )
        item = OrderItem(
            order_id=None,
            product_id=uuid4(),
            product_name="Test Product",
            quantity=1,
            unit_price=Decimal('100.00'),
            subtotal=Decimal('100.00')
        )
        order.items.append(item)
        db.add(order)
        db.commit()

        bill_service = BillService(db)
        bill_service.generate_bill(order.order_id, user_id_1)

        # Try to access with different user
        with pytest.raises(ValidationError):
            bill_service.get_bill_by_order(order.order_id, user_id_2)

    def test_get_bill_by_order(self, db):
        """Verify bill retrieval by order ID."""
        user_id = uuid4()
        order = Order(
            user_id=user_id,
            cart_id=uuid4(),
            shipping_street="123 Main St",
            shipping_city="Chicago",
            shipping_state="IL",
            shipping_postal_code="60601",
            shipping_country="USA",
            items_subtotal=Decimal('100.00'),
            shipping_fee=Decimal('5.00'),
            tax_amount=Decimal('8.00'),
            total_amount=Decimal('113.00')
        )
        item = OrderItem(
            order_id=None,
            product_id=uuid4(),
            product_name="Test Product",
            quantity=1,
            unit_price=Decimal('100.00'),
            subtotal=Decimal('100.00')
        )
        order.items.append(item)
        db.add(order)
        db.commit()

        bill_service = BillService(db)
        bill_data_created = bill_service.generate_bill(order.order_id, user_id)

        bill_data_retrieved = bill_service.get_bill_by_order(order.order_id, user_id)

        assert bill_data_retrieved is not None
        assert bill_data_retrieved['bill_id'] == bill_data_created['bill_id']

    def test_get_bill_by_id(self, db):
        """Verify bill retrieval by bill ID."""
        user_id = uuid4()
        order = Order(
            user_id=user_id,
            cart_id=uuid4(),
            shipping_street="123 Main St",
            shipping_city="Chicago",
            shipping_state="IL",
            shipping_postal_code="60601",
            shipping_country="USA",
            items_subtotal=Decimal('100.00'),
            shipping_fee=Decimal('5.00'),
            tax_amount=Decimal('8.00'),
            total_amount=Decimal('113.00')
        )
        item = OrderItem(
            order_id=None,
            product_id=uuid4(),
            product_name="Test Product",
            quantity=1,
            unit_price=Decimal('100.00'),
            subtotal=Decimal('100.00')
        )
        order.items.append(item)
        db.add(order)
        db.commit()

        bill_service = BillService(db)
        bill_data_created = bill_service.generate_bill(order.order_id, user_id)

        bill_data_retrieved = bill_service.get_bill(
            __import__('uuid').UUID(bill_data_created['bill_id']),
            user_id
        )

        assert bill_data_retrieved['bill_id'] == bill_data_created['bill_id']

    def test_bill_order_not_found(self, db):
        """Verify error when order doesn't exist."""
        bill_service = BillService(db)

        with pytest.raises(NotFoundError):
            bill_service.generate_bill(uuid4())

    def test_bill_not_found(self, db):
        """Verify error when bill doesn't exist."""
        bill_service = BillService(db)

        with pytest.raises(NotFoundError):
            bill_service.get_bill(uuid4())

    def test_bill_items_json_structure(self, db):
        """Verify bill items JSON has correct structure."""
        user_id = uuid4()
        order = Order(
            user_id=user_id,
            cart_id=uuid4(),
            shipping_street="123 Main St",
            shipping_city="Chicago",
            shipping_state="IL",
            shipping_postal_code="60601",
            shipping_country="USA",
            items_subtotal=Decimal('100.00'),
            shipping_fee=Decimal('5.00'),
            tax_amount=Decimal('8.00'),
            total_amount=Decimal('113.00')
        )
        item = OrderItem(
            order_id=None,
            product_id=uuid4(),
            product_name="Test Product",
            quantity=2,
            unit_price=Decimal('50.00'),
            subtotal=Decimal('100.00')
        )
        order.items.append(item)
        db.add(order)
        db.commit()

        bill_service = BillService(db)
        bill_data = bill_service.generate_bill(order.order_id, user_id)

        # Verify items structure
        assert isinstance(bill_data['items'], list)
        assert len(bill_data['items']) > 0
        assert 'product_id' in bill_data['items'][0]
        assert 'product_name' in bill_data['items'][0]
        assert 'quantity' in bill_data['items'][0]
        assert 'unit_price' in bill_data['items'][0]
        assert 'subtotal' in bill_data['items'][0]
