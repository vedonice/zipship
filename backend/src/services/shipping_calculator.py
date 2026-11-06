"""Shipping cost calculation service."""
from decimal import Decimal


class ShippingCalculator:
    """Calculate shipping costs for orders.

    Shipping Model:
    - Flat rate: $5.00 for all orders
    """

    FLAT_RATE = Decimal("5.00")

    @classmethod
    def calculate_shipping(cls, **kwargs) -> Decimal:
        """Calculate shipping cost for an order.

        Args:
            **kwargs: Flexible arguments (address, items count, etc.)
                      Currently unused - flat rate applies to all orders

        Returns:
            Shipping cost as Decimal
        """
        return cls.FLAT_RATE

    @classmethod
    def get_shipping_rate(cls) -> Decimal:
        """Get the current shipping rate.

        Returns:
            Flat shipping rate
        """
        return cls.FLAT_RATE
