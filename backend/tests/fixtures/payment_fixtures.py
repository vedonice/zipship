"""Test fixtures for Payment model using factory_boy."""
import factory
from decimal import Decimal
from uuid import uuid4

from src.models.payment import Payment, PaymentStatus
from src.db.session import SessionLocal


class PaymentFactory(factory.Factory):
    """Factory for creating Payment instances."""

    class Meta:
        model = Payment

    payment_id = factory.LazyFunction(uuid4)
    order_id = factory.LazyFunction(uuid4)
    amount = Decimal('113.00')
    status = PaymentStatus.SUCCESS.value
    processor_transaction_id = factory.LazyFunction(lambda: f"txn_{uuid4().hex[:8]}")
    idempotency_key = factory.LazyFunction(lambda: str(uuid4()))


# Helper functions
def create_successful_payment(order_id=None, amount=None, db=None):
    """Create a successful payment for testing.

    Args:
        order_id: Order ID for the payment
        amount: Payment amount (default 113.00)
        db: Database session

    Returns:
        Successful Payment instance
    """
    if db is None:
        db = SessionLocal()

    if order_id is None:
        order_id = uuid4()

    if amount is None:
        amount = Decimal('113.00')

    payment = PaymentFactory(
        order_id=order_id,
        amount=amount,
        status=PaymentStatus.SUCCESS.value
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def create_pending_payment(order_id=None, amount=None, db=None):
    """Create a pending payment for testing.

    Args:
        order_id: Order ID for the payment
        amount: Payment amount (default 113.00)
        db: Database session

    Returns:
        Pending Payment instance
    """
    if db is None:
        db = SessionLocal()

    if order_id is None:
        order_id = uuid4()

    if amount is None:
        amount = Decimal('113.00')

    payment = PaymentFactory(
        order_id=order_id,
        amount=amount,
        status=PaymentStatus.PENDING.value,
        processor_transaction_id=None
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def create_failed_payment(order_id=None, amount=None, db=None):
    """Create a failed payment for testing.

    Args:
        order_id: Order ID for the payment
        amount: Payment amount (default 113.00)
        db: Database session

    Returns:
        Failed Payment instance
    """
    if db is None:
        db = SessionLocal()

    if order_id is None:
        order_id = uuid4()

    if amount is None:
        amount = Decimal('113.00')

    payment = PaymentFactory(
        order_id=order_id,
        amount=amount,
        status=PaymentStatus.FAILED.value,
        processor_transaction_id=None
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def create_payment_with_idempotency(
    order_id=None,
    amount=None,
    idempotency_key=None,
    db=None
):
    """Create a payment with specific idempotency key for testing duplicate prevention.

    Args:
        order_id: Order ID for the payment
        amount: Payment amount (default 113.00)
        idempotency_key: Idempotency key for duplicate prevention
        db: Database session

    Returns:
        Payment instance with specific idempotency key
    """
    if db is None:
        db = SessionLocal()

    if order_id is None:
        order_id = uuid4()

    if amount is None:
        amount = Decimal('113.00')

    if idempotency_key is None:
        idempotency_key = str(uuid4())

    payment = PaymentFactory(
        order_id=order_id,
        amount=amount,
        idempotency_key=idempotency_key
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
