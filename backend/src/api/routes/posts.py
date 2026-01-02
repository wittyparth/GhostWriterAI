"""
Post generation API routes.

Endpoints for creating and managing LinkedIn posts.
"""

import logging
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.database.models import User, Post
from src.database.repositories.base import PostRepository, UserRepository, BrandProfileRepository
from src.api.routes.auth import get_current_user
from src.models.schemas import (
    IdeaInput,
    SubmitAnswersRequest,
    ClarifyingQuestionsResponse,
    PostResponse,
    GenerationStatusResponse,
)
from src.orchestration import run_generation, continue_generation, AgentState

from sqlalchemy import select, func

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/posts", tags=["posts"])

@router.get("/analytics")
async def get_analytics(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Get analytics summary."""
    # Total Posts
    stmt = select(func.count()).select_from(Post).where(Post.user_id == user.user_id)
    total_posts = (await session.execute(stmt)).scalar() or 0
    
    # Avg Quality Score
    stmt = select(func.avg(Post.quality_score)).where(Post.user_id == user.user_id)
    avg_score = (await session.execute(stmt)).scalar() or 0.0

    # Format Distribution
    stmt = select(Post.format, func.count()).where(Post.user_id == user.user_id).group_by(Post.format)
    formats = (await session.execute(stmt)).all()
    format_distribution = [{"name": f or "Unknown", "value": c} for f, c in formats]

    # Status Distribution
    stmt = select(Post.status, func.count()).where(Post.user_id == user.user_id).group_by(Post.status)
    statuses = (await session.execute(stmt)).all()
    status_distribution = [{"status": s or "Unknown", "count": c} for s, c in statuses]
    
    return {
        "total_posts": total_posts,
        "avg_quality_score": round(avg_score, 1) if avg_score else 0.0,
        "total_impressions": 0,
        "engagement_rate": 0.0,
        "format_distribution": format_distribution,
        "status_distribution": status_distribution,
    }

# In-memory state store (use Redis in production)
_generation_states: dict[str, AgentState] = {}


from src.config.settings import get_settings

@router.post("/generate", response_model=ClarifyingQuestionsResponse)
async def generate_post(
    request: IdeaInput,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """
    Start post generation from an idea.
    
    Returns clarifying questions that need to be answered.
    """
    # Check rate limit
    settings = get_settings()
    
    # Determine limit
    limit = settings.free_tier_daily_limit
    if getattr(user, "subscription_tier", "free") == "premium":
        limit = 1000
        
    post_repo = PostRepository(session)
    count = await post_repo.count_today(user.user_id)
    if count >= limit:
        raise HTTPException(
            status_code=429,
            detail=f"Daily limit reached. Limit is {limit} posts per day."
        )
        
    post_id = str(uuid4())
    
    try:
        # Fetch user's brand profile from database
        from src.database.models import BrandProfile
        stmt = select(BrandProfile).where(BrandProfile.user_id == user.user_id)
        result = await session.execute(stmt)
        profile = result.scalar_one_or_none()
        
        brand_profile = {}
        if profile:
            brand_profile = {
                "professional_title": profile.professional_title,
                "industry": profile.industry,
                "years_of_experience": profile.years_of_experience,
                "company_name": profile.company_name,
                "content_pillars": profile.content_pillars or [],
                "target_audience": profile.target_audience,
                "audience_pain_points": profile.audience_pain_points or [],
                "desired_outcome": profile.desired_outcome,
                "expertise_areas": profile.expertise_areas or [],
                "brand_voice": profile.brand_voice,
                "writing_style": profile.writing_style,
                "personality_traits": profile.personality_traits or [],
                "words_to_use": profile.words_to_use or [],
                "words_to_avoid": profile.words_to_avoid or [],
                "sample_posts": profile.sample_posts or [],
                "tone_preferences": profile.tone_preferences or {},
                "primary_goal": profile.primary_goal,
                "unique_positioning": profile.unique_positioning,
                "unique_story": profile.unique_story,
                "unique_perspective": profile.unique_perspective,
                "achievements": profile.achievements or [],
                "personal_experiences": profile.personal_experiences or [],
            }
        
        state = await run_generation(
            raw_idea=request.raw_idea,
            brand_profile=brand_profile,
        )
        
        # Check if rejected
        validator_output = state.get("validator_output", {})
        if validator_output.get("decision") == "REJECT":
            raise HTTPException(
                status_code=422,
                detail={
                    "status": "rejected",
                    "reason": validator_output.get("reasoning"),
                    "quality_score": validator_output.get("quality_score"),
                    "suggestions": validator_output.get("refinement_suggestions", []),
                }
            )
        
        # Store state for continuation
        _generation_states[post_id] = state
        
        return ClarifyingQuestionsResponse(
            post_id=UUID(post_id),
            questions=state.get("clarifying_questions", []),
            original_idea=request.raw_idea,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{post_id}/answers")
async def submit_answers(
    post_id: str,
    request: SubmitAnswersRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Submit answers to clarifying questions and complete generation.
    """
    if post_id not in _generation_states:
        raise HTTPException(status_code=404, detail="Post not found or expired")
    
    state = _generation_states[post_id]
    
    # Convert answers to dict
    answers = {a.question_id: a.answer for a in request.answers}
    
    try:
        final_state = await continue_generation(state, answers)
        
        # Clean up state
        del _generation_states[post_id]
        
        # Save to database
        post_repo = PostRepository(session)
        post = await post_repo.create(
            raw_idea=state["raw_idea"],
            final_content=_build_final_content(final_state.get("final_post", {})),
            format=final_state.get("format", "text"),
            status="completed",
            hooks_generated=final_state.get("writer_output", {}).get("hooks", []),
            visual_specs=final_state.get("visual_specs"),
            quality_score=final_state.get("optimizer_output", {}).get("quality_score"),
        )
        
        return {
            "post_id": post_id,
            "status": "completed",
            "post": final_state.get("final_post"),
            "quality_score": final_state.get("optimizer_output", {}).get("quality_score"),
            "predicted_engagement": final_state.get("optimizer_output", {}).get("predicted_engagement_rate"),
        }
        
    except Exception as e:
        logger.error(f"Continuation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{post_id}/status", response_model=GenerationStatusResponse)
async def get_status(post_id: str):
    """Get generation status."""
    if post_id not in _generation_states:
        return GenerationStatusResponse(
            post_id=UUID(post_id),
            status="completed",
            progress_percent=100,
        )
    
    state = _generation_states[post_id]
    return GenerationStatusResponse(
        post_id=UUID(post_id),
        status=state.get("status", "processing"),
        current_agent=state.get("current_agent"),
        progress_percent=50 if state.get("status") == "awaiting_answers" else 25,
    )


@router.get("/{post_id}")
async def get_post(
    post_id: str,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Get a generated post by ID."""
    post_repo = PostRepository(session)
    post = await post_repo.get_by_id(UUID(post_id))
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this post")
    
    return {
        "post_id": str(post.post_id),
        "raw_idea": post.raw_idea,
        "final_content": post.final_content,
        "format": post.format,
        "status": post.status,
        "quality_score": post.quality_score,
        "created_at": post.created_at,
    }


@router.get("/")
async def list_posts(
    limit: int = 20,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """List all posts for the current user."""
    post_repo = PostRepository(session)
    posts = await post_repo.get_by_user_id(user.user_id, limit=limit, offset=offset)
    
    return {
        "posts": [
            {
                "post_id": str(p.post_id),
                "raw_idea": p.raw_idea, # Return full idea or truncated depending on frontend needs. Let's keep it full as frontend truncates via CSS mostly, but mockup showed full text. Actually, frontend PostHistoryPage shows "raw_idea".
                "format": p.format,
                "status": p.status,
                "quality_score": p.quality_score,
                "created_at": p.created_at,
            }
            for p in posts
        ],
        "count": len(posts),
    }


from src.database.repositories.history import GenerationHistoryRepository

# ... (keep existing imports, I will insert this one separately or grouped)

@router.delete("/{post_id}", status_code=204)
async def delete_post(
    post_id: str,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Delete a post."""
    post_repo = PostRepository(session)
    history_repo = GenerationHistoryRepository(session)
    post_uuid = UUID(post_id)
    
    # Check ownership
    post = await post_repo.get_by_id(post_uuid)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    # Delete history first (manual cascade)
    await history_repo.delete_by_post_id(post_uuid)
    
    await post_repo.delete_by_id(post_uuid)
    return None


def _build_final_content(final_post: dict) -> str:
    """Build final content string from post components."""
    hook = final_post.get("hook", {}).get("text", "")
    body = final_post.get("body", "")
    cta = final_post.get("cta", "")
    hashtags = final_post.get("hashtags", [])
    
    content = f"{hook}\n\n{body}\n\n{cta}"
    if hashtags:
        content += f"\n\n{' '.join('#' + h for h in hashtags)}"
    
    return content
