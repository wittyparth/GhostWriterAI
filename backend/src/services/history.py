"""
History Service for managing generation history storage.

Provides methods to save generation history as agents execute.
Works with the ExecutionTracker to persist events to the database.
"""

import logging
from datetime import datetime
from uuid import UUID
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories import (
    GenerationHistoryRepository,
    GenerationEventRepository,
)
from src.orchestration.callbacks import ExecutionTracker, AgentEvent

logger = logging.getLogger(__name__)


class HistoryService:
    """
    Service for persisting generation history to the database.
    
    Usage:
        service = HistoryService(session)
        await service.create_history(post_id, raw_idea)
        await service.save_event(post_id, event)
        await service.complete_phase1(post_id, validator_output, strategist_output)
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.history_repo = GenerationHistoryRepository(session)
        self.event_repo = GenerationEventRepository(session)
        self._history_cache: dict[str, UUID] = {}  # post_id -> history_id
    
    async def create_history(
        self,
        post_id: str | UUID,
        raw_idea: str,
        preferred_format: str | None = None,
        brand_profile: dict | None = None,
        user_id: str | UUID | None = None,
    ) -> UUID:
        """
        Create a new generation history record.
        
        Call this at the start of generation to initialize the history.
        """
        if isinstance(post_id, str):
            post_id = UUID(post_id)
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        
        history = await self.history_repo.create(
            post_id=post_id,
            raw_idea=raw_idea,
            preferred_format=preferred_format,
            brand_profile=brand_profile,
            user_id=user_id,
        )
        
        self._history_cache[str(post_id)] = history.history_id
        await self.session.commit()
        
        logger.info(f"Created history {history.history_id} for post {post_id}")
        return history.history_id
    
    async def save_event(
        self,
        post_id: str | UUID,
        event: AgentEvent,
    ) -> None:
        """
        Save an individual event to the database.
        
        Call this from the ExecutionTracker callback.
        """
        history_id = await self._get_history_id(post_id)
        if not history_id:
            logger.warning(f"No history found for post {post_id}, skipping event save")
            return
        
        await self.event_repo.create(
            history_id=history_id,
            event_type=event.event_type,
            agent_name=event.agent_name,
            message=event.message,
            execution_time_ms=event.execution_time_ms,
            progress_percent=event.progress_percent,
            output_summary=event.data.get("summary"),
            decision=event.data.get("decision"),
            score=event.data.get("score"),
            event_data=event.data,
            error_message=event.data.get("error") if event.event_type == "agent_error" else None,
            retry_attempt=event.data.get("attempt") if event.event_type == "agent_error" else None,
        )
        
        await self.session.commit()
    
    async def save_events_from_tracker(
        self,
        post_id: str | UUID,
        tracker: ExecutionTracker,
    ) -> None:
        """
        Save all events from a tracker to the database.
        
        Call this when generation completes to persist all events.
        """
        history_id = await self._get_history_id(post_id)
        if not history_id:
            logger.warning(f"No history found for post {post_id}")
            return
        
        events_data = [
            {
                "event_type": e.event_type,
                "agent_name": e.agent_name,
                "message": e.message,
                "execution_time_ms": e.execution_time_ms,
                "progress_percent": e.progress_percent,
                "output_summary": e.data.get("summary"),
                "decision": e.data.get("decision"),
                "score": e.data.get("score"),
                "event_data": e.data,
                "error_message": e.data.get("error") if e.event_type == "agent_error" else None,
                "retry_attempt": e.data.get("attempt"),
                "timestamp": e.timestamp,
            }
            for e in tracker.events
        ]
        
        await self.event_repo.bulk_create(history_id, events_data)
        await self.session.commit()
    
    async def update_phase1_complete(
        self,
        post_id: str | UUID,
        validator_output: dict,
        strategist_output: dict,
        clarifying_questions: list,
        validator_time_ms: int,
        strategist_time_ms: int,
    ) -> None:
        """
        Update history after Phase 1 completes.
        
        Call this after Validator and Strategist have run.
        """
        if isinstance(post_id, str):
            post_id = UUID(post_id)
        
        await self.history_repo.update_phase1_complete(
            post_id=post_id,
            validator_output=validator_output,
            strategist_output=strategist_output,
            clarifying_questions=clarifying_questions,
            validator_time_ms=validator_time_ms,
            strategist_time_ms=strategist_time_ms,
        )
        await self.session.commit()
        
        logger.info(f"Phase 1 complete for post {post_id}")
    
    async def update_rejected(
        self,
        post_id: str | UUID,
        validator_output: dict,
        validator_time_ms: int,
    ) -> None:
        """
        Update history when idea is rejected.
        """
        if isinstance(post_id, str):
            post_id = UUID(post_id)
        
        await self.history_repo.update_rejected(
            post_id=post_id,
            validator_output=validator_output,
            validator_time_ms=validator_time_ms,
        )
        await self.session.commit()
        
        logger.info(f"Post {post_id} rejected")
    
    async def update_answers_submitted(
        self,
        post_id: str | UUID,
        user_answers: dict,
    ) -> None:
        """
        Update history when user submits answers.
        """
        if isinstance(post_id, str):
            post_id = UUID(post_id)
        
        await self.history_repo.update_answers_submitted(
            post_id=post_id,
            user_answers=user_answers,
        )
        await self.session.commit()
        
        logger.info(f"Answers submitted for post {post_id}")
    
    async def update_phase2_complete(
        self,
        post_id: str | UUID,
        writer_output: dict,
        visual_output: dict | None,
        optimizer_output: dict,
        final_post: dict,
        writer_time_ms: int,
        visual_time_ms: int | None,
        optimizer_time_ms: int,
        total_execution_time_ms: int,
        revision_count: int = 0,
    ) -> None:
        """
        Update history after Phase 2 completes.
        
        Call this after Writer, Visual, and Optimizer have run.
        """
        if isinstance(post_id, str):
            post_id = UUID(post_id)
        
        await self.history_repo.update_phase2_complete(
            post_id=post_id,
            writer_output=writer_output,
            visual_output=visual_output,
            optimizer_output=optimizer_output,
            final_post=final_post,
            writer_time_ms=writer_time_ms,
            visual_time_ms=visual_time_ms,
            optimizer_time_ms=optimizer_time_ms,
            total_execution_time_ms=total_execution_time_ms,
            revision_count=revision_count,
        )
        await self.session.commit()
        
        logger.info(f"Phase 2 complete for post {post_id}")
    
    async def update_failed(
        self,
        post_id: str | UUID,
        error_message: str,
        failed_agent: str,
    ) -> None:
        """
        Update history when generation fails.
        """
        if isinstance(post_id, str):
            post_id = UUID(post_id)
        
        await self.history_repo.update_failed(
            post_id=post_id,
            error_message=error_message,
            failed_agent=failed_agent,
        )
        await self.session.commit()
        
        logger.warning(f"Post {post_id} failed at {failed_agent}: {error_message}")
    
    async def _get_history_id(self, post_id: str | UUID) -> UUID | None:
        """Get history_id for a post, using cache or DB lookup."""
        post_id_str = str(post_id)
        
        if post_id_str in self._history_cache:
            return self._history_cache[post_id_str]
        
        if isinstance(post_id, str):
            post_id = UUID(post_id)
        
        history = await self.history_repo.get_by_post_id(post_id)
        if history:
            self._history_cache[post_id_str] = history.history_id
            return history.history_id
        
        return None


def get_history_service(session: AsyncSession) -> HistoryService:
    """Factory function to create a HistoryService."""
    return HistoryService(session)
