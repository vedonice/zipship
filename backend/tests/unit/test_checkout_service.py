"""Unit tests for CheckoutService."""
import pytest
from decimal import Decimal
from unittest.mock import Mock, patch
from uuid import uuid4

from src.services.checkout_service import CheckoutService
from src.services.tax_calculator import TaxCalculator
from src.services.shipping_calculator import ShippingCalculator
from src.utils.errors import ValidationError


class TestCheckoutService:
    """Unit tests for CheckoutService."""

    def test_checkout_service_initializes_with_db(self):
        """Verify CheckoutService initializes with database session."""
        db = Mock()
        service = CheckoutService(db)
        assert service.db is db
        assert isinstance(service.tax_calc, TaxCalculator)
        assert isinstance(service.shipping_calc, ShippingCalculator)

    def test_validate_address_with_all_fields(self):
        """Verify address validation passes with all fields."""
        service = CheckoutService(Mock())
        address = {
            "street": "123 Main St",
            "city": "Chicago",
            "state": "IL",
            "postal_code": "60601",
            "country": "USA"
        }
        # Should not raise
        service.validate_address(address)

    def test_validate_address_missing_street(self):
        """Verify address validation fails without street."""
        service = CheckoutService(Mock())
        address = {
            "city": "Chicago",
            "state": "IL",
            "postal_code": "60601",
            "country": "USA"
        }
        with pytest.raises(ValidationError):
            service.validate_address(address)

    def test_validate_address_missing_city(self):
        """Verify address validation fails without city."""
        service = CheckoutService(Mock())
        address = {
            "street": "123 Main St",
            "state": "IL",
            "postal_code": "60601",
            "country": "USA"
        }
        with pytest.raises(ValidationError):
            service.validate_address(address)

    def test_validate_address_missing_state(self):
        """Verify address validation fails without state."""
        service = CheckoutService(Mock())
        address = {
            "street": "123 Main St",
            "city": "Chicago",
            "postal_code": "60601",
            "country": "USA"
        }
        with pytest.raises(ValidationError):
            service.validate_address(address)

    def test_validate_address_missing_postal_code(self):
        """Verify address validation fails without postal code."""
        service = CheckoutService(Mock())
        address = {
            "street": "123 Main St",
            "city": "Chicago",
            "state": "IL",
            "country": "USA"
        }
        with pytest.raises(ValidationError):
            service.validate_address(address)

    def test_validate_address_missing_country(self):
        """Verify address validation fails without country."""
        service = CheckoutService(Mock())
        address = {
            "street": "123 Main St",
            "city": "Chicago",
            "state": "IL",
            "postal_code": "60601"
        }
        with pytest.raises(ValidationError):
            service.validate_address(address)

    def test_calculate_tax_uses_tax_calculator(self):
        """Verify calculate_tax delegates to TaxCalculator."""
        db = Mock()
        service = CheckoutService(db)

        tax = service.calculate_tax(Decimal('100.00'), 'IL')
        assert tax == Decimal('8.00')

    def test_calculate_shipping_uses_shipping_calculator(self):
        """Verify calculate_shipping delegates to ShippingCalculator."""
        db = Mock()
        service = CheckoutService(db)
        address = {"street": "Test", "city": "Test", "state": "IL", "postal_code": "12345", "country": "USA"}

        shipping = service.calculate_shipping(address, [])
        assert shipping == Decimal('5.00')
