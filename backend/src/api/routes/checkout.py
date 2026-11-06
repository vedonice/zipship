"""Checkout and payment endpoints."""
import logging
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db.session import get_db_session
from src.middleware.auth import extract_user_id
from src.services.checkout_service import CheckoutService
from src.services.payment_service import PaymentService
from src.services.bill_service import BillService
from src.utils.response import create_response
from src.utils.errors import ValidationError, NotFoundError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/checkout", tags=["checkout"])


class CheckoutRequest(BaseModel):
    """Checkout request schema."""
    cart_id: str
    shipping_address: dict


class PaymentRequest(BaseModel):
    """Payment request schema."""
    amount: Decimal
    idempotency_key: str
    processor_transaction_id: str = None


@router.post("")
async def initiate_checkout(
    body: CheckoutRequest,
    http_request: Request,
    db: Session = Depends(get_db_session),
):
    """Initiate checkout from cart.

    Args:
        body: CheckoutRequest with cart_id and shipping_address
        http_request: HTTP request for auth
        db: Database session

    Returns:
        Order summary with calculated shipping and tax
    """
    try:
        user_id = await extract_user_id(http_request)
        logger.info(f"Checkout initiated for user {user_id} cart {body.cart_id}")

        checkout_service = CheckoutService(db)
        order_data = checkout_service.initiate_checkout(
            cart_id=UUID(body.cart_id),
            user_id=user_id,
            shipping_address=body.shipping_address,
        )

        logger.info(f"Checkout successful: order {order_data['order_id']}")
        return create_response(data=order_data, status_code=201)

    except (ValidationError, NotFoundError) as e:
        logger.error(f"Checkout validation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Checkout failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{order_id}/payment")
async def process_payment(
    order_id: str,
    body: PaymentRequest,
    http_request: Request,
    db: Session = Depends(get_db_session),
):
    """Process payment for order.

    Args:
        order_id: Order ID to pay
        body: PaymentRequest with amount, idempotency_key, processor_transaction_id
        http_request: HTTP request for auth
        db: Database session

    Returns:
        Payment confirmation with status
    """
    try:
        user_id = await extract_user_id(http_request)
        logger.info(f"Payment processing for user {user_id} order {order_id}")

        payment_service = PaymentService(db)
        payment_data = payment_service.process_payment(
            order_id=UUID(order_id),
            user_id=user_id,
            amount=body.amount,
            idempotency_key=body.idempotency_key,
            processor_transaction_id=body.processor_transaction_id,
        )

        # Generate bill after successful payment
        try:
            bill_service = BillService(db)
            bill_service.generate_bill(UUID(order_id), user_id)
            logger.info(f"Bill generated for order {order_id}")
        except Exception as bill_error:
            logger.error(f"Bill generation failed for order {order_id}: {str(bill_error)}", exc_info=True)
            # Don't fail payment if bill generation fails - bill can be generated later
            pass

        logger.info(f"Payment successful: payment {payment_data['payment_id']}")
        return create_response(data=payment_data, status_code=200)

    except (ValidationError, NotFoundError) as e:
        logger.error(f"Payment validation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Payment failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
