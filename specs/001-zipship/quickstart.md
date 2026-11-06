# Phase 1: Quickstart Validation Guide

**Date**: 2026-09-16  
**Purpose**: Runnable validation scenarios proving the shopping cart & checkout feature works end-to-end

## Setup Prerequisites

**Database**:
```bash
# Ensure PostgreSQL is running
# Run migrations to create schema
python -m alembic upgrade head
```

**Environment**:
```bash
# Set test environment variables
export DATABASE_URL=postgresql://test:test@localhost/cart_checkout_test
export STRIPE_API_KEY=sk_test_...
export STRIPE_WEBHOOK_SECRET=whsec_test_...
export JWT_SECRET=test_secret_key
```

**Test Data**:
```bash
# Seed product catalog
python -m scripts.seed_products

# Output: Product IDs
# - PROD_001: "Premium Widget" ($29.99)
# - PROD_002: "Standard Gadget" ($14.99)
# - PROD_003: "Deluxe Kit" ($99.99)
```

**Test User**:
```bash
# Create test user and get JWT token
python -m scripts.create_test_user --email test@example.com --password testpass123

# Output:
# User ID: USER_001
# JWT Token: eyJhbGc...
```

Store the JWT token for use in all API calls:
```bash
export AUTH_TOKEN="eyJhbGc..."
```

---

## Test Scenario 1: Add Items to Cart

**Goal**: Validate basic cart operations (add, view, modify, remove items)

**Setup**: Start with fresh cart

### 1.1 Create Empty Cart

```bash
curl -X POST http://localhost:8000/api/v1/carts \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"initial_items": []}'
```

**Expected Response** (201):
```json
{
  "success": true,
  "data": {
    "cart_id": "uuid-1",
    "user_id": "USER_001",
    "status": "active",
    "items": [],
    "created_at": "2026-09-16T10:00:00Z",
    "expires_at": "2026-09-17T10:00:00Z"
  }
}
```

**Validation**:
- ✓ HTTP 201 Created
- ✓ Cart has unique cart_id
- ✓ Status is "active"
- ✓ expires_at is 24 hours from now
- ✓ Items list is empty

---

### 1.2 Add First Item to Cart

```bash
export CART_ID="uuid-1"

curl -X POST http://localhost:8000/api/v1/carts/$CART_ID/items \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "PROD_001",
    "quantity": 2
  }'
```

**Expected Response** (200):
```json
{
  "success": true,
  "data": {
    "cart_item_id": "uuid-item-1",
    "product_id": "PROD_001",
    "product_name": "Premium Widget",
    "quantity": 2,
    "unit_price": "29.99",
    "subtotal": "59.98",
    "added_at": "2026-09-16T10:05:00Z"
  }
}
```

**Validation**:
- ✓ HTTP 200 OK
- ✓ Quantity is 2 as requested
- ✓ Subtotal calculated correctly: 2 × $29.99 = $59.98
- ✓ unit_price matches product catalog

---

### 1.3 View Cart Contents

```bash
curl -X GET http://localhost:8000/api/v1/carts/$CART_ID \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

**Expected Response** (200):
```json
{
  "success": true,
  "data": {
    "cart_id": "uuid-1",
    "user_id": "USER_001",
    "status": "active",
    "items": [
      {
        "cart_item_id": "uuid-item-1",
        "product_id": "PROD_001",
        "product_name": "Premium Widget",
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

**Validation**:
- ✓ Item count reflects quantity (2, not 1)
- ✓ Subtotal is correct ($59.98)
- ✓ Total equals items_subtotal (no shipping/tax yet)

---

### 1.4 Add Second Item

```bash
curl -X POST http://localhost:8000/api/v1/carts/$CART_ID/items \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "PROD_002",
    "quantity": 1
  }'
```

**Expected Response** (200): New CartItem for PROD_002

**Validation**:
- ✓ Cart now has 2 distinct items (3 total units)
- ✓ Both items present in GET /carts/{id}

---

### 1.5 Modify Item Quantity

```bash
export CART_ITEM_ID="uuid-item-1"

curl -X PUT http://localhost:8000/api/v1/carts/$CART_ID/items/$CART_ITEM_ID \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity": 5}'
```

**Expected Response** (200):
```json
{
  "success": true,
  "data": {
    "cart_item_id": "uuid-item-1",
    "quantity": 5,
    "subtotal": "149.95",
    "product_name": "Premium Widget"
  }
}
```

**Validation**:
- ✓ Quantity updated to 5
- ✓ Subtotal recalculated: 5 × $29.99 = $149.95
- ✓ GET /carts/{id} reflects new total

---

### 1.6 Remove Item

```bash
curl -X DELETE http://localhost:8000/api/v1/carts/$CART_ID/items/$CART_ITEM_ID \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

**Expected Response** (204): No Content

**Validation**:
- ✓ Item removed from cart
- ✓ GET /carts/{id} no longer includes this item
- ✓ Cart still contains second item (PROD_002)

---

## Test Scenario 2: Checkout Flow

**Goal**: Validate checkout process with shipping and tax calculation

**Setup**: Cart with items ready for checkout

### 2.1 Initiate Checkout

```bash
curl -X POST http://localhost:8000/api/v1/checkout \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cart_id": "uuid-1",
    "shipping_address": {
      "street": "123 Main St",
      "city": "Springfield",
      "state": "IL",
      "postal_code": "62701",
      "country": "US"
    }
  }'
```

**Expected Response** (200):
```json
{
  "success": true,
  "data": {
    "checkout_session_id": "checkout-session-uuid",
    "order_summary": {
      "items_subtotal": "14.99",
      "shipping_fee": "5.00",
      "tax_amount": "1.60",
      "total_amount": "21.59"
    }
  }
}
```

**Validation**:
- ✓ HTTP 200 OK
- ✓ Checkout session created
- ✓ Shipping fee calculated (based on address and items)
- ✓ Tax calculated for Illinois (8% on $14.99 = ~$1.20, adjusted for total)
- ✓ Total = $14.99 + $5.00 + $1.60 = $21.59

---

### 2.2 Validate Cart Cannot Checkout Twice

```bash
curl -X POST http://localhost:8000/api/v1/checkout \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cart_id": "uuid-1",
    "shipping_address": { ... }
  }'
```

**Expected Response** (409):
```json
{
  "success": false,
  "error": {
    "code": "CONFLICT",
    "message": "Cart is already checked out"
  }
}
```

---

## Test Scenario 3: Payment Processing

**Goal**: Validate payment submission and order creation

**Setup**: Checkout session from Scenario 2

### 3.1 Successful Payment

```bash
export CHECKOUT_SESSION_ID="checkout-session-uuid"

curl -X POST http://localhost:8000/api/v1/checkout/$CHECKOUT_SESSION_ID/payment \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_method": "credit_card",
    "payment_token": "tok_visa",
    "email": "test@example.com"
  }'
```

**Expected Response** (200 - Success):
```json
{
  "success": true,
  "data": {
    "order_id": "ORDER-001",
    "payment_id": "PAYMENT-001",
    "status": "confirmed",
    "total_amount": "21.59",
    "confirmed_at": "2026-09-16T10:15:00Z",
    "message": "Payment successful. Order confirmed. Bill will be sent to your email."
  }
}
```

**Validation**:
- ✓ Order created with unique order_id
- ✓ Payment status is "confirmed"
- ✓ Amount matches checkout total ($21.59)
- ✓ Timestamp is recent
- ✓ User receives confirmation message

**Log Verification** (structured logs should show):
```
timestamp=2026-09-16T10:15:00Z level=INFO service=payment_service \
  event=payment_completed order_id=ORDER-001 amount=21.59 status=confirmed
```

---

### 3.2 Payment Failure Handling

```bash
curl -X POST http://localhost:8000/api/v1/checkout/$CHECKOUT_SESSION_ID/payment \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_method": "credit_card",
    "payment_token": "tok_chargeDeclined",
    "email": "test@example.com"
  }'
```

**Expected Response** (200 - But failure):
```json
{
  "success": false,
  "error": {
    "code": "PAYMENT_FAILED",
    "message": "Your card was declined.",
    "details": {
      "processor_code": "card_declined",
      "retry_allowed": true
    }
  }
}
```

**Validation**:
- ✓ Checkout session NOT converted to order
- ✓ Cart remains in checkout state (can retry)
- ✓ Clear error message for user
- ✓ retry_allowed=true (user can resubmit)

---

### 3.3 Concurrent Payment Protection

Send two payment requests simultaneously to same checkout session:

```bash
# Terminal 1
curl -X POST http://localhost:8000/api/v1/checkout/$CHECKOUT_SESSION_ID/payment ...

# Terminal 2 (at same time)
curl -X POST http://localhost:8000/api/v1/checkout/$CHECKOUT_SESSION_ID/payment ...
```

**Expected Behavior**:
- ✓ First request succeeds with order_id and payment_id
- ✓ Second request fails: "Checkout session already completed" (409)
- ✓ Only ONE charge appears in Stripe webhook logs
- ✓ No duplicate orders created

---

## Test Scenario 4: Bill Generation

**Goal**: Validate bill is generated and downloadable after payment

**Setup**: Completed order from Scenario 3

### 4.1 View Bill Metadata

```bash
export ORDER_ID="ORDER-001"

curl -X GET http://localhost:8000/api/v1/orders/$ORDER_ID/bill \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

**Expected Response** (200):
```json
{
  "success": true,
  "data": {
    "bill_id": "BILL-001",
    "bill_number": "INV-2026-001234",
    "status": "generated",
    "bill_date": "2026-09-16",
    "items": [
      {
        "product_name": "Standard Gadget",
        "quantity": 1,
        "unit_price": "14.99",
        "subtotal": "14.99"
      }
    ],
    "subtotal": "14.99",
    "shipping_fee": "5.00",
    "tax_amount": "1.60",
    "total_amount": "21.59",
    "download_url": "/orders/ORDER-001/bill/download?format=pdf",
    "generated_at": "2026-09-16T10:15:30Z"
  }
}
```

**Validation**:
- ✓ Bill generated within 10 seconds of payment (generated_at - payment.confirmed_at < 10s)
- ✓ Bill number in correct format (INV-YYYY-XXXXXX)
- ✓ Status is "generated"
- ✓ Items match order items
- ✓ Total matches order total ($21.59)
- ✓ Download URL provided

**Log Verification**:
```
timestamp=2026-09-16T10:15:30Z level=INFO service=bill_service \
  event=bill_generated order_id=ORDER-001 bill_id=BILL-001 processing_time_ms=300
```

---

### 4.2 Download Bill as PDF

```bash
curl -X GET http://localhost:8000/api/v1/orders/$ORDER_ID/bill/download?format=pdf \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -o bill_invoice.pdf
```

**Expected Response** (200):
- ✓ HTTP 200 OK
- ✓ Content-Type: application/pdf
- ✓ Content-Disposition: attachment; filename="INV-2026-001234.pdf"
- ✓ Binary PDF file downloaded successfully
- ✓ PDF contains all order details (items, total, date, company info)

---

### 4.3 Bill Not Yet Generated (Edge Case)

Create a new order and immediately try to download bill:

```bash
# Payment just completed; bill generation is async
curl -X GET http://localhost:8000/api/v1/orders/ORDER-002/bill/download \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

**Expected Response** (409) - within first 5 seconds:
```json
{
  "success": false,
  "error": {
    "code": "BILL_GENERATION_PENDING",
    "message": "Bill is being generated. Please try again in a few seconds."
  }
}
```

**Validation**:
- ✓ Returns 409 Conflict, not 500 error
- ✓ Clear message guides user to retry
- ✓ After 10 seconds: retry succeeds with 200 OK

---

## Test Scenario 5: Edge Cases

### 5.1 Empty Cart Cannot Proceed to Checkout

```bash
# Create cart but don't add items
curl -X POST http://localhost:8000/api/v1/carts \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d '{"initial_items": []}'
# Returns cart_id: uuid-empty

curl -X POST http://localhost:8000/api/v1/checkout \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d '{"cart_id": "uuid-empty", "shipping_address": {...}}'
```

**Expected Response** (409):
```json
{
  "success": false,
  "error": {
    "code": "CART_EMPTY",
    "message": "Cannot checkout with empty cart"
  }
}
```

---

### 5.2 Expired Cart Cannot Checkout

```bash
# Create cart, wait 24+ hours (or mock time)
# Then try to checkout

curl -X POST http://localhost:8000/api/v1/checkout \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d '{"cart_id": "expired-cart-id", "shipping_address": {...}}'
```

**Expected Response** (409):
```json
{
  "success": false,
  "error": {
    "code": "CART_EXPIRED",
    "message": "Cart has expired"
  }
}
```

---

### 5.3 Invalid Product ID

```bash
curl -X POST http://localhost:8000/api/v1/carts/$CART_ID/items \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d '{
    "product_id": "NONEXISTENT",
    "quantity": 1
  }'
```

**Expected Response** (422):
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Product not found in catalog"
  }
}
```

---

### 5.4 Duplicate Payment Prevention

Send same payment request twice with identical idempotency key:

```bash
curl -X POST http://localhost:8000/api/v1/checkout/$SESSION/payment \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Idempotency-Key: duplicate-key-123" \
  -d '{...}'

# Immediately retry with same Idempotency-Key
curl -X POST http://localhost:8000/api/v1/checkout/$SESSION/payment \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Idempotency-Key: duplicate-key-123" \
  -d '{...}'
```

**Expected Response**: 
- ✓ First request: 200 OK with order_id
- ✓ Second request: 200 OK with SAME order_id (not duplicated)
- ✓ Only ONE charge in Stripe webhook logs

---

## Performance Validation

### Cart Operations (Goal: <200ms)

```bash
# Measure add item latency
time curl -X POST http://localhost:8000/api/v1/carts/$CART_ID/items \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d '{...}'
```

**Validation**: ✓ Response time < 200ms

---

### Checkout Flow (Goal: <3 minutes user time)

```bash
# Start timer
curl -X POST http://localhost:8000/api/v1/checkout -H "..."
# User enters payment: ~30 seconds
curl -X POST http://localhost:8000/api/v1/checkout/$SESSION/payment -H "..."
# End timer
```

**Validation**: ✓ Total time < 3 minutes

---

### Bill Generation (Goal: <10 seconds)

```bash
# At time T: Payment confirmed
# At time T+X: Bill ready for download

# Measure: generated_at - confirmed_at < 10 seconds
```

**Log Check**:
```bash
grep "bill_generated" /var/log/app.log | grep "processing_time_ms"
# Expected: processing_time_ms < 10000
```

---

## Concurrent Load Test

**Goal**: Support 100+ concurrent users without degradation

```bash
# Load test: 100 users adding items to carts
ab -n 1000 -c 100 http://localhost:8000/api/v1/carts/$CART_ID/items \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

**Validation**:
- ✓ Requests per second: ≥ 100 rps
- ✓ Failed requests: 0
- ✓ P95 latency: < 500ms
- ✓ P99 latency: < 1000ms
- ✓ Database connections healthy

---

## Completion Checklist

After running all scenarios, verify:

- [ ] Scenario 1: All cart operations complete successfully
- [ ] Scenario 2: Checkout calculates shipping & tax correctly
- [ ] Scenario 3: Successful and failed payments handled properly
- [ ] Scenario 4: Bill generated within 10 seconds; PDF downloadable
- [ ] Scenario 5: All edge cases handled gracefully
- [ ] Performance: All operations meet latency targets
- [ ] Load: System handles 100+ concurrent users
- [ ] Logs: Structured logging shows complete flow with no errors
- [ ] Database: No orphaned records; all foreign keys intact

**Reference**: 
- Data model details: [data-model.md](data-model.md)
- API contract: [contracts/rest-api.md](contracts/rest-api.md)
