"""Pytest configuration and global fixtures."""

import asyncio
from typing import AsyncGenerator
from uuid import uuid4
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app
from app.database import get_db, get_redis
from app.config import settings
from app.models import Base
from app.domains.identity.services.jwt_service import JWTService

# Generate a safe isolated test database URL
TEST_DATABASE_URL = settings.database_url.replace(
    "neet_db", "neet_test_db"
) if "neet_db" in settings.database_url else settings.database_url + "_test"

# CRITICAL FIX: Use NullPool to prevent async socket sharing across pytest event loops
engine = create_async_engine(
    TEST_DATABASE_URL, 
    poolclass=NullPool, 
    echo=False
)

TestingSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Create test database schema once per session."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(autouse=True)
async def clear_data():
    """Clear data between tests to ensure absolute isolation."""
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f"TRUNCATE TABLE {table.name} CASCADE;"))
    yield


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Database session fixture."""
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def db_session(db: AsyncSession) -> AsyncSession:
    """Alias for db fixture, mapping to specific domain test signatures."""
    return db


@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """FastAPI test client with robust dependency overrides."""
    app.dependency_overrides[get_db] = lambda: db
    
    # Mock Redis to ensure tests run without requiring a live Redis server
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    app.dependency_overrides[get_redis] = lambda: mock_redis

    # FIX: Wrap the FastAPI app in ASGITransport to support modern httpx versions
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
        
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_headers() -> dict:
    """Provide authorization headers for authenticated route tests."""
    mock_redis = AsyncMock()
    jwt_service = JWTService(mock_redis)
    token, _ = jwt_service.create_access_token(uuid4(), "student")
    return {"Authorization": f"Bearer {token}"}