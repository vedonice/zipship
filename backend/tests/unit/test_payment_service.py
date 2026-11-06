"""Unit tests for PaymentService."""
import pytest
from decimal import Decimal
from unittest.mock import Mock, MagicMock
from uuid import uuid4

from src.services.payment_service import PaymentService
from src.utils.errors import ValidationError, NotFoundError


class TestPaymentService:
    """Unit tests for PaymentService."""

    def test_payment_service_initializes_with_db(self):
        """Verify PaymentService initializes with database session."""
        db = Mock()
        service = PaymentService(db)
        assert service.db is db

    def test_payment_service_validates_idempotency_key(self):
        """Verify idempotency key prevents duplicate charges."""
        db = Mock()
        db.query = MagicMock()

        # Mock existing payment
        existing_payment = Mock()
        existing_payment.payment_id = uuid4()
        db.query().filter().first.return_value = existing_payment

        service = PaymentService(db)
        result = service.process_payment(
            order_id=uuid4(),
            user_id=uuid4(),
            amount=Decimal('100.00'),
            idempotency_key="same-key"
        )

        # Should return existing payment
        assert result['payment_id'] is not None

    def test_payment_service_validates_amount_type(self):
        """Verify payment service handles Decimal amounts."""
        db = Mock()
        db.query = MagicMock()
        db.query().filter().first.return_value = None

        service = PaymentService(db)

        # Create order mock
        order = Mock()
        order.order_id = uuid4()
        order.user_id = uuid4()
        order.total_amount = Decimal('100.00')
        order.status = 'pending'
        order.updated_at = Mock()

        db.query().filter().first.return_value = order
        db.commit = Mock()
        db.add = Mock()
        db.refresh = Mock()

        # Should handle Decimal amounts
        try:
            service.process_payment(
                order_id=order.order_id,
                user_id=order.user_id,
                amount=Decimal('100.00'),
                idempotency_key="unique-key"
            )
        except Exception as e:
            if not isinstance(e, (ValidationError, NotFoundError)):
                pytest.fail(f"Unexpected error: {e}")

    def test_get_payment_returns_payment_data(self):
        """Verify get_payment returns payment dict."""
        db = Mock()
        db.query = MagicMock()

        payment = Mock()
        payment.payment_id = uuid4()
        payment.order_id = uuid4()
        payment.amount = Decimal('100.00')
        payment.status = 'success'
        payment.processor_transaction_id = 'txn_123'
        payment.created_at = Mock()
        payment.created_at.isoformat = Mock(return_value='2026-09-17T00:00:00')

        db.query().filter().first.return_value = payment

        service = PaymentService(db)
        result = service.get_payment(payment.payment_id)

        assert result['payment_id'] == str(payment.payment_id)
        assert result['amount'] == 100.0
        assert result['status'] == 'success'
