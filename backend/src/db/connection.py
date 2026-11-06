from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from src.config import settings

# Create engine with connection pooling
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
)


def get_engine():
    """Get database engine"""
    return engine
