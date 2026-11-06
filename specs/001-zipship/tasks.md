# Tasks: ZipShip - Express Shopping Cart (Containerized)

**Input**: Design documents from `/specs/001-zipship/`

**Prerequisites**: plan.md (tech stack), spec.md (user stories), data-model.md (entities), contracts/ (API), constitution.md (principles)

**Architecture**: FastAPI backend + PostgreSQL + React frontend (all containerized with Docker Compose)

**Organization**: Tasks grouped by user story, containerization layer, and infrastructure

## Format: `[ID] [P?] [Story] Description with file path`

- **[P]**: Parallelizable (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3, US4)
- Include exact file paths

---

## Phase 1: Setup & Containerization (Shared Infrastructure)

**Purpose**: Project initialization with Docker containerization - no local installation required

- [x] T001 Create project structure (backend, frontend, docs)
- [x] T002 Create requirements.txt with FastAPI, SQLAlchemy, Pydantic, Stripe SDK, Alembic, pytest
- [x] T003 [P] Create backend Dockerfile with multi-stage build
- [x] T004 [P] Create .dockerignore for backend
- [x] T005 [P] Create docker-compose.yml orchestrating backend, database, frontend
- [x] T006 [P] Create docker-compose.override.yml for development hot-reload
- [x] T007 Create DOCKER_SETUP.md comprehensive Docker guide
- [x] T008 Create .gitignore with Python, Docker, IDE patterns
- [x] T009 Update README.md with Docker quick-start instructions
- [x] T010 Update spec.md with Infrastructure & Deployment Requirements section

---

## Phase 2: Foundational Infrastructure (Blocking Prerequisites)

**Purpose**: Core infrastructure - MUST complete before user story implementation

### Database & ORM Setup

- [x] T011 Create database connection in backend/src/db/connection.py (PostgreSQL pooling)
- [x] T012 Create SQLAlchemy session management in backend/src/db/session.py
- [x] T013 Create base declarative model in backend/src/db/base.py
- [x] T014 Initialize Alembic migrations in backend/src/db/migrations/
- [x] T015 Create first migration for Cart and CartItem tables

### API & Middleware

- [x] T016 Create FastAPI app in backend/src/app.py with CORS, exception handlers
- [x] T017 Create JWT authentication middleware in backend/src/middleware/auth.py
- [x] T018 Create request/response logging middleware in backend/src/middleware/logging.py
- [x] T019 [P] Create API schemas (CommonResponse, ErrorResponse) in backend/src/api/schemas.py
- [x] T020 [P] Create validators in backend/src/utils/validators.py (quantity, price, address)
- [x] T021 [P] Create response formatters in backend/src/utils/response.py

### Error Handling & Logging

- [x] T022 Create custom exception classes in backend/src/utils/errors.py
- [x] T023 Create structured JSON logging in backend/src/utils/logging.py

### Testing Foundation

- [x] T024 Create pytest conftest.py with fixtures in backend/tests/conftest.py

**✅ Checkpoint**: Foundation complete - user story implementation can now begin

---

## Phase 3: User Story 1 - Add Items to Shopping Cart (Priority: P1) 🎯 MVP

**Goal**: Enable users to create shopping carts, add/remove/modify items with persistence

**Independent Test**: Can be fully tested by cart CRUD operations in containers with no checkout/payment

### Models for User Story 1

- [x] T025 [P] [US1] Create Cart model in backend/src/models/cart.py (UUID PK, user_id, status enum, 24h expiration, timestamps)
- [x] T025 [P] [US1] Create CartItem model in backend/src/models/cart_item.py (quantity 1-999, price ≥0, computed subtotal)

### Service Layer for User Story 1

- [x] T026 [US1] Create CartService in backend/src/services/cart_service.py with CRUD methods (create, get, add_item, update_quantity, remove_item, get_user_carts)

### API Endpoints for User Story 1

- [x] T027 [US1] Create cart routes in backend/src/api/routes/cart.py (POST/GET /carts, POST/PUT/DELETE /items)

### Testing for User Story 1

- [x] T028 [P] [US1] Create contract tests in tests/contract/test_cart_model.py (model structure validation)
- [x] T029 [P] [US1] Create integration tests in tests/integration/test_cart_endpoints.py (endpoint validation)
- [x] T030 [P] [US1] Create unit tests in tests/unit/test_cart_service.py (CartService methods)
- [x] T031 [US1] Create test fixtures in tests/fixtures/cart_fixtures.py (factory_boy factories)

### Database Migration for User Story 1

- [x] T032 [US1] Create Alembic migration for Cart and CartItem tables in backend/src/db/migrations/versions/

### Validation & Logging for User Story 1

- [x] T033 [US1] Add validation to CartService (ownership, expiration, quantity, empty cart checks)
- [x] T034 [US1] Add structured logging to CartService and cart routes (per Observability principle)

**✅ Checkpoint US1**: Cart operations fully functional, independently testable, ready for validation

---

## Phase 4: User Story 2 - Review Cart and Proceed to Checkout (Priority: P2)

**Goal**: Users can review cart and enter shipping/payment info, system calculates shipping and tax

**Independent Test**: Checkout flow testable without payment processing

### Models for User Story 2

- [x] T035 [P] [US2] Create Order model in backend/src/models/order.py (UUID PK, user_id, status, shipping_address, subtotal/shipping/tax/total)
- [x] T035 [P] [US2] Create OrderItem model in backend/src/models/order_item.py (immutable copy of CartItem)

### Services for User Story 2

- [x] T036 [US2] Create CheckoutService in backend/src/services/checkout_service.py (initiate_checkout, calculate_shipping, calculate_tax, validate_address)
- [x] T037 [US2] Create TaxCalculator in backend/src/services/tax_calculator.py (state-based tax rates: IL=8%, CA=8.625%, default=0%)
- [x] T038 [US2] Create ShippingCalculator in backend/src/services/shipping_calculator.py (flat $5 rate)

### API Endpoints for User Story 2

- [x] T039 [US2] Create checkout routes in backend/src/api/routes/checkout.py (POST /checkout with address validation)

### Testing for User Story 2

- [ ] T040 [P] [US2] Create contract tests for Order models in tests/contract/test_order_model.py
- [ ] T041 [P] [US2] Create integration tests for checkout in tests/integration/test_checkout_flow.py
- [ ] T042 [US2] Create test fixtures for orders in tests/fixtures/order_fixtures.py

### Database Migration for User Story 2

- [x] T043 [US2] Create Alembic migration for Order and OrderItem tables

**✅ Checkpoint US2**: Checkout flow functional, shipping/tax calculated, ready for payment

---

## Phase 5: User Story 3 - Complete Payment (Priority: P3)

**Goal**: Process payments securely, create confirmed orders, prevent duplicate charges

**Independent Test**: Payment processing testable with mocked Stripe via Docker

### Models for User Story 3

- [x] T044 [P] [US3] Create Payment model in backend/src/models/payment.py (payment_id, order_id, amount, status, processor_transaction_id, idempotency_key)

### Services for User Story 3

- [x] T045 [US3] Create PaymentService in backend/src/services/payment_service.py (process_payment, validate_idempotency, handle_success, handle_failure)
- [ ] T046 [US3] Create StripeClient wrapper in backend/src/services/stripe_client.py (charge_card with idempotency)
- [ ] T047 [US3] Create webhook handler in backend/src/api/routes/webhooks.py (POST /webhooks/stripe)

### API Endpoints for User Story 3

- [x] T048 [US3] Create payment endpoint in backend/src/api/routes/checkout.py (POST /checkout/{session_id}/payment)

### Testing for User Story 3

- [ ] T049 [P] [US3] Create contract tests for Payment model in tests/contract/test_payment_model.py
- [ ] T050 [P] [US3] Create integration tests for payment flow in tests/integration/test_payment_flow.py
- [ ] T051 [US3] Create test fixtures for payments in tests/fixtures/payment_fixtures.py

### Database Migration for User Story 3

- [x] T052 [US3] Create Alembic migration for Payment table

**✅ Checkpoint US3**: Payments processed, orders confirmed, duplicate charges prevented

---

## Phase 6: User Story 4 - Generate and View Bill (Priority: P4)

**Goal**: Generate invoices after payment, provide download/view capability

**Independent Test**: Bill generation tested with mocked payment events

### Models for User Story 4

- [x] T053 [P] [US4] Create Bill model in backend/src/models/bill.py (bill_id, order_id, bill_number INV-YYYY-XXXXXX, status, items_json, subtotal/shipping/tax/total)

### Services for User Story 4

- [x] T054 [US4] Create BillService in backend/src/services/bill_service.py (generate_bill_async, generate_pdf, get_bill, download_bill)
- [ ] T055 [US4] Create PDFGenerator in backend/src/services/pdf_generator.py (invoice template with reportlab/weasyprint)
- [x] T056 [US4] Create BillNumberGenerator in backend/src/services/bill_number_generator.py (INV-YYYY-XXXXXX format)

### API Endpoints for User Story 4

- [x] T057 [US4] Create bill routes in backend/src/api/routes/bills.py (GET /orders/{id}/bill, GET /orders/{id}/bill/download)

### Testing for User Story 4

- [ ] T058 [P] [US4] Create contract tests for Bill model in tests/contract/test_bill_model.py
- [ ] T059 [P] [US4] Create integration tests for bill flow in tests/integration/test_bill_flow.py
- [ ] T060 [US4] Create test fixtures for bills in tests/fixtures/bill_fixtures.py

### Database Migration for User Story 4

- [x] T061 [US4] Create Alembic migration for Bill table

**✅ Checkpoint US4**: Bills generated, downloadable, complete e-commerce flow operational

---

## Phase 7: Frontend Setup

**Purpose**: Create React frontend application that communicates with backend API

- [ ] T062 Create frontend/ directory with React create-react-app template
- [ ] T063 [P] Create frontend Dockerfile with Node.js multi-stage build
- [ ] T064 [P] Create frontend/.dockerignore for build optimization
- [ ] T065 Create API client service in frontend/src/services/api.js (axios with backend base URL)
- [ ] T066 Create Cart page component in frontend/src/pages/Cart.jsx
- [ ] T067 Create Checkout page component in frontend/src/pages/Checkout.jsx
- [ ] T068 Create Payment page component in frontend/src/pages/Payment.jsx
- [ ] T069 Create Bill/Order page component in frontend/src/pages/Bill.jsx
- [ ] T070 Create Redux store for cart state management in frontend/src/store/
- [ ] T071 Create routing in frontend/src/App.jsx (cart, checkout, payment, bill pages)
- [ ] T072 Create environment configuration in frontend/.env for API_URL

---

## Phase 8: Testing & Validation

**Purpose**: Comprehensive testing and validation across all user stories

- [ ] T073 [P] Run unit test suite with coverage target: pytest tests/unit/ --cov=src (target 85%+)
- [ ] T074 [P] Run contract tests: pytest tests/contract/ -v
- [ ] T075 [P] Run integration tests: pytest tests/integration/ -v
- [ ] T076 Run full test suite with coverage report: pytest tests/ --cov=src --cov-report=html
- [ ] T077 Run quickstart.md validation scenarios end-to-end in containers
- [ ] T078 Verify all Docker containers healthy: docker-compose ps
- [ ] T079 Verify API accessible: curl http://localhost:8000/docs
- [ ] T080 Verify frontend accessible: curl http://localhost:3000

**✅ Checkpoint**: All tests pass, coverage ≥85%, all services healthy

---

## Phase 9: Documentation & Deployment

**Purpose**: Complete documentation and prepare for production

- [ ] T081 Create API documentation in docs/API.md with all endpoints
- [ ] T082 Create developer guide in docs/DEVELOPMENT.md (local setup, Docker commands)
- [ ] T083 Create deployment guide in docs/DEPLOYMENT.md (production setup, cloud deployment)
- [ ] T084 Create architecture diagram in docs/ARCHITECTURE.md
- [ ] T085 Create troubleshooting guide in docs/TROUBLESHOOTING.md
- [ ] T086 [P] Create GitHub Actions CI/CD pipeline in .github/workflows/
- [ ] T087 [P] Create production docker-compose.yml without hot-reload, debug mode
- [ ] T088 Create secrets management documentation for production Stripe keys
- [ ] T089 Create monitoring setup guide (Prometheus, Grafana, or cloud provider)
- [ ] T090 Verify constitution compliance: Simplicity ✅, Test-First/TDD ✅, Observability ✅

---

## Phase 10: Polish & Optimization

**Purpose**: Performance, security, and code quality improvements

- [ ] T091 [P] Database query optimization - add indices on frequently queried columns
- [ ] T092 [P] Backend performance testing - load test with 100+ concurrent users
- [ ] T093 [P] Frontend performance optimization - optimize bundle size, lazy load routes
- [ ] T094 Security audit - verify no sensitive data in logs, secure headers configured
- [ ] T095 Code cleanup - remove debug statements, unused imports, commented code
- [ ] T096 Update requirements.txt with exact versions
- [ ] T097 Setup database backup strategy in production docs
- [ ] T098 Configure rate limiting on payment endpoints (3 attempts per session)
- [ ] T099 Add CSRF protection to checkout and payment forms
- [ ] T100 Final end-to-end testing in containers: docker-compose up && validate all flows

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup & Containerization)
    ↓
Phase 2 (Foundational Infrastructure) ← CRITICAL: Blocks all user stories
    ↓
Phases 3-6 (User Stories 1-4) ← Can proceed in parallel after Phase 2
    ↓
Phase 7 (Frontend) ← Depends on backend API
    ↓
Phase 8 (Testing & Validation) ← Depends on all implementations
    ↓
Phase 9 (Documentation & Deployment) ← Final polish
    ↓
Phase 10 (Optimization) ← Optional: performance tuning
```

### User Story Dependencies

- **US1 (Cart)**: No dependencies - start after Phase 2 ✅
- **US2 (Checkout)**: Depends on US1 (needs cart data)
- **US3 (Payment)**: Depends on US2 (needs order created)
- **US4 (Bill)**: Depends on US3 (triggered by payment webhook)

### Parallel Opportunities

- **Phase 1**: All [P] tasks (Dockerfile, docker-compose, .dockerignore) run in parallel
- **Phase 2**: Database + API setup can be parallelized by [P] markers
- **Phase 3-6**: Within each user story, models can be created in parallel [P]
- **Phase 7**: Frontend development can start once backend API is ready
- **Phase 8**: Unit, contract, and integration tests run in parallel

---

## Implementation Strategy

### MVP First (Recommended - 2-3 days)

1. ✅ Phase 1: Setup & Containerization (done)
2. ✅ Phase 2: Foundational (mostly done, need migrations T014-T015)
3. ✅ Phase 3: User Story 1 - Cart (done, need tests T028-T031)
4. **STOP and VALIDATE**: Test with `docker-compose up && docker-compose exec backend pytest`
5. Deploy MVP for demo/testing

### Incremental Delivery (Then add features)

- Phase 4: Checkout functionality
- Phase 5: Payment processing
- Phase 6: Bill generation
- Phase 7: Frontend UI
- Phase 8: Full test coverage
- Phase 9: Documentation & deployment
- Phase 10: Performance optimization

### Parallel Team Strategy (3+ developers)

1. Everyone completes Phase 1-2 together
2. Once Phase 2 done:
   - Dev A: Phase 3 (Cart US1)
   - Dev B: Phase 4 (Checkout US2)
   - Dev C: Phase 5 (Payment US3)
3. Dev D: Phase 6 (Bill US4) after US3 half-complete
4. Converge on Phase 7 (Frontend)
5. Team-wide Phase 8-10 (testing, docs, deploy)

---

## Current Status (As of Latest Session)

**Completed** (✅):
- Phase 1: Setup & Containerization - 100% (10 tasks)
- Phase 2: Foundational - 75% (18/23 tasks)
- Phase 3: US1 Cart - 100% (models, service, endpoints, unit tests)
- Containerization infrastructure fully in place
- Docker Compose orchestrating all services
- DOCKER_SETUP.md guide complete

**Pending** (⬜):
- Phase 2: Database migrations (T014-T015)
- Phase 3: Contract & integration tests (T028-T031)
- Phase 4-6: Checkout, Payment, Bill (55 tasks)
- Phase 7: Frontend (12 tasks)
- Phase 8-10: Testing, docs, deployment (38 tasks)

**Total Tasks**: ~100
**Completed**: ~40 (40%)
**Remaining**: ~60 (60%)

---

## Phase 11: Convergence

**Purpose**: Close implementation gaps identified by convergence audit

### Critical Path Blockers (MUST COMPLETE BEFORE PROCEEDING)

- [x] T101 [US2] Create checkout endpoint in backend/src/api/routes/checkout.py with POST /checkout (missing)
- [x] T102 [US2] Create Alembic migration for Order and OrderItem tables (missing)
- [x] T103 [US3] Create Payment model in backend/src/models/payment.py (missing)
- [ ] T104 [US3] Create PaymentService in backend/src/services/payment_service.py (missing)
- [ ] T105 [US3] Create StripeClient wrapper in backend/src/services/stripe_client.py (missing)
- [ ] T106 [US3] Create payment endpoint in backend/src/api/routes/checkout.py POST /checkout/{session_id}/payment (missing)
- [ ] T107 [US3] Create Alembic migration for Payment table (missing)
- [x] T108 [US4] Create Bill model in backend/src/models/bill.py (missing)
- [ ] T109 [US4] Create BillService in backend/src/services/bill_service.py (missing)
- [ ] T110 [US4] Create bill endpoints in backend/src/api/routes/bills.py (missing)
- [ ] T111 [US4] Create Alembic migration for Bill table (missing)

### Test Coverage for US2-4 (Constitution II: Test-First/TDD - CRITICAL)

- [ ] T112 [P] [US2] Create contract tests for Order model in tests/contract/test_order_model.py (missing)
- [ ] T113 [P] [US2] Create integration tests for checkout flow in tests/integration/test_checkout_flow.py (missing)
- [ ] T114 [US2] Create test fixtures for orders in tests/fixtures/order_fixtures.py (missing)
- [ ] T115 [P] [US3] Create contract tests for Payment model in tests/contract/test_payment_model.py (missing)
- [ ] T116 [P] [US3] Create integration tests for payment flow in tests/integration/test_payment_flow.py (missing)
- [ ] T117 [US3] Create test fixtures for payments in tests/fixtures/payment_fixtures.py (missing)
- [ ] T118 [P] [US4] Create contract tests for Bill model in tests/contract/test_bill_model.py (missing)
- [ ] T119 [P] [US4] Create integration tests for bill flow in tests/integration/test_bill_flow.py (missing)
- [ ] T120 [US4] Create test fixtures for bills in tests/fixtures/bill_fixtures.py (missing)

### Frontend Integration

- [ ] T121 Update frontend Payment page to call real payment endpoint (partial - currently stubs)
- [ ] T122 Update frontend Order page to call real order/bill endpoints (partial - currently stubs)
- [ ] T123 Test frontend integration with completed backend (end-to-end validation)

### Remaining Implementation Tasks

- [ ] T124 Create webhook handler in backend/src/api/routes/webhooks.py for Stripe events (missing)
- [ ] T125 Create unit tests for PaymentService in tests/unit/test_payment_service.py (missing)
- [ ] T126 Create unit tests for BillService in tests/unit/test_bill_service.py (missing)
- [ ] T127 Create unit tests for CheckoutService in tests/unit/test_checkout_service.py (missing)

### Validation & Final Testing

- [ ] T128 Run full test suite and verify coverage ≥85% (Phase 8 T076)
- [ ] T129 Verify all containers healthy: docker-compose ps (Phase 8 T078)
- [ ] T130 End-to-end testing of complete cart→checkout→payment→bill flow

---

## Phase 12: Convergence - Close Implementation Gaps

**Purpose**: Complete missing tests, integrations, and frontend to close gap between spec and implementation

### Constitution II Compliance: Test-First/TDD (CRITICAL)

- [x] T131 [P] [US2] Create contract tests for Order model in tests/contract/test_order_model.py (model constraints, relationships, cascade delete)
- [x] T132 [P] [US3] Create contract tests for Payment model in tests/contract/test_payment_model.py (idempotency key uniqueness, FK to Order)
- [x] T133 [P] [US4] Create contract tests for Bill model in tests/contract/test_bill_model.py (bill_number format INV-YYYY-XXXXXX, unique constraints)
- [x] T134 [P] [US2] Create integration tests for checkout flow in tests/integration/test_checkout_flow.py (address validation, tax/shipping calculation)
- [x] T135 [P] [US3] Create integration tests for payment flow in tests/integration/test_payment_flow.py (idempotency handling, bill generation trigger)
- [x] T136 [P] [US4] Create integration tests for bill flow in tests/integration/test_bill_flow.py (bill generation after payment, retrieval by order)
- [x] T137 [US2] Create CheckoutService unit tests in tests/unit/test_checkout_service.py (all service methods with mocks)
- [x] T138 [US3] Create PaymentService unit tests in tests/unit/test_payment_service.py (idempotency, payment processing, validation)
- [x] T139 [US4] Create BillService unit tests in tests/unit/test_bill_service.py (bill generation, retrieval, bill number generation)

### Test Fixtures

- [x] T140 [US2] Create test fixtures in tests/fixtures/order_fixtures.py (OrderFactory, factory_boy factories)
- [x] T141 [US3] Create test fixtures in tests/fixtures/payment_fixtures.py (PaymentFactory with idempotency support)
- [x] T142 [US4] Create test fixtures in tests/fixtures/bill_fixtures.py (BillFactory with bill number generation)

### Missing Core Features

- [x] T143 [US3] Create StripeClient wrapper in backend/src/services/stripe_client.py (charge_card with idempotency_key support)
- [x] T144 [US3] Create webhook handler in backend/src/api/routes/webhooks.py (POST /webhooks/stripe for Stripe events)
- [x] T145 [US4] Create PDFGenerator in backend/src/services/pdf_generator.py (invoice template with reportlab/weasyprint)

### Frontend Implementation (Phase 7)

- [x] T146 Create frontend directory structure and package.json with React 18, axios, react-router-dom
- [x] T147 [P] Create frontend Dockerfile with Node.js 18-alpine multi-stage build
- [x] T148 [P] Create frontend/.dockerignore for build optimization
- [x] T149 Create API client service in frontend/src/services/api.js (axios with Bearer auth, base URL from env)
- [x] T150 Create Redux store and cart slice in frontend/src/store/index.js and cartSlice.js
- [x] T151 Create Cart page component in frontend/src/pages/Cart.jsx (list items, add/remove/update UI)
- [x] T152 Create Checkout page component in frontend/src/pages/Checkout.jsx (shipping address form, tax/shipping display)
- [x] T153 Create Payment page component in frontend/src/pages/Payment.jsx (payment form, idempotency key generation)
- [x] T154 Create Order/Bill page component in frontend/src/pages/Order.jsx (order summary, bill details, download link)
- [x] T155 Create routing in frontend/src/App.jsx with pages for cart, checkout, payment, order
- [x] T156 Create responsive CSS styling in frontend/src/styles/*.css for all pages

### Full Test Suite Validation

- [x] T157 Run full test suite: pytest tests/ --cov=src --cov-report=html (target 85%+)
- [x] T158 Run end-to-end validation: docker-compose up && complete full cart→checkout→payment→bill flow with curl

### API & Documentation

- [ ] T159 Create OpenAPI schema documentation (auto-generated from FastAPI routes)
- [ ] T160 Create API.md documenting all endpoints with request/response examples
- [ ] T161 Create DEVELOPMENT.md with local Docker setup instructions
- [ ] T162 Create ARCHITECTURE.md with system diagram and component descriptions

### Performance & Security (Phase 10)

- [ ] T163 Add database query optimization: indices on frequently queried columns (user_id, order_id, created_at)
- [ ] T164 Configure rate limiting on payment endpoint (3 attempts per session, 1 minute window)
- [ ] T165 Add CSRF protection to checkout and payment forms
- [ ] T166 Security audit: verify no sensitive data in logs, configure secure headers

---

## Phase 13: Final Polish & Release Readiness

**Purpose**: Complete documentation and security hardening; prepare for production deployment

### Documentation (CRITICAL - User/Developer Experience)

- [ ] T167 Create docs/API.md with Swagger link and endpoint reference (auto-generated from FastAPI @app routes)
- [ ] T168 Create docs/DEVELOPMENT.md with Docker local setup, test execution, and debugging instructions
- [ ] T169 Create docs/ARCHITECTURE.md with system diagram, component descriptions, and data flow (Cart→Order→Payment→Bill)
- [ ] T170 Update README.md with feature overview, quick-start commands, and links to docs/

### Performance Optimization (SC-006 Compliance: 100+ concurrent users)

- [ ] T171 Add database indices on frequently queried columns: user_id, order_id, created_at in migration
- [ ] T172 Profile backend with locust load test (100 concurrent users, 30-second ramp) and document results

### Security Hardening (FR-007 Compliance: Secure Payment Data)

- [ ] T173 Add CSRF protection with double-submit cookies to checkout and payment endpoints
- [ ] T174 Implement rate limiting on payment endpoint: 3 attempts per 60-second window per user_id
- [ ] T175 Configure secure HTTP headers: Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, Strict-Transport-Security
- [ ] T176 Security audit: scan logs for sensitive data exposure, verify no card data logged, verify bearer tokens redacted

### Production Readiness

- [ ] T177 Create docker-compose.prod.yml with production-safe settings (no debug, no hot-reload, health checks)
- [ ] T178 Document production deployment process: environment variables, secrets management, database backups
- [ ] T179 Create .github/workflows/ci-cd.yml for automated testing and image building on PR/merge
- [ ] T180 Final end-to-end validation: docker-compose up -f docker-compose.prod.yml && test complete flow

---

## Notes

- [P] tasks = parallelizable (different files, independent)
- [Story] label maps task to user story
- Each user story independently completable and testable
- Docker Compose enables complete development in containers
- No local Python/PostgreSQL/Node.js installation required
- Tests written before implementation (TDD per constitution)
- All components logged and observable (per constitution)
- Simple, straightforward architecture (per constitution)
