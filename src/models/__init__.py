"""
Models Package - Pydantic schemas for validation and serialization.

Exports all schemas for API request/response and internal data transfer.
"""

from src.models.schemas import (
    # Base
    BaseSchema,
    # User & Brand
    UserCreate,
    UserResponse,
    BrandProfileCreate,
    BrandProfileResponse,
    # Post Generation
    IdeaInput,
    ClarifyingQuestion,
    ClarifyingQuestionsResponse,
    QuestionAnswer,
    SubmitAnswersRequest,
    # Generated Content
    HookVariation,
    VisualSlide,
    VisualSpecs,
    GeneratedPost,
    PostResponse,
    # Agent Outputs
    ValidatorOutput,
    StrategistOutput,
    WriterOutput,
    VisualOutput,
    OptimizerOutput,
    # API
    HealthResponse,
    ErrorResponse,
    GenerationStatusResponse,
)

__all__ = [
    "BaseSchema",
    "UserCreate",
    "UserResponse",
    "BrandProfileCreate",
    "BrandProfileResponse",
    "IdeaInput",
    "ClarifyingQuestion",
    "ClarifyingQuestionsResponse",
    "QuestionAnswer",
    "SubmitAnswersRequest",
    "HookVariation",
    "VisualSlide",
    "VisualSpecs",
    "GeneratedPost",
    "PostResponse",
    "ValidatorOutput",
    "StrategistOutput",
    "WriterOutput",
    "VisualOutput",
    "OptimizerOutput",
    "HealthResponse",
    "ErrorResponse",
    "GenerationStatusResponse",
]
