"""
Brand Profile API routes.

Provides endpoints for managing user brand profiles including:
- Create/update brand profile
- Get brand profile
- Manage content pillars
- Update voice settings
"""

import logging
from uuid import UUID, uuid4
from typing import Optional, Any

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.database.models import User, BrandProfile
from src.api.routes.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/brand-profile", tags=["brand-profile"])


# ============ Request/Response Schemas ============

class ContentPillar(BaseModel):
    id: str
    name: str
    description: str
    color: str


class VoiceTone(BaseModel):
    formality: int = Field(default=50, ge=0, le=100)
    humor: int = Field(default=50, ge=0, le=100)
    emotion: int = Field(default=50, ge=0, le=100)
    technicality: int = Field(default=50, ge=0, le=100)


class BrandProfileRequest(BaseModel):
    # Professional Context
    professional_title: Optional[str] = None
    industry: Optional[str] = None
    years_of_experience: Optional[int] = None
    company_name: Optional[str] = None
    linkedin_profile_url: Optional[str] = None
    
    # Content Strategy
    content_pillars: Optional[list[ContentPillar]] = None
    target_audience: Optional[str] = None
    audience_pain_points: Optional[list[str]] = None
    desired_outcome: Optional[str] = None
    expertise_areas: Optional[list[str]] = None
    
    # Voice & Personality
    brand_voice: Optional[str] = None
    writing_style: Optional[str] = None  # "story-driven", "data-focused", "contrarian"
    personality_traits: Optional[list[str]] = None
    words_to_use: Optional[list[str]] = None
    words_to_avoid: Optional[list[str]] = None
    sample_posts: Optional[list[str]] = None
    voice_tone: Optional[VoiceTone] = None
    
    # Goals & Metrics
    primary_goal: Optional[str] = None  # "thought_leadership", "lead_generation", "hiring"
    posting_frequency: Optional[str] = None
    ideal_engagement_type: Optional[str] = None
    
    # Differentiators
    unique_positioning: Optional[str] = None
    unique_story: Optional[str] = None
    unique_perspective: Optional[str] = None
    achievements: Optional[list[str]] = None
    personal_experiences: Optional[list[str]] = None
    
    # Visual
    brand_colors: Optional[list[str]] = None


class BrandProfileResponse(BaseModel):
    profile_id: str
    user_id: str
    
    # Professional Context
    professional_title: Optional[str] = None
    industry: Optional[str] = None
    years_of_experience: Optional[int] = None
    company_name: Optional[str] = None
    linkedin_profile_url: Optional[str] = None
    
    # Content Strategy
    content_pillars: list[ContentPillar]
    target_audience: Optional[str] = None
    audience_pain_points: list[str]
    desired_outcome: Optional[str] = None
    expertise_areas: list[str]
    
    # Voice & Personality
    brand_voice: Optional[str] = None
    writing_style: Optional[str] = None
    personality_traits: list[str]
    words_to_use: list[str]
    words_to_avoid: list[str]
    sample_posts: list[str]
    voice_tone: VoiceTone
    
    # Goals & Metrics
    primary_goal: Optional[str] = None
    posting_frequency: Optional[str] = None
    ideal_engagement_type: Optional[str] = None
    
    # Differentiators
    unique_positioning: Optional[str] = None
    unique_story: Optional[str] = None
    unique_perspective: Optional[str] = None
    achievements: list[str]
    personal_experiences: list[str]
    
    # Visual
    brand_colors: list[str]
    
    created_at: str
    updated_at: Optional[str] = None


class AddPillarRequest(BaseModel):
    name: str
    description: str
    color: str


# ============ Helper Functions ============

def _serialize_profile(profile: BrandProfile, user: User) -> dict:
    """Convert BrandProfile model to response dict."""
    content_pillars = profile.content_pillars or []
    tone_preferences = profile.tone_preferences or {}
    
    return {
        "profile_id": str(profile.profile_id),
        "user_id": str(profile.user_id),
        
        # Professional Context
        "professional_title": profile.professional_title,
        "industry": profile.industry,
        "years_of_experience": profile.years_of_experience,
        "company_name": profile.company_name,
        "linkedin_profile_url": profile.linkedin_profile_url,
        
        # Content Strategy
        "content_pillars": content_pillars,
        "target_audience": profile.target_audience,
        "audience_pain_points": profile.audience_pain_points or [],
        "desired_outcome": profile.desired_outcome,
        "expertise_areas": profile.expertise_areas or [],
        
        # Voice & Personality
        "brand_voice": profile.brand_voice,
        "writing_style": profile.writing_style,
        "personality_traits": profile.personality_traits or [],
        "words_to_use": profile.words_to_use or [],
        "words_to_avoid": profile.words_to_avoid or [],
        "sample_posts": profile.sample_posts or [],
        "voice_tone": {
            "formality": tone_preferences.get("formality", 50),
            "humor": tone_preferences.get("humor", 50),
            "emotion": tone_preferences.get("emotion", 50),
            "technicality": tone_preferences.get("technicality", 50),
        },
        
        # Goals & Metrics
        "primary_goal": profile.primary_goal,
        "posting_frequency": profile.posting_frequency,
        "ideal_engagement_type": profile.ideal_engagement_type,
        
        # Differentiators
        "unique_positioning": profile.unique_positioning,
        "unique_story": profile.unique_story,
        "unique_perspective": profile.unique_perspective,
        "achievements": profile.achievements or [],
        "personal_experiences": profile.personal_experiences or [],
        
        # Visual
        "brand_colors": profile.brand_colors or [],
        
        "created_at": profile.created_at.isoformat(),
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
    }


# ============ API Endpoints ============

@router.get("/")
async def get_brand_profile(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get the current user's brand profile.
    
    Returns 404 if no profile exists.
    """
    stmt = select(BrandProfile).where(BrandProfile.user_id == user.user_id)
    result = await session.execute(stmt)
    profile = result.scalar_one_or_none()
    
    if not profile:
        return None
    
    return _serialize_profile(profile, user)


@router.post("/")
async def create_brand_profile(
    request: BrandProfileRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new brand profile for the current user.
    
    Only one brand profile is allowed per user.
    """
    # Check if profile already exists
    stmt = select(BrandProfile).where(BrandProfile.user_id == user.user_id)
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand profile already exists. Use PUT to update."
        )
    
    # Create profile with all fields
    profile = BrandProfile(
        user_id=user.user_id,
        # Professional Context
        professional_title=request.professional_title,
        industry=request.industry,
        years_of_experience=request.years_of_experience,
        company_name=request.company_name,
        linkedin_profile_url=request.linkedin_profile_url,
        # Content Strategy
        content_pillars=[p.model_dump() for p in (request.content_pillars or [])],
        target_audience=request.target_audience,
        audience_pain_points=request.audience_pain_points or [],
        desired_outcome=request.desired_outcome,
        expertise_areas=request.expertise_areas or [],
        # Voice & Personality
        brand_voice=request.brand_voice,
        writing_style=request.writing_style,
        personality_traits=request.personality_traits or [],
        words_to_use=request.words_to_use or [],
        words_to_avoid=request.words_to_avoid or [],
        sample_posts=request.sample_posts or [],
        tone_preferences=request.voice_tone.model_dump() if request.voice_tone else {},
        # Goals & Metrics
        primary_goal=request.primary_goal,
        posting_frequency=request.posting_frequency,
        ideal_engagement_type=request.ideal_engagement_type,
        # Differentiators
        unique_positioning=request.unique_positioning,
        unique_story=request.unique_story,
        unique_perspective=request.unique_perspective,
        achievements=request.achievements or [],
        personal_experiences=request.personal_experiences or [],
        # Visual
        brand_colors=request.brand_colors or [],
    )
    
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    
    logger.info(f"Brand profile created for user {user.user_id}")
    
    return _serialize_profile(profile, user)


@router.put("/")
async def update_brand_profile(
    request: BrandProfileRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Update the current user's brand profile.
    
    Creates a new profile if one doesn't exist.
    """
    stmt = select(BrandProfile).where(BrandProfile.user_id == user.user_id)
    result = await session.execute(stmt)
    profile = result.scalar_one_or_none()
    
    if not profile:
        # Create new profile
        return await create_brand_profile(request, user, session)
    
    # Update Professional Context
    if request.professional_title is not None:
        profile.professional_title = request.professional_title
    if request.industry is not None:
        profile.industry = request.industry
    if request.years_of_experience is not None:
        profile.years_of_experience = request.years_of_experience
    if request.company_name is not None:
        profile.company_name = request.company_name
    if request.linkedin_profile_url is not None:
        profile.linkedin_profile_url = request.linkedin_profile_url
    
    # Update Content Strategy
    if request.content_pillars is not None:
        profile.content_pillars = [p.model_dump() for p in request.content_pillars]
    if request.target_audience is not None:
        profile.target_audience = request.target_audience
    if request.audience_pain_points is not None:
        profile.audience_pain_points = request.audience_pain_points
    if request.desired_outcome is not None:
        profile.desired_outcome = request.desired_outcome
    if request.expertise_areas is not None:
        profile.expertise_areas = request.expertise_areas
    
    # Update Voice & Personality
    if request.brand_voice is not None:
        profile.brand_voice = request.brand_voice
    if request.writing_style is not None:
        profile.writing_style = request.writing_style
    if request.personality_traits is not None:
        profile.personality_traits = request.personality_traits
    if request.words_to_use is not None:
        profile.words_to_use = request.words_to_use
    if request.words_to_avoid is not None:
        profile.words_to_avoid = request.words_to_avoid
    if request.sample_posts is not None:
        profile.sample_posts = request.sample_posts
    if request.voice_tone is not None:
        profile.tone_preferences = request.voice_tone.model_dump()
    
    # Update Goals & Metrics
    if request.primary_goal is not None:
        profile.primary_goal = request.primary_goal
    if request.posting_frequency is not None:
        profile.posting_frequency = request.posting_frequency
    if request.ideal_engagement_type is not None:
        profile.ideal_engagement_type = request.ideal_engagement_type
    
    # Update Differentiators
    if request.unique_positioning is not None:
        profile.unique_positioning = request.unique_positioning
    if request.unique_story is not None:
        profile.unique_story = request.unique_story
    if request.unique_perspective is not None:
        profile.unique_perspective = request.unique_perspective
    if request.achievements is not None:
        profile.achievements = request.achievements
    if request.personal_experiences is not None:
        profile.personal_experiences = request.personal_experiences
    
    # Update Visual
    if request.brand_colors is not None:
        profile.brand_colors = request.brand_colors
    
    await session.commit()
    await session.refresh(profile)
    
    logger.info(f"Brand profile updated for user {user.user_id}")
    
    return _serialize_profile(profile, user)


@router.post("/pillars")
async def add_content_pillar(
    request: AddPillarRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Add a new content pillar to the brand profile.
    """
    stmt = select(BrandProfile).where(BrandProfile.user_id == user.user_id)
    result = await session.execute(stmt)
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand profile not found. Create one first."
        )
    
    # Create new pillar
    new_pillar = {
        "id": str(uuid4()),
        "name": request.name,
        "description": request.description,
        "color": request.color,
    }
    
    pillars = profile.content_pillars or []
    pillars.append(new_pillar)
    profile.content_pillars = pillars
    
    await session.commit()
    
    return {"pillar": new_pillar, "total_pillars": len(pillars)}


@router.delete("/pillars/{pillar_id}")
async def remove_content_pillar(
    pillar_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Remove a content pillar from the brand profile.
    """
    stmt = select(BrandProfile).where(BrandProfile.user_id == user.user_id)
    result = await session.execute(stmt)
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand profile not found"
        )
    
    pillars = profile.content_pillars or []
    new_pillars = [p for p in pillars if p.get("id") != pillar_id]
    
    if len(new_pillars) == len(pillars):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pillar not found"
        )
    
    profile.content_pillars = new_pillars
    await session.commit()
    
    return {"message": "Pillar removed", "remaining_pillars": len(new_pillars)}


@router.patch("/voice")
async def update_voice_settings(
    request: VoiceTone,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Update the brand voice/tone settings.
    """
    stmt = select(BrandProfile).where(BrandProfile.user_id == user.user_id)
    result = await session.execute(stmt)
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand profile not found"
        )
    
    profile.tone_preferences = request.model_dump()
    await session.commit()
    
    return {"message": "Voice settings updated", "voice_tone": request.model_dump()}


@router.get("/summary")
async def get_profile_summary(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get a summary of the brand profile for use in generation.
    """
    stmt = select(BrandProfile).where(BrandProfile.user_id == user.user_id)
    result = await session.execute(stmt)
    profile = result.scalar_one_or_none()
    
    if not profile:
        return {
            "has_profile": False,
            "summary": "No brand profile configured",
        }
    
    pillars = profile.content_pillars or []
    pillar_names = [p.get("name", "") for p in pillars if p.get("name")]
    
    tone = profile.tone_preferences or {}
    tone_desc = []
    if tone.get("formality", 50) > 60:
        tone_desc.append("professional")
    elif tone.get("formality", 50) < 40:
        tone_desc.append("casual")
    if tone.get("humor", 50) > 60:
        tone_desc.append("playful")
    if tone.get("emotion", 50) > 60:
        tone_desc.append("empathetic")
    if tone.get("technicality", 50) > 60:
        tone_desc.append("technical")
    
    return {
        "has_profile": True,
        "name": user.name,
        "content_pillars": pillar_names,
        "target_audience": profile.target_audience,
        "voice_description": ", ".join(tone_desc) if tone_desc else "balanced",
        "summary": f"Content creator focusing on {', '.join(pillar_names[:3])}. Target audience: {profile.target_audience or 'general audience'}. Voice: {', '.join(tone_desc) if tone_desc else 'balanced'}.",
    }
