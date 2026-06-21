"""Database configuration and session management."""

from typing import AsyncGenerator

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

# Redis client
redis_client: redis.Redis | None = None

# Create async engine with robust connection pooling for production
engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_pre_ping=True,  # Verifies connection health before using
    pool_size=settings.database_pool_size,        # Base pool size from env
    max_overflow=settings.database_max_overflow,  # Overflow connections from env
    pool_recycle=3600,   # Recycle connections every hour to prevent DB-side timeouts
)

# Create async session factory (SQLAlchemy 2.0 syntax)
async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session.
    
    Yields:
        AsyncSession: Database session for use in route handlers.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        # In production, Alembic handles migrations.
        # This function acts as a readiness hook for the DB engine.
        pass


async def close_db() -> None:
    """Close database engine."""
    await engine.dispose()


async def init_redis() -> None:
    """Initialize Redis connection with strict timeouts."""
    global redis_client
    redis_client = await redis.from_url(
        settings.redis_url, 
        decode_responses=True,
        socket_timeout=5.0,           # Prevent hanging on broken connections
        socket_connect_timeout=5.0,   # Prevent hanging on initial connect
        retry_on_timeout=True,        # Safe retry for idempotent operations
        protocol=2,                   # CRITICAL FIX: Use older protocol for Windows Redis compatibility
    )


async def close_redis() -> None:
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


def get_redis() -> redis.Redis:
    """Get Redis client.
    
    Returns:
        Redis: Redis async client
        
    Raises:
        RuntimeError: If Redis is not initialized
    """
    if redis_client is None:
        raise RuntimeError("Redis is not initialized")
    return redis_client