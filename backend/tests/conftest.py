import pytest
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
import os

from src.app import app
from src.db.base import Base


# Test database - use PostgreSQL (in Docker the host is 'db')
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://cartuser:cartpassword@db:5432/cart_checkout_db"
)


@pytest.fixture(scope="function")
def test_db():
    """Create test database session"""
    # Create fresh engine for each test
    if "sqlite" in TEST_DATABASE_URL:
        engine = create_engine(
            TEST_DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=pool.StaticPool,
        )
    else:
        engine = create_engine(TEST_DATABASE_URL)

    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    yield db
    db.close()

    # Cleanup
    try:
        Base.metadata.drop_all(bind=engine)
    except Exception:
        pass  # Cleanup may fail in some cases, continue anyway


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create auth headers for testing"""
    return {"Authorization": "Bearer test_user_123456789"}
