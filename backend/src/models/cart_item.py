from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from decimal import Decimal

from src.db.base import Base


class CartItem(Base):
    """Individual item in shopping cart"""
    __tablename__ = "cart_items"

    cart_item_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_id = Column(UUID(as_uuid=True), ForeignKey("carts.cart_id"), nullable=False)
    product_id = Column(String(100), nullable=False)
    product_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)  # Constraint: 1-999
    unit_price = Column(Numeric(10, 2), nullable=False)  # Constraint: >= 0
    subtotal = Column(Numeric(10, 2), nullable=False)  # Computed: quantity * unit_price
    added_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    cart = relationship("Cart", back_populates="items")

    def __init__(
        self,
        cart_id: str,
        product_id: str,
        product_name: str,
        quantity: int,
        unit_price: Decimal,
    ):
        self.cart_id = cart_id
        self.product_id = product_id
        self.product_name = product_name
        self.quantity = quantity
        self.unit_price = unit_price
        self.subtotal = Decimal(quantity) * unit_price
        self.added_at = datetime.utcnow()

    def update_quantity(self, new_quantity: int) -> None:
        """Update quantity and recalculate subtotal"""
        if not (1 <= new_quantity <= 999):
            raise ValueError("Quantity must be between 1 and 999")
        self.quantity = new_quantity
        self.subtotal = Decimal(new_quantity) * self.unit_price

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "cart_item_id": str(self.cart_item_id),
            "product_id": str(self.product_id),
            "product_name": self.product_name,
            "quantity": self.quantity,
            "unit_price": f"{self.unit_price:.2f}",
            "subtotal": f"{self.subtotal:.2f}",
            "added_at": self.added_at.isoformat(),
        }
