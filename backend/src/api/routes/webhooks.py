"""Webhook endpoints for payment processor events."""
import logging
import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session

from src.db.session import get_db_session
from src.models.order import Order, OrderStatus
from src.models.payment import Payment, PaymentStatus
from src.services.bill_service import BillService
from src.utils.response import create_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def verify_stripe_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str
) -> bool:
    """Verify Stripe webhook signature.

    Args:
        payload: Raw webhook payload
        signature: Stripe signature from header
        secret: Webhook secret from Stripe

    Returns:
        True if signature is valid, False otherwise
    """
    try:
        # Extract timestamp and signatures from header
        if not signature or "," not in signature:
            return False

        timestamp = None
        signatures = []

        for part in signature.split(","):
            if part.startswith("t="):
                timestamp = part.split("=")[1]
            elif part.startswith("v1="):
                signatures.append(part.split("=")[1])

        if not timestamp or not signatures:
            return False

        # Create signed content
        signed_content = f"{timestamp}.{payload.decode('utf-8')}"

        # Compute expected signature
        expected_signature = hmac.new(
            secret.encode("utf-8"),
            signed_content.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        # Compare with provided signatures (constant-time comparison)
        for provided_sig in signatures:
            if hmac.compare_digest(provided_sig, expected_signature):
                return True

        return False

    except Exception as e:
        logger.error(f"Webhook signature verification failed: {str(e)}")
        return False


@router.post("/stripe")
async def handle_stripe_webhook(
    request: Request,
    db: Session = Depends(get_db_session)
):
    """Handle Stripe webhook events.

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        Webhook acknowledgment response
    """
    try:
        # Get raw body and signature
        payload = await request.body()
        signature = request.headers.get("Stripe-Signature")

        # In production, verify signature:
        # stripe_webhook_secret = settings.stripe_webhook_secret
        # if not verify_stripe_webhook_signature(payload, signature, stripe_webhook_secret):
        #     logger.warning("Invalid Stripe webhook signature")
        #     raise HTTPException(status_code=401, detail="Invalid signature")

        # Parse JSON
        import json
        event = json.loads(payload)
        event_type = event.get("type")

        logger.info(f"Received Stripe webhook: {event_type}")

        # Handle charge.succeeded event
        if event_type == "charge.succeeded":
            return await handle_charge_succeeded(event, db)

        # Handle charge.failed event
        elif event_type == "charge.failed":
            return await handle_charge_failed(event, db)

        # Handle payment_intent.succeeded event
        elif event_type == "payment_intent.succeeded":
            return await handle_payment_intent_succeeded(event, db)

        # Acknowledge receipt of unknown event type
        else:
            logger.info(f"Ignoring unhandled webhook event: {event_type}")
            return create_response({"received": True})

    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def handle_charge_succeeded(event: dict, db: Session) -> dict:
    """Handle successful charge event.

    Args:
        event: Stripe event object
        db: Database session

    Returns:
        Webhook acknowledgment
    """
    try:
        charge = event.get("data", {}).get("object", {})
        transaction_id = charge.get("id")

        logger.info(f"Processing charge.succeeded: {transaction_id}")

        # In production, would:
        # 1. Find payment by processor_transaction_id
        # 2. Update payment status to SUCCESS
        # 3. Update order status to CONFIRMED
        # 4. Generate bill

        logger.info(f"Charge succeeded event processed: {transaction_id}")
        return create_response({"received": True})

    except Exception as e:
        logger.error(f"charge.succeeded processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Event processing failed")


async def handle_charge_failed(event: dict, db: Session) -> dict:
    """Handle failed charge event.

    Args:
        event: Stripe event object
        db: Database session

    Returns:
        Webhook acknowledgment
    """
    try:
        charge = event.get("data", {}).get("object", {})
        transaction_id = charge.get("id")
        error_message = charge.get("failure_message", "Unknown error")

        logger.warning(f"Processing charge.failed: {transaction_id} - {error_message}")

        # In production, would:
        # 1. Find payment by processor_transaction_id
        # 2. Update payment status to FAILED
        # 3. Log error for user display

        logger.info(f"Charge failed event processed: {transaction_id}")
        return create_response({"received": True})

    except Exception as e:
        logger.error(f"charge.failed processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Event processing failed")


async def handle_payment_intent_succeeded(event: dict, db: Session) -> dict:
    """Handle successful payment intent event.

    Args:
        event: Stripe event object
        db: Database session

    Returns:
        Webhook acknowledgment
    """
    try:
        payment_intent = event.get("data", {}).get("object", {})
        intent_id = payment_intent.get("id")
        amount = payment_intent.get("amount")

        logger.info(f"Processing payment_intent.succeeded: {intent_id}")

        # In production, would update order and payment statuses

        logger.info(f"Payment intent succeeded event processed: {intent_id}")
        return create_response({"received": True})

    except Exception as e:
        logger.error(f"payment_intent.succeeded processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Event processing failed")
