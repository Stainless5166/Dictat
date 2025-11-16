"""
Database session configuration and connection management

TODO Phase 1:
- Configure async SQLAlchemy engine
- Set up session factory
- Implement connection pooling
- Add database health check
- Configure for different environments
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# Create async engine
# TODO: Add SSL configuration for production
# TODO: Configure connection pool settings
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,  # Verify connections before using
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for all models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session

    Usage in FastAPI endpoints:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...

    TODO:
    - Add transaction management
    - Implement rollback on exception
    - Add query logging for debugging
    - Add connection timeout handling
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database (create all tables)

    TODO:
    - Use Alembic migrations instead in production
    - Add database seeding for development
    - Create initial admin user
    - Set up default roles
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections

    TODO:
    - Add connection cleanup
    - Flush pending changes
    - Log closure event
    """
    await engine.dispose()
