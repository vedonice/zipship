"""Payment service for processing and tracking payments."""
import logging
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.order import Order, OrderStatus
from src.models.payment import Payment, PaymentStatus
from src.utils.errors import ValidationError, NotFoundError

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for processing payments with idempotency support."""

    def __init__(self, db: Session):
        """Initialize payment service.

        Args:
            db: Database session
        """
        self.db = db

    def process_payment(
        self,
        order_id: UUID,
        user_id: UUID,
        amount: Decimal,
        idempotency_key: str,
        processor_transaction_id: str = None,
    ) -> dict:
        """Process payment for order.

        Args:
            order_id: Order ID to pay
            user_id: User ID for ownership validation
            amount: Payment amount
            idempotency_key: Idempotency key to prevent duplicate charges
            processor_transaction_id: Transaction ID from payment processor

        Returns:
            Payment result dict with:
            - payment_id: Payment ID
            - order_id: Order ID
            - amount: Amount paid
            - status: Payment status
            - processor_transaction_id: Transaction ID

        Raises:
            ValidationError: If payment fails validation
            NotFoundError: If order not found
        """
        # Check for duplicate payment using idempotency key
        existing_payment = self.db.query(Payment).filter(
            Payment.idempotency_key == idempotency_key
        ).first()
        if existing_payment:
            logger.info(f"Duplicate payment detected for idempotency key {idempotency_key}, returning existing payment")
            return {
                "payment_id": str(existing_payment.payment_id),
                "order_id": str(existing_payment.order_id),
                "amount": float(existing_payment.amount),
                "status": existing_payment.status,
                "processor_transaction_id": existing_payment.processor_transaction_id,
            }

        # Get order
        order = self.db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            logger.warning(f"Order not found: {order_id}")
            raise NotFoundError(f"Order {order_id} not found")

        # Validate ownership
        if order.user_id != user_id:
            logger.warning(f"Unauthorized payment attempt: user {user_id} trying to pay order {order_id}")
            raise ValidationError("Unauthorized access to order")

        # Validate amount matches order total
        if Decimal(str(amount)) != order.total_amount:
            logger.warning(
                f"Payment amount mismatch: order {order_id} total {order.total_amount}, payment {amount}"
            )
            raise ValidationError(
                f"Payment amount {amount} does not match order total {order.total_amount}"
            )

        # Create payment record
        payment = Payment(
            payment_id=None,  # Will be auto-generated
            order_id=order_id,
            amount=Decimal(str(amount)),
            status=PaymentStatus.SUCCESS.value,
            processor_transaction_id=processor_transaction_id,
            idempotency_key=idempotency_key,
        )

        # Update order status to confirmed
        order.status = OrderStatus.CONFIRMED.value
        order.updated_at = __import__('datetime').datetime.utcnow()

        # Persist
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)

        logger.info(f"Payment processed: payment {payment.payment_id} for order {order_id}")

        return {
            "payment_id": str(payment.payment_id),
            "order_id": str(payment.order_id),
            "amount": float(payment.amount),
            "status": payment.status,
            "processor_transaction_id": payment.processor_transaction_id,
        }

    def get_payment(self, payment_id: UUID, user_id: UUID = None) -> dict:
        """Get payment details.

        Args:
            payment_id: Payment ID
            user_id: Optional user ID for ownership validation

        Returns:
            Payment dict

        Raises:
            NotFoundError: If payment not found
        """
        payment = self.db.query(Payment).filter(Payment.payment_id == payment_id).first()
        if not payment:
            logger.warning(f"Payment not found: {payment_id}")
            raise NotFoundError(f"Payment {payment_id} not found")

        # Check ownership if user_id provided
        if user_id:
            order = self.db.query(Order).filter(Order.order_id == payment.order_id).first()
            if order and order.user_id != user_id:
                logger.warning(f"Unauthorized payment access: user {user_id} trying to access payment {payment_id}")
                raise ValidationError("Unauthorized access to payment")

        return {
            "payment_id": str(payment.payment_id),
            "order_id": str(payment.order_id),
            "amount": float(payment.amount),
            "status": payment.status,
            "processor_transaction_id": payment.processor_transaction_id,
            "created_at": payment.created_at.isoformat(),
        }

    def get_payment_by_order(self, order_id: UUID) -> dict:
        """Get latest payment for order.

        Args:
            order_id: Order ID

        Returns:
            Payment dict or None if no payment found

        Raises:
            NotFoundError: If order not found
        """
        order = self.db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            logger.warning(f"Order not found: {order_id}")
            raise NotFoundError(f"Order {order_id} not found")

        payment = (
            self.db.query(Payment)
            .filter(Payment.order_id == order_id)
            .order_by(Payment.created_at.desc())
            .first()
        )

        if not payment:
            return None

        return {
            "payment_id": str(payment.payment_id),
            "order_id": str(payment.order_id),
            "amount": float(payment.amount),
            "status": payment.status,
            "processor_transaction_id": payment.processor_transaction_id,
            "created_at": payment.created_at.isoformat(),
        }
