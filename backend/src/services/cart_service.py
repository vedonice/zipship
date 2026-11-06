from uuid import UUID
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from src.models.cart import Cart
from src.models.cart_item import CartItem
from src.utils.errors import NotFoundError, ConflictError, ValidationError
from src.utils.logging import setup_logging

logger = setup_logging(__name__)


class CartService:
    """Cart business logic service"""

    def __init__(self, db: Session):
        self.db = db

    def create_cart(self, user_id: UUID) -> Cart:
        """Create new shopping cart"""
        cart = Cart(user_id=user_id)
        self.db.add(cart)
        self.db.commit()
        self.db.refresh(cart)

        logger.info(f"Cart created: cart_id={cart.cart_id}, user_id={user_id}")
        return cart

    def get_cart(self, cart_id: str, user_id: UUID) -> Cart:
        """Get cart with ownership validation"""
        cart = self.db.query(Cart).filter(Cart.cart_id == cart_id).first()

        if not cart:
            raise NotFoundError("Cart", cart_id)

        if cart.user_id != user_id:
            raise NotFoundError("Cart", cart_id)  # Don't reveal ownership

        if cart.is_expired():
            raise ConflictError("Cart has expired")

        return cart

    def get_user_carts(self, user_id: UUID, limit: int = 5) -> List[Cart]:
        """Get user's active carts"""
        carts = (
            self.db.query(Cart)
            .filter(Cart.user_id == user_id, Cart.status == "active")
            .order_by(Cart.created_at.desc())
            .limit(limit)
            .all()
        )
        return carts

    def add_item(
        self,
        cart_id: str,
        user_id: UUID,
        product_id: str,
        product_name: str,
        quantity: int,
        unit_price: Decimal = None,
    ) -> CartItem:
        """Add item to cart"""
        # Validate quantity
        if not (1 <= quantity <= 999):
            raise ValidationError(
                "Invalid quantity",
                {"quantity": "Must be between 1 and 999"}
            )

        # Get cart
        cart = self.get_cart(cart_id, user_id)

        # Check if item already in cart
        existing_item = (
            self.db.query(CartItem)
            .filter(
                CartItem.cart_id == cart_id,
                CartItem.product_id == product_id,
            )
            .first()
        )

        if existing_item:
            # Update quantity
            new_quantity = existing_item.quantity + quantity
            if new_quantity > 999:
                raise ValidationError(
                    "Quantity too high",
                    {"quantity": f"Total would be {new_quantity}, max is 999"}
                )
            existing_item.update_quantity(new_quantity)
            self.db.commit()
            self.db.refresh(existing_item)
            logger.info(
                f"Item quantity updated: cart_id={cart_id}, "
                f"product_id={product_id}, new_quantity={new_quantity}"
            )
            return existing_item

        # Create new item (use provided price or default)
        if unit_price is None:
            unit_price = Decimal("0.00")

        item = CartItem(
            cart_id=cart_id,
            product_id=product_id,
            product_name=product_name,
            quantity=quantity,
            unit_price=unit_price,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        logger.info(
            f"Item added to cart: cart_id={cart_id}, "
            f"product_id={product_id}, quantity={quantity}"
        )
        return item

    def update_item_quantity(
        self,
        cart_id: str,
        user_id: UUID,
        cart_item_id: str,
        new_quantity: int,
    ) -> CartItem:
        """Update item quantity"""
        # Validate quantity
        if new_quantity == 0:
            return self.remove_item(cart_id, user_id, cart_item_id)

        if not (1 <= new_quantity <= 999):
            raise ValidationError(
                "Invalid quantity",
                {"quantity": "Must be between 1 and 999"}
            )

        # Get cart (validates ownership)
        cart = self.get_cart(cart_id, user_id)

        # Get item
        item = (
            self.db.query(CartItem)
            .filter(CartItem.cart_item_id == cart_item_id)
            .first()
        )

        if not item or item.cart_id != UUID(cart_id):
            raise NotFoundError("CartItem", cart_item_id)

        item.update_quantity(new_quantity)
        self.db.commit()
        self.db.refresh(item)

        logger.info(
            f"Item quantity updated: cart_id={cart_id}, "
            f"item_id={cart_item_id}, new_quantity={new_quantity}"
        )
        return item

    def remove_item(
        self,
        cart_id: str,
        user_id: UUID,
        cart_item_id: str,
    ) -> None:
        """Remove item from cart"""
        # Get cart (validates ownership)
        cart = self.get_cart(cart_id, user_id)

        # Get item
        item = (
            self.db.query(CartItem)
            .filter(CartItem.cart_item_id == cart_item_id)
            .first()
        )

        if not item or item.cart_id != UUID(cart_id):
            raise NotFoundError("CartItem", cart_item_id)

        self.db.delete(item)
        self.db.commit()

        logger.info(
            f"Item removed from cart: cart_id={cart_id}, item_id={cart_item_id}"
        )

    def to_dict(self, cart: Cart) -> Dict[str, Any]:
        """Convert cart to dictionary"""
        return {
            "cart_id": str(cart.cart_id),
            "user_id": str(cart.user_id),
            "status": cart.status,
            "items": [item.to_dict() for item in cart.items],
            "summary": cart.get_summary(),
            "created_at": cart.created_at.isoformat(),
            "expires_at": cart.expires_at.isoformat(),
        }
