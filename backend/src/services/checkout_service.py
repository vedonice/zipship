"""Checkout service orchestrating cart-to-order conversion."""
import logging
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.cart import Cart
from src.models.order import Order, OrderStatus
from src.models.order_item import OrderItem
from src.services.tax_calculator import TaxCalculator
from src.services.shipping_calculator import ShippingCalculator
from src.utils.errors import ValidationError, NotFoundError

logger = logging.getLogger(__name__)


class CheckoutService:
    """Orchestrate checkout flow from cart to order."""

    def __init__(self, db: Session):
        """Initialize checkout service.

        Args:
            db: Database session
        """
        self.db = db
        self.tax_calc = TaxCalculator()
        self.shipping_calc = ShippingCalculator()

    def initiate_checkout(
        self,
        cart_id: UUID,
        user_id: UUID,
        shipping_address: dict,
    ) -> dict:
        """Convert cart to order with shipping and tax calculation.

        Args:
            cart_id: Cart ID to convert
            user_id: User ID for ownership validation
            shipping_address: Address dict with keys:
                - street (required): Street address
                - city (required): City
                - state (required): State code
                - postal_code (required): Postal code
                - country (required): Country

        Returns:
            Order summary dict with:
            - order_id: Created order ID
            - user_id: User ID
            - items: List of order items
            - items_subtotal: Subtotal of items
            - shipping_fee: Calculated shipping
            - tax_amount: Calculated tax
            - total_amount: Grand total
            - status: Order status (pending)

        Raises:
            ValidationError: If address validation fails
            NotFoundError: If cart not found
        """
        # Validate address
        self.validate_address(shipping_address)

        # Get cart
        cart = self.db.query(Cart).filter(Cart.cart_id == cart_id).first()
        if not cart:
            logger.warning(f"Cart not found: {cart_id}")
            raise NotFoundError(f"Cart {cart_id} not found")

        # Validate ownership
        if cart.user_id != user_id:
            logger.warning(f"Unauthorized cart access: user {user_id} trying to access cart {cart_id}")
            raise ValidationError("Unauthorized access to cart")

        # Validate cart has items
        if not cart.items:
            logger.warning(f"Empty cart checkout attempted: {cart_id}")
            raise ValidationError("Cannot checkout empty cart")

        # Calculate totals
        items_subtotal = sum(item.subtotal for item in cart.items)
        shipping_fee = self.calculate_shipping(shipping_address, cart.items)
        tax_amount = self.calculate_tax(items_subtotal, shipping_address["state"])
        total_amount = items_subtotal + shipping_fee + tax_amount

        # Create order
        order = Order(
            user_id=user_id,
            cart_id=cart_id,
            shipping_street=shipping_address["street"],
            shipping_city=shipping_address["city"],
            shipping_state=shipping_address["state"],
            shipping_postal_code=shipping_address["postal_code"],
            shipping_country=shipping_address["country"],
            items_subtotal=items_subtotal,
            shipping_fee=shipping_fee,
            tax_amount=tax_amount,
            total_amount=total_amount,
            status=OrderStatus.PENDING.value,
        )

        # Copy cart items to order items
        for cart_item in cart.items:
            order_item = OrderItem(
                order_id=order.order_id,
                product_id=cart_item.product_id,
                product_name=cart_item.product_name,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                subtotal=cart_item.subtotal,
            )
            order.items.append(order_item)

        # Persist
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)

        logger.info(f"Checkout initiated: order {order.order_id} for user {user_id} from cart {cart_id}")

        return {
            "order_id": str(order.order_id),
            "user_id": str(order.user_id),
            "items": [
                {
                    "order_item_id": str(item.order_item_id),
                    "product_id": str(item.product_id),
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "unit_price": str(item.unit_price),
                    "subtotal": str(item.subtotal),
                }
                for item in order.items
            ],
            "items_subtotal": str(items_subtotal),
            "shipping_fee": str(shipping_fee),
            "tax_amount": str(tax_amount),
            "total_amount": str(total_amount),
            "status": order.status,
        }

    def validate_address(self, address: dict) -> None:
        """Validate shipping address.

        Args:
            address: Address dict

        Raises:
            ValidationError: If any required field is missing
        """
        required_fields = ["street", "city", "state", "postal_code", "country"]
        missing = [field for field in required_fields if not address.get(field)]
        if missing:
            logger.warning(f"Invalid address: missing fields {missing}")
            raise ValidationError(f"Address missing required fields: {', '.join(missing)}")

    def calculate_tax(self, subtotal: Decimal, state: str) -> Decimal:
        """Calculate tax for order.

        Args:
            subtotal: Subtotal amount
            state: State code

        Returns:
            Tax amount
        """
        tax = self.tax_calc.calculate_tax(subtotal, state)
        logger.debug(f"Tax calculated: subtotal={subtotal} state={state} tax={tax}")
        return tax

    def calculate_shipping(self, address: dict, items: list) -> Decimal:
        """Calculate shipping for order.

        Args:
            address: Shipping address
            items: Order items

        Returns:
            Shipping fee
        """
        shipping = self.shipping_calc.calculate_shipping(address=address, item_count=len(items))
        logger.debug(f"Shipping calculated: {shipping}")
        return shipping
