"""
SQLAlchemy database models for LinkedIn AI Agent.

Models:
- User: User profiles
- BrandProfile: Content pillars, voice, audience
- Post: Generated posts with performance data
- ReferencePost: Knowledge base posts
- AgentExecution: Execution logs and costs
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class User(Base):
    """User profile table."""
    
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    linkedin_profile_url = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    brand_profile = relationship("BrandProfile", back_populates="user", uselist=False)
    posts = relationship("Post", back_populates="user")


class BrandProfile(Base):
    """Brand profile for user's content strategy."""
    
    __tablename__ = "brand_profiles"
    
    profile_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), unique=True, nullable=False)
    
    # Content strategy
    content_pillars = Column(JSONB, default=list)  # ["Building in Public", "SaaS Marketing"]
    target_audience = Column(Text, nullable=True)
    brand_voice = Column(Text, nullable=True)  # "Conversational, data-driven, authentic"
    tone_preferences = Column(JSONB, default=dict)
    unique_positioning = Column(Text, nullable=True)
    
    # Visual guidelines
    visual_guidelines = Column(JSONB, default=dict)
    brand_colors = Column(JSONB, default=list)  # ["#1E3A8A", "#FBBF24"]
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="brand_profile")


class Post(Base):
    """Generated LinkedIn posts."""
    
    __tablename__ = "posts"
    
    post_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    
    # Content
    raw_idea = Column(Text, nullable=False)
    final_content = Column(Text, nullable=True)
    format = Column(String(50), nullable=True)  # text, carousel, video
    status = Column(String(50), default="draft")  # draft, approved, published
    
    # Strategy metadata
    structure_type = Column(String(100), nullable=True)
    tone = Column(String(100), nullable=True)
    content_pillar = Column(String(100), nullable=True)
    hook_type = Column(String(100), nullable=True)
    
    # Generated content details
    hooks_generated = Column(JSONB, default=list)  # [{version, text, score, reasoning}]
    selected_hook_index = Column(Integer, nullable=True)
    visual_specs = Column(JSONB, default=dict)  # Carousel/image specifications
    
    # Performance data (filled after publishing)
    impressions = Column(Integer, nullable=True)
    engagement_rate = Column(Float, nullable=True)
    comments_count = Column(Integer, nullable=True)
    reactions_count = Column(Integer, nullable=True)
    shares_count = Column(Integer, nullable=True)
    saves_count = Column(Integer, nullable=True)
    
    # AI metadata
    quality_score = Column(Float, nullable=True)
    predicted_impressions_min = Column(Integer, nullable=True)
    predicted_impressions_max = Column(Integer, nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Versioning
    generation_version = Column(Integer, default=1)
    optimization_suggestions = Column(JSONB, default=list)
    
    # Timestamps
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="posts")
    executions = relationship("AgentExecution", back_populates="post")


class ReferencePost(Base):
    """Knowledge base of successful LinkedIn posts."""
    
    __tablename__ = "reference_posts"
    
    ref_post_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Source info
    source = Column(String(50), default="manual")  # scraped, manual, user_generated
    creator_name = Column(String(255), nullable=True)
    creator_profile_url = Column(Text, nullable=True)
    original_url = Column(Text, nullable=True)
    
    # Content
    content = Column(Text, nullable=False)
    format = Column(String(50), nullable=True)
    structure_type = Column(String(100), nullable=True)
    hook_type = Column(String(100), nullable=True)
    hook_text = Column(Text, nullable=True)
    
    # Engagement metrics
    impressions = Column(Integer, nullable=True)
    engagement_rate = Column(Float, nullable=True)
    comments_count = Column(Integer, nullable=True)
    reactions_count = Column(Integer, nullable=True)
    
    # Classification
    niche = Column(String(100), nullable=True)
    content_pillar = Column(String(100), nullable=True)
    psychological_triggers = Column(JSONB, default=list)
    tone = Column(String(100), nullable=True)
    
    # Analysis
    hook_score = Column(Float, nullable=True)
    value_density_score = Column(Float, nullable=True)
    why_it_works = Column(Text, nullable=True)
    replicable_pattern = Column(Text, nullable=True)
    
    # Vector embedding (stored as reference, actual vectors in vector DB)
    embedding_id = Column(String(255), nullable=True)  # ID in vector database
    
    # Timestamps
    original_post_date = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AgentExecution(Base):
    """Logs for agent executions."""
    
    __tablename__ = "agent_executions"
    
    execution_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.post_id"), nullable=True)
    
    # Agent info
    agent_name = Column(String(100), nullable=False)
    model_used = Column(String(100), nullable=True)
    
    # Input/Output
    input_data = Column(JSONB, default=dict)
    output_data = Column(JSONB, default=dict)
    
    # Metrics
    execution_time_ms = Column(Integer, nullable=True)
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    cost_usd = Column(Float, nullable=True)
    
    # Status
    status = Column(String(50), default="success")  # success, error, timeout
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    post = relationship("Post", back_populates="executions")


class UserFeedback(Base):
    """User feedback on generated content."""
    
    __tablename__ = "user_feedback"
    
    feedback_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.post_id"), nullable=False)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("agent_executions.execution_id"), nullable=True)
    
    feedback_type = Column(String(50), nullable=False)  # rating, iteration_request, approval
    rating = Column(Integer, nullable=True)  # 1-5
    comments = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
