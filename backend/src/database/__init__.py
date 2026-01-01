"""
Database Package - PostgreSQL layer with async SQLAlchemy.

Exports:
    Base: SQLAlchemy declarative base
    User, BrandProfile, Post, ReferencePost, AgentExecution, UserFeedback: Models
    DatabaseManager, get_db_manager, get_session: Connection management
"""

from src.database.models import (
    Base,
    User,
    BrandProfile,
    Post,
    ReferencePost,
    AgentExecution,
    UserFeedback,
)
from src.database.connection import (
    DatabaseManager,
    get_db_manager,
    get_session,
)

__all__ = [
    # Base
    "Base",
    # Models
    "User",
    "BrandProfile",
    "Post",
    "ReferencePost",
    "AgentExecution",
    "UserFeedback",
    # Connection
    "DatabaseManager",
    "get_db_manager",
    "get_session",
]
