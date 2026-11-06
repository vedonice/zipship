from typing import Optional, Dict, Any


class AppException(Exception):
    """Base application exception"""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(AppException):
    """Validation error (422 Unprocessable Entity)"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=422,
            details=details,
        )


class NotFoundError(AppException):
    """Resource not found (404)"""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} not found",
            status_code=404,
            details={"resource": resource, "identifier": identifier},
        )


class ConflictError(AppException):
    """State conflict (409)"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="CONFLICT",
            message=message,
            status_code=409,
            details=details,
        )


class UnauthorizedError(AppException):
    """Authentication error (401)"""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            status_code=401,
        )


class PaymentError(AppException):
    """Payment processing error"""

    def __init__(self, message: str, retry_allowed: bool = True):
        super().__init__(
            code="PAYMENT_FAILED",
            message=message,
            status_code=200,  # Return 200 with error in body
            details={"retry_allowed": retry_allowed},
        )
