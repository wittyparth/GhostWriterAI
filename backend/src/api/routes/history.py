"""
Generation History API routes.

Endpoints for retrieving and managing generation history.
Allows users to revisit how any post was created, seeing
all agent outputs, questions, answers, and timeline.
"""

import logging
from uuid import UUID
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import func, desc, cast, Float, text
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from src.database import get_session
from src.database.models import GenerationHistory, User
from src.api.routes.auth import get_current_user
from src.database.repositories import (
    GenerationHistoryRepository,
    GenerationEventRepository,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/history", tags=["history"])


# ═══════════════════════════════════════════════════════════════════════════
# Response Schemas
# ═══════════════════════════════════════════════════════════════════════════

class EventResponse(BaseModel):
    """Single event in the generation timeline."""
    event_id: str
    event_type: str
    agent_name: str
    message: str
    execution_time_ms: int
    progress_percent: int
    output_summary: str | None = None
    decision: str | None = None
    score: float | None = None
    event_data: dict = Field(default_factory=dict)
    error_message: str | None = None
    retry_attempt: int | None = None
    timestamp: datetime


class AgentOutputSummary(BaseModel):
    """Summary of an agent's output."""
    agent_name: str
    status: str
    execution_time_ms: int
    decision: str | None = None
    score: float | None = None
    summary: str | None = None
    has_output: bool = False


class GenerationHistoryListItem(BaseModel):
    """Brief history item for list view."""
    history_id: str
    post_id: str
    raw_idea: str
    status: str
    format: str | None = None
    quality_score: float | None = None
    total_execution_time_ms: int | None = None
    started_at: datetime
    completed_at: datetime | None = None


class GenerationHistoryDetail(BaseModel):
    """Complete generation history with all details."""
    history_id: str
    post_id: str
    
    # Input
    raw_idea: str
    preferred_format: str | None = None
    brand_profile_snapshot: dict = Field(default_factory=dict)
    
    # Agent Outputs
    validator_output: dict = Field(default_factory=dict)
    strategist_output: dict = Field(default_factory=dict)
    writer_output: dict = Field(default_factory=dict)
    visual_output: dict = Field(default_factory=dict)
    optimizer_output: dict = Field(default_factory=dict)
    
    # User Interaction
    clarifying_questions: list = Field(default_factory=list)
    user_answers: dict = Field(default_factory=dict)
    
    # Final Output
    final_post: dict = Field(default_factory=dict)
    selected_hook_index: int = 0
    
    # Execution Metadata
    status: str
    total_execution_time_ms: int | None = None
    revision_count: int = 0
    
    # Agent Timing
    validator_time_ms: int | None = None
    strategist_time_ms: int | None = None
    writer_time_ms: int | None = None
    visual_time_ms: int | None = None
    optimizer_time_ms: int | None = None
    
    # Error Info
    error_message: str | None = None
    failed_agent: str | None = None
    
    # Timestamps
    started_at: datetime
    phase1_completed_at: datetime | None = None
    answers_submitted_at: datetime | None = None
    completed_at: datetime | None = None
    
    # Timeline
    events: list[EventResponse] = Field(default_factory=list)
    
    # Computed summaries
    agents_summary: list[AgentOutputSummary] = Field(default_factory=list)


class GenerationHistoryListResponse(BaseModel):
    """Response for list of generation histories."""
    histories: list[GenerationHistoryListItem]
    total: int
    limit: int
    offset: int


# ═══════════════════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/", response_model=GenerationHistoryListResponse)
async def list_generation_histories(
    limit: int = 20,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """
    List all generation histories.
    
    Returns a paginated list of all post generations,
    useful for showing generation history in a dashboard.
    """
    repo = GenerationHistoryRepository(session)
    histories = await repo.get_by_user_id(user.user_id, limit=limit, offset=offset)
    
    items = []
    for h in histories:
        quality_score = None
        if h.optimizer_output:
            quality_score = h.optimizer_output.get("quality_score")
        
        items.append(GenerationHistoryListItem(
            history_id=str(h.history_id),
            post_id=str(h.post_id),
            raw_idea=h.raw_idea[:100] + "..." if len(h.raw_idea) > 100 else h.raw_idea,
            status=h.status,
            format=h.final_post.get("format") if h.final_post else None,
            quality_score=quality_score,
            total_execution_time_ms=h.total_execution_time_ms,
            started_at=h.started_at,
            completed_at=h.completed_at,
        ))
    
    return GenerationHistoryListResponse(
        histories=items,
        total=len(items),  # TODO: Add proper count query
        limit=limit,
        offset=offset,
    )


# ═══════════════════════════════════════════════════════════════════════════
# Analytics Endpoint
# ═══════════════════════════════════════════════════════════════════════════

class AnalyticsStats(BaseModel):
    total_posts: int
    completed_posts: int
    avg_quality_score: float
    posts_this_week: int

class AnalyticsChartData(BaseModel):
    date: str
    count: int = 0
    avg_score: float = 0.0

class AnalyticsResponse(BaseModel):
    stats: AnalyticsStats
    daily_activity: list[AnalyticsChartData]
    format_distribution: list[dict]
    status_distribution: list[dict]
    top_posts: list[dict]


@router.get("/stats", response_model=AnalyticsResponse)
async def get_analytics_stats(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """
    Get aggregated analytics data for the dashboard/analytics page.
    """
    from datetime import timedelta
    
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Base query for all visible history
    repo = GenerationHistoryRepository(session)
    
    # 1. Overview Stats
    # We'll use raw SQL for some complex aggregations to be efficient with JSONB
    # Note: SQLAlchemy's async session.execute supports raw SQL nicely.
    
    # Total Posts & Status Breakdown
    status_query = select(
        GenerationHistory.status, 
        func.count(GenerationHistory.history_id)
    ).where(
        GenerationHistory.user_id == user.user_id
    ).group_by(GenerationHistory.status)
    
    status_result = await session.execute(status_query)
    status_map = {row[0]: row[1] for row in status_result.all()}
    
    total_posts = sum(status_map.values())
    completed_posts = status_map.get("completed", 0)
    
    # Posts this week
    week_query = select(func.count(GenerationHistory.history_id)).where(
        GenerationHistory.started_at >= week_ago,
        GenerationHistory.user_id == user.user_id
    )
    week_result = await session.execute(week_query)
    posts_this_week = week_result.scalar() or 0
    
    # Average Quality Score (completed posts only)
    # Extract quality_score from optimizer_output JSON
    # Note: dependent on DB driver, but we'll try Python-side calculation for simpler robust code 
    # if dataset is small, or specific JSON operator if we want DB side.
    # Given typical volume, DB aggregation is better.
    # Using text() helper for JSON operator ->>
    avg_score_query = text("""
        SELECT AVG(CAST(optimizer_output->>'quality_score' AS FLOAT))
        FROM generation_history
        WHERE status = 'completed' 
        AND optimizer_output->>'quality_score' IS NOT NULL
        AND user_id = :user_id
    """)
    avg_score_result = await session.execute(avg_score_query, {"user_id": user.user_id})
    avg_quality_score = avg_score_result.scalar() or 0.0
    
    # 2. Daily Activity (Last 30 days)
    # Group by date
    daily_query = text("""
        SELECT 
            TO_CHAR(started_at, 'YYYY-MM-DD') as date_str,
            COUNT(*) as count,
            AVG(CAST(optimizer_output->>'quality_score' AS FLOAT)) as avg_score
        FROM generation_history
        WHERE started_at >= :month_ago
        AND user_id = :user_id
        GROUP BY date_str
        ORDER BY date_str ASC
    """)
    
    daily_result = await session.execute(daily_query, {"month_ago": month_ago, "user_id": user.user_id})
    daily_data = []
    
    # map results to daily_Activity
    rows = daily_result.fetchall()
    # Fill in missing days in frontend or here? Let's send available days.
    for row in rows:
        daily_data.append(AnalyticsChartData(
            date=row[0],
            count=row[1],
            avg_score=round(row[2] or 0, 1)
        ))
        
    # 3. Format Distribution
    # Use final_post->format or preferred_format
    format_query = text("""
        SELECT 
            COALESCE(final_post->>'format', preferred_format, 'unknown') as fmt,
            COUNT(*)
        FROM generation_history
        WHERE user_id = :user_id
        GROUP BY fmt
    """)
    format_result = await session.execute(format_query, {"user_id": user.user_id})
    format_dist = [{"name": row[0].capitalize(), "value": row[1]} for row in format_result.fetchall()]
    
    # Status Distribution formatted
    status_dist = [{"status": k.capitalize(), "count": v} for k, v in status_map.items()]
    
    # 4. Top Posts (by score)
    top_posts_query = text("""
        SELECT 
            raw_idea, 
            CAST(optimizer_output->>'quality_score' AS FLOAT) as score,
            status
        FROM generation_history
        WHERE status = 'completed' 
        AND optimizer_output->>'quality_score' IS NOT NULL
        AND user_id = :user_id
        ORDER BY score DESC
        LIMIT 5
    """)
    top_result = await session.execute(top_posts_query, {"user_id": user.user_id})
    top_posts = [
        {
            "idea": row[0][:60] + "..." if len(row[0]) > 60 else row[0], 
            "score": row[1],
            "status": row[2]
        } 
        for row in top_result.fetchall()
    ]
    
    return AnalyticsResponse(
        stats=AnalyticsStats(
            total_posts=total_posts,
            completed_posts=completed_posts,
            avg_quality_score=round(avg_quality_score, 1),
            posts_this_week=posts_this_week,
        ),
        daily_activity=daily_data,
        format_distribution=format_dist,
        status_distribution=status_dist,
        top_posts=top_posts,
    )


@router.get("/{history_id}", response_model=GenerationHistoryDetail)
async def get_generation_history(
    history_id: str,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """
    Get complete generation history by ID.
    
    Returns the full history including all agent outputs,
    user answers, timeline events, and final post.
    """
    repo = GenerationHistoryRepository(session)
    history = await repo.get_by_id(UUID(history_id))
    
    if not history:
        raise HTTPException(status_code=404, detail="History not found")
        
    if history.user_id != user.user_id:
         raise HTTPException(status_code=403, detail="Not authorized to view this history")
    
    # Build events list
    events = []
    for e in history.events:
        events.append(EventResponse(
            event_id=str(e.event_id),
            event_type=e.event_type,
            agent_name=e.agent_name,
            message=e.message,
            execution_time_ms=e.execution_time_ms,
            progress_percent=e.progress_percent,
            output_summary=e.output_summary,
            decision=e.decision,
            score=e.score,
            event_data=e.event_data or {},
            error_message=e.error_message,
            retry_attempt=e.retry_attempt,
            timestamp=e.timestamp,
        ))
    
    # Build agents summary
    agents_summary = _build_agents_summary(history)
    
    return GenerationHistoryDetail(
        history_id=str(history.history_id),
        post_id=str(history.post_id),
        raw_idea=history.raw_idea,
        preferred_format=history.preferred_format,
        brand_profile_snapshot=history.brand_profile_snapshot or {},
        validator_output=history.validator_output or {},
        strategist_output=history.strategist_output or {},
        writer_output=history.writer_output or {},
        visual_output=history.visual_output or {},
        optimizer_output=history.optimizer_output or {},
        clarifying_questions=history.clarifying_questions or [],
        user_answers=history.user_answers or {},
        final_post=history.final_post or {},
        selected_hook_index=history.selected_hook_index or 0,
        status=history.status,
        total_execution_time_ms=history.total_execution_time_ms,
        revision_count=history.revision_count or 0,
        validator_time_ms=history.validator_time_ms,
        strategist_time_ms=history.strategist_time_ms,
        writer_time_ms=history.writer_time_ms,
        visual_time_ms=history.visual_time_ms,
        optimizer_time_ms=history.optimizer_time_ms,
        error_message=history.error_message,
        failed_agent=history.failed_agent,
        started_at=history.started_at,
        phase1_completed_at=history.phase1_completed_at,
        answers_submitted_at=history.answers_submitted_at,
        completed_at=history.completed_at,
        events=events,
        agents_summary=agents_summary,
    )


@router.get("/post/{post_id}", response_model=GenerationHistoryDetail)
async def get_history_by_post(
    post_id: str,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """
    Get generation history by post ID.
    
    Use this to view the generation history for a specific post.
    """
    repo = GenerationHistoryRepository(session)
    history = await repo.get_by_post_id(UUID(post_id))
    
    if not history:
        raise HTTPException(status_code=404, detail="History not found for this post")
        
    if history.user_id != user.user_id:
         raise HTTPException(status_code=403, detail="Not authorized to view this history")
    
    # Reuse the same logic
    return await get_generation_history(str(history.history_id), session, user)


@router.get("/{history_id}/events")
async def get_generation_events(
    history_id: str,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """
    Get just the timeline events for a generation.
    
    Returns chronological list of all events that occurred
    during the generation process.
    """
    # Check ownership first
    history_repo = GenerationHistoryRepository(session)
    history = await history_repo.get_by_id(UUID(history_id))
    
    if not history:
        raise HTTPException(status_code=404, detail="History not found")
        
    if history.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this history")
    
    repo = GenerationEventRepository(session)
    events = await repo.get_by_history_id(UUID(history_id))
    
    return {
        "history_id": history_id,
        "events": [
            {
                "event_id": str(e.event_id),
                "event_type": e.event_type,
                "agent_name": e.agent_name,
                "message": e.message,
                "execution_time_ms": e.execution_time_ms,
                "progress_percent": e.progress_percent,
                "output_summary": e.output_summary,
                "decision": e.decision,
                "score": e.score,
                "timestamp": e.timestamp.isoformat(),
                "event_data": e.event_data,
            }
            for e in events
        ],
        "total_events": len(events),
    }


@router.get("/{history_id}/agent/{agent_name}")
async def get_agent_output(
    history_id: str,
    agent_name: str,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """
    Get output from a specific agent for a generation.
    
    Valid agent_names: validator, strategist, writer, visual, optimizer
    """
    repo = GenerationHistoryRepository(session)
    history = await repo.get_by_id(UUID(history_id))
    
    if not history:
        raise HTTPException(status_code=404, detail="History not found")
        
    if history.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this history")
    
    agent_outputs = {
        "validator": history.validator_output,
        "strategist": history.strategist_output,
        "writer": history.writer_output,
        "visual": history.visual_output,
        "optimizer": history.optimizer_output,
    }
    
    agent_times = {
        "validator": history.validator_time_ms,
        "strategist": history.strategist_time_ms,
        "writer": history.writer_time_ms,
        "visual": history.visual_time_ms,
        "optimizer": history.optimizer_time_ms,
    }
    
    if agent_name not in agent_outputs:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid agent name. Must be one of: {list(agent_outputs.keys())}"
        )
    
    output = agent_outputs.get(agent_name, {})
    
    return {
        "history_id": history_id,
        "agent_name": agent_name,
        "execution_time_ms": agent_times.get(agent_name),
        "has_output": bool(output),
        "output": output,
        "summary": _generate_agent_summary(agent_name, output) if output else None,
    }


@router.patch("/{history_id}/selected-hook")
async def update_selected_hook(
    history_id: str,
    hook_index: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """
    Update which hook variation the user selected.
    
    Call this when user picks a different hook for their post.
    """
    if hook_index < 0 or hook_index > 2:
        raise HTTPException(status_code=400, detail="hook_index must be 0, 1, or 2")
    
    repo = GenerationHistoryRepository(session)
    
    # Check ownership
    history = await repo.get_by_id(UUID(history_id))
    if not history:
        raise HTTPException(status_code=404, detail="History not found")
        
    if history.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this history")
        
    history = await repo.update_selected_hook(UUID(history_id), hook_index)
    
    if not history:
        raise HTTPException(status_code=404, detail="History not found")
    
    await session.commit()
    
    return {
        "history_id": history_id,
        "selected_hook_index": hook_index,
        "status": "updated",
    }


# ═══════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════

def _build_agents_summary(history) -> list[AgentOutputSummary]:
    """Build summary for each agent."""
    agents = []
    
    # Validator
    if history.validator_output:
        vo = history.validator_output
        agents.append(AgentOutputSummary(
            agent_name="validator",
            status="success",
            execution_time_ms=history.validator_time_ms or 0,
            decision=vo.get("decision"),
            score=vo.get("quality_score"),
            summary=f"Decision: {vo.get('decision', 'N/A')} | Quality: {vo.get('quality_score', 0)}/10",
            has_output=True,
        ))
    
    # Strategist
    if history.strategist_output:
        so = history.strategist_output
        num_q = len(so.get("clarifying_questions", []))
        agents.append(AgentOutputSummary(
            agent_name="strategist",
            status="success",
            execution_time_ms=history.strategist_time_ms or 0,
            summary=f"Format: {so.get('recommended_format', 'N/A')} | Questions: {num_q}",
            has_output=True,
        ))
    
    # Writer
    if history.writer_output:
        wo = history.writer_output
        hooks = wo.get("hooks", [])
        best_score = max((h.get("score", 0) for h in hooks), default=0)
        agents.append(AgentOutputSummary(
            agent_name="writer",
            status="success",
            execution_time_ms=history.writer_time_ms or 0,
            score=best_score,
            summary=f"Hooks: {len(hooks)} | Best Score: {best_score}/10",
            has_output=True,
        ))
    
    # Visual (optional)
    if history.visual_output and history.visual_output.get("visual_specs"):
        vs = history.visual_output.get("visual_specs", {})
        agents.append(AgentOutputSummary(
            agent_name="visual",
            status="success",
            execution_time_ms=history.visual_time_ms or 0,
            summary=f"Slides: {vs.get('total_slides', 0)} | Style: {vs.get('overall_style', 'default')}",
            has_output=True,
        ))
    
    # Optimizer
    if history.optimizer_output:
        oo = history.optimizer_output
        agents.append(AgentOutputSummary(
            agent_name="optimizer",
            status="success",
            execution_time_ms=history.optimizer_time_ms or 0,
            decision=oo.get("decision"),
            score=oo.get("quality_score"),
            summary=f"Decision: {oo.get('decision', 'N/A')} | Quality: {oo.get('quality_score', 0)}/10",
            has_output=True,
        ))
    
    return agents


def _generate_agent_summary(agent_name: str, output: dict) -> str:
    """Generate a human-readable summary for an agent's output."""
    if not output:
        return "No output"
    
    if agent_name == "validator":
        return f"Decision: {output.get('decision', 'N/A')} | Quality Score: {output.get('quality_score', 0)}/10 | Brand Alignment: {output.get('brand_alignment_score', 0)}/10"
    
    elif agent_name == "strategist":
        num_q = len(output.get("clarifying_questions", []))
        return f"Format: {output.get('recommended_format', 'N/A')} | Structure: {output.get('structure_type', 'N/A')} | Questions: {num_q}"
    
    elif agent_name == "writer":
        hooks = output.get("hooks", [])
        best = max((h.get("score", 0) for h in hooks), default=0)
        return f"Hooks: {len(hooks)} | Best Hook Score: {best}/10 | Hashtags: {len(output.get('hashtags', []))}"
    
    elif agent_name == "visual":
        specs = output.get("visual_specs", output)
        return f"Slides: {specs.get('total_slides', 0)} | Style: {specs.get('overall_style', 'default')}"
    
    elif agent_name == "optimizer":
        pred = f"{output.get('predicted_impressions_min', 0):,}-{output.get('predicted_impressions_max', 0):,}"
        return f"Decision: {output.get('decision', 'N/A')} | Quality: {output.get('quality_score', 0)}/10 | Impressions: {pred}"
    
    return "Unknown agent"
