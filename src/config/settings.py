"""
Application settings using Pydantic Settings.

Load configuration from environment variables with validation.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ========== Gemini API Configuration ==========
    gemini_api_key: SecretStr = Field(
        ...,
        description="Google Gemini API key from AI Studio",
    )
    
    # Model configuration
    gemini_model: str = Field(
        default="gemini-3-flash-preview",
        description="Gemini model to use for generation",
    )
    embedding_model: str = Field(
        default="text-embedding-004",
        description="Gemini embedding model for vector operations",
    )
    
    # ========== Database Configuration ==========
    database_url: SecretStr = Field(
        ...,
        description="PostgreSQL connection string",
    )
    
    # ========== Redis Configuration ==========
    redis_url: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL for caching",
    )
    
    # ========== Vector Store Configuration ==========
    chromadb_path: str = Field(
        default="./data/chromadb",
        description="Path for local ChromaDB storage",
    )
    pinecone_api_key: SecretStr | None = Field(
        default=None,
        description="Pinecone API key (optional, for production)",
    )
    pinecone_index_name: str = Field(
        default="linkedin-posts",
        description="Pinecone index name",
    )
    
    # ========== Application Settings ==========
    app_env: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment",
    )
    debug: bool = Field(
        default=True,
        description="Enable debug mode",
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging level",
    )
    
    # ========== API Settings ==========
    api_host: str = Field(
        default="0.0.0.0",
        description="API server host",
    )
    api_port: int = Field(
        default=8000,
        description="API server port",
    )
    api_rate_limit: int = Field(
        default=10,
        description="Requests per minute per user",
    )
    
    # ========== Cost Management ==========
    daily_cost_budget: float = Field(
        default=10.0,
        description="Daily cost budget in USD",
    )
    
    # ========== Agent Configuration ==========
    max_agent_retries: int = Field(
        default=3,
        description="Maximum retries for failed agent calls",
    )
    agent_timeout_seconds: int = Field(
        default=60,
        description="Timeout for agent execution",
    )
    max_generation_iterations: int = Field(
        default=2,
        description="Maximum revision iterations for optimization",
    )

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env == "production"

    @property
    def database_url_async(self) -> str:
        """Get async database URL for SQLAlchemy."""
        url = self.database_url.get_secret_value()
        # Convert postgresql:// to postgresql+asyncpg:// for async support
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def database_url_sync(self) -> str:
        """Get sync database URL for migrations."""
        url = self.database_url.get_secret_value()
        # Ensure it's the standard postgresql:// format
        if url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql+asyncpg://", "postgresql://", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    Returns:
        Settings instance (cached for performance)
    """
    return Settings()
