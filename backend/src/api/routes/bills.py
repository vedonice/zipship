"""Bill/invoice endpoints."""
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.db.session import get_db_session
from src.middleware.auth import extract_user_id
from src.services.bill_service import BillService
from src.services.pdf_service import PDFService
from src.utils.response import create_response
from src.utils.errors import ValidationError, NotFoundError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bills", tags=["bills"])


@router.get("/orders/{order_id}")
async def get_bill_for_order(
    order_id: str,
    http_request: Request,
    db: Session = Depends(get_db_session),
):
    """Get bill for order.

    Args:
        order_id: Order ID to get bill for
        http_request: HTTP request for auth
        db: Database session

    Returns:
        Bill details or 404 if not found
    """
    try:
        user_id = await extract_user_id(http_request)
        logger.info(f"Retrieving bill for order {order_id} by user {user_id}")

        bill_service = BillService(db)
        bill_data = bill_service.get_bill_by_order(UUID(order_id), user_id)

        if not bill_data:
            logger.warning(f"Bill not found for order {order_id}")
            raise HTTPException(status_code=404, detail="Bill not found for order")

        return create_response(data=bill_data, status_code=200)

    except (ValidationError, NotFoundError) as e:
        logger.error(f"Bill retrieval validation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Bill retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/orders/{order_id}/download")
async def download_bill_for_order(
    order_id: str,
    http_request: Request,
    db: Session = Depends(get_db_session),
):
    """Download bill PDF for order.

    Args:
        order_id: Order ID to download bill for
        http_request: HTTP request for auth
        db: Database session

    Returns:
        PDF file
    """
    try:
        user_id = await extract_user_id(http_request)
        logger.info(f"Downloading bill PDF for order {order_id} by user {user_id}")

        bill_service = BillService(db)
        bill_data = bill_service.get_bill_by_order(UUID(order_id), user_id)

        if not bill_data:
            logger.warning(f"Bill not found for order {order_id}")
            raise HTTPException(status_code=404, detail="Bill not found for order")

        pdf_bytes = PDFService.generate_invoice_pdf(bill_data)

        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=\"{bill_data['bill_number']}.pdf\""}
        )

    except (ValidationError, NotFoundError) as e:
        logger.error(f"Bill download validation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Bill download failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{bill_id}")
async def get_bill(
    bill_id: str,
    http_request: Request,
    db: Session = Depends(get_db_session),
):
    """Get bill by ID.

    Args:
        bill_id: Bill ID
        http_request: HTTP request for auth
        db: Database session

    Returns:
        Bill details
    """
    try:
        user_id = await extract_user_id(http_request)
        logger.info(f"Retrieving bill {bill_id} by user {user_id}")

        bill_service = BillService(db)
        bill_data = bill_service.get_bill(UUID(bill_id), user_id)

        return create_response(data=bill_data, status_code=200)

    except (ValidationError, NotFoundError) as e:
        logger.error(f"Bill retrieval validation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Bill retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
