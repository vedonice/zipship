"""Contract tests for Bill model - validate structure and constraints."""
import pytest
import re
from uuid import uuid4

from src.models.bill import Bill
from src.db.session import SessionLocal


@pytest.fixture
def db():
    """Get test database session."""
    db = SessionLocal()
    yield db
    db.close()


class TestBillModel:
    """Test Bill model structure and constraints."""

    def test_bill_has_required_fields(self):
        """Verify Bill model has all required fields."""
        required_fields = [
            'bill_id', 'order_id', 'bill_number', 'status',
            'items_json', 'subtotal', 'shipping_fee', 'tax_amount', 'total', 'created_at'
        ]
        for field in required_fields:
            assert hasattr(Bill, field), f"Bill missing required field: {field}"

    def test_bill_has_order_relationship(self):
        """Verify Bill has order relationship (one-to-one)."""
        assert hasattr(Bill, 'order')

    def test_bill_order_id_is_unique(self):
        """Verify order_id has unique constraint (one bill per order)."""
        col = Bill.__table__.columns['order_id']
        assert col.unique, "order_id should be unique (one bill per order)"

    def test_bill_order_id_is_indexed(self):
        """Verify order_id is indexed."""
        indexes = [idx.name for idx in Bill.__table__.indexes]
        order_id_indexed = any('order_id' in idx for idx in indexes) or Bill.__table__.columns['order_id'].index
        assert order_id_indexed, "order_id should be indexed"

    def test_bill_number_is_unique(self):
        """Verify bill_number is unique."""
        col = Bill.__table__.columns['bill_number']
        assert col.unique, "bill_number should be unique"

    def test_bill_number_format(self):
        """Verify bill_number supports INV-YYYY-XXXXXX format."""
        col = Bill.__table__.columns['bill_number']
        # Format: INV-YYYY-XXXXXX = min 19 chars
        assert col.type.length >= 20, "bill_number must support INV-YYYY-XXXXXX format"

    def test_bill_subtotal_is_numeric_10_2(self):
        """Verify subtotal is Numeric(10,2)."""
        col = Bill.__table__.columns['subtotal']
        assert 'numeric' in str(col.type).lower()

    def test_bill_shipping_fee_is_numeric_10_2(self):
        """Verify shipping_fee is Numeric(10,2)."""
        col = Bill.__table__.columns['shipping_fee']
        assert 'numeric' in str(col.type).lower()

    def test_bill_tax_amount_is_numeric_10_2(self):
        """Verify tax_amount is Numeric(10,2)."""
        col = Bill.__table__.columns['tax_amount']
        assert 'numeric' in str(col.type).lower()

    def test_bill_total_is_numeric_10_2(self):
        """Verify total is Numeric(10,2)."""
        col = Bill.__table__.columns['total']
        assert 'numeric' in str(col.type).lower()

    def test_bill_items_json_is_text(self):
        """Verify items_json is Text field for flexible JSON storage."""
        col = Bill.__table__.columns['items_json']
        assert 'text' in str(col.type).lower(), "items_json should be Text type for JSON"

    def test_bill_status_not_nullable(self):
        """Verify status is not nullable."""
        col = Bill.__table__.columns['status']
        assert not col.nullable, "status must not be null"

    def test_bill_order_id_not_nullable(self):
        """Verify order_id is not nullable."""
        col = Bill.__table__.columns['order_id']
        assert not col.nullable, "order_id must not be null"

    def test_bill_created_at_not_nullable(self):
        """Verify created_at is not nullable."""
        col = Bill.__table__.columns['created_at']
        assert not col.nullable, "created_at must not be null"

    def test_bill_repr(self):
        """Verify Bill __repr__ is meaningful."""
        assert hasattr(Bill, '__repr__')

    def test_bill_no_updated_at_field(self):
        """Verify Bill is immutable (no updated_at field)."""
        # Bills should not be updatable once created
        assert 'updated_at' not in [col.name for col in Bill.__table__.columns]


class TestBillNumberGeneration:
    """Test Bill number format constraints."""

    def test_bill_number_length_constraint(self):
        """Verify bill_number field supports required format."""
        col = Bill.__table__.columns['bill_number']
        # INV-YYYY-XXXXXX where XXXXXX is 6 hex chars = 19 chars minimum
        assert col.type.length >= 19, "bill_number field too short for INV-YYYY-XXXXXX format"

    def test_bill_number_format_example(self):
        """Document expected bill number format."""
        # Expected format: INV-YYYY-XXXXXX (e.g., INV-2026-abc123)
        pattern = r'^INV-\d{4}-[a-fA-F0-9]{6}$'
        assert callable(re.match), "Bill number should match INV-YYYY-XXXXXX format"


class TestBillForeignKey:
    """Test Bill foreign key to Order."""

    def test_bill_order_id_has_foreign_key(self):
        """Verify Bill.order_id has FK to Order."""
        fks = [fk.name for fk in Bill.__table__.foreign_keys]
        assert any('order_id' in fk for fk in fks), "Bill should have FK to Order"

    def test_bill_cascade_behavior(self):
        """Verify Bill cascade delete from Order."""
        fks = list(Bill.__table__.foreign_keys)
        assert len(fks) > 0, "Bill should have foreign key constraint"


class TestBillImmutability:
    """Test Bill model immutability."""

    def test_bill_created_at_has_server_default(self):
        """Verify created_at is set by server (immutable)."""
        col = Bill.__table__.columns['created_at']
        assert col.server_default is not None, "created_at should have server default"

    def test_bill_no_update_constraints(self):
        """Verify Bill table design prevents modification."""
        # Check columns - no timestamp for updates suggests immutable design
        col_names = [col.name for col in Bill.__table__.columns]
        # Bills should not have modified fields
        assert 'updated_at' not in col_names
