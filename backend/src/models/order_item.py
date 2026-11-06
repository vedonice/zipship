"""OrderItem model - immutable snapshot of cart items at order time."""
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Numeric, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy import String

from src.db.base import Base


class OrderItem(Base):
    """OrderItem model - immutable snapshot of cart items at order time."""

    __tablename__ = "order_items"

    order_item_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Product snapshot
    product_id: Mapped[str] = mapped_column(String(100), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Timestamp
    added_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    # Relationship
    order: Mapped["Order"] = relationship("Order", back_populates="items")

    def __repr__(self) -> str:
        return f"<OrderItem {self.order_item_id} product={self.product_name} qty={self.quantity}>"


# Needed for circular import
from src.models.order import Order  # noqa: E402, F401
