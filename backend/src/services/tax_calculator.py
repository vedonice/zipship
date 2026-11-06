"""Tax calculation service based on shipping location."""
from decimal import Decimal
from typing import Optional


class TaxCalculator:
    """Calculate sales tax based on state/location.

    Tax Rates:
    - Illinois (IL): 8%
    - California (CA): 8.625%
    - Default (all other states): 0%
    """

    TAX_RATES = {
        "IL": Decimal("0.08"),
        "CA": Decimal("0.08625"),
    }

    @classmethod
    def calculate_tax(cls, subtotal: Decimal, state: str) -> Decimal:
        """Calculate tax amount for a given subtotal and state.

        Args:
            subtotal: Cart/Order subtotal amount
            state: State code (e.g., 'IL', 'CA')

        Returns:
            Calculated tax amount, rounded to 2 decimal places
        """
        rate = cls.TAX_RATES.get(state.upper(), Decimal("0"))
        tax = subtotal * rate
        return tax.quantize(Decimal("0.01"))

    @classmethod
    def get_tax_rate(cls, state: str) -> Decimal:
        """Get the tax rate for a given state.

        Args:
            state: State code

        Returns:
            Tax rate as decimal (e.g., Decimal("0.08") for 8%)
        """
        return cls.TAX_RATES.get(state.upper(), Decimal("0"))

    @classmethod
    def get_supported_states(cls) -> list[str]:
        """Get list of states with special tax rates.

        Returns:
            List of state codes with custom rates
        """
        return list(cls.TAX_RATES.keys())
