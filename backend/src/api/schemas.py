"""API request/response schemas"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class CommonResponse(BaseModel):
    """Standard response envelope for all API responses"""
    success: bool
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Standard error response"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ValidationError(BaseModel):
    """Validation error details"""
    field: str
    message: str
