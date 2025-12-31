"""
FastAPI application for LinkedIn AI Agent.

Provides REST endpoints for post generation.
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

logger = logging.getLogger(__name__)
settings = get_settings()

# In-memory state store (use Redis in production)
_generation_states: dict[str, AgentState] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting LinkedIn AI Agent API")
    db = get_db_manager()
    try:
        await db.create_tables()
    except Exception as e:
        logger.warning(f"Could not create tables: {e}")
    yield
    await db.close()
    logger.info("Shutting down LinkedIn AI Agent API")


app = FastAPI(
    title="LinkedIn AI Agent",
    description="Multi-agent AI system for LinkedIn content generation",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(posts_router)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health."""
    return HealthResponse(status="healthy", version="0.1.0")


@app.post("/api/v1/posts/generate")
async def generate_post(request: IdeaInput):
    """
    Start post generation from an idea.
    
    Returns clarifying questions that need to be answered.
    """
    post_id = str(uuid4())
    
    try:
        state = await run_generation(
            raw_idea=request.raw_idea,
            brand_profile={},
        )
        
        # Check if rejected
        if state.get("validator_output", {}).get("decision") == "REJECT":
            return {
                "post_id": post_id,
                "status": "rejected",
                "reason": state["validator_output"].get("reasoning"),
                "suggestions": state["validator_output"].get("refinement_suggestions", []),
            }
        
        # Store state for continuation
        _generation_states[post_id] = state
        
        return ClarifyingQuestionsResponse(
            post_id=post_id,
            questions=state.get("clarifying_questions", []),
            original_idea=request.raw_idea,
        )
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/posts/{post_id}/answers")
async def submit_answers(post_id: str, request: SubmitAnswersRequest):
    """
    Submit answers to clarifying questions and complete generation.
    """
    if post_id not in _generation_states:
        raise HTTPException(status_code=404, detail="Post not found")
    
    state = _generation_states[post_id]
    
    # Convert answers to dict
    answers = {a.question_id: a.answer for a in request.answers}
    
    try:
        final_state = await continue_generation(state, answers)
        
        # Clean up
        del _generation_states[post_id]
        
        return {
            "post_id": post_id,
            "status": "completed",
            "post": final_state.get("final_post"),
            "execution_log": final_state.get("execution_log", []),
        }
        
    except Exception as e:
        logger.error(f"Continuation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/posts/{post_id}/status")
async def get_status(post_id: str):
    """Get generation status."""
    if post_id not in _generation_states:
        return GenerationStatusResponse(
            post_id=post_id,
            status="completed",
            progress_percent=100,
        )
    
    state = _generation_states[post_id]
    return GenerationStatusResponse(
        post_id=post_id,
        status=state.get("status", "processing"),
        current_agent=state.get("current_agent"),
        progress_percent=50 if state.get("status") == "awaiting_answers" else 25,
    )
