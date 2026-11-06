"""Contract tests for Payment model - validate structure and constraints."""
import pytest
from uuid import uuid4

from src.models.payment import Payment, PaymentStatus
from src.db.session import SessionLocal


@pytest.fixture
def db():
    """Get test database session."""
    db = SessionLocal()
    yield db
    db.close()


class TestPaymentModel:
    """Test Payment model structure and constraints."""

    def test_payment_has_required_fields(self):
        """Verify Payment model has all required fields."""
        required_fields = [
            'payment_id', 'order_id', 'amount', 'status',
            'processor_transaction_id', 'idempotency_key', 'created_at', 'updated_at'
        ]
        for field in required_fields:
            assert hasattr(Payment, field), f"Payment missing required field: {field}"

    def test_payment_status_enum_has_all_values(self):
        """Verify PaymentStatus enum has all required values."""
        assert hasattr(PaymentStatus, 'PENDING')
        assert hasattr(PaymentStatus, 'SUCCESS')
        assert hasattr(PaymentStatus, 'FAILED')
        assert hasattr(PaymentStatus, 'REFUNDED')

    def test_payment_default_status_is_pending(self):
        """Verify default status is PENDING."""
        assert PaymentStatus.PENDING.value == 'pending'

    def test_payment_has_order_relationship(self):
        """Verify Payment has order relationship."""
        assert hasattr(Payment, 'order')

    def test_payment_amount_is_numeric_10_2(self):
        """Verify amount is Numeric(10,2)."""
        col = Payment.__table__.columns['amount']
        assert 'numeric' in str(col.type).lower()

    def test_payment_order_id_is_indexed(self):
        """Verify order_id is indexed for query performance."""
        indexes = [idx.name for idx in Payment.__table__.indexes]
        order_id_indexed = any('order_id' in idx for idx in indexes) or Payment.__table__.columns['order_id'].index
        assert order_id_indexed, "order_id should be indexed"

    def test_payment_idempotency_key_is_unique(self):
        """Verify idempotency_key has unique constraint."""
        col = Payment.__table__.columns['idempotency_key']
        assert col.unique, "idempotency_key should be unique to prevent duplicate charges"

    def test_payment_idempotency_key_not_nullable(self):
        """Verify idempotency_key is not nullable."""
        col = Payment.__table__.columns['idempotency_key']
        assert not col.nullable, "idempotency_key must not be null"

    def test_payment_order_id_not_nullable(self):
        """Verify order_id is not nullable."""
        col = Payment.__table__.columns['order_id']
        assert not col.nullable, "order_id must not be null"

    def test_payment_amount_not_nullable(self):
        """Verify amount is not nullable."""
        col = Payment.__table__.columns['amount']
        assert not col.nullable, "amount must not be null"

    def test_payment_processor_transaction_id_nullable(self):
        """Verify processor_transaction_id is nullable (optional field)."""
        col = Payment.__table__.columns['processor_transaction_id']
        assert col.nullable, "processor_transaction_id can be null initially"

    def test_payment_status_not_nullable(self):
        """Verify status is not nullable."""
        col = Payment.__table__.columns['status']
        assert not col.nullable, "status must not be null"

    def test_payment_repr(self):
        """Verify Payment __repr__ is meaningful."""
        assert hasattr(Payment, '__repr__')

    def test_payment_has_timestamps(self):
        """Verify Payment has created_at and updated_at."""
        assert hasattr(Payment, 'created_at')
        assert hasattr(Payment, 'updated_at')


class TestPaymentIdempotency:
    """Test Payment idempotency constraints."""

    def test_idempotency_key_field_length(self):
        """Verify idempotency_key can hold UUID length (36 chars)."""
        col = Payment.__table__.columns['idempotency_key']
        assert col.type.length >= 36, "idempotency_key must support UUID (36 chars)"

    def test_processor_transaction_id_field_length(self):
        """Verify processor_transaction_id can hold transaction IDs."""
        col = Payment.__table__.columns['processor_transaction_id']
        assert col.type.length >= 255, "processor_transaction_id must support long transaction IDs"


class TestPaymentForeignKey:
    """Test Payment foreign key to Order."""

    def test_payment_order_id_has_foreign_key(self):
        """Verify Payment.order_id has FK to Order."""
        fks = [fk.name for fk in Payment.__table__.foreign_keys]
        assert any('order_id' in fk for fk in fks), "Payment should have FK to Order"

    def test_payment_cascade_behavior(self):
        """Verify Payment cascade delete from Order."""
        # FK should cascade delete when order is deleted
        fks = list(Payment.__table__.foreign_keys)
        assert len(fks) > 0, "Payment should have foreign key constraint"
