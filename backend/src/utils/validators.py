"""Data validators for application"""

from decimal import Decimal
from typing import Dict, List, Optional


def validate_quantity(quantity: int) -> bool:
    """Validate quantity is in valid range (1-999)"""
    return 1 <= quantity <= 999


def validate_price(price: Decimal) -> bool:
    """Validate price is non-negative with correct decimal places"""
    if price < 0:
        return False
    # Check decimal places (max 2)
    if price.as_tuple().exponent < -2:
        return False
    return True


def validate_shipping_address(address: Dict[str, str]) -> tuple[bool, Optional[List[str]]]:
    """Validate shipping address has all required fields

    Returns:
        (is_valid, errors) - tuple of validity and list of error messages
    """
    required_fields = ["street", "city", "state", "postal_code", "country"]
    errors = []

    for field in required_fields:
        if field not in address or not address[field]:
            errors.append(f"Missing required field: {field}")

    if errors:
        return False, errors

    # Validate field lengths
    if len(address.get("street", "")) > 255:
        errors.append("Street address too long (max 255 characters)")
    if len(address.get("city", "")) > 100:
        errors.append("City name too long (max 100 characters)")
    if len(address.get("state", "")) > 100:
        errors.append("State name too long (max 100 characters)")
    if len(address.get("postal_code", "")) > 20:
        errors.append("Postal code too long (max 20 characters)")
    if len(address.get("country", "")) > 100:
        errors.append("Country name too long (max 100 characters)")

    return len(errors) == 0, errors if errors else None


def validate_email(email: str) -> bool:
    """Basic email validation"""
    if not email or "@" not in email or len(email) > 255:
        return False
    return True
