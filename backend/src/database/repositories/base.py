"""
Repository pattern for database access.

Provides async CRUD operations for all models.
"""

import logging
from typing import Any, Sequence
from uuid import UUID

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, BrandProfile, Post, ReferencePost, AgentExecution

logger = logging.getLogger(__name__)


class BaseRepository:
    """Base repository with common CRUD operations."""
    
    model = None
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, id: UUID) -> Any | None:
        """Get a record by ID."""
        result = await self.session.get(self.model, id)
        return result
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> Sequence[Any]:
        """Get all records with pagination."""
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def create(self, **kwargs) -> Any:
        """Create a new record."""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance
    
    async def update_by_id(self, id: UUID, **kwargs) -> Any | None:
        """Update a record by ID."""
        stmt = update(self.model).where(self.model.id == id).values(**kwargs)
        await self.session.execute(stmt)
        return await self.get_by_id(id)
    
    async def delete_by_id(self, id: UUID) -> bool:
        """Delete a record by ID."""
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0


class UserRepository(BaseRepository):
    """Repository for User model."""
    model = User
    
    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class BrandProfileRepository(BaseRepository):
    """Repository for BrandProfile model."""
    model = BrandProfile
    
    async def get_by_user_id(self, user_id: UUID) -> BrandProfile | None:
        """Get brand profile by user ID."""
        stmt = select(BrandProfile).where(BrandProfile.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class PostRepository(BaseRepository):
    """Repository for Post model."""
    model = Post
    
    async def get_by_user_id(self, user_id: UUID, limit: int = 50, offset: int = 0) -> Sequence[Post]:
        """Get posts by user ID."""
        stmt = select(Post).where(Post.user_id == user_id).order_by(Post.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_recent(self, user_id: UUID, count: int = 5) -> Sequence[Post]:
        """Get recent posts for a user."""
        stmt = select(Post).where(Post.user_id == user_id).order_by(Post.created_at.desc()).limit(count)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def update(self, post_id: UUID, **kwargs) -> Post | None:
        """Update a post by ID."""
        stmt = update(Post).where(Post.post_id == post_id).values(**kwargs)
        await self.session.execute(stmt)
        return await self.get_by_id(post_id)
    
    async def get_by_id(self, post_id: UUID) -> Post | None:
        """Get post by ID (override base to use post_id)."""
        return await self.session.get(Post, post_id)
    
    async def delete_by_id(self, post_id: UUID) -> bool:
        """Delete a post by ID (override base to use post_id)."""
        stmt = delete(Post).where(Post.post_id == post_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0
    
    async def count_today(self, user_id: UUID) -> int:
        """Count posts created by user in the last 24 hours."""
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(days=1)
        
        stmt = select(func.count()).select_from(Post).where(
            Post.user_id == user_id,
            Post.created_at >= cutoff
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0


class ReferencePostRepository(BaseRepository):
    """Repository for ReferencePost model."""
    model = ReferencePost
    
    async def get_by_niche(self, niche: str, limit: int = 20) -> Sequence[ReferencePost]:
        """Get reference posts by niche."""
        stmt = select(ReferencePost).where(ReferencePost.niche == niche).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_high_engagement(self, min_rate: float = 0.05, limit: int = 50) -> Sequence[ReferencePost]:
        """Get high engagement reference posts."""
        stmt = select(ReferencePost).where(ReferencePost.engagement_rate >= min_rate).order_by(ReferencePost.engagement_rate.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()


class ExecutionLogRepository(BaseRepository):
    """Repository for AgentExecution model."""
    model = AgentExecution
    
    async def get_by_post_id(self, post_id: UUID) -> Sequence[AgentExecution]:
        """Get execution logs for a post."""
        stmt = select(AgentExecution).where(AgentExecution.post_id == post_id).order_by(AgentExecution.created_at)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_cost_summary(self, post_id: UUID) -> dict:
        """Get total cost for a post generation."""
        logs = await self.get_by_post_id(post_id)
        return {
            "total_cost_usd": sum(log.cost_usd or 0 for log in logs),
            "total_input_tokens": sum(log.input_tokens or 0 for log in logs),
            "total_output_tokens": sum(log.output_tokens or 0 for log in logs),
            "execution_count": len(logs),
        }
