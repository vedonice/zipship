# Phase 0: Research & Clarification

**Date**: 2026-09-16  
**Status**: Complete

## Technology Stack Decisions

All technical context items were resolved through best practices analysis. No unresolved clarifications remain.

### Python 3.11+ Backend

**Decision**: Python 3.11+ with FastAPI async framework

**Rationale**: 
- FastAPI provides async I/O for handling concurrent checkout requests
- Built-in OpenAPI documentation for API contracts
- Strong Pydantic integration for automatic request/response validation aligns with constitution's "self-documenting" simplicity principle
- Mature ecosystem with excellent testing tools

**Alternatives Considered**:
- Node.js/Express: Equally viable; Python chosen for team familiarity and better data validation
- Go: Would be faster; Python provides better developer experience for rapid development

### PostgreSQL Storage

**Decision**: PostgreSQL for relational data

**Rationale**:
- Transactional guarantees needed for payment + order creation atomicity
- ACID compliance prevents duplicate orders and payment inconsistencies
- JSON support for flexible bill generation storage
- Native support for proper foreign keys (carts → orders → payments → bills)

**Alternatives Considered**:
- MongoDB: Lacks transaction support needed for payment safety; dropped
- Redis: Cache layer only; not primary store

### Stripe/PayPal Payment Integration

**Decision**: Abstract payment processor interface; implement Stripe as primary with PayPal as fallback option

**Rationale**:
- Stripe + PayPal cover 80%+ of e-commerce market
- Both offer strong fraud detection and recurring payment support
- PCI-DSS compliance through tokenization; card data never touches our servers
- Webhooks enable asynchronous bill generation (decoupling payment from bill processing)

**Alternatives Considered**:
- Custom payment gateway: Security liability; dropped
- Square/Authorize.net: Smaller market share; can add if needed later

### Test Framework: pytest

**Decision**: pytest with fixtures, factory_boy, and responses library

**Rationale**:
- pytest aligns with constitution's Test-First/TDD principle through fixture-based test organization
- factory_boy provides readable test data factories (improves simplicity)
- responses library mocks external HTTP calls (payment processor) without brittle string matching
- Excellent integration with FastAPI testing client

## Integration Patterns

### Payment Webhook Handling

**Decision**: Asynchronous bill generation triggered by payment webhook from Stripe/PayPal

**Rationale**:
- Payment success webhook triggers bill service independently from checkout API response
- Decouples payment confirmation from bill generation (resolves edge case: "bill generation fails after successful payment")
- Improves observability: each component logs independently; failures don't cascade
- Scales better: checkout API returns immediately; bill generation happens in background

### Cart Persistence

**Decision**: Database-backed carts with Redis caching layer (optional v2 optimization)

**Rationale**:
- v1: PostgreSQL cart table with indexed lookups by user_id
- Supports 24-hour persistence requirement
- Simplicity: no separate cache; single source of truth reduces debugging complexity
- Future: Redis can be added for performance without breaking existing code

## Research Outcomes

| Item | Status | Decision |
|------|--------|----------|
| Language/Framework | ✅ Resolved | Python 3.11 + FastAPI |
| Database | ✅ Resolved | PostgreSQL with SQLAlchemy |
| Payment Integration | ✅ Resolved | Stripe (primary) + PayPal (fallback) |
| Testing Framework | ✅ Resolved | pytest + fixtures + factory_boy |
| Bill Generation | ✅ Resolved | Async webhook handler + PDF generation (reportlab/weasyprint) |
| Session Management | ✅ Resolved | JWT tokens; cart tied to authenticated user |
| Tax Calculation | ✅ Resolved | TaxJar API or country/state lookup table (v1: simple lookup) |
| Logging | ✅ Resolved | Python logging + structlog for structured JSON logs |

## Architecture Overview

```
Client (Browser/Mobile)
    ↓
REST API (FastAPI)
    ├── Cart Endpoints (GET, POST, PUT, DELETE)
    ├── Checkout Endpoint (POST)
    └── Order/Bill Endpoints (GET)
    ↓
Services Layer
    ├── CartService
    ├── CheckoutService
    ├── PaymentService
    └── BillService
    ↓
PostgreSQL Database
    ├── carts table
    ├── orders table
    ├── order_items table
    ├── payments table
    └── bills table
    ↓
External Services
    ├── Stripe API (payment processing)
    └── Stripe Webhooks → Bill Generation
```

## No Clarifications Required

All technical decisions have clear rationales. Ready to proceed to Phase 1 design.
