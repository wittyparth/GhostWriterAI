"""
Agent execution callback system for real-time streaming.

Provides hooks to track and stream agent execution progress.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Callable, Awaitable
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class AgentEvent:
    """Represents an event during agent execution."""
    
    event_type: str  # agent_start, agent_complete, agent_error, status_update
    agent_name: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    execution_time_ms: int = 0
    data: dict[str, Any] = field(default_factory=dict)
    progress_percent: int = 0
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "agent_name": self.agent_name,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "execution_time_ms": self.execution_time_ms,
            "data": self.data,
            "progress_percent": self.progress_percent,
        }


# Define progress percentages for each agent
AGENT_PROGRESS = {
    "validator": 15,
    "strategist": 30,
    "writer": 55,
    "visual": 75,
    "optimizer": 90,
    "finalize": 100,
}


class ExecutionTracker:
    """
    Tracks agent execution and provides callbacks for streaming.
    
    Usage:
        tracker = ExecutionTracker(post_id="123")
        tracker.on_event(my_callback)  # Register callback
        
        # During execution:
        tracker.agent_started("validator")
        tracker.agent_completed("validator", output, execution_time_ms=500)
    """
    
    def __init__(self, post_id: str):
        self.post_id = post_id
        self.events: list[AgentEvent] = []
        self.callbacks: list[Callable[[AgentEvent], Awaitable[None]]] = []
        self.start_time = time.time()
        self.agent_outputs: dict[str, dict[str, Any]] = {}
        self.current_agent: str | None = None
        self._lock = asyncio.Lock()
    
    def on_event(self, callback: Callable[[AgentEvent], Awaitable[None]]):
        """Register a callback to be called on each event."""
        self.callbacks.append(callback)
    
    async def _emit(self, event: AgentEvent):
        """Emit an event to all registered callbacks."""
        async with self._lock:
            self.events.append(event)
            for callback in self.callbacks:
                try:
                    await callback(event)
                except Exception as e:
                    logger.error(f"Callback error: {e}")
    
    async def agent_started(self, agent_name: str):
        """Called when an agent starts execution."""
        self.current_agent = agent_name
        event = AgentEvent(
            event_type="agent_start",
            agent_name=agent_name,
            message=f"🔄 {agent_name.capitalize()} agent is analyzing...",
            progress_percent=AGENT_PROGRESS.get(agent_name, 0) - 10,
        )
        await self._emit(event)
    
    async def agent_completed(
        self, 
        agent_name: str, 
        output: dict[str, Any], 
        execution_time_ms: int = 0
    ):
        """Called when an agent completes successfully."""
        self.agent_outputs[agent_name] = output
        
        # Generate summary based on agent type
        summary = self._generate_summary(agent_name, output)
        
        event = AgentEvent(
            event_type="agent_complete",
            agent_name=agent_name,
            message=f"✅ {agent_name.capitalize()} completed in {execution_time_ms}ms",
            execution_time_ms=execution_time_ms,
            progress_percent=AGENT_PROGRESS.get(agent_name, 0),
            data={
                "summary": summary,
                "decision": output.get("decision"),
                "score": output.get("quality_score") or output.get("score"),
                "output": output,
            },
        )
        await self._emit(event)
    
    async def agent_error(self, agent_name: str, error: str, attempt: int = 1):
        """Called when an agent encounters an error."""
        event = AgentEvent(
            event_type="agent_error",
            agent_name=agent_name,
            message=f"❌ {agent_name.capitalize()} failed (attempt {attempt}): {error}",
            data={"error": error, "attempt": attempt},
        )
        await self._emit(event)
    
    async def status_update(self, message: str, progress: int = 0):
        """Emit a general status update."""
        event = AgentEvent(
            event_type="status_update",
            agent_name=self.current_agent or "system",
            message=message,
            progress_percent=progress,
        )
        await self._emit(event)
    
    async def complete(self, final_output: dict[str, Any] | None = None):
        """Called when the entire workflow completes."""
        total_time = int((time.time() - self.start_time) * 1000)
        event = AgentEvent(
            event_type="complete",
            agent_name="system",
            message=f"🎉 Post generation complete in {total_time}ms",
            execution_time_ms=total_time,
            progress_percent=100,
            data={"final_output": final_output} if final_output else {},
        )
        await self._emit(event)
    
    def _generate_summary(self, agent_name: str, output: dict[str, Any]) -> str:
        """Generate a human-readable summary for agent output."""
        if agent_name == "validator":
            decision = output.get("decision", "UNKNOWN")
            score = output.get("quality_score", 0)
            return f"Decision: {decision} | Quality Score: {score}/10"
        
        elif agent_name == "strategist":
            fmt = output.get("recommended_format", "text")
            structure = output.get("structure_type", "unknown")
            num_questions = len(output.get("clarifying_questions", []))
            return f"Format: {fmt} | Structure: {structure} | Questions: {num_questions}"
        
        elif agent_name == "writer":
            hooks = output.get("hooks", [])
            num_hooks = len(hooks)
            best_score = max((h.get("score", 0) for h in hooks), default=0)
            hashtags = output.get("hashtags", [])
            return f"Hooks: {num_hooks} (best score: {best_score}/10) | Hashtags: {len(hashtags)}"
        
        elif agent_name == "visual":
            specs = output.get("visual_specs", output)
            num_slides = specs.get("total_slides", 0)
            style = specs.get("overall_style", "default")
            return f"Slides: {num_slides} | Style: {style}"
        
        elif agent_name == "optimizer":
            decision = output.get("decision", "UNKNOWN")
            score = output.get("quality_score", 0)
            impressions = f"{output.get('predicted_impressions_min', 0):,}-{output.get('predicted_impressions_max', 0):,}"
            return f"Decision: {decision} | Quality: {score}/10 | Predicted: {impressions} impressions"
        
        return "Completed"
    
    def get_execution_summary(self) -> dict[str, Any]:
        """Get a summary of all agent executions."""
        return {
            "post_id": self.post_id,
            "total_time_ms": int((time.time() - self.start_time) * 1000),
            "agents": {
                name: {
                    "summary": self._generate_summary(name, output),
                    "output": output,
                }
                for name, output in self.agent_outputs.items()
            },
            "events": [e.to_dict() for e in self.events],
        }


# Store active trackers by post_id
_active_trackers: dict[str, ExecutionTracker] = {}


def get_tracker(post_id: str) -> ExecutionTracker:
    """Get or create a tracker for a post."""
    if post_id not in _active_trackers:
        _active_trackers[post_id] = ExecutionTracker(post_id)
    return _active_trackers[post_id]


def remove_tracker(post_id: str):
    """Remove a tracker when done."""
    _active_trackers.pop(post_id, None)


def get_all_trackers() -> dict[str, ExecutionTracker]:
    """Get all active trackers."""
    return _active_trackers
