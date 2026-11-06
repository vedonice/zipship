"""Bill service for generating and managing invoices."""
import json
import logging
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy.orm import Session, joinedload

from src.models.order import Order
from src.models.bill import Bill
from src.utils.errors import ValidationError, NotFoundError

logger = logging.getLogger(__name__)


class BillNumberGenerator:
    """Generate bill numbers in format INV-YYYY-XXXXXX."""

    @staticmethod
    def generate(order_id: UUID) -> str:
        """Generate bill number.

        Args:
            order_id: Order ID for uniqueness

        Returns:
            Bill number in format INV-YYYY-XXXXXX
        """
        year = datetime.utcnow().year
        # Use last 6 characters of UUID hex as random suffix
        suffix = str(order_id).replace('-', '')[-6:].upper()
        return f"INV-{year}-{suffix}"


class BillService:
    """Service for generating and managing bills/invoices."""

    def __init__(self, db: Session):
        """Initialize bill service.

        Args:
            db: Database session
        """
        self.db = db

    def generate_bill(self, order_id: UUID, user_id: UUID = None) -> dict:
        """Generate bill for order.

        Args:
            order_id: Order ID to generate bill for
            user_id: Optional user ID for ownership validation

        Returns:
            Bill dict with:
            - bill_id: Bill ID
            - bill_number: Bill number (INV-YYYY-XXXXXX)
            - order_id: Order ID
            - status: Bill status
            - items: Items from order
            - subtotal: Items subtotal
            - shipping_fee: Shipping fee
            - tax_amount: Tax amount
            - total: Grand total
            - created_at: Creation timestamp

        Raises:
            ValidationError: If bill cannot be generated
            NotFoundError: If order not found
        """
        # Get order with items eagerly loaded
        order = self.db.query(Order).options(joinedload(Order.items)).filter(Order.order_id == order_id).first()
        if not order:
            logger.warning(f"Order not found: {order_id}")
            raise NotFoundError(f"Order {order_id} not found")

        # Check ownership if user_id provided
        if user_id and order.user_id != user_id:
            logger.warning(f"Unauthorized bill access: user {user_id} trying to generate bill for order {order_id}")
            raise ValidationError("Unauthorized access to order")

        # Check if bill already exists
        existing_bill = self.db.query(Bill).filter(Bill.order_id == order_id).first()
        if existing_bill:
            logger.info(f"Bill already exists for order {order_id}: {existing_bill.bill_number}")
            return {
                "bill_id": str(existing_bill.bill_id),
                "bill_number": existing_bill.bill_number,
                "order_id": str(existing_bill.order_id),
                "status": existing_bill.status,
                "items": json.loads(existing_bill.items_json),
                "subtotal": float(existing_bill.subtotal),
                "shipping_fee": float(existing_bill.shipping_fee),
                "tax_amount": float(existing_bill.tax_amount),
                "total": float(existing_bill.total),
                "created_at": existing_bill.created_at.isoformat(),
            }

        # Create bill number
        bill_number = BillNumberGenerator.generate(order_id)

        # Serialize order items
        items_json = json.dumps([
            {
                "product_id": str(item.product_id),
                "product_name": item.product_name,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "subtotal": float(item.subtotal),
            }
            for item in order.items
        ])

        # Create bill
        bill = Bill(
            bill_id=None,  # Will be auto-generated
            order_id=order_id,
            bill_number=bill_number,
            status="generated",
            items_json=items_json,
            subtotal=order.items_subtotal,
            shipping_fee=order.shipping_fee,
            tax_amount=order.tax_amount,
            total=order.total_amount,
        )

        # Persist
        self.db.add(bill)
        self.db.commit()
        self.db.refresh(bill)

        logger.info(f"Bill generated: {bill.bill_number} for order {order_id}")

        return {
            "bill_id": str(bill.bill_id),
            "bill_number": bill.bill_number,
            "order_id": str(bill.order_id),
            "status": bill.status,
            "items": json.loads(bill.items_json),
            "subtotal": float(bill.subtotal),
            "shipping_fee": float(bill.shipping_fee),
            "tax_amount": float(bill.tax_amount),
            "total": float(bill.total),
            "created_at": bill.created_at.isoformat(),
        }

    def get_bill(self, bill_id: UUID, user_id: UUID = None) -> dict:
        """Get bill details.

        Args:
            bill_id: Bill ID
            user_id: Optional user ID for ownership validation

        Returns:
            Bill dict

        Raises:
            NotFoundError: If bill not found
        """
        bill = self.db.query(Bill).filter(Bill.bill_id == bill_id).first()
        if not bill:
            logger.warning(f"Bill not found: {bill_id}")
            raise NotFoundError(f"Bill {bill_id} not found")

        # Check ownership if user_id provided
        if user_id:
            order = self.db.query(Order).filter(Order.order_id == bill.order_id).first()
            if order and order.user_id != user_id:
                logger.warning(f"Unauthorized bill access: user {user_id} trying to access bill {bill_id}")
                raise ValidationError("Unauthorized access to bill")

        return {
            "bill_id": str(bill.bill_id),
            "bill_number": bill.bill_number,
            "order_id": str(bill.order_id),
            "status": bill.status,
            "items": json.loads(bill.items_json),
            "subtotal": float(bill.subtotal),
            "shipping_fee": float(bill.shipping_fee),
            "tax_amount": float(bill.tax_amount),
            "total": float(bill.total),
            "created_at": bill.created_at.isoformat(),
        }

    def get_bill_by_order(self, order_id: UUID, user_id: UUID = None) -> dict:
        """Get bill for order.

        Args:
            order_id: Order ID
            user_id: Optional user ID for ownership validation

        Returns:
            Bill dict or None if no bill found

        Raises:
            NotFoundError: If order not found
        """
        order = self.db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            logger.warning(f"Order not found: {order_id}")
            raise NotFoundError(f"Order {order_id} not found")

        # Check ownership if user_id provided
        if user_id and order.user_id != user_id:
            logger.warning(f"Unauthorized order access: user {user_id} trying to access order {order_id}")
            raise ValidationError("Unauthorized access to order")

        bill = self.db.query(Bill).filter(Bill.order_id == order_id).first()
        if not bill:
            return None

        return {
            "bill_id": str(bill.bill_id),
            "bill_number": bill.bill_number,
            "order_id": str(bill.order_id),
            "status": bill.status,
            "items": json.loads(bill.items_json),
            "subtotal": float(bill.subtotal),
            "shipping_fee": float(bill.shipping_fee),
            "tax_amount": float(bill.tax_amount),
            "total": float(bill.total),
            "created_at": bill.created_at.isoformat(),
        }
