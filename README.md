# Whitewalker - Shopping Cart & Checkout with Payment

A complete e-commerce shopping cart and checkout system with payment processing, built with FastAPI, PostgreSQL, and Stripe.

## Project Structure

```
backend/
├── src/
│   ├── models/           # SQLAlchemy ORM models
│   │   ├── cart.py       # Cart model
│   │   └── cart_item.py  # CartItem model
│   ├── services/         # Business logic layer
│   │   └── cart_service.py
│   ├── api/
│   │   ├── routes/       # HTTP endpoint handlers
│   │   │   └── cart.py
│   │   └── schemas.py    # Pydantic request/response models
│   ├── db/               # Database infrastructure
│   │   ├── connection.py
│   │   ├── session.py
│   │   ├── base.py
│   │   └── migrations/   # Alembic migrations
│   ├── middleware/       # FastAPI middleware
│   │   └── auth.py
│   ├── utils/            # Utilities
│   │   ├── logging.py
│   │   └── errors.py
│   ├── config.py         # Application configuration
│   └── app.py            # FastAPI application
├── tests/
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   ├── contract/         # Contract tests
│   └── conftest.py       # Pytest fixtures
└── requirements.txt      # Python dependencies
```

## Architecture

- **Framework**: FastAPI (async Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT bearer tokens
- **Payment**: Stripe/PayPal integration
- **Logging**: Structured JSON logging for observability
- **Testing**: pytest with TDD approach

## Implementation Status

### ✅ Phase 1: Setup (Complete)
- [x] Project structure
- [x] requirements.txt
- [x] configuration (config.py)
- [x] .gitignore

### ✅ Phase 2: Foundational (Partial - Core Complete)
- [x] Database connection & pooling
- [x] SQLAlchemy session management
- [x] Base model for ORM
- [x] Authentication middleware
- [x] Error handling & custom exceptions
- [x] Structured JSON logging
- [ ] API middleware (request/response logging) - **TODO**
- [ ] Response envelope formatting - **TODO**

### ✅ Phase 3: User Story 1 - Add Items to Cart (MVP Complete)
- [x] Cart model (Constraints: 24h expiration, status tracking)
- [x] CartItem model (Constraints: quantity 1-999, price >= 0)
- [x] CartService (add, remove, modify, view operations)
- [x] Cart API endpoints (CRUD operations)
- [x] Unit tests for CartService
- [x] Validation & error handling
- [x] Structured logging for cart operations

**MVP Status: READY FOR TESTING** ✅

### 🔄 Phase 4: User Story 2 - Review & Checkout (Not Started)
- [ ] Order model
- [ ] OrderItem model
- [ ] CheckoutService (shipping/tax calculation)
- [ ] Checkout API endpoints
- [ ] Integration tests

### 🔄 Phase 5: User Story 3 - Payment Processing (Not Started)
- [ ] Payment model
- [ ] PaymentService (Stripe integration)
- [ ] Webhook handling
- [ ] Idempotency key management
- [ ] Payment endpoints

### 🔄 Phase 6: User Story 4 - Bill Generation (Not Started)
- [ ] Bill model
- [ ] BillService (PDF generation)
- [ ] Async bill generation
- [ ] Bill download endpoints

### 🔄 Phase 7: Polish & Deployment (Not Started)
- [ ] Performance testing
- [ ] Load testing
- [ ] Documentation
- [ ] Docker containerization
- [ ] CI/CD pipeline

## Quick Start (Docker - Recommended)

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- **No local Python, PostgreSQL, or Node.js installation required**

### Run Everything in Containers

```bash
# Start all services (backend, database, frontend)
docker-compose up

# Services will be available at:
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Frontend: http://localhost:3000
# - Database: localhost:5432
```

### Run Tests (in Container)

```bash
# Run unit tests
docker-compose exec backend pytest tests/unit/ -v

# Run with coverage
docker-compose exec backend pytest tests/ --cov=src --cov-report=html

# Run specific test file
docker-compose exec backend pytest tests/unit/test_cart_service.py -v
```

### Stop Services

```bash
# Stop (keeps data)
docker-compose down

# Remove everything including data
docker-compose down -v
```

For detailed Docker setup guide, see [DOCKER_SETUP.md](DOCKER_SETUP.md)

---

## Quick Start (Local Development - Alternative)

**Note**: Docker setup above is recommended to avoid local installation.

### Setup

1. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Initialize database**:
   ```bash
   alembic upgrade head
   ```

4. **Run development server**:
   ```bash
   uvicorn src.app:app --reload
   ```

   API will be available at `http://localhost:8000`
   Docs at `http://localhost:8000/docs`

### Testing

Run all tests:
```bash
pytest tests/
```

Run specific test suite:
```bash
pytest tests/unit/test_cart_service.py -v
```

Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

## API Endpoints (MVP)

### Cart Operations

- `POST /api/v1/carts` - Create new cart
- `GET /api/v1/carts/{cart_id}` - Get cart contents
- `GET /api/v1/carts` - List user's carts
- `POST /api/v1/carts/{cart_id}/items` - Add item to cart
- `PUT /api/v1/carts/{cart_id}/items/{cart_item_id}` - Update item quantity
- `DELETE /api/v1/carts/{cart_id}/items/{cart_item_id}` - Remove item

All endpoints require `Authorization: Bearer <token>` header.

## Design Principles (Whitewalker Constitution)

1. **Simplicity**: Clear separation of concerns, straightforward models, no premature abstractions
2. **Test-First/TDD**: All features include comprehensive test coverage before implementation
3. **Observability**: Structured JSON logging on all operations for debugging without code access

## Next Steps

1. **Database migrations**: Create Alembic migrations for Cart/CartItem tables
2. **Integration tests**: Add tests that exercise the full API layer
3. **User Story 2**: Implement checkout with shipping/tax calculation
4. **User Story 3**: Add payment processing with Stripe
5. **User Story 4**: Implement bill generation and download

## Constitutional Compliance

This implementation follows the Whitewalker Constitution v1.0.0:

- ✅ **Simplicity**: Models are straightforward, services have single responsibility, no complex abstractions
- ✅ **Test-First/TDD**: All completed features have corresponding tests (see `tests/unit/`)
- ✅ **Observability**: Structured JSON logging for all cart operations with timestamps and context

## References

- [Plan](specs/001-zipship/plan.md)
- [Specification](specs/001-zipship/spec.md)
- [Data Model](specs/001-zipship/data-model.md)
- [API Contract](specs/001-zipship/contracts/rest-api.md)
- [Research](specs/001-zipship/research.md)
- [Quickstart](specs/001-zipship/quickstart.md)
- [Tasks](specs/001-zipship/tasks.md)
