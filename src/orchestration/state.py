"""
LangGraph state definition for the agent workflow.

Defines the state schema that flows through all agents.
"""

from typing import Any, Literal, TypedDict
from uuid import UUID


class AgentState(TypedDict, total=False):
    """State that flows through the agent workflow."""
    
    # Request info
    post_id: str
    user_id: str
    raw_idea: str
    brand_profile: dict[str, Any]
    
    # Agent outputs
    validator_output: dict[str, Any]
    strategy: dict[str, Any]
    clarifying_questions: list[dict[str, Any]]
    user_answers: dict[str, str]
    writer_output: dict[str, Any]
    visual_specs: dict[str, Any]
    optimizer_output: dict[str, Any]
    
    # Final output
    final_post: dict[str, Any]
    
    # Workflow control
    current_agent: str
    status: Literal["pending", "processing", "awaiting_answers", "completed", "failed"]
    format: Literal["text", "carousel", "video"]
    revision_count: int
    max_revisions: int
    
    # Error tracking
    error: str | None
    
    # Metadata
    execution_log: list[dict[str, Any]]
