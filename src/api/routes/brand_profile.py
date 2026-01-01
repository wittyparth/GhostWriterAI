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
    name: Optional[str] = None
    title: Optional[str] = None
    bio: Optional[str] = None
    content_pillars: Optional[list[ContentPillar]] = None
    target_audience: Optional[str] = None
    voice_tone: Optional[VoiceTone] = None
    brand_colors: Optional[list[str]] = None


class BrandProfileResponse(BaseModel):
    profile_id: str
    user_id: str
    name: str
    title: Optional[str] = None
    bio: Optional[str] = None
    content_pillars: list[ContentPillar]
    target_audience: Optional[str] = None
    voice_tone: VoiceTone
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
        "name": user.name,
        "title": profile.unique_positioning,  # Using for title
        "bio": profile.brand_voice,  # Using for bio
        "content_pillars": content_pillars,
        "target_audience": profile.target_audience,
        "voice_tone": {
            "formality": tone_preferences.get("formality", 50),
            "humor": tone_preferences.get("humor", 50),
            "emotion": tone_preferences.get("emotion", 50),
            "technicality": tone_preferences.get("technicality", 50),
        },
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand profile not found. Create one first."
        )
    
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
    
    # Update user name if provided
    if request.name:
        user.name = request.name
    
    # Create profile
    profile = BrandProfile(
        user_id=user.user_id,
        content_pillars=[p.model_dump() for p in (request.content_pillars or [])],
        target_audience=request.target_audience,
        brand_voice=request.bio,
        unique_positioning=request.title,
        tone_preferences=request.voice_tone.model_dump() if request.voice_tone else {},
        brand_colors=request.brand_colors or [],
    )
    
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    await session.refresh(user)
    
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
    
    # Update fields
    if request.name:
        user.name = request.name
    
    if request.content_pillars is not None:
        profile.content_pillars = [p.model_dump() for p in request.content_pillars]
    
    if request.target_audience is not None:
        profile.target_audience = request.target_audience
    
    if request.bio is not None:
        profile.brand_voice = request.bio
    
    if request.title is not None:
        profile.unique_positioning = request.title
    
    if request.voice_tone is not None:
        profile.tone_preferences = request.voice_tone.model_dump()
    
    if request.brand_colors is not None:
        profile.brand_colors = request.brand_colors
    
    await session.commit()
    await session.refresh(profile)
    await session.refresh(user)
    
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
