from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel

from src.db.session import get_db_session
from src.middleware.auth import extract_user_id
from src.services.cart_service import CartService
from src.utils.errors import ValidationError

router = APIRouter(prefix="/carts", tags=["carts"])


# Request/Response schemas
class AddItemRequest(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    unit_price: Optional[Decimal] = None


class UpdateItemRequest(BaseModel):
    quantity: int


class CartResponse(BaseModel):
    cart_id: str
    user_id: str
    status: str
    items: List[dict]
    summary: dict
    created_at: str
    expires_at: str


class CartItemResponse(BaseModel):
    cart_item_id: str
    product_id: str
    product_name: str
    quantity: int
    unit_price: str
    subtotal: str
    added_at: str


# Routes
@router.post("", response_model=CartResponse, status_code=201)
async def create_cart(
    request: Request,
    db: Session = Depends(get_db_session),
):
    """Create new shopping cart"""
    user_id = await extract_user_id(request)
    service = CartService(db)
    cart = service.create_cart(user_id)
    return service.to_dict(cart)


@router.get("/{cart_id}", response_model=CartResponse)
async def get_cart(
    cart_id: str,
    request: Request,
    db: Session = Depends(get_db_session),
):
    """Get cart contents"""
    user_id = await extract_user_id(request)
    service = CartService(db)
    cart = service.get_cart(cart_id, user_id)
    return service.to_dict(cart)


@router.get("", response_model=List[dict])
async def list_user_carts(
    request: Request,
    db: Session = Depends(get_db_session),
):
    """List user's active carts"""
    user_id = await extract_user_id(request)
    service = CartService(db)
    carts = service.get_user_carts(user_id)
    return [service.to_dict(cart) for cart in carts]


@router.post("/{cart_id}/items", response_model=CartItemResponse, status_code=201)
async def add_item(
    cart_id: str,
    body: AddItemRequest,
    request: Request,
    db: Session = Depends(get_db_session),
):
    """Add item to cart"""
    user_id = await extract_user_id(request)
    service = CartService(db)
    item = service.add_item(
        cart_id, user_id, body.product_id, body.product_name, body.quantity, body.unit_price
    )
    return item.to_dict()


@router.put("/{cart_id}/items/{cart_item_id}", response_model=CartItemResponse)
async def update_item(
    cart_id: str,
    cart_item_id: str,
    body: UpdateItemRequest,
    request: Request,
    db: Session = Depends(get_db_session),
):
    """Update item quantity"""
    user_id = await extract_user_id(request)
    service = CartService(db)
    item = service.update_item_quantity(cart_id, user_id, cart_item_id, body.quantity)
    return item.to_dict()


@router.delete("/{cart_id}/items/{cart_item_id}", status_code=204)
async def remove_item(
    cart_id: str,
    cart_item_id: str,
    request: Request,
    db: Session = Depends(get_db_session),
):
    """Remove item from cart"""
    user_id = await extract_user_id(request)
    service = CartService(db)
    service.remove_item(cart_id, user_id, cart_item_id)
    return None
