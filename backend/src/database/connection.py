"""
Database connection management for PostgreSQL/SQLite.

Uses SQLAlchemy async engine with connection pooling.
Supports Neon PostgreSQL with SSL and local SQLite.
"""

import logging
import ssl
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from src.config.settings import get_settings
from src.database.models import Base

logger = logging.getLogger(__name__)


def prepare_async_url(url: str) -> tuple[str, dict]:
    """
    Prepare database URL for asyncpg.
    
    Handles SSL mode conversion for Neon DB and other PostgreSQL providers.
    
    Args:
        url: Original database URL
        
    Returns:
        Tuple of (modified_url, connect_args)
    """
    connect_args = {}
    
    # Parse the URL
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    # Handle sslmode for asyncpg
    if 'sslmode' in query_params:
        sslmode = query_params.pop('sslmode')[0]
        
        if sslmode in ('require', 'verify-ca', 'verify-full'):
            # asyncpg uses 'ssl' parameter instead
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connect_args['ssl'] = ssl_context
    
    # Rebuild URL without sslmode
    new_query = urlencode({k: v[0] for k, v in query_params.items()}, doseq=False)
    new_parsed = parsed._replace(query=new_query)
    new_url = urlunparse(new_parsed)
    
    return new_url, connect_args


class DatabaseManager:
    """
    Manages database connections and sessions.
    
    Uses async SQLAlchemy with connection pooling.
    Supports Neon PostgreSQL (serverless) with NullPool.
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
            url = self.settings.database_url_async
            connect_args = {}
            
            # Handle PostgreSQL with SSL (Neon, Supabase, etc.)
            if url.startswith("postgresql"):
                url, connect_args = prepare_async_url(url)
            
            # Use NullPool for serverless databases like Neon
            # Use default pooling for SQLite
            pool_class = NullPool if not url.startswith("sqlite") else None
            
            engine_kwargs = {
                "echo": False,  # Set to True only for debugging SQL queries
            }
            
            if pool_class:
                engine_kwargs["poolclass"] = pool_class
            
            if connect_args:
                engine_kwargs["connect_args"] = connect_args
            
            self._engine = create_async_engine(url, **engine_kwargs)
            logger.info(f"Database engine created: {url.split('@')[-1] if '@' in url else url}")
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
        from sqlalchemy import text
        try:
            async with self.session() as session:
                await session.execute(text("SELECT 1"))
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
