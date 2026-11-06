from fastapi import Request, HTTPException, status
from src.utils.errors import UnauthorizedError
from uuid import uuid5, NAMESPACE_DNS
import json


async def extract_user_id(request: Request):
    """Extract user_id from Authorization header and convert to UUID"""
    from uuid import UUID
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise UnauthorizedError("Missing Authorization header")

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedError("Invalid Authorization header format")

    token = parts[1]
    # For MVP: convert token to UUID for database storage
    try:
        if not token or len(token) < 8:
            raise UnauthorizedError("Invalid token")
        # Generate deterministic UUID from token string
        user_uuid = uuid5(NAMESPACE_DNS, token)
        return user_uuid
    except Exception:
        raise UnauthorizedError("Invalid token")
