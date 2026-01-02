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
        default="gemini-2.0-flash",
        description="Gemini model to use for generation (free tier: gemini-1.5-flash)",
    )
    embedding_model: str = Field(
        default="text-embedding-004",
        description="Gemini embedding model for vector operations",
    )
    
    # ========== Database Configuration ==========
    # Made optional with SQLite fallback for development
    database_url: SecretStr | None = Field(
        default=None,
        description="PostgreSQL connection string (optional, uses SQLite if not provided)",
    )
    
    # ========== Redis Configuration ==========
    redis_url: str | None = Field(
        default=None,
        description="Redis connection URL for caching (optional, uses in-memory if not provided)",
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
    
    # ========== Authentication ==========
    jwt_secret: str = Field(
        default="development-secret-key-change-in-production",
        description="Secret key for JWT token signing",
    )
    frontend_url: str = Field(
        default="http://localhost:5173",
        description="Frontend application URL for CORS",
    )
    google_client_id: str | None = Field(
        default=None,
        description="Google OAuth Client ID",
    )
    google_client_secret: str | None = Field(
        default=None,
        description="Google OAuth Client Secret",
    )
    google_redirect_uri: str = Field(
        default="http://localhost:8000/api/v1/auth/google/callback",
        description="Google OAuth Redirect URI",
    )
    
    # ========== Email Configuration (SMTP) ==========
    smtp_host: str = Field(
        default="smtp-relay.brevo.com",
        description="SMTP Server Host",
    )
    smtp_port: int = Field(
        default=587,
        description="SMTP Server Port",
    )
    smtp_user: str | None = Field(
        default=None,
        description="SMTP Username (Login)",
    )
    smtp_password: SecretStr | None = Field(
        default=None,
        description="SMTP Password",
    )
    from_email: str = Field(
        default="onboarding@resend.dev",
        description="Sender email address",
    )
    
    # ========== Cost Management ==========
    daily_cost_budget: float = Field(
        default=10.0,
        description="Daily cost budget in USD",
    )
    free_tier_daily_limit: int = Field(
        default=5,
        description="Daily post generation limit for free tier users",
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
    def use_sqlite(self) -> bool:
        """Check if using SQLite (no database URL or development mode)."""
        if self.database_url is None:
            return True
        # Check if it's explicitly a SQLite URL
        url = self.database_url.get_secret_value()
        return url.startswith("sqlite")

    @property
    def database_url_async(self) -> str:
        """Get async database URL for SQLAlchemy."""
        if self.database_url is None:
            # Use SQLite for development
            return "sqlite+aiosqlite:///./data/linkedin_ai.db"
        
        url = self.database_url.get_secret_value()
        
        # Handle SQLite URLs
        if url.startswith("sqlite"):
            if "+aiosqlite" not in url:
                return url.replace("sqlite://", "sqlite+aiosqlite://", 1)
            return url
        
        # Convert postgresql:// to postgresql+asyncpg:// for async support
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def database_url_sync(self) -> str:
        """Get sync database URL for migrations."""
        if self.database_url is None:
            # Use SQLite for development
            return "sqlite:///./data/linkedin_ai.db"
        
        url = self.database_url.get_secret_value()
        
        # Handle SQLite URLs
        if url.startswith("sqlite"):
            # Remove async driver for sync operations
            return url.replace("+aiosqlite", "")
        
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
