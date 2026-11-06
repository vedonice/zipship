"""Request/response logging middleware"""

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses"""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Log request and response"""
        start_time = time.time()

        # Get request details
        method = request.method
        path = request.url.path
        query = request.url.query

        try:
            # Process request
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Log request
            logger.info(
                f"HTTP {method} {path} - "
                f"Status: {response.status_code} - "
                f"Duration: {process_time:.3f}s",
                extra={
                    "method": method,
                    "path": path,
                    "query": query,
                    "status_code": response.status_code,
                    "process_time_ms": int(process_time * 1000),
                },
            )

            # Add processing time header
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            logger.error(
                f"HTTP {method} {path} - Error: {str(e)}",
                extra={
                    "method": method,
                    "path": path,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise
