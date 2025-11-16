"""
Pytest configuration and fixtures

Provides comprehensive test fixtures for:
- Database sessions (isolated per test)
- HTTP test clients
- User fixtures (doctor, secretary, admin)
- Authentication fixtures (JWT tokens, headers)
- Model factories (User, Dictation, Transcription)
"""

import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from app.db.session import Base, get_db
from app.core.config import settings
from app.core.security import hash_password, create_access_token
from app.models.user import User, UserRole


# Test database URL
TEST_DATABASE_URL = (
    settings.TEST_DATABASE_URL or "postgresql+asyncpg://test:test@localhost:5432/dictat_test"
)

# Skip marker for Docker-dependent tests
skip_docker = pytest.mark.skipif(
    settings.SKIP_DOCKER_TESTS,
    reason="Skipping Docker-dependent tests (SKIP_DOCKER_TESTS=true)"
)


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
@skip_docker
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create test database session

    Requires Docker (PostgreSQL). Skip with SKIP_DOCKER_TESTS=true

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

    Lazily imports the FastAPI app to avoid import errors in unit tests.
    """
    from app.main import app

    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_doctor(test_db: AsyncSession) -> User:
    """
    Create test doctor user

    Returns:
        User object with doctor role
    """
    user = User(
        email="doctor@test.com",
        hashed_password=hash_password("testpassword123"),
        full_name="Dr. Test Doctor",
        role=UserRole.DOCTOR,
        is_active=True,
        is_verified=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_secretary(test_db: AsyncSession) -> User:
    """
    Create test secretary user

    Returns:
        User object with secretary role
    """
    user = User(
        email="secretary@test.com",
        hashed_password=hash_password("testpassword123"),
        full_name="Test Secretary",
        role=UserRole.SECRETARY,
        is_active=True,
        is_verified=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_admin(test_db: AsyncSession) -> User:
    """
    Create test admin user

    Returns:
        User object with admin role
    """
    user = User(
        email="admin@test.com",
        hashed_password=hash_password("testpassword123"),
        full_name="Test Admin",
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture
def doctor_token(test_doctor: User) -> str:
    """
    Generate JWT access token for test doctor

    Returns:
        JWT token string
    """
    token_data = {
        "sub": str(test_doctor.id),
        "email": test_doctor.email,
        "role": test_doctor.role.value,
    }
    return create_access_token(token_data)


@pytest.fixture
def secretary_token(test_secretary: User) -> str:
    """
    Generate JWT access token for test secretary

    Returns:
        JWT token string
    """
    token_data = {
        "sub": str(test_secretary.id),
        "email": test_secretary.email,
        "role": test_secretary.role.value,
    }
    return create_access_token(token_data)


@pytest.fixture
def admin_token(test_admin: User) -> str:
    """
    Generate JWT access token for test admin

    Returns:
        JWT token string
    """
    token_data = {
        "sub": str(test_admin.id),
        "email": test_admin.email,
        "role": test_admin.role.value,
    }
    return create_access_token(token_data)


@pytest.fixture
def doctor_auth_headers(doctor_token: str) -> Dict[str, str]:
    """
    Get authentication headers for test doctor

    Returns:
        Dictionary with Authorization header
    """
    return {"Authorization": f"Bearer {doctor_token}"}


@pytest.fixture
def secretary_auth_headers(secretary_token: str) -> Dict[str, str]:
    """
    Get authentication headers for test secretary

    Returns:
        Dictionary with Authorization header
    """
    return {"Authorization": f"Bearer {secretary_token}"}


@pytest.fixture
def admin_auth_headers(admin_token: str) -> Dict[str, str]:
    """
    Get authentication headers for test admin

    Returns:
        Dictionary with Authorization header
    """
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def user_factory(test_db: AsyncSession):
    """
    Factory function for creating test users

    Usage:
        user = await user_factory(email="test@example.com", role=UserRole.DOCTOR)
    """

    async def _create_user(
        email: str = "test@example.com",
        password: str = "testpassword123",
        full_name: str = "Test User",
        role: UserRole = UserRole.DOCTOR,
        is_active: bool = True,
        is_verified: bool = True,
    ) -> User:
        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            role=role,
            is_active=is_active,
            is_verified=is_verified,
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user

    return _create_user
