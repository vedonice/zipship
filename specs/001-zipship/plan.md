# Implementation Plan: ZipShip - Express Shopping Cart

**Branch**: `001-zipship` | **Date**: 2026-09-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-zipship/spec.md`

## Summary

Implement a complete e-commerce shopping cart and checkout system enabling users to add items to cart, review their selection, proceed to checkout with shipping and payment information, process payments securely, and generate invoices. 

**Technical Approach**: RESTful API backend with persistent cart storage, integration with payment processor, and asynchronous bill generation. Structured logging and comprehensive tests ensure observability and reliability per constitution principles.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: 
- FastAPI (async web framework)
- SQLAlchemy 2.0 (ORM for data persistence)
- Pydantic (request/response validation)
- Stripe/PayPal SDK (payment processing)
- Alembic (database migrations)

**Storage**: PostgreSQL (relational data: carts, orders, payments, bills)

**Testing**: pytest with fixtures, factory_boy for test data, responses library for mocking HTTP calls

**Target Platform**: Linux server / Cloud (AWS, GCP, or similar)

**Project Type**: REST API web service with persistent storage

**Performance Goals**: 
- Cart operations: <200ms p95 latency
- Checkout flow: Complete in <3 minutes user-perceived time
- Payment success rate: 99.5% reliability

**Constraints**: 
- Payment data compliance: PCI-DSS (no sensitive card data stored locally)
- Bill generation: Complete within 10 seconds of payment success
- Session persistence: Cart data persists for 24 hours minimum
- Concurrent load: Support 100+ concurrent users without degradation

**Scale/Scope**: Single currency, simple shipping address (no validation), tax calculated by location lookup, integration with payment processor

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Project Constitution**: Whitewalker Constitution v1.0.0 ([see constitution.md](../../.specify/memory/constitution.md))

### Principle 1: Simplicity
✅ **PASS** — Design respects simplicity:
- Clear separation of concerns: cart service, order service, payment service, bill service
- Straightforward data models matching spec requirements (no over-engineering)
- RESTful endpoints with single responsibility per route
- No premature abstractions; patterns introduced only when repeated

### Principle 2: Test-First / TDD
✅ **PASS** — Every feature includes test coverage:
- Cart operations: unit tests (add/remove/modify) + integration tests with DB
- Checkout: acceptance tests validating end-to-end flow
- Payment: contract tests with payment processor mocking + integration tests
- Bill generation: unit tests + event handling tests
- Scope: No code merges without test coverage

### Principle 3: Observability  
✅ **PASS** — Structured logging and metrics throughout:
- All cart operations (add, remove, modify) logged with user_id, item details, timestamp
- Payment processing logs include attempt, success/failure, error details
- Bill generation logs include trigger event, processing time, result status
- Error scenarios logged with sufficient context for debugging from logs alone
- Metrics tracked: cart size distribution, checkout completion rate, payment success rate, bill generation latency

**Constitutional Status**: ✅ All gates pass. No violations or justifications needed.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── app.py                          # FastAPI application entry point
│   ├── config.py                       # Configuration (DB, payment processor)
│   ├── models/
│   │   ├── cart.py                     # Cart model
│   │   ├── order.py                    # Order model
│   │   ├── payment.py                  # Payment model
│   │   └── bill.py                     # Bill/Invoice model
│   ├── services/
│   │   ├── cart_service.py             # Cart business logic
│   │   ├── checkout_service.py         # Checkout orchestration
│   │   ├── payment_service.py          # Payment processing
│   │   └── bill_service.py             # Bill generation
│   ├── api/
│   │   ├── routes/
│   │   │   ├── cart.py                 # Cart endpoints
│   │   │   ├── checkout.py             # Checkout endpoints
│   │   │   └── bills.py                # Bill viewing/download endpoints
│   │   └── schemas.py                  # Pydantic request/response models
│   ├── db/
│   │   ├── connection.py               # Database connection
│   │   ├── session.py                  # SQLAlchemy session management
│   │   └── migrations/                 # Alembic migrations
│   ├── utils/
│   │   ├── logging.py                  # Structured logging configuration
│   │   ├── errors.py                   # Error handling
│   │   └── validators.py               # Data validation helpers
│   └── middleware/
│       ├── auth.py                     # Authentication/authorization
│       └── logging.py                  # Request/response logging

tests/
├── unit/
│   ├── test_cart_service.py
│   ├── test_checkout_service.py
│   ├── test_payment_service.py
│   └── test_bill_service.py
├── integration/
│   ├── test_cart_endpoints.py
│   ├── test_checkout_flow.py
│   └── test_payment_processing.py
├── contract/
│   ├── test_payment_processor_contract.py
│   └── test_bill_format_contract.py
├── conftest.py                         # Shared pytest fixtures
└── factories.py                        # Factory Boy test data
```

**Structure Decision**: Single backend service with FastAPI. Clear separation:
- **models/**: SQLAlchemy ORM definitions matching spec entities (Cart, Order, Payment, Bill)
- **services/**: Business logic layer (cart operations, checkout flow, payment handling, bill generation)
- **api/**: HTTP layer (routes, request/response schemas)
- **db/**: Persistence (database connection, migrations)
- **utils/**: Cross-cutting concerns (logging, error handling, validation)
- **tests/**: Comprehensive coverage (unit, integration, contract tests following TDD principle)

## Complexity Tracking

> **Not applicable** — Constitution Check passed with no violations. All design decisions honor Simplicity, Test-First/TDD, and Observability principles.
