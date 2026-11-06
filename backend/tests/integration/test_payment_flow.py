"""Integration tests for payment flow."""
import pytest
from decimal import Decimal
from uuid import uuid4

from src.db.session import SessionLocal
from src.models.order import Order, OrderStatus
from src.models.payment import Payment, PaymentStatus
from src.services.payment_service import PaymentService
from src.utils.errors import ValidationError, NotFoundError


@pytest.fixture
def db():
    """Get test database session."""
    db = SessionLocal()
    yield db
    db.close()


class TestPaymentFlow:
    """Test payment processing flow."""

    def test_payment_creates_payment_record(self, db):
        """Verify payment creates Payment model record."""
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
        db.add(order)
        db.commit()

        payment_service = PaymentService(db)
        payment_data = payment_service.process_payment(
            order_id=order.order_id,
            user_id=user_id,
            amount=Decimal('113.00'),
            idempotency_key=str(uuid4()),
            processor_transaction_id="txn_123456"
        )

        assert payment_data['payment_id']
        assert payment_data['status'] == PaymentStatus.SUCCESS.value
        assert payment_data['processor_transaction_id'] == "txn_123456"

    def test_payment_idempotency_prevents_duplicates(self, db):
        """Verify idempotency key prevents duplicate charges."""
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
        db.add(order)
        db.commit()

        payment_service = PaymentService(db)
        idempotency_key = str(uuid4())

        # First payment
        payment_data_1 = payment_service.process_payment(
            order_id=order.order_id,
            user_id=user_id,
            amount=Decimal('113.00'),
            idempotency_key=idempotency_key,
            processor_transaction_id="txn_123456"
        )

        # Second payment with same idempotency key
        payment_data_2 = payment_service.process_payment(
            order_id=order.order_id,
            user_id=user_id,
            amount=Decimal('113.00'),
            idempotency_key=idempotency_key,
            processor_transaction_id="txn_123456"
        )

        # Should return same payment
        assert payment_data_1['payment_id'] == payment_data_2['payment_id']

    def test_payment_confirms_order(self, db):
        """Verify payment changes order status to CONFIRMED."""
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
            total_amount=Decimal('113.00'),
            status=OrderStatus.PENDING.value
        )
        db.add(order)
        db.commit()

        payment_service = PaymentService(db)
        payment_service.process_payment(
            order_id=order.order_id,
            user_id=user_id,
            amount=Decimal('113.00'),
            idempotency_key=str(uuid4())
        )

        # Refresh order to get updated status
        db.refresh(order)
        assert order.status == OrderStatus.CONFIRMED.value

    def test_payment_validates_amount_matches_order(self, db):
        """Verify payment amount must match order total."""
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
        db.add(order)
        db.commit()

        payment_service = PaymentService(db)

        with pytest.raises(ValidationError):
            payment_service.process_payment(
                order_id=order.order_id,
                user_id=user_id,
                amount=Decimal('100.00'),  # Wrong amount
                idempotency_key=str(uuid4())
            )

    def test_payment_validates_ownership(self, db):
        """Verify payment validates order ownership."""
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
        db.add(order)
        db.commit()

        payment_service = PaymentService(db)

        with pytest.raises(ValidationError):
            payment_service.process_payment(
                order_id=order.order_id,
                user_id=user_id_2,  # Different user
                amount=Decimal('113.00'),
                idempotency_key=str(uuid4())
            )

    def test_payment_order_not_found(self, db):
        """Verify error when order doesn't exist."""
        user_id = uuid4()

        payment_service = PaymentService(db)

        with pytest.raises(NotFoundError):
            payment_service.process_payment(
                order_id=uuid4(),  # Non-existent
                user_id=user_id,
                amount=Decimal('113.00'),
                idempotency_key=str(uuid4())
            )

    def test_get_payment(self, db):
        """Verify payment retrieval by ID."""
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
        db.add(order)
        db.commit()

        payment_service = PaymentService(db)
        payment_data_created = payment_service.process_payment(
            order_id=order.order_id,
            user_id=user_id,
            amount=Decimal('113.00'),
            idempotency_key=str(uuid4())
        )

        payment_data_retrieved = payment_service.get_payment(
            payment_id=__import__('uuid').UUID(payment_data_created['payment_id']),
            user_id=user_id
        )

        assert payment_data_retrieved['payment_id'] == payment_data_created['payment_id']

    def test_get_payment_by_order(self, db):
        """Verify payment retrieval by order ID."""
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
        db.add(order)
        db.commit()

        payment_service = PaymentService(db)
        payment_data_created = payment_service.process_payment(
            order_id=order.order_id,
            user_id=user_id,
            amount=Decimal('113.00'),
            idempotency_key=str(uuid4())
        )

        payment_data_retrieved = payment_service.get_payment_by_order(order.order_id)

        assert payment_data_retrieved is not None
        assert payment_data_retrieved['order_id'] == str(order.order_id)
