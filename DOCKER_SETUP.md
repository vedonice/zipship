# Docker Setup Guide

This guide explains how to run the entire ZipShip & Checkout application stack in Docker without installing anything locally.

## Prerequisites

- **Docker**: Version 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose**: Version 2.0+ (included with Docker Desktop)

## Quick Start

### 1. Start All Services

```bash
docker-compose up
```

This will:
- Build the backend Docker image
- Start PostgreSQL database
- Start FastAPI backend server
- Start frontend (placeholder)
- Create necessary volumes and networks

**Output should show:**
```
cart-db is healthy
cart-backend is healthy
cart-frontend is healthy
```

### 2. Access the Application

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Database**: localhost:5432 (PostgreSQL)

### 3. Run Tests (in Container)

```bash
# Run unit tests
docker-compose exec backend pytest tests/unit/ -v

# Run with coverage
docker-compose exec backend pytest tests/ --cov=src --cov-report=html

# Run specific test file
docker-compose exec backend pytest tests/unit/test_cart_service.py -v
```

### 4. Stop Services

```bash
# Stop (keeps data)
docker-compose stop

# Stop and remove containers (keeps data via volumes)
docker-compose down

# Remove everything including data
docker-compose down -v
```

---

## Development Workflow

### Make Code Changes

Files in `backend/` are mounted as volumes, so changes auto-reload:

```bash
# Edit a file
nano backend/src/services/cart_service.py

# Changes automatically reload in the running container
docker-compose logs -f backend
```

### Database Initialization

Migrations run automatically on container startup:

```bash
# Check migration status
docker-compose exec backend python -m alembic current

# Create a new migration
docker-compose exec backend python -m alembic revision --autogenerate -m "Add new table"
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f db
docker-compose logs -f frontend

# Follow from specific time
docker-compose logs -f --since 10m backend
```

---

## Testing API Endpoints

### Using curl (in container)

```bash
# Create cart
docker-compose exec backend curl -X POST http://localhost:8000/api/v1/carts \
  -H "Authorization: Bearer test_user_12345678" \
  -H "Content-Type: application/json" \
  -d '{"initial_items": []}'

# Add item to cart
docker-compose exec backend curl -X POST http://localhost:8000/api/v1/carts/{cart_id}/items \
  -H "Authorization: Bearer test_user_12345678" \
  -H "Content-Type: application/json" \
  -d '{"product_id": "prod-123", "quantity": 2, "unit_price": 29.99}'
```

### Using Swagger UI

1. Open http://localhost:8000/docs
2. Click "Authorize"
3. Enter token: `test_user_12345678`
4. Try endpoints interactively

---

## Container Architecture

```
┌─────────────────────────────────────┐
│      Docker Network (bridge)       │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────────────┐               │
│  │   Frontend       │               │
│  │  (Node.js)       │               │
│  │  Port 3000       │               │
│  └──────────────────┘               │
│           ↓                         │
│  ┌──────────────────┐               │
│  │  Backend API     │               │
│  │  (FastAPI)       │               │
│  │  Port 8000       │               │
│  └──────────────────┘               │
│           ↓                         │
│  ┌──────────────────┐               │
│  │  PostgreSQL DB   │               │
│  │  Port 5432       │               │
│  │  Volume: data    │               │
│  └──────────────────┘               │
│                                     │
└─────────────────────────────────────┘
```

---

## Environment Variables

### Set in docker-compose.yml

The database credentials are configured in `docker-compose.yml`:
- **DB User**: cartuser
- **DB Password**: cartpassword
- **DB Name**: cart_checkout_db

### For Local .env (Not Committed)

Create `.env` in project root with production secrets:

```env
STRIPE_API_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_live_...
JWT_SECRET=your-production-secret
```

Then pass to docker-compose:
```bash
docker-compose config
```

---

## Troubleshooting

### Port Already in Use

```bash
# Free port 8000
lsof -i :8000
kill -9 <PID>

# Or change port in docker-compose.yml
# Change "8000:8000" to "8001:8000"
```

### Database Connection Failed

```bash
# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db

# Wait for health check
docker-compose ps
```

### Tests Fail with Import Errors

```bash
# Rebuild container
docker-compose build backend
docker-compose up
```

### Need to Reset Data

```bash
# Remove volume and restart
docker-compose down -v
docker-compose up
```

---

## Data Persistence

- **Database Data**: Stored in Docker volume `postgres_data`
- **Application Code**: Mounted as volume for hot-reload
- **Volume Cleanup**: `docker-compose down -v` removes volumes

---

## Production Considerations

For production deployment:

1. Use separate `.env.production` with secrets management
2. Remove volume mounts (use COPY in Dockerfile)
3. Remove `--reload` flag (production doesn't need hot-reload)
4. Use health checks for orchestration
5. Configure proper logging (not DEBUG mode)
6. Set appropriate resource limits

---

## Common Commands

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# Rebuild images
docker-compose build

# View running containers
docker-compose ps

# Access backend shell
docker-compose exec backend /bin/bash

# Access database
docker-compose exec db psql -U cartuser -d cart_checkout_db

# View logs
docker-compose logs -f backend

# Run tests
docker-compose exec backend pytest tests/ -v

# Check health
docker-compose ps
```

---

## Next Steps

1. ✅ Start services: `docker-compose up`
2. ✅ Run tests: `docker-compose exec backend pytest -v`
3. ✅ Test API: http://localhost:8000/docs
4. ⬜ Create frontend (currently placeholder)
5. ⬜ Implement checkout and payment flows
6. ⬜ Add bill generation

---

## Support

For issues:
- Check logs: `docker-compose logs -f`
- Rebuild: `docker-compose build --no-cache`
- Reset: `docker-compose down -v && docker-compose up`
