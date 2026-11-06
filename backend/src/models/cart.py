from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timedelta
from enum import Enum as PyEnum

from src.db.base import Base


class CartStatus(str, PyEnum):
    """Cart status enum"""
    ACTIVE = "active"
    ABANDONED = "abandoned"
    CONVERTED = "converted"


class Cart(Base):
    """Shopping cart model"""
    __tablename__ = "carts"

    cart_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    status = Column(String(20), default=CartStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False)

    # Relationships
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.status = CartStatus.ACTIVE
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(hours=24)

    def is_expired(self) -> bool:
        """Check if cart has expired"""
        return datetime.utcnow() > self.expires_at

    def get_summary(self):
        """Get cart summary with totals"""
        item_count = sum(item.quantity for item in self.items)
        items_subtotal = sum(float(item.subtotal) for item in self.items)
        return {
            "item_count": item_count,
            "items_subtotal": f"{items_subtotal:.2f}",
            "tax": "0.00",  # Will be calculated in checkout
            "shipping": "0.00",  # Will be calculated in checkout
            "total": f"{items_subtotal:.2f}",
        }
