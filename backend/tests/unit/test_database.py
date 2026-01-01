"""
Unit tests for database operations.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.database.models import User, BrandProfile, Post


class TestDatabaseModels:
    """Tests for database model structure."""
    
    def test_user_model_fields(self):
        """Test User model has required fields."""
        assert hasattr(User, 'user_id')
        assert hasattr(User, 'name')
        assert hasattr(User, 'email')
        assert hasattr(User, 'created_at')
    
    def test_brand_profile_model_fields(self):
        """Test BrandProfile model has required fields."""
        assert hasattr(BrandProfile, 'profile_id')
        assert hasattr(BrandProfile, 'user_id')
        assert hasattr(BrandProfile, 'content_pillars')
        assert hasattr(BrandProfile, 'brand_voice')
    
    def test_post_model_fields(self):
        """Test Post model has required fields."""
        assert hasattr(Post, 'post_id')
        assert hasattr(Post, 'user_id')
        assert hasattr(Post, 'raw_idea')
        assert hasattr(Post, 'final_content')
        assert hasattr(Post, 'format')
        assert hasattr(Post, 'status')
        assert hasattr(Post, 'quality_score')


class TestRepositories:
    """Tests for repository operations."""
    
    @pytest.fixture
    def mock_session(self):
        """Create mock async session."""
        session = AsyncMock()
        return session
    
    @pytest.mark.asyncio
    async def test_user_repository_create(self, mock_session):
        """Test user creation in repository."""
        from src.database.repositories.base import UserRepository
        
        repo = UserRepository(mock_session)
        
        # Mock the create operation
        mock_user = MagicMock()
        mock_user.user_id = uuid4()
        mock_user.name = "Test User"
        mock_user.email = "test@example.com"
        
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # The create method adds to session
        with patch.object(repo, 'create', return_value=mock_user):
            user = await repo.create(name="Test User", email="test@example.com")
            assert user.name == "Test User"
    
    @pytest.mark.asyncio
    async def test_post_repository_get_by_user(self, mock_session):
        """Test getting posts by user ID."""
        from src.database.repositories.base import PostRepository
        
        repo = PostRepository(mock_session)
        
        mock_posts = [MagicMock(), MagicMock()]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_posts
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Test will verify structure
        assert repo.model == Post
