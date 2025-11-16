"""
Pytest configuration and fixtures

TODO Phase 4:
- Set up test database
- Create fixtures for models
- Add authentication fixtures
- Create factory functions
- Set up test client
"""

import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import Base, get_db
from app.core.config import settings


# Test database URL
TEST_DATABASE_URL = settings.TEST_DATABASE_URL or "postgresql+asyncpg://test:test@localhost:5432/dictat_test"


@pytest.fixture(scope="session")
def event_loop():
    """
    Create event loop for async tests

    TODO Phase 4:
    - Configure event loop policy
    - Set up event loop for session scope
    """
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create test database session

    TODO Phase 4:
    - Create async engine for test database
    - Create all tables before test
    - Drop all tables after test
    - Yield session for test
    - Handle cleanup properly
    """
    # Create async engine for tests
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    # Drop tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def client(test_db: AsyncSession) -> Generator[TestClient, None, None]:
    """
    Create test client

    TODO Phase 4:
    - Override get_db dependency
    - Create test client
    - Yield client for tests
    """

    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# TODO Phase 4: Add user fixtures
# @pytest_asyncio.fixture
# async def test_user(test_db: AsyncSession):
#     """Create test user"""
#     pass
#
# @pytest_asyncio.fixture
# async def test_doctor(test_db: AsyncSession):
#     """Create test doctor"""
#     pass
#
# @pytest_asyncio.fixture
# async def test_secretary(test_db: AsyncSession):
#     """Create test secretary"""
#     pass
#
# @pytest_asyncio.fixture
# async def test_admin(test_db: AsyncSession):
#     """Create test admin"""
#     pass


# TODO Phase 4: Add authentication fixtures
# @pytest.fixture
# def auth_headers(test_user):
#     """Get authentication headers for test user"""
#     pass


# TODO Phase 4: Add model factories
# @pytest.fixture
# def user_factory():
#     """Factory for creating users"""
#     pass
#
# @pytest.fixture
# def dictation_factory():
#     """Factory for creating dictations"""
#     pass
