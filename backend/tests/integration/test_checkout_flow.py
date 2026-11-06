"""Integration tests for checkout flow."""
import pytest
from decimal import Decimal
from uuid import uuid4
from fastapi.testclient import FastAPI

from src.db.session import SessionLocal
from src.models.cart import Cart, CartStatus
from src.models.cart_item import CartItem
from src.models.order import Order
from src.services.checkout_service import CheckoutService
from src.utils.errors import ValidationError, NotFoundError


@pytest.fixture
def db():
    """Get test database session."""
    db = SessionLocal()
    yield db
    db.close()


class TestCheckoutFlow:
    """Test complete checkout flow."""

    def test_checkout_creates_order_from_cart(self, db):
        """Verify checkout converts cart to order."""
        user_id = uuid4()

        # Create cart with items
        cart = Cart(user_id=user_id)
        cart.status = CartStatus.ACTIVE
        item = CartItem(
            cart_id=None,  # Will be set by relationship
            product_id=uuid4(),
            product_name="Test Product",
            quantity=2,
            unit_price=Decimal('50.00')
        )
        cart.items.append(item)
        db.add(cart)
        db.commit()

        # Perform checkout
        checkout_service = CheckoutService(db)
        shipping_address = {
            "street": "123 Main St",
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

        # Verify order was created
        assert order_data['order_id']
        assert order_data['user_id'] == str(user_id)
        assert order_data['status'] == 'pending'
        assert len(order_data['items']) == 1

    def test_checkout_validates_address(self, db):
        """Verify address validation."""
        user_id = uuid4()
        cart_id = uuid4()

        checkout_service = CheckoutService(db)

        # Missing required field
        invalid_address = {
            "street": "123 Main St",
            "city": "Chicago",
            # missing state
        }

        with pytest.raises(ValidationError):
            checkout_service.validate_address(invalid_address)

    def test_checkout_calculates_tax_for_il(self, db):
        """Verify IL tax calculation (8%)."""
        user_id = uuid4()

        cart = Cart(user_id=user_id)
        item = CartItem(
            cart_id=None,
            product_id=uuid4(),
            product_name="Test Product",
            quantity=1,
            unit_price=Decimal('100.00')
        )
        cart.items.append(item)
        db.add(cart)
        db.commit()

        checkout_service = CheckoutService(db)
        tax = checkout_service.calculate_tax(Decimal('100.00'), 'IL')

        # IL tax is 8%
        assert tax == Decimal('8.00')

    def test_checkout_calculates_tax_for_ca(self, db):
        """Verify CA tax calculation (8.625%)."""
        checkout_service = CheckoutService(SessionLocal())
        tax = checkout_service.calculate_tax(Decimal('100.00'), 'CA')

        # CA tax is 8.625%
        assert tax == Decimal('8.63')  # Rounded

    def test_checkout_default_tax_for_other_states(self, db):
        """Verify default tax (0%) for other states."""
        checkout_service = CheckoutService(SessionLocal())
        tax = checkout_service.calculate_tax(Decimal('100.00'), 'NY')

        assert tax == Decimal('0.00')

    def test_checkout_calculates_flat_shipping(self, db):
        """Verify flat $5 shipping rate."""
        user_id = uuid4()

        cart = Cart(user_id=user_id)
        item = CartItem(
            cart_id=None,
            product_id=uuid4(),
            product_name="Test Product",
            quantity=1,
            unit_price=Decimal('100.00')
        )
        cart.items.append(item)
        db.add(cart)
        db.commit()

        checkout_service = CheckoutService(db)
        address = {"street": "Test", "city": "Test", "state": "IL", "postal_code": "12345", "country": "USA"}
        shipping = checkout_service.calculate_shipping(address, cart.items)

        assert shipping == Decimal('5.00')

    def test_checkout_rejects_empty_cart(self, db):
        """Verify empty cart cannot be checked out."""
        user_id = uuid4()

        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()

        checkout_service = CheckoutService(db)
        address = {"street": "Test", "city": "Test", "state": "IL", "postal_code": "12345", "country": "USA"}

        with pytest.raises(ValidationError):
            checkout_service.initiate_checkout(cart.cart_id, user_id, address)

    def test_checkout_validates_cart_ownership(self, db):
        """Verify user can only checkout their own cart."""
        user_id_1 = uuid4()
        user_id_2 = uuid4()

        cart = Cart(user_id=user_id_1)
        item = CartItem(
            cart_id=None,
            product_id=uuid4(),
            product_name="Test Product",
            quantity=1,
            unit_price=Decimal('50.00')
        )
        cart.items.append(item)
        db.add(cart)
        db.commit()

        checkout_service = CheckoutService(db)
        address = {"street": "Test", "city": "Test", "state": "IL", "postal_code": "12345", "country": "USA"}

        # Try to checkout with different user
        with pytest.raises(ValidationError):
            checkout_service.initiate_checkout(cart.cart_id, user_id_2, address)

    def test_checkout_includes_all_costs_in_total(self, db):
        """Verify total = subtotal + shipping + tax."""
        user_id = uuid4()

        cart = Cart(user_id=user_id)
        item = CartItem(
            cart_id=None,
            product_id=uuid4(),
            product_name="Product",
            quantity=1,
            unit_price=Decimal('100.00')
        )
        cart.items.append(item)
        db.add(cart)
        db.commit()

        checkout_service = CheckoutService(db)
        address = {"street": "Test", "city": "Test", "state": "IL", "postal_code": "12345", "country": "USA"}

        order_data = checkout_service.initiate_checkout(cart.cart_id, user_id, address)

        # IL: subtotal=100, tax=8, shipping=5, total=113
        subtotal = Decimal(order_data['items_subtotal'])
        tax = Decimal(order_data['tax_amount'])
        shipping = Decimal(order_data['shipping_fee'])
        total = Decimal(order_data['total_amount'])

        assert total == subtotal + tax + shipping

    def test_checkout_persists_order_items(self, db):
        """Verify order items are persisted as snapshots."""
        user_id = uuid4()

        cart = Cart(user_id=user_id)
        item = CartItem(
            cart_id=None,
            product_id=uuid4(),
            product_name="Test Product",
            quantity=3,
            unit_price=Decimal('25.00')
        )
        cart.items.append(item)
        db.add(cart)
        db.commit()

        checkout_service = CheckoutService(db)
        address = {"street": "Test", "city": "Test", "state": "IL", "postal_code": "12345", "country": "USA"}

        order_data = checkout_service.initiate_checkout(cart.cart_id, user_id, address)

        # Verify items are persisted
        assert len(order_data['items']) == 1
        assert order_data['items'][0]['quantity'] == 3
        assert order_data['items'][0]['unit_price'] == '25.00'

    def test_checkout_cart_not_found(self, db):
        """Verify error when cart doesn't exist."""
        user_id = uuid4()
        cart_id = uuid4()

        checkout_service = CheckoutService(db)
        address = {"street": "Test", "city": "Test", "state": "IL", "postal_code": "12345", "country": "USA"}

        with pytest.raises(NotFoundError):
            checkout_service.initiate_checkout(cart_id, user_id, address)
