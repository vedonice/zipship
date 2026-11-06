"""Response formatting utilities"""

from datetime import datetime
from typing import Any, Optional, Dict


def format_success_response(data: Any = None) -> Dict[str, Any]:
    """Format successful response with envelope"""
    return {
        "success": True,
        "data": data,
        "error": None,
        "timestamp": datetime.utcnow().isoformat(),
    }


def format_error_response(
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Format error response with envelope"""
    return {
        "success": False,
        "data": None,
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


# Aliases for compatibility
def create_response(data: Any = None, status_code: int = 200) -> Dict[str, Any]:
    """Compatibility alias for format_success_response"""
    return format_success_response(data)
