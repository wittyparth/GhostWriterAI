"""
Repository for generation history storage and retrieval.

Provides methods to save and retrieve complete generation flows.
"""

import logging
from datetime import datetime
from typing import Any, Sequence
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import GenerationHistory, GenerationEvent

logger = logging.getLogger(__name__)


class GenerationHistoryRepository:
    """Repository for GenerationHistory model."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        post_id: UUID,
        raw_idea: str,
        preferred_format: str | None = None,
        brand_profile: dict | None = None,
        user_id: UUID | None = None,
    ) -> GenerationHistory:
        """Create a new generation history record."""
        history = GenerationHistory(
            post_id=post_id,
            user_id=user_id,
            raw_idea=raw_idea,
            preferred_format=preferred_format,
            brand_profile_snapshot=brand_profile or {},
            status="processing",
            started_at=datetime.utcnow(),
        )
        self.session.add(history)
        await self.session.flush()
        await self.session.refresh(history)
        return history
    
    async def get_by_id(self, history_id: UUID) -> GenerationHistory | None:
        """Get history by ID with all events."""
        stmt = select(GenerationHistory).where(
            GenerationHistory.history_id == history_id
        ).options(selectinload(GenerationHistory.events))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_post_id(self, post_id: UUID) -> GenerationHistory | None:
        """Get history by post ID with all events."""
        stmt = select(GenerationHistory).where(
            GenerationHistory.post_id == post_id
        ).options(selectinload(GenerationHistory.events))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_user_id(
        self, 
        user_id: UUID, 
        limit: int = 20, 
        offset: int = 0
    ) -> Sequence[GenerationHistory]:
        """Get all generation histories for a user."""
        stmt = select(GenerationHistory).where(
            GenerationHistory.user_id == user_id
        ).order_by(
            GenerationHistory.started_at.desc()
        ).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_all(self, limit: int = 50, offset: int = 0) -> Sequence[GenerationHistory]:
        """Get all generation histories."""
        stmt = select(GenerationHistory).order_by(
            GenerationHistory.started_at.desc()
        ).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def update_phase1_complete(
        self,
        post_id: UUID,
        validator_output: dict,
        strategist_output: dict,
        clarifying_questions: list,
        validator_time_ms: int,
        strategist_time_ms: int,
    ) -> GenerationHistory | None:
        """Update history after Phase 1 (Validator + Strategist)."""
        stmt = update(GenerationHistory).where(
            GenerationHistory.post_id == post_id
        ).values(
            validator_output=validator_output,
            strategist_output=strategist_output,
            clarifying_questions=clarifying_questions,
            validator_time_ms=validator_time_ms,
            strategist_time_ms=strategist_time_ms,
            status="awaiting_answers",
            phase1_completed_at=datetime.utcnow(),
        )
        await self.session.execute(stmt)
        return await self.get_by_post_id(post_id)
    
    async def update_rejected(
        self,
        post_id: UUID,
        validator_output: dict,
        validator_time_ms: int,
    ) -> GenerationHistory | None:
        """Update history when idea is rejected."""
        stmt = update(GenerationHistory).where(
            GenerationHistory.post_id == post_id
        ).values(
            validator_output=validator_output,
            validator_time_ms=validator_time_ms,
            status="rejected",
            completed_at=datetime.utcnow(),
        )
        await self.session.execute(stmt)
        return await self.get_by_post_id(post_id)
    
    async def update_answers_submitted(
        self,
        post_id: UUID,
        user_answers: dict,
    ) -> GenerationHistory | None:
        """Update history when user submits answers."""
        stmt = update(GenerationHistory).where(
            GenerationHistory.post_id == post_id
        ).values(
            user_answers=user_answers,
            status="processing",
            answers_submitted_at=datetime.utcnow(),
        )
        await self.session.execute(stmt)
        return await self.get_by_post_id(post_id)
    
    async def update_phase2_complete(
        self,
        post_id: UUID,
        writer_output: dict,
        visual_output: dict | None,
        optimizer_output: dict,
        final_post: dict,
        writer_time_ms: int,
        visual_time_ms: int | None,
        optimizer_time_ms: int,
        total_execution_time_ms: int,
        revision_count: int = 0,
    ) -> GenerationHistory | None:
        """Update history after Phase 2 (Writer → Visual → Optimizer)."""
        stmt = update(GenerationHistory).where(
            GenerationHistory.post_id == post_id
        ).values(
            writer_output=writer_output,
            visual_output=visual_output or {},
            optimizer_output=optimizer_output,
            final_post=final_post,
            writer_time_ms=writer_time_ms,
            visual_time_ms=visual_time_ms,
            optimizer_time_ms=optimizer_time_ms,
            total_execution_time_ms=total_execution_time_ms,
            revision_count=revision_count,
            status="completed",
            completed_at=datetime.utcnow(),
        )
        await self.session.execute(stmt)
        return await self.get_by_post_id(post_id)
    
    async def update_failed(
        self,
        post_id: UUID,
        error_message: str,
        failed_agent: str,
    ) -> GenerationHistory | None:
        """Update history when generation fails."""
        stmt = update(GenerationHistory).where(
            GenerationHistory.post_id == post_id
        ).values(
            error_message=error_message,
            failed_agent=failed_agent,
            status="failed",
            completed_at=datetime.utcnow(),
        )
        await self.session.execute(stmt)
        return await self.get_by_post_id(post_id)
    
    async def update_selected_hook(
        self,
        post_id: UUID,
        hook_index: int,
    ) -> GenerationHistory | None:
        """Update which hook the user selected."""
        stmt = update(GenerationHistory).where(
            GenerationHistory.post_id == post_id
        ).values(selected_hook_index=hook_index)
        await self.session.execute(stmt)
        return await self.get_by_post_id(post_id)
    
    async def delete_by_post_id(self, post_id: UUID) -> bool:
        """Delete history and dependent events by post ID."""
        history = await self.get_by_post_id(post_id)
        if not history:
            return False
            
        # Delete events first (manual cascade)
        stmt_events = delete(GenerationEvent).where(GenerationEvent.history_id == history.history_id)
        await self.session.execute(stmt_events)
        
        # Delete history
        stmt_history = delete(GenerationHistory).where(GenerationHistory.history_id == history.history_id)
        await self.session.execute(stmt_history)
        
        return True


class GenerationEventRepository:
    """Repository for GenerationEvent model."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        history_id: UUID,
        event_type: str,
        agent_name: str,
        message: str,
        execution_time_ms: int = 0,
        progress_percent: int = 0,
        output_summary: str | None = None,
        decision: str | None = None,
        score: float | None = None,
        event_data: dict | None = None,
        error_message: str | None = None,
        retry_attempt: int | None = None,
    ) -> GenerationEvent:
        """Create a new event record."""
        event = GenerationEvent(
            history_id=history_id,
            event_type=event_type,
            agent_name=agent_name,
            message=message,
            execution_time_ms=execution_time_ms,
            progress_percent=progress_percent,
            output_summary=output_summary,
            decision=decision,
            score=score,
            event_data=event_data or {},
            error_message=error_message,
            retry_attempt=retry_attempt,
            timestamp=datetime.utcnow(),
        )
        self.session.add(event)
        await self.session.flush()
        return event
    
    async def get_by_history_id(self, history_id: UUID) -> Sequence[GenerationEvent]:
        """Get all events for a history, ordered by timestamp."""
        stmt = select(GenerationEvent).where(
            GenerationEvent.history_id == history_id
        ).order_by(GenerationEvent.timestamp)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def bulk_create(
        self,
        history_id: UUID,
        events: list[dict],
    ) -> list[GenerationEvent]:
        """Create multiple events at once."""
        event_objects = []
        for e in events:
            event = GenerationEvent(
                history_id=history_id,
                event_type=e.get("event_type", "status_update"),
                agent_name=e.get("agent_name", "system"),
                message=e.get("message", ""),
                execution_time_ms=e.get("execution_time_ms", 0),
                progress_percent=e.get("progress_percent", 0),
                output_summary=e.get("output_summary"),
                decision=e.get("decision"),
                score=e.get("score"),
                event_data=e.get("event_data", {}),
                error_message=e.get("error_message"),
                retry_attempt=e.get("retry_attempt"),
                timestamp=e.get("timestamp", datetime.utcnow()),
            )
            event_objects.append(event)
            self.session.add(event)
        
        await self.session.flush()
        return event_objects
