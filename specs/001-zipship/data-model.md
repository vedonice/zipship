# Phase 1: Data Model Design

**Date**: 2026-09-16  
**Status**: Complete  
**Schema Version**: 1.0.0

## Entity Definitions

### Cart

**Purpose**: Temporary shopping container for authenticated user's selected items during a shopping session.

**Fields**:
- `cart_id` (UUID, primary key): Unique identifier
- `user_id` (UUID, foreign key): Owner of the cart
- `status` (enum: "active" | "abandoned" | "converted"): Lifecycle state
- `created_at` (timestamp): When cart was created
- `updated_at` (timestamp): Last modification time
- `expires_at` (timestamp): When cart data should be purged (24 hours from creation)

**Relationships**:
- One-to-Many with CartItem
- Zero-or-One with Order (after checkout)

**Validation Rules**:
- `user_id` is required and must exist
- `expires_at` defaults to current_time + 24 hours
- `status` transitions: active → (abandoned | converted); no reverse transitions
- Cart cannot be empty when transitioning to checkout

**State Transitions**:
- ACTIVE: Normal state, items can be added/removed
- ABANDONED: User left without checking out (after 24 hours or explicit abandonment)
- CONVERTED: Successfully converted to order (immutable after this point)

---

### CartItem

**Purpose**: Individual product entry in a shopping cart with quantity and calculated price.

**Fields**:
- `cart_item_id` (UUID, primary key): Unique identifier
- `cart_id` (UUID, foreign key): Parent cart
- `product_id` (UUID, foreign key): Reference to product catalog
- `product_name` (string, 255 chars): Denormalized product name (for cart display if product deleted)
- `quantity` (integer): Number of units
- `unit_price` (decimal 10,2): Price per unit at time of addition
- `subtotal` (decimal 10,2, computed): quantity × unit_price
- `added_at` (timestamp): When item was added to cart

**Relationships**:
- Many-to-One with Cart
- Implicit reference to Product catalog (external)

**Validation Rules**:
- `quantity` must be ≥ 1, max 999 per item
- `unit_price` must be ≥ 0.00
- `product_id` must exist in product catalog (external validation)
- `subtotal` is computed; not user-supplied

**Computed Fields**:
- `subtotal` = quantity × unit_price (calculated at storage, updated on quantity changes)

---

### Order

**Purpose**: Completed purchase record, created after successful payment. Immutable after creation.

**Fields**:
- `order_id` (UUID, primary key): Unique order identifier
- `user_id` (UUID, foreign key): Purchaser
- `cart_id` (UUID, foreign key): Source cart (for audit trail)
- `status` (enum: "pending" | "confirmed" | "failed"): Payment status
- `shipping_address` (text): Full address provided at checkout
- `subtotal` (decimal 10,2): Sum of item prices before shipping/tax
- `shipping_fee` (decimal 10,2): Calculated based on address and items
- `tax_amount` (decimal 10,2): Calculated tax based on location
- `total_amount` (decimal 10,2): subtotal + shipping_fee + tax_amount
- `created_at` (timestamp): Order creation time
- `confirmed_at` (timestamp, nullable): When payment was confirmed

**Relationships**:
- One-to-Many with OrderItem (immutable copy of CartItems)
- One-to-One with Payment
- One-to-One with Bill
- References Cart (immutable)

**Validation Rules**:
- All amounts must be ≥ 0.00
- `total_amount` must equal sum of component amounts (verified at creation)
- `status` transitions: pending → (confirmed | failed); no reverse
- `confirmed_at` is set only when status transitions to "confirmed"
- Shipping address must not be empty or invalid format (basic validation)

**State Transitions**:
- PENDING: Created when checkout started; awaiting payment confirmation
- CONFIRMED: Payment succeeded; order is finalized
- FAILED: Payment failed; order is cancelled

---

### Payment

**Purpose**: Payment transaction record. Tracks payment attempt, processor response, and compliance data.

**Fields**:
- `payment_id` (UUID, primary key): Unique transaction identifier
- `order_id` (UUID, foreign key): Associated order
- `user_id` (UUID, foreign key): Payer
- `amount` (decimal 10,2): Amount charged
- `currency` (string, 3 chars): ISO 4217 code (e.g., "USD")
- `payment_method` (enum: "credit_card" | "debit_card" | "paypal" | "bank_transfer"): Method used
- `processor` (enum: "stripe" | "paypal"): Which external processor handled it
- `processor_transaction_id` (string, 255 chars): External ID from Stripe/PayPal
- `status` (enum: "pending" | "succeeded" | "failed"): Result
- `failure_reason` (text, nullable): If failed, why (e.g., "insufficient_funds", "network_error")
- `attempted_at` (timestamp): When payment was attempted
- `confirmed_at` (timestamp, nullable): When payment succeeded
- `idempotency_key` (string, 255 chars, unique): Prevents duplicate charges on retry

**Relationships**:
- Many-to-One with Order
- References User (immutable)

**Validation Rules**:
- `amount` must match order.total_amount (enforced before sending to processor)
- `processor_transaction_id` is provided only when processor responds
- `status` transitions: pending → (succeeded | failed); no reverse
- `confirmed_at` is set only when status transitions to "succeeded"
- `idempotency_key` is required and must be unique to prevent duplicate charges
- No sensitive card data stored (tokens/references only, managed by Stripe/PayPal)

**State Transitions**:
- PENDING: Payment request sent to processor; awaiting response
- SUCCEEDED: Processor confirmed payment; bill can be generated
- FAILED: Processor declined or error occurred; user can retry with same or different card

---

### Bill

**Purpose**: Invoice document generated after successful payment. Immutable record for user download/reference.

**Fields**:
- `bill_id` (UUID, primary key): Unique bill identifier
- `order_id` (UUID, foreign key): Associated order
- `user_id` (UUID, foreign key): Bill owner
- `bill_number` (string, 20 chars): Human-readable invoice number (e.g., "INV-2026-001234")
- `bill_date` (date): Date bill was issued
- `status` (enum: "pending" | "generated" | "failed"): Generation status
- `file_path` (string, 512 chars, nullable): Path to generated PDF
- `file_format` (enum: "pdf" | "html"): Current format
- `items_json` (text): JSON array of line items (price, quantity, subtotal for each)
- `subtotal` (decimal 10,2): Goods subtotal
- `shipping_fee` (decimal 10,2): Shipping charged
- `tax_amount` (decimal 10,2): Tax charged
- `total_amount` (decimal 10,2): Final total (should match order.total_amount)
- `created_at` (timestamp): When bill record was created
- `generated_at` (timestamp, nullable): When PDF was successfully generated

**Relationships**:
- One-to-One with Order
- References User

**Validation Rules**:
- `bill_number` is auto-generated and immutable
- `total_amount` must match associated order.total_amount
- `items_json` must contain at least one item
- `file_path` is populated only after successful generation
- `status` transitions: pending → (generated | failed); no reverse on failure
- Bill cannot be downloaded until status is "generated"

**State Transitions**:
- PENDING: Awaiting background generation (triggered by payment webhook)
- GENERATED: PDF successfully created; user can download
- FAILED: Generation error occurred; support intervention needed

---

## Entity Relationship Diagram

```
User (external auth system)
  ↓
  ├─→ Cart (1 user : M carts)
  │    ├─→ CartItem (1 cart : M items)
  │    └─→ Order (1 cart → 1 order after checkout)
  │
  ├─→ Order (1 user : M orders)
  │    ├─→ OrderItem (1 order : M items, copy of CartItems)
  │    ├─→ Payment (1 order : 1 payment)
  │    └─→ Bill (1 order : 1 bill)
  │
  └─→ Payment (1 user : M payments)
  
Product Catalog (external, reference only)
  ↑
  └─→ Referenced by CartItem.product_id, OrderItem.product_id
```

## Database Design

### Indexes for Performance

- `carts.user_id, carts.status` (compound): Fast lookups of user's active carts
- `orders.user_id, orders.created_at` (compound): User's order history
- `payments.order_id` (unique): Fast lookup by order
- `bills.order_id` (unique): Fast lookup by order
- `payments.processor_transaction_id` (unique): Idempotency checks, reconciliation

### Migration Strategy

**v1**: All tables created fresh. No legacy data migration needed.

**Future compatibility**: 
- New columns must be nullable or have defaults
- Enum types should be handled via database views or application logic migration
- Foreign key constraints enabled to prevent orphaned records

## Constraints & Guarantees

### Consistency

- Order creation and Payment creation are transactional (both succeed or both fail)
- Bill generation is asynchronous but idempotent (can be retried safely)
- Cart→Order conversion is atomic (prevents race conditions during concurrent checkouts)

### Integrity

- All amounts stored as DECIMAL(10,2) to prevent floating-point precision errors
- user_id and order_id always present (NOT NULL) to maintain traceability
- Foreign keys enforced at database level to prevent orphaned records
- Timestamps use database server time (not client time) to prevent clock skew issues

## Audit & Logging

All entities log to structured logs on:
- CREATE: Full entity details
- UPDATE: Changed fields before/after, timestamp
- DELETE: Never delete; set status to inactive or use soft deletes
- Errors: Full entity state + error message + stack trace
- Payment success/failure: Full payment details logged for compliance

See [research.md](research.md) for logging infrastructure details.
