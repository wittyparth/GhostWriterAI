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
    subscription_tier = Column(String(50), default="free", nullable=False)
    
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
    
    # ========== Professional Context ==========
    professional_title = Column(String(200), nullable=True)  # "Founder @ XYZ"
    industry = Column(String(100), nullable=True)  # "SaaS", "Healthcare", "FinTech"
    years_of_experience = Column(Integer, nullable=True)
    company_name = Column(String(200), nullable=True)
    linkedin_profile_url = Column(Text, nullable=True)
    
    # ========== Content Strategy ==========
    content_pillars = Column(JSONB, default=list)  # ["Building in Public", "SaaS Marketing"]
    target_audience = Column(Text, nullable=True)  # "B2B SaaS founders and marketers"
    audience_pain_points = Column(JSONB, default=list)  # ["scaling", "hiring", "fundraising"]
    desired_outcome = Column(Text, nullable=True)  # What action they want readers to take
    expertise_areas = Column(JSONB, default=list)  # ["growth hacking", "product management"]
    
    # ========== Voice & Personality ==========
    brand_voice = Column(Text, nullable=True)  # "Conversational, data-driven, authentic"
    writing_style = Column(String(50), nullable=True)  # "story-driven", "data-focused", "contrarian"
    personality_traits = Column(JSONB, default=list)  # ["witty", "empathetic", "direct"]
    words_to_use = Column(JSONB, default=list)  # Phrases they love
    words_to_avoid = Column(JSONB, default=list)  # Language to never use
    sample_posts = Column(JSONB, default=list)  # 3-5 of their best posts
    tone_preferences = Column(JSONB, default=dict)
    
    # ========== Goals & Metrics ==========
    primary_goal = Column(String(50), nullable=True)  # "thought_leadership", "lead_generation", "hiring"
    posting_frequency = Column(String(50), nullable=True)  # "daily", "3x_week", "weekly"
    ideal_engagement_type = Column(String(50), nullable=True)  # "comments", "shares", "dms"
    
    # ========== Differentiators ==========
    unique_positioning = Column(Text, nullable=True)
    unique_story = Column(Text, nullable=True)  # Their origin story/journey
    unique_perspective = Column(Text, nullable=True)  # What makes their take different
    achievements = Column(JSONB, default=list)  # ["Grew to $1M ARR", "Built 10k newsletter"]
    personal_experiences = Column(JSONB, default=list)  # Stories they can tell
    
    # ========== Visual (Optional) ==========
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


class GenerationHistory(Base):
    """
    Complete generation flow history for a post.
    
    Stores the entire flow from raw idea to final output,
    allowing users to revisit how any post was created.
    """
    
    __tablename__ = "generation_history"
    
    history_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.post_id"), nullable=False, unique=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    
    # ═══════════════════════════════════════════════════════════
    # INPUT DATA
    # ═══════════════════════════════════════════════════════════
    raw_idea = Column(Text, nullable=False)
    preferred_format = Column(String(50), nullable=True)  # auto, text, carousel, video
    brand_profile_snapshot = Column(JSONB, default=dict)  # Copy of brand profile at generation time
    
    # ═══════════════════════════════════════════════════════════
    # AGENT OUTPUTS (complete data from each agent)
    # ═══════════════════════════════════════════════════════════
    validator_output = Column(JSONB, default=dict)
    # {decision, quality_score, brand_alignment_score, reasoning, concerns, refinement_suggestions}
    
    strategist_output = Column(JSONB, default=dict)
    # {recommended_format, format_reasoning, structure_type, hook_types, psychological_triggers, 
    #  tone, clarifying_questions, similar_posts}
    
    writer_output = Column(JSONB, default=dict)
    # {hooks: [{version, text, hook_type, score, reasoning}], body_content, cta, hashtags, 
    #  formatting_metadata: {word_count, reading_time_seconds, line_count}}
    
    visual_output = Column(JSONB, default=dict)
    # {visual_specs: {total_slides, slides, overall_style, color_palette, typography_notes}, image_prompts}
    
    optimizer_output = Column(JSONB, default=dict)
    # {decision, quality_score, brand_consistency_score, formatting_issues, suggestions,
    #  predicted_impressions_min, predicted_impressions_max, predicted_engagement_rate, confidence}
    
    # ═══════════════════════════════════════════════════════════
    # USER INTERACTION
    # ═══════════════════════════════════════════════════════════
    clarifying_questions = Column(JSONB, default=list)
    # [{question_id, question, rationale, required}]
    
    user_answers = Column(JSONB, default=dict)
    # {question_id: answer_text, ...}
    
    # ═══════════════════════════════════════════════════════════
    # FINAL OUTPUT
    # ═══════════════════════════════════════════════════════════
    final_post = Column(JSONB, default=dict)
    # {format, hook, body, cta, hashtags, visual_specs, quality_score, predicted_impressions}
    
    selected_hook_index = Column(Integer, default=0)  # Which hook user selected (0-2)
    
    # ═══════════════════════════════════════════════════════════
    # EXECUTION METADATA
    # ═══════════════════════════════════════════════════════════
    status = Column(String(50), default="pending")
    # pending, processing, awaiting_answers, completed, failed, rejected
    
    total_execution_time_ms = Column(Integer, nullable=True)
    revision_count = Column(Integer, default=0)
    
    # Individual agent timing
    validator_time_ms = Column(Integer, nullable=True)
    strategist_time_ms = Column(Integer, nullable=True)
    writer_time_ms = Column(Integer, nullable=True)
    visual_time_ms = Column(Integer, nullable=True)
    optimizer_time_ms = Column(Integer, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    failed_agent = Column(String(100), nullable=True)
    
    # ═══════════════════════════════════════════════════════════
    # TIMESTAMPS
    # ═══════════════════════════════════════════════════════════
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    phase1_completed_at = Column(DateTime, nullable=True)  # After strategist
    answers_submitted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    post = relationship("Post", backref="history")
    events = relationship("GenerationEvent", back_populates="history", order_by="GenerationEvent.timestamp")


class GenerationEvent(Base):
    """
    Individual events during generation.
    
    Stores every event (agent_start, agent_complete, etc.) for the timeline view.
    """
    
    __tablename__ = "generation_events"
    
    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    history_id = Column(UUID(as_uuid=True), ForeignKey("generation_history.history_id"), nullable=False)
    
    # Event details
    event_type = Column(String(50), nullable=False)
    # agent_start, agent_complete, agent_error, status_update, complete
    
    agent_name = Column(String(100), nullable=False)
    # validator, strategist, writer, visual, optimizer, system
    
    message = Column(Text, nullable=False)
    # Human-readable message like "✅ Validator completed in 1234ms"
    
    # Event data
    execution_time_ms = Column(Integer, default=0)
    progress_percent = Column(Integer, default=0)
    
    # Output summary (for agent_complete events)
    output_summary = Column(Text, nullable=True)
    # e.g., "Decision: APPROVE | Quality Score: 8.5/10"
    
    decision = Column(String(50), nullable=True)
    # APPROVE, REJECT, REVISE, etc.
    
    score = Column(Float, nullable=True)
    # Quality score from agent
    
    # Full event data (JSON blob)
    event_data = Column(JSONB, default=dict)
    # Complete data including full agent output if applicable
    
    # Error info (for agent_error events)
    error_message = Column(Text, nullable=True)
    retry_attempt = Column(Integer, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    history = relationship("GenerationHistory", back_populates="events")

