# REST API Contract

**Feature**: Shopping Cart & Checkout with Payment  
**Version**: 1.0.0  
**Date**: 2026-09-16

## Overview

This contract defines the REST API endpoints for shopping cart management, checkout, and order fulfillment. All endpoints require authentication via JWT bearer token. All requests and responses use `application/json` content type.

**Base URL**: `/api/v1`  
**Authentication**: Bearer token in `Authorization` header

## Common Response Format

All responses follow a consistent envelope:

```json
{
  "success": true|false,
  "data": {} or null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {} or null
  } or null,
  "timestamp": "2026-09-16T10:30:00Z"
}
```

**HTTP Status Codes**:
- `200 OK`: Successful GET/POST/PUT
- `201 Created`: Resource created
- `204 No Content`: Successful DELETE
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Missing/invalid auth token
- `404 Not Found`: Resource not found
- `409 Conflict`: State conflict (e.g., empty cart at checkout)
- `422 Unprocessable Entity`: Semantic validation error
- `500 Internal Server Error`: Server error

---

## Cart Endpoints

### POST /carts

**Description**: Create a new shopping cart for authenticated user.

**Request**:
```json
{
  "initial_items": [
    {
      "product_id": "uuid",
      "quantity": 1
    }
  ] or []
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "cart_id": "uuid",
    "user_id": "uuid",
    "status": "active",
    "items": [],
    "created_at": "2026-09-16T10:00:00Z",
    "expires_at": "2026-09-17T10:00:00Z"
  }
}
```

**Validation**:
- `product_id` must exist in catalog
- `quantity` must be 1-999

---

### GET /carts/{cart_id}

**Description**: Retrieve cart contents and summary.

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "cart_id": "uuid",
    "user_id": "uuid",
    "status": "active",
    "items": [
      {
        "cart_item_id": "uuid",
        "product_id": "uuid",
        "product_name": "Widget",
        "quantity": 2,
        "unit_price": "29.99",
        "subtotal": "59.98",
        "added_at": "2026-09-16T10:05:00Z"
      }
    ],
    "summary": {
      "item_count": 2,
      "items_subtotal": "59.98",
      "tax": "0.00",
      "shipping": "0.00",
      "total": "59.98"
    },
    "created_at": "2026-09-16T10:00:00Z",
    "expires_at": "2026-09-17T10:00:00Z"
  }
}
```

**Errors**:
- `404 Not Found`: Cart does not exist or expired
- `401 Unauthorized`: Cart belongs to different user

---

### POST /carts/{cart_id}/items

**Description**: Add item to cart or increase quantity if already present.

**Request**:
```json
{
  "product_id": "uuid",
  "quantity": 1
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "cart_item_id": "uuid",
    "product_id": "uuid",
    "product_name": "Widget",
    "quantity": 3,
    "unit_price": "29.99",
    "subtotal": "89.97",
    "added_at": "2026-09-16T10:05:00Z"
  }
}
```

**Errors**:
- `404 Not Found`: Cart not found
- `422 Unprocessable Entity`: Product not in catalog; quantity invalid
- `409 Conflict`: Cart expired or converted to order

---

### PUT /carts/{cart_id}/items/{cart_item_id}

**Description**: Update quantity or remove item from cart.

**Request**:
```json
{
  "quantity": 5
}
```

**Response** (200 OK): Updated CartItem, or empty success if deleted

**Special Case - Quantity 0 or negative**: Treated as delete (see DELETE below)

**Errors**:
- `404 Not Found`: Cart or item not found
- `422 Unprocessable Entity`: Invalid quantity (not 1-999)

---

### DELETE /carts/{cart_id}/items/{cart_item_id}

**Description**: Remove item from cart.

**Response** (204 No Content): Item removed

**Errors**:
- `404 Not Found`: Cart or item not found

---

### GET /carts (Current User's Carts)

**Description**: List active carts for authenticated user (max 5 most recent).

**Query Parameters**:
- `status` (optional): Filter by "active" | "abandoned" | "converted"

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "cart_id": "uuid",
      "status": "active",
      "item_count": 2,
      "total": "59.98",
      "created_at": "2026-09-16T10:00:00Z",
      "expires_at": "2026-09-17T10:00:00Z"
    }
  ]
}
```

---

## Checkout Endpoints

### POST /checkout

**Description**: Initiate checkout with cart items and shipping information.

**Request**:
```json
{
  "cart_id": "uuid",
  "shipping_address": {
    "street": "123 Main St",
    "city": "Springfield",
    "state": "IL",
    "postal_code": "62701",
    "country": "US"
  }
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "checkout_session_id": "uuid",
    "order_summary": {
      "items_subtotal": "59.98",
      "shipping_fee": "5.00",
      "tax_amount": "5.02",
      "total_amount": "70.00"
    }
  }
}
```

**Validation**:
- Cart must exist and contain items
- Shipping address must have all required fields
- Cart must not be expired (created_at + 24h > now)

**Errors**:
- `404 Not Found`: Cart not found
- `409 Conflict`: Cart is empty
- `422 Unprocessable Entity`: Invalid address; missing fields

---

### POST /checkout/{checkout_session_id}/payment

**Description**: Submit payment information to complete purchase.

**Request**:
```json
{
  "payment_method": "credit_card",
  "payment_token": "stripe_token_...",
  "email": "user@example.com"
}
```

**Response** (200 OK - Success):
```json
{
  "success": true,
  "data": {
    "order_id": "uuid",
    "payment_id": "uuid",
    "status": "confirmed",
    "total_amount": "70.00",
    "confirmed_at": "2026-09-16T10:15:00Z",
    "message": "Payment successful. Order confirmed. Bill will be sent to your email."
  }
}
```

**Response** (200 OK - Failure):
```json
{
  "success": false,
  "error": {
    "code": "PAYMENT_FAILED",
    "message": "Payment declined. Insufficient funds.",
    "details": {
      "processor_code": "insufficient_funds",
      "retry_allowed": true
    }
  }
}
```

**Payment Methods Accepted**:
- `credit_card`: Visa, Mastercard, Amex (via Stripe token)
- `debit_card`: Stripe token
- `paypal`: PayPal token

**Validation**:
- Payment token must be valid from Stripe/PayPal
- Amount must match order total (re-verified server-side)
- Idempotency key prevents duplicate charges on retry

**Errors**:
- `404 Not Found`: Checkout session not found or expired
- `400 Bad Request`: Invalid payment token
- `422 Unprocessable Entity`: Amount mismatch; fraud detection triggered
- `503 Service Unavailable`: Payment processor unreachable (client can retry)

---

## Order & Bill Endpoints

### GET /orders/{order_id}

**Description**: Retrieve order details.

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "order_id": "uuid",
    "user_id": "uuid",
    "status": "confirmed",
    "items": [
      {
        "product_id": "uuid",
        "product_name": "Widget",
        "quantity": 2,
        "unit_price": "29.99",
        "subtotal": "59.98"
      }
    ],
    "shipping_address": {
      "street": "123 Main St",
      "city": "Springfield",
      "state": "IL",
      "postal_code": "62701",
      "country": "US"
    },
    "summary": {
      "items_subtotal": "59.98",
      "shipping_fee": "5.00",
      "tax_amount": "5.02",
      "total_amount": "70.00"
    },
    "payment": {
      "payment_id": "uuid",
      "status": "succeeded",
      "confirmed_at": "2026-09-16T10:15:00Z"
    },
    "bill": {
      "bill_id": "uuid",
      "bill_number": "INV-2026-001234",
      "status": "generated",
      "download_url": "/orders/{order_id}/bill/download"
    },
    "created_at": "2026-09-16T10:15:00Z"
  }
}
```

**Errors**:
- `404 Not Found`: Order not found
- `401 Unauthorized`: Order belongs to different user

---

### GET /orders

**Description**: List user's orders (paginated).

**Query Parameters**:
- `page` (default: 1): Page number
- `limit` (default: 10, max: 100): Items per page
- `status` (optional): Filter by "pending" | "confirmed" | "failed"

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "orders": [
      {
        "order_id": "uuid",
        "status": "confirmed",
        "total_amount": "70.00",
        "created_at": "2026-09-16T10:15:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 42,
      "pages": 5
    }
  }
}
```

---

### GET /orders/{order_id}/bill

**Description**: Retrieve bill metadata and download URL.

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "bill_id": "uuid",
    "bill_number": "INV-2026-001234",
    "status": "generated",
    "bill_date": "2026-09-16",
    "items": [
      {
        "product_name": "Widget",
        "quantity": 2,
        "unit_price": "29.99",
        "subtotal": "59.98"
      }
    ],
    "subtotal": "59.98",
    "shipping_fee": "5.00",
    "tax_amount": "5.02",
    "total_amount": "70.00",
    "download_url": "/orders/{order_id}/bill/download?format=pdf",
    "generated_at": "2026-09-16T10:15:30Z"
  }
}
```

**Errors**:
- `404 Not Found`: Order or bill not found
- `409 Conflict`: Bill not yet generated (status: pending)

---

### GET /orders/{order_id}/bill/download

**Description**: Download bill as PDF.

**Query Parameters**:
- `format` (default: "pdf"): "pdf" | "html"

**Response** (200 OK): Binary PDF file with `Content-Disposition: attachment; filename="INV-2026-001234.pdf"`

**Errors**:
- `404 Not Found`: Bill not found
- `409 Conflict`: Bill not yet generated

---

## Error Codes Reference

| Code | HTTP | Description |
|------|------|-------------|
| `UNAUTHORIZED` | 401 | Missing or invalid auth token |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 400/422 | Input validation failed |
| `CART_EMPTY` | 409 | Cannot checkout with empty cart |
| `CART_EXPIRED` | 409 | Cart expired (>24h old) |
| `PAYMENT_FAILED` | 200 | Payment declined by processor |
| `PAYMENT_PROCESSOR_ERROR` | 503 | Stripe/PayPal unavailable |
| `BILL_GENERATION_PENDING` | 409 | Bill not yet generated (retry in 10s) |
| `CONFLICT` | 409 | State conflict (e.g., cart already converted) |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Rate Limiting

- Cart operations: 100 requests/minute per user
- Checkout: 10 requests/minute per user (prevent brute force)
- Payment submission: 3 requests/minute per checkout session (prevent duplicate charges)
- Bill download: No limit

Responses include headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp when limit resets

---

## Security Considerations

1. **Authentication**: All endpoints require valid JWT token
2. **Authorization**: Users can only access their own carts/orders/bills
3. **Sensitive Data**: Payment tokens never logged; only processor transaction IDs stored
4. **HTTPS Only**: All production requests must use HTTPS
5. **CORS**: Configured per deployment environment
6. **Idempotency**: Payment endpoint uses `Idempotency-Key` header to prevent duplicate charges on network retry

---

## Testing Contract

Automated contract tests validate:
- All endpoints return correct HTTP status codes
- Response structure matches this schema
- Error responses include required fields (code, message)
- State transitions work as documented (e.g., cart → order)
- Payment processor integration behavior (via mocked webhooks)

See [../quickstart.md](../quickstart.md) for testing scenarios.
