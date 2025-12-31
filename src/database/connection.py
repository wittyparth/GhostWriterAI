"""
Database connection management for PostgreSQL.

Uses SQLAlchemy async engine with connection pooling for Neon PostgreSQL.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from src.config.settings import get_settings
from src.database.models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages database connections and sessions.
    
    Uses async SQLAlchemy with connection pooling for PostgreSQL.
    Designed for serverless PostgreSQL (Neon) with NullPool.
    """

    def __init__(self):
        """Initialize database manager with settings."""
        self.settings = get_settings()
        self._engine = None
        self._session_factory = None

    @property
    def engine(self):
        """Get or create the async engine."""
        if self._engine is None:
            # Use NullPool for serverless databases like Neon
            # This prevents connection pooling issues with serverless
            self._engine = create_async_engine(
                self.settings.database_url_async,
                poolclass=NullPool,
                echo=self.settings.debug,
            )
            logger.info("Database engine created")
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get or create the session factory."""
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )
        return self._session_factory

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Provide a transactional scope around a series of operations.
        
        Usage:
            async with db_manager.session() as session:
                user = await session.get(User, user_id)
                ...
        """
        session = self.session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def create_tables(self):
        """Create all tables defined in models."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created")

    async def drop_tables(self):
        """Drop all tables (use with caution!)."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logger.warning("Database tables dropped")

    async def close(self):
        """Close the database engine."""
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("Database engine closed")

    async def health_check(self) -> bool:
        """
        Check if database connection is healthy.
        
        Returns:
            True if database is accessible, False otherwise
        """
        try:
            async with self.session() as session:
                await session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Singleton instance
_db_manager: DatabaseManager | None = None


def get_db_manager() -> DatabaseManager:
    """
    Get or create the database manager singleton.
    
    Returns:
        DatabaseManager instance
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI to get a database session.
    
    Usage:
        @app.get("/users/{user_id}")
        async def get_user(user_id: str, session: AsyncSession = Depends(get_session)):
            user = await session.get(User, user_id)
            return user
    """
    db = get_db_manager()
    async with db.session() as session:
        yield session
