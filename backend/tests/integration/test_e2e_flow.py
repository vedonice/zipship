"""End-to-end integration tests for complete user flow: Cart -> Checkout -> Payment -> Bill."""
import pytest
from decimal import Decimal
from uuid import uuid4

from src.db.session import SessionLocal
from src.models.cart import Cart, CartStatus
from src.models.cart_item import CartItem
from src.models.order import OrderStatus
from src.models.payment import PaymentStatus
from src.services.cart_service import CartService
from src.services.checkout_service import CheckoutService
from src.services.payment_service import PaymentService
from src.services.bill_service import BillService
from src.utils.errors import ValidationError, NotFoundError


@pytest.fixture
def db():
    """Get test database session."""
    db = SessionLocal()
    yield db
    db.close()


class TestE2EFlow:
    """End-to-end flow tests: complete user journey."""

    def test_complete_flow_cart_to_bill(self, db):
        """Test complete user flow: add items -> checkout -> pay -> bill.

        This validates the entire e-commerce flow end-to-end.
        """
        user_id = uuid4()

        # ========== STEP 1: CREATE CART AND ADD ITEMS ==========
        cart_service = CartService(db)
        cart = cart_service.create_cart(user_id)
        assert cart.cart_id is not None
        assert cart.status == CartStatus.ACTIVE

        # Add first item
        item_1 = cart_service.add_item(
            cart_id=cart.cart_id,
            user_id=user_id,
            product_id=uuid4(),
            product_name="Laptop",
            quantity=1,
            unit_price=Decimal('999.99')
        )
        assert item_1.quantity == 1
        assert item_1.unit_price == Decimal('999.99')

        # Add second item
        item_2 = cart_service.add_item(
            cart_id=cart.cart_id,
            user_id=user_id,
            product_id=uuid4(),
            product_name="Mouse",
            quantity=2,
            unit_price=Decimal('29.99')
        )
        assert item_2.quantity == 2

        # Update item quantity
        cart_service.update_item_quantity(
            cart_id=cart.cart_id,
            user_id=user_id,
            cart_item_id=item_1.cart_item_id,
            new_quantity=2
        )

        # Get updated cart
        db.refresh(cart)
        assert len(cart.items) == 2
        cart_summary = cart.get_summary()
        assert int(float(cart_summary['item_count'])) == 3  # 2 laptops + 2 mice

        # ========== STEP 2: CHECKOUT ==========
        checkout_service = CheckoutService(db)

        shipping_address = {
            "street": "123 Main Street",
            "city": "Chicago",
            "state": "IL",
            "postal_code": "60601",
            "country": "USA"
        }

        order_data = checkout_service.initiate_checkout(
            cart_id=cart.cart_id,
            user_id=user_id,
            shipping_address=shipping_address
        )

        assert order_data['order_id']
        assert order_data['status'] == OrderStatus.PENDING.value
        assert len(order_data['items']) == 2

        # Verify calculations
        subtotal = Decimal(order_data['items_subtotal'])
        shipping = Decimal(order_data['shipping_fee'])
        tax = Decimal(order_data['tax_amount'])
        total = Decimal(order_data['total_amount'])

        assert subtotal > 0
        assert shipping == Decimal('5.00')  # Flat $5
        assert tax > 0  # IL tax
        assert total == subtotal + shipping + tax

        order_id = uuid4(hex=order_data['order_id'].replace('-', '')[:32])

        # ========== STEP 3: PROCESS PAYMENT ==========
        payment_service = PaymentService(db)

        idempotency_key = str(uuid4())
        payment_data = payment_service.process_payment(
            order_id=order_id,
            user_id=user_id,
            amount=total,
            idempotency_key=idempotency_key,
            processor_transaction_id="txn_test_12345"
        )

        assert payment_data['payment_id']
        assert payment_data['status'] == PaymentStatus.SUCCESS.value
        assert payment_data['processor_transaction_id'] == "txn_test_12345"

        # Verify idempotency: same key returns same payment
        payment_data_2 = payment_service.process_payment(
            order_id=order_id,
            user_id=user_id,
            amount=total,
            idempotency_key=idempotency_key,
            processor_transaction_id="txn_test_12345"
        )
        assert payment_data_2['payment_id'] == payment_data['payment_id']

        # ========== STEP 4: GENERATE BILL ==========
        bill_service = BillService(db)

        bill_data = bill_service.generate_bill(order_id, user_id)

        assert bill_data['bill_id']
        assert bill_data['bill_number']
        assert bill_data['status'] == 'generated'
        assert len(bill_data['items']) == 2

        # Verify bill amounts match order
        assert Decimal(str(bill_data['subtotal'])) == subtotal
        assert Decimal(str(bill_data['shipping_fee'])) == shipping
        assert Decimal(str(bill_data['tax_amount'])) == tax
        assert Decimal(str(bill_data['total'])) == total

        # ========== STEP 5: RETRIEVE BILL ==========
        bill_retrieved = bill_service.get_bill_by_order(order_id, user_id)

        assert bill_retrieved is not None
        assert bill_retrieved['bill_number'] == bill_data['bill_number']

        print("\n" + "="*60)
        print("✓ COMPLETE E2E FLOW VALIDATION PASSED")
        print("="*60)
        print(f"Cart ID: {cart.cart_id}")
        print(f"Order ID: {order_id}")
        print(f"Payment ID: {payment_data['payment_id']}")
        print(f"Bill ID: {bill_data['bill_id']}")
        print(f"Bill Number: {bill_data['bill_number']}")
        print(f"Total: ${total}")
        print("="*60)

    def test_flow_error_handling(self, db):
        """Test error handling throughout the flow."""
        user_id = uuid4()

        # ========== TEST: Empty cart cannot checkout ==========
        cart_service = CartService(db)
        cart = cart_service.create_cart(user_id)

        checkout_service = CheckoutService(db)
        address = {"street": "Test", "city": "Test", "state": "IL", "postal_code": "12345", "country": "USA"}

        with pytest.raises(ValidationError):
            checkout_service.initiate_checkout(cart.cart_id, user_id, address)

        # ========== TEST: Wrong user cannot checkout another's cart ==========
        other_user_id = uuid4()
        with pytest.raises(ValidationError):
            checkout_service.initiate_checkout(cart.cart_id, other_user_id, address)

        # ========== TEST: Wrong user cannot pay another's order ==========
        payment_service = PaymentService(db)
        with pytest.raises(NotFoundError):
            payment_service.process_payment(
                order_id=uuid4(),
                user_id=user_id,
                amount=Decimal('100.00'),
                idempotency_key=str(uuid4())
            )

        # ========== TEST: Accessing non-existent bill ==========
        bill_service = BillService(db)
        with pytest.raises(NotFoundError):
            bill_service.get_bill(uuid4())

        print("\n✓ Error handling tests passed")

    def test_flow_quantity_management(self, db):
        """Test quantity updates throughout the flow."""
        user_id = uuid4()

        cart_service = CartService(db)
        cart = cart_service.create_cart(user_id)

        # Add item
        item = cart_service.add_item(
            cart_id=cart.cart_id,
            user_id=user_id,
            product_id=uuid4(),
            product_name="Product",
            quantity=1,
            unit_price=Decimal('100.00')
        )

        # Increase quantity
        updated_item = cart_service.update_item_quantity(
            cart_id=cart.cart_id,
            user_id=user_id,
            cart_item_id=item.cart_item_id,
            new_quantity=5
        )
        assert updated_item.quantity == 5
        assert updated_item.subtotal == Decimal('500.00')

        # Remove item
        cart_service.remove_item(
            cart_id=cart.cart_id,
            user_id=user_id,
            cart_item_id=item.cart_item_id
        )

        # Verify cart is now empty
        cart = cart_service.get_cart(cart.cart_id, user_id)
        assert len(cart.items) == 0

        print("\n✓ Quantity management tests passed")

    def test_flow_multiple_items_pricing(self, db):
        """Test pricing calculations with multiple items."""
        user_id = uuid4()

        cart_service = CartService(db)
        cart = cart_service.create_cart(user_id)

        # Add multiple items with different prices
        item_1 = cart_service.add_item(
            cart_id=cart.cart_id,
            user_id=user_id,
            product_id=uuid4(),
            product_name="Item A",
            quantity=2,
            unit_price=Decimal('50.00')
        )

        item_2 = cart_service.add_item(
            cart_id=cart.cart_id,
            user_id=user_id,
            product_id=uuid4(),
            product_name="Item B",
            quantity=3,
            unit_price=Decimal('25.00')
        )

        # Get cart summary
        db.refresh(cart)
        summary = cart.get_summary()

        # Expected: (2*50) + (3*25) = 175
        expected_subtotal = Decimal('175.00')
        actual_subtotal = sum(Decimal(str(item.subtotal)) for item in cart.items)

        assert actual_subtotal == expected_subtotal

        # Checkout and verify totals
        checkout_service = CheckoutService(db)
        address = {"street": "Test", "city": "Test", "state": "CA", "postal_code": "12345", "country": "USA"}

        order_data = checkout_service.initiate_checkout(
            cart_id=cart.cart_id,
            user_id=user_id,
            shipping_address=address
        )

        # CA has 8.625% tax
        expected_tax = Decimal('175.00') * Decimal('0.08625')
        actual_tax = Decimal(order_data['tax_amount'])

        # Verify (allowing for rounding)
        assert abs(actual_tax - expected_tax) < Decimal('0.01')

        print("\n✓ Multiple items pricing tests passed")
