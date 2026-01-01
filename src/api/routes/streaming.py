"""
Streaming API routes for real-time agent execution tracking.

Provides Server-Sent Events (SSE) endpoints for streaming agent thoughts
and execution progress to clients.
"""

import asyncio
import json
import logging
from datetime import datetime
from uuid import UUID, uuid4
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.database.repositories.base import PostRepository
from src.database.models import User
from src.api.routes.auth import get_current_user
from src.models.schemas import (
    IdeaInput,
    AgentThoughtsResponse,
    AgentExecutionStep,
)
from src.orchestration import (
    run_generation_with_tracking,
    continue_generation_with_tracking,
    get_tracker,
    remove_tracker,
    get_all_trackers,
    AgentEvent,
)
from src.services.history import HistoryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/posts", tags=["streaming"])

# In-memory state store for tracked generations
_tracked_states: dict[str, dict] = {}


def _format_sse_event(data: dict, event_type: str = "message") -> str:
    """Format data as a Server-Sent Event."""
    json_data = json.dumps(data, default=str)
    return f"event: {event_type}\ndata: {json_data}\n\n"


async def _stream_events(
    post_id: str, 
    events_queue: asyncio.Queue
) -> AsyncGenerator[str, None]:
    """Generate SSE events from a queue."""
    try:
        while True:
            try:
                # Wait for event with timeout
                event = await asyncio.wait_for(events_queue.get(), timeout=60.0)
                
                if event is None:  # Sentinel to stop streaming
                    break
                
                yield _format_sse_event(event.to_dict(), event.event_type)
                
                if event.event_type == "complete":
                    break
                    
            except asyncio.TimeoutError:
                # Send keepalive
                yield _format_sse_event({"type": "keepalive", "timestamp": datetime.now().isoformat()}, "ping")
                
    except asyncio.CancelledError:
        logger.info(f"Stream cancelled for post {post_id}")
    finally:
        logger.info(f"Stream ended for post {post_id}")


@router.post("/generate/stream")
async def generate_post_with_stream(
    request: IdeaInput,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """
    Start post generation with real-time streaming of agent thoughts.
    
    Returns Server-Sent Events (SSE) stream with agent progress updates.
    Use this endpoint to see what each agent is thinking in real-time.
    
    Example events:
    - agent_start: Agent begins processing
    - agent_complete: Agent finished with output summary
    - status_update: General progress update
    - complete: All agents finished
    """
    post_id = str(uuid4())
    events_queue: asyncio.Queue[AgentEvent | None] = asyncio.Queue()
    
    # Initialize history service
    history_service = HistoryService(session)
    
    async def event_callback(event: AgentEvent):
        """Callback to push events to the queue and save to history."""
        await events_queue.put(event)
        # Save event to history
        try:
            await history_service.save_event(post_id, event)
        except Exception as e:
            logger.warning(f"Failed to save event to history: {e}")
    
    async def run_generation_task():
        """Background task to run the generation."""
        try:
            # Create initial post record
            post_repo = PostRepository(session)
            await post_repo.create(
                post_id=UUID(post_id),
                user_id=user.user_id,
                raw_idea=request.raw_idea,
                format=request.preferred_format or "text",
                status="processing",
            )

            # Create history record at start
            await history_service.create_history(
                post_id=post_id,
                raw_idea=request.raw_idea,
                preferred_format=request.preferred_format,
                brand_profile={},
                user_id=user.user_id,
            )
            
            state, tracker = await run_generation_with_tracking(
                raw_idea=request.raw_idea,
                post_id=post_id,
                brand_profile={},
            )
            
            # Store state for continuation
            _tracked_states[post_id] = {
                "state": state,
                "tracker": tracker,
            }
            
            # Check for rejection
            validator_output = state.get("validator_output", {})
            if validator_output.get("decision") == "REJECT":
                # Update history as rejected
                validator_time = 0
                for e in tracker.events:
                    if e.agent_name == "validator" and e.event_type == "agent_complete":
                        validator_time = e.execution_time_ms
                        break
                
                await history_service.update_rejected(
                    post_id=post_id,
                    validator_output=validator_output,
                    validator_time_ms=validator_time,
                )
                
                await events_queue.put(AgentEvent(
                    event_type="complete",
                    agent_name="system",
                    message="Idea rejected - see validator output for suggestions",
                    data={
                        "status": "rejected",
                        "post_id": post_id,
                        "validator_output": validator_output,
                    },
                    progress_percent=100,
                ))
            else:
                # Update history for phase 1 complete
                validator_time = 0
                strategist_time = 0
                for e in tracker.events:
                    if e.agent_name == "validator" and e.event_type == "agent_complete":
                        validator_time = e.execution_time_ms
                    if e.agent_name == "strategist" and e.event_type == "agent_complete":
                        strategist_time = e.execution_time_ms
                
                strategist_output = state.get("strategist_output", {})
                clarifying_questions = state.get("clarifying_questions", [])
                
                await history_service.update_phase1_complete(
                    post_id=post_id,
                    validator_output=validator_output,
                    strategist_output=strategist_output,
                    clarifying_questions=clarifying_questions,
                    validator_time_ms=validator_time,
                    strategist_time_ms=strategist_time,
                )
                
                # Waiting for user answers
                await events_queue.put(AgentEvent(
                    event_type="complete",
                    agent_name="system",
                    message="Ready for your answers to clarifying questions",
                    data={
                        "status": "awaiting_answers",
                        "post_id": post_id,
                        "questions": clarifying_questions,
                        "original_idea": request.raw_idea,
                    },
                    progress_percent=30,
                ))
                
        except Exception as e:
            logger.error(f"Generation error: {e}")
            await history_service.update_failed(
                post_id=post_id,
                error_message=str(e),
                failed_agent="system",
            )
            await events_queue.put(AgentEvent(
                event_type="agent_error",
                agent_name="system",
                message=f"Generation failed: {str(e)}",
                data={"error": str(e)},
            ))
            await events_queue.put(None)  # Stop the stream
    
    # Register callback with tracker
    tracker = get_tracker(post_id)
    tracker.on_event(event_callback)
    
    # Start generation in background
    asyncio.create_task(run_generation_task())
    
    # Return SSE stream
    return StreamingResponse(
        _stream_events(post_id, events_queue),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Post-ID": post_id,
        },
    )


@router.post("/{post_id}/answers/stream")
async def submit_answers_with_stream(
    post_id: str,
    answers: dict[str, str],
    session: AsyncSession = Depends(get_session),
):
    """
    Submit answers and stream the remaining agent execution.
    
    Continues from where generate/stream left off, streaming
    writer, visual (if carousel), and optimizer agent outputs.
    """
    if post_id not in _tracked_states:
        raise HTTPException(status_code=404, detail="Post not found or expired")
    
    stored = _tracked_states[post_id]
    state = stored["state"]
    
    events_queue: asyncio.Queue[AgentEvent | None] = asyncio.Queue()
    
    # Initialize history service
    history_service = HistoryService(session)
    
    async def event_callback(event: AgentEvent):
        await events_queue.put(event)
        # Save event to history
        try:
            await history_service.save_event(post_id, event)
        except Exception as e:
            logger.warning(f"Failed to save event to history: {e}")
    
    async def continue_generation_task():
        try:
            # Update history that answers were submitted
            await history_service.update_answers_submitted(
                post_id=post_id,
                user_answers=answers,
            )
            
            final_state, tracker = await continue_generation_with_tracking(
                state=state,
                user_answers=answers,
                post_id=post_id,
            )
            
            # Save to database
            post_repo = PostRepository(session)
            final_post = final_state.get("final_post", {})
            
            hook = final_post.get("hook", {}).get("text", "")
            body = final_post.get("body", "")
            cta = final_post.get("cta", "")
            hashtags = final_post.get("hashtags", [])
            
            final_content = f"{hook}\n\n{body}\n\n{cta}"
            if hashtags:
                final_content += f"\n\n{' '.join('#' + h for h in hashtags)}"
            
            await post_repo.update(
                post_id=UUID(post_id),
                final_content=final_content,
                format=final_state.get("format", "text"),
                status="completed",
                hooks_generated=final_state.get("writer_output", {}).get("hooks", []),
                visual_specs=final_state.get("visual_specs"),
                quality_score=final_state.get("optimizer_output", {}).get("quality_score"),
            )
            
            # Extract timing info from tracker
            writer_time = 0
            visual_time = 0
            optimizer_time = 0
            total_time = 0
            
            for e in tracker.events:
                if e.event_type == "agent_complete":
                    if e.agent_name == "writer":
                        writer_time = e.execution_time_ms
                    elif e.agent_name == "visual":
                        visual_time = e.execution_time_ms
                    elif e.agent_name == "optimizer":
                        optimizer_time = e.execution_time_ms
                    total_time += e.execution_time_ms
            
            # Update history with Phase 2 complete
            await history_service.update_phase2_complete(
                post_id=post_id,
                writer_output=final_state.get("writer_output", {}),
                visual_output=final_state.get("visual_specs"),
                optimizer_output=final_state.get("optimizer_output", {}),
                final_post=final_post,
                writer_time_ms=writer_time,
                visual_time_ms=visual_time if visual_time else None,
                optimizer_time_ms=optimizer_time,
                total_execution_time_ms=total_time,
                revision_count=final_state.get("revision_count", 0),
            )
            
            # Clean up
            del _tracked_states[post_id]
            remove_tracker(post_id)
            
            # Final event with complete post
            await events_queue.put(AgentEvent(
                event_type="complete",
                agent_name="system",
                message="Post generation complete!",
                data={
                    "status": "completed",
                    "post_id": post_id,
                    "final_post": final_post,
                    "quality_score": final_state.get("optimizer_output", {}).get("quality_score"),
                    "execution_summary": tracker.get_execution_summary(),
                },
                progress_percent=100,
            ))
            
        except Exception as e:
            logger.error(f"Continuation error: {e}")
            await history_service.update_failed(
                post_id=post_id,
                error_message=str(e),
                failed_agent="system",
            )
            await events_queue.put(AgentEvent(
                event_type="agent_error",
                agent_name="system",
                message=f"Generation failed: {str(e)}",
                data={"error": str(e)},
            ))
            await events_queue.put(None)
    
    # Register callback
    tracker = get_tracker(post_id)
    tracker.on_event(event_callback)
    
    # Start continuation in background
    asyncio.create_task(continue_generation_task())
    
    return StreamingResponse(
        _stream_events(post_id, events_queue),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )



@router.get("/{post_id}/agents")
async def get_agent_thoughts(post_id: str) -> AgentThoughtsResponse:
    """
    Get detailed output from each agent for a post.
    
    Returns the execution log and individual agent outputs,
    useful for debugging or displaying agent reasoning.
    """
    # Check if in progress
    if post_id in _tracked_states:
        stored = _tracked_states[post_id]
        state = stored["state"]
        tracker = stored["tracker"]
        
        # Build response from tracker
        agents = {}
        total_time = 0
        
        for name, output in tracker.agent_outputs.items():
            exec_time = 0
            for event in tracker.events:
                if event.agent_name == name and event.event_type == "agent_complete":
                    exec_time = event.execution_time_ms
                    break
            
            total_time += exec_time
            agents[name] = AgentExecutionStep(
                agent_name=name,
                status="success",
                execution_time_ms=exec_time,
                output_summary=tracker._generate_summary(name, output),
                decision=output.get("decision"),
                score=output.get("quality_score") or output.get("score"),
                full_output=output,
            )
        
        execution_log = [
            AgentExecutionStep(
                agent_name=e.agent_name,
                status="success" if e.event_type == "agent_complete" else "pending",
                execution_time_ms=e.execution_time_ms,
                output_summary=e.data.get("summary"),
                decision=e.data.get("decision"),
                score=e.data.get("score"),
                timestamp=e.timestamp,
            )
            for e in tracker.events
            if e.event_type in ("agent_complete", "agent_start")
        ]
        
        return AgentThoughtsResponse(
            post_id=UUID(post_id),
            status=state.get("status", "processing"),
            total_execution_time_ms=total_time,
            revision_count=state.get("revision_count", 0),
            agents=agents,
            execution_log=execution_log,
        )
    
    # TODO: Load from database for completed posts
    raise HTTPException(
        status_code=404, 
        detail="Post not found or no longer in memory. Check the database for completed posts."
    )


@router.get("/{post_id}/execution-log")
async def get_execution_log(post_id: str):
    """
    Get the raw execution log for a post.
    
    Returns all events that occurred during generation,
    useful for detailed debugging.
    """
    if post_id not in _tracked_states:
        raise HTTPException(status_code=404, detail="Post not found or expired")
    
    tracker = _tracked_states[post_id]["tracker"]
    
    return {
        "post_id": post_id,
        "events": [e.to_dict() for e in tracker.events],
        "agent_outputs": {
            name: {
                "summary": tracker._generate_summary(name, output),
                "output": output,
            }
            for name, output in tracker.agent_outputs.items()
        },
    }
