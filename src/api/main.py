"""
FastAPI application for LinkedIn AI Agent.

Provides REST endpoints for post generation with rate limiting and health checks.
"""

import logging
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import get_settings
from src.database import get_db_manager
from src.models.schemas import (
    IdeaInput,
    SubmitAnswersRequest,
    ClarifyingQuestionsResponse,
    GeneratedPost,
    HealthResponse,
    ErrorResponse,
    GenerationStatusResponse,
)
from src.orchestration import run_generation, continue_generation, AgentState
from src.api.routes.posts import router as posts_router
from src.api.middleware.rate_limit import RateLimitMiddleware
from src.services.health import get_health_service
from src.services.cache import get_cache_service

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting LinkedIn AI Agent API")
    
    # Initialize database
    db = get_db_manager()
    try:
        await db.create_tables()
        logger.info("Database tables ready")
    except Exception as e:
        logger.warning(f"Could not create tables: {e}")
    
    # Initialize cache
    cache = get_cache_service()
    try:
        await cache.connect()
        logger.info("Cache connected")
    except Exception as e:
        logger.warning(f"Could not connect to cache: {e}")
    
    yield
    
    # Cleanup
    await db.close()
    await cache.disconnect()
    logger.info("Shutting down LinkedIn AI Agent API")


app = FastAPI(
    title="LinkedIn AI Agent",
    description="Multi-agent AI system for LinkedIn content generation powered by Google Gemini",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware, requests_per_minute=30)

# Include routers
app.include_router(posts_router)


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health_check():
    """
    Basic health check endpoint.
    
    Returns simple status without checking dependencies.
    """
    return HealthResponse(status="healthy", version="0.1.0")


@app.get("/health/detailed", tags=["system"])
async def detailed_health_check():
    """
    Detailed health check with all component statuses.
    
    Checks database, cache, and LLM connectivity.
    """
    health_service = get_health_service()
    result = await health_service.check_all()
    
    return {
        "status": result.status,
        "version": result.version,
        "components": [
            {
                "name": c.name,
                "status": c.status,
                "message": c.message,
                "latency_ms": c.latency_ms,
            }
            for c in result.components
        ],
    }


@app.get("/", tags=["system"])
async def root():
    """API root endpoint."""
    return {
        "name": "LinkedIn AI Agent",
        "version": "0.1.0",
        "description": "Multi-agent AI system for LinkedIn content generation",
        "docs": "/docs",
        "health": "/health",
    }
