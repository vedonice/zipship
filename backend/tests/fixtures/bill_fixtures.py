"""Test fixtures for Bill model using factory_boy."""
import factory
import json
from decimal import Decimal
from datetime import datetime
from uuid import uuid4

from src.models.bill import Bill
from src.services.bill_service import BillNumberGenerator
from src.db.session import SessionLocal


class BillFactory(factory.Factory):
    """Factory for creating Bill instances."""

    class Meta:
        model = Bill

    bill_id = factory.LazyFunction(uuid4)
    order_id = factory.LazyFunction(uuid4)
    bill_number = factory.LazyFunction(
        lambda: BillNumberGenerator.generate(uuid4())
    )
    status = "generated"
    items_json = factory.LazyFunction(
        lambda: json.dumps([
            {
                "product_id": str(uuid4()),
                "product_name": "Test Product",
                "quantity": 1,
                "unit_price": "50.00",
                "subtotal": "50.00"
            }
        ])
    )
    subtotal = Decimal('100.00')
    shipping_fee = Decimal('5.00')
    tax_amount = Decimal('8.00')
    total = Decimal('113.00')


# Helper functions
def create_generated_bill(order_id=None, db=None):
    """Create a generated bill for testing.

    Args:
        order_id: Order ID for the bill
        db: Database session

    Returns:
        Generated Bill instance
    """
    if db is None:
        db = SessionLocal()

    if order_id is None:
        order_id = uuid4()

    bill = BillFactory(
        order_id=order_id,
        status="generated"
    )

    db.add(bill)
    db.commit()
    db.refresh(bill)
    return bill


def create_bill_with_items(order_id=None, num_items=1, db=None):
    """Create a bill with specific items for testing.

    Args:
        order_id: Order ID for the bill
        num_items: Number of items to include
        db: Database session

    Returns:
        Bill instance with specified items
    """
    if db is None:
        db = SessionLocal()

    if order_id is None:
        order_id = uuid4()

    items = []
    total_subtotal = Decimal('0.00')

    for i in range(num_items):
        unit_price = Decimal(f"{50 + i * 10}.00")
        quantity = i + 1
        subtotal = unit_price * quantity

        items.append({
            "product_id": str(uuid4()),
            "product_name": f"Product {i+1}",
            "quantity": quantity,
            "unit_price": str(unit_price),
            "subtotal": str(subtotal)
        })
        total_subtotal += subtotal

    bill = BillFactory(
        order_id=order_id,
        items_json=json.dumps(items),
        subtotal=total_subtotal,
        total=total_subtotal + Decimal('5.00') + (total_subtotal * Decimal('0.08'))
    )

    db.add(bill)
    db.commit()
    db.refresh(bill)
    return bill


def create_bill_with_custom_totals(
    order_id=None,
    subtotal=None,
    shipping_fee=None,
    tax_amount=None,
    db=None
):
    """Create a bill with custom financial totals for testing.

    Args:
        order_id: Order ID for the bill
        subtotal: Items subtotal (default 100.00)
        shipping_fee: Shipping fee (default 5.00)
        tax_amount: Tax amount (default 8.00)
        db: Database session

    Returns:
        Bill instance with custom totals
    """
    if db is None:
        db = SessionLocal()

    if order_id is None:
        order_id = uuid4()

    if subtotal is None:
        subtotal = Decimal('100.00')

    if shipping_fee is None:
        shipping_fee = Decimal('5.00')

    if tax_amount is None:
        tax_amount = Decimal('8.00')

    total = subtotal + shipping_fee + tax_amount

    bill = BillFactory(
        order_id=order_id,
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        tax_amount=tax_amount,
        total=total
    )

    db.add(bill)
    db.commit()
    db.refresh(bill)
    return bill


def create_bill_with_bill_number(order_id=None, bill_number=None, db=None):
    """Create a bill with specific bill number for testing.

    Args:
        order_id: Order ID for the bill
        bill_number: Bill number (generated if not provided)
        db: Database session

    Returns:
        Bill instance with specific bill number
    """
    if db is None:
        db = SessionLocal()

    if order_id is None:
        order_id = uuid4()

    if bill_number is None:
        bill_number = BillNumberGenerator.generate(order_id)

    bill = BillFactory(
        order_id=order_id,
        bill_number=bill_number
    )

    db.add(bill)
    db.commit()
    db.refresh(bill)
    return bill
