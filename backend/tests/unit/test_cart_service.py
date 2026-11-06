import pytest
from uuid import uuid4
from decimal import Decimal
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine

from src.db.base import Base
from src.models.cart import Cart
from src.models.cart_item import CartItem
from src.services.cart_service import CartService
from src.utils.errors import NotFoundError, ConflictError, ValidationError


@pytest.fixture
def test_db():
    """Create test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()


def test_create_cart(test_db: Session):
    """Test cart creation"""
    service = CartService(test_db)
    user_id = str(uuid4())

    cart = service.create_cart(user_id)

    assert cart.user_id == user_id
    assert cart.status == "active"
    assert not cart.items


def test_add_item_to_cart(test_db: Session):
    """Test adding item to cart"""
    service = CartService(test_db)
    user_id = str(uuid4())
    cart = service.create_cart(user_id)
    product_id = str(uuid4())

    item = service.add_item(
        str(cart.cart_id),
        user_id,
        product_id,
        quantity=2,
        unit_price=Decimal("29.99"),
    )

    assert item.quantity == 2
    assert item.unit_price == Decimal("29.99")
    assert item.subtotal == Decimal("59.98")


def test_add_item_invalid_quantity(test_db: Session):
    """Test adding item with invalid quantity"""
    service = CartService(test_db)
    user_id = str(uuid4())
    cart = service.create_cart(user_id)
    product_id = str(uuid4())

    with pytest.raises(ValidationError):
        service.add_item(
            str(cart.cart_id),
            user_id,
            product_id,
            quantity=1000,  # Invalid: > 999
            unit_price=Decimal("29.99"),
        )


def test_update_item_quantity(test_db: Session):
    """Test updating item quantity"""
    service = CartService(test_db)
    user_id = str(uuid4())
    cart = service.create_cart(user_id)
    product_id = str(uuid4())

    item = service.add_item(
        str(cart.cart_id),
        user_id,
        product_id,
        quantity=2,
        unit_price=Decimal("29.99"),
    )

    updated = service.update_item_quantity(
        str(cart.cart_id),
        user_id,
        str(item.cart_item_id),
        new_quantity=5,
    )

    assert updated.quantity == 5
    assert updated.subtotal == Decimal("149.95")


def test_remove_item(test_db: Session):
    """Test removing item from cart"""
    service = CartService(test_db)
    user_id = str(uuid4())
    cart = service.create_cart(user_id)
    product_id = str(uuid4())

    item = service.add_item(
        str(cart.cart_id),
        user_id,
        product_id,
        quantity=1,
        unit_price=Decimal("29.99"),
    )

    service.remove_item(str(cart.cart_id), user_id, str(item.cart_item_id))

    # Verify item is removed
    cart = service.get_cart(str(cart.cart_id), user_id)
    assert len(cart.items) == 0


def test_cart_ownership_validation(test_db: Session):
    """Test that carts are validated for ownership"""
    service = CartService(test_db)
    user1_id = str(uuid4())
    user2_id = str(uuid4())

    cart = service.create_cart(user1_id)

    with pytest.raises(NotFoundError):
        service.get_cart(str(cart.cart_id), user2_id)


def test_cart_expiration(test_db: Session):
    """Test cart expiration check"""
    service = CartService(test_db)
    user_id = str(uuid4())

    cart = service.create_cart(user_id)
    # Expire the cart
    from datetime import datetime, timedelta

    cart.expires_at = datetime.utcnow() - timedelta(hours=1)
    test_db.commit()

    with pytest.raises(ConflictError):
        service.get_cart(str(cart.cart_id), user_id)
