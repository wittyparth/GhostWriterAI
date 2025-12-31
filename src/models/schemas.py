"""
Pydantic schemas for request/response validation and serialization.

These schemas are used for:
- API request/response validation
- Internal data transfer between components
- Agent input/output structures
"""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# ============================================
# Base Schemas
# ============================================

class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,  # Allow ORM model conversion
        str_strip_whitespace=True,
    )


# ============================================
# User & Brand Schemas
# ============================================

class BrandProfileCreate(BaseSchema):
    """Schema for creating a brand profile."""
    
    content_pillars: list[str] = Field(
        default_factory=list,
        description="Main content topics/themes",
        examples=[["Building in Public", "SaaS Marketing", "Startup Lessons"]],
    )
    target_audience: str | None = Field(
        default=None,
        description="Description of target audience",
        examples=["Tech founders, product managers, and startup operators"],
    )
    brand_voice: str | None = Field(
        default=None,
        description="Tone and style of writing",
        examples=["Conversational, data-driven, authentic with occasional humor"],
    )
    unique_positioning: str | None = Field(
        default=None,
        description="What makes this brand unique",
    )


class BrandProfileResponse(BrandProfileCreate):
    """Schema for brand profile response."""
    
    profile_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime | None = None


class UserCreate(BaseSchema):
    """Schema for creating a user."""
    
    name: str = Field(..., min_length=1, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    linkedin_profile_url: str | None = None


class UserResponse(UserCreate):
    """Schema for user response."""
    
    user_id: UUID
    created_at: datetime
    brand_profile: BrandProfileResponse | None = None


# ============================================
# Post Generation Schemas
# ============================================

class IdeaInput(BaseSchema):
    """Schema for submitting a new idea for content generation."""
    
    raw_idea: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="The raw idea or topic for the LinkedIn post",
        examples=["3 lessons I learned from failing my first startup"],
    )
    preferred_format: Literal["text", "carousel", "video", "auto"] | None = Field(
        default="auto",
        description="Preferred post format (auto lets AI decide)",
    )
    content_pillar: str | None = Field(
        default=None,
        description="Content pillar this belongs to",
    )


class ClarifyingQuestion(BaseSchema):
    """A single clarifying question from the strategist."""
    
    question_id: str = Field(..., description="Unique identifier for the question")
    question: str = Field(..., description="The question text")
    rationale: str = Field(..., description="Why this question matters")
    required: bool = Field(default=True)


class ClarifyingQuestionsResponse(BaseSchema):
    """Response containing clarifying questions."""
    
    post_id: UUID
    questions: list[ClarifyingQuestion]
    original_idea: str


class QuestionAnswer(BaseSchema):
    """Answer to a clarifying question."""
    
    question_id: str
    answer: str


class SubmitAnswersRequest(BaseSchema):
    """Request to submit answers to clarifying questions."""
    
    answers: list[QuestionAnswer]


# ============================================
# Generated Content Schemas
# ============================================

class HookVariation(BaseSchema):
    """A generated hook variation."""
    
    version: int = Field(..., ge=1, le=5)
    text: str
    hook_type: str
    score: float = Field(..., ge=0, le=10)
    reasoning: str


class VisualSlide(BaseSchema):
    """Specification for a carousel slide."""
    
    slide_number: int
    layout: str
    headline: str
    body_text: str | None = None
    image_description: str | None = None
    design_notes: str | None = None


class VisualSpecs(BaseSchema):
    """Visual specifications for carousel/image posts."""
    
    total_slides: int
    slides: list[VisualSlide]
    overall_style: str
    color_palette: list[str] = Field(default_factory=list)
    typography_notes: str | None = None


class GeneratedPost(BaseSchema):
    """Complete generated post with all components."""
    
    post_id: UUID
    format: Literal["text", "carousel", "video"]
    structure_type: str
    
    # Content
    hooks: list[HookVariation]
    recommended_hook_index: int = 0
    body_content: str
    cta: str
    hashtags: list[str] = Field(default_factory=list)
    
    # Visual specs (for carousel)
    visual_specs: VisualSpecs | None = None
    
    # Metadata
    quality_score: float
    brand_consistency_score: float
    predicted_impressions: tuple[int, int] | None = None
    predicted_engagement_rate: float | None = None
    
    # Suggestions
    optimization_suggestions: list[str] = Field(default_factory=list)


class PostResponse(BaseSchema):
    """Full post response including status and metadata."""
    
    post_id: UUID
    user_id: UUID
    raw_idea: str
    status: str
    format: str | None = None
    final_content: str | None = None
    
    # Generated content
    generated: GeneratedPost | None = None
    
    # Performance (if published)
    impressions: int | None = None
    engagement_rate: float | None = None
    
    created_at: datetime
    published_at: datetime | None = None


# ============================================
# Agent Schemas
# ============================================

class ValidatorOutput(BaseSchema):
    """Output from the Validator agent."""
    
    decision: Literal["APPROVE", "REFINE", "REJECT"]
    quality_score: float = Field(..., ge=0, le=10)
    reasoning: str
    concerns: list[str] = Field(default_factory=list)
    brand_alignment_score: float = Field(..., ge=0, le=10)
    refinement_suggestions: list[str] = Field(default_factory=list)


class StrategistOutput(BaseSchema):
    """Output from the Strategist agent."""
    
    recommended_format: Literal["text", "carousel", "video"]
    format_reasoning: str
    structure_type: str
    hook_types: list[str]
    psychological_triggers: list[str]
    tone: str
    clarifying_questions: list[ClarifyingQuestion]
    similar_posts: list[dict[str, Any]] = Field(default_factory=list)


class WriterOutput(BaseSchema):
    """Output from the Writer agent."""
    
    hooks: list[HookVariation]
    body_content: str
    cta: str
    hashtags: list[str]
    formatting_metadata: dict[str, Any] = Field(default_factory=dict)


class VisualOutput(BaseSchema):
    """Output from the Visual Specialist agent."""
    
    visual_specs: VisualSpecs
    image_prompts: list[str] = Field(default_factory=list)


class OptimizerOutput(BaseSchema):
    """Output from the Optimizer agent."""
    
    decision: Literal["APPROVE", "REVISE"]
    quality_score: float = Field(..., ge=0, le=10)
    brand_consistency_score: float = Field(..., ge=0, le=10)
    formatting_issues: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    predicted_impressions_min: int
    predicted_impressions_max: int
    predicted_engagement_rate: float
    confidence: float = Field(..., ge=0, le=1)


# ============================================
# API Schemas
# ============================================

class HealthResponse(BaseSchema):
    """Health check response."""
    
    status: Literal["healthy", "unhealthy"]
    database: bool = True
    cache: bool = True
    llm: bool = True
    version: str = "0.1.0"


class ErrorResponse(BaseSchema):
    """Error response schema."""
    
    error: str
    detail: str | None = None
    error_code: str | None = None


class GenerationStatusResponse(BaseSchema):
    """Status of a generation request."""
    
    post_id: UUID
    status: Literal["pending", "processing", "awaiting_answers", "completed", "failed"]
    current_agent: str | None = None
    progress_percent: int = 0
    estimated_seconds_remaining: int | None = None
