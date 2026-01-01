"""
LangGraph workflow for LinkedIn content generation.

Orchestrates the 5 agents in sequence with conditional routing.
Includes real-time execution tracking via callbacks.
"""

import logging
import time
from typing import Any
from langgraph.graph import StateGraph, END

from src.orchestration.state import AgentState
from src.orchestration.callbacks import get_tracker, remove_tracker, ExecutionTracker
from src.agents import (
    ValidatorAgent,
    StrategistAgent,
    WriterAgent,
    VisualAgent,
    OptimizerAgent,
)
from src.config.constants import DECISION_APPROVE, DECISION_REJECT, FORMAT_CAROUSEL

logger = logging.getLogger(__name__)


# Initialize agents
validator = ValidatorAgent()
strategist = StrategistAgent()
writer = WriterAgent()
visual = VisualAgent()
optimizer = OptimizerAgent()


async def validate_node(state: AgentState, tracker: ExecutionTracker | None = None) -> AgentState:
    """Run the validator agent."""
    if tracker:
        await tracker.agent_started("validator")
    
    result = await validator.execute({
        "raw_idea": state["raw_idea"],
        "brand_profile": state.get("brand_profile", {}),
    })
    
    state["validator_output"] = result["output"]
    state["current_agent"] = "validator"
    state["execution_log"] = state.get("execution_log", []) + [result]
    
    if tracker:
        await tracker.agent_completed(
            "validator", 
            result.get("output", {}), 
            result.get("execution_time_ms", 0)
        )
    
    return state


async def strategize_node(state: AgentState, tracker: ExecutionTracker | None = None) -> AgentState:
    """Run the strategist agent."""
    if tracker:
        await tracker.agent_started("strategist")
    
    result = await strategist.execute({
        "raw_idea": state["raw_idea"],
        "brand_profile": state.get("brand_profile", {}),
        "validator_output": state.get("validator_output", {}),
    })
    
    state["strategy"] = result["output"]
    state["clarifying_questions"] = result["output"].get("clarifying_questions", [])
    state["format"] = result["output"].get("recommended_format", "text")
    state["current_agent"] = "strategist"
    state["status"] = "awaiting_answers"
    state["execution_log"] = state.get("execution_log", []) + [result]
    
    if tracker:
        await tracker.agent_completed(
            "strategist", 
            result.get("output", {}), 
            result.get("execution_time_ms", 0)
        )
    
    return state


async def write_node(state: AgentState, tracker: ExecutionTracker | None = None) -> AgentState:
    """Run the writer agent."""
    if tracker:
        await tracker.agent_started("writer")
    
    result = await writer.execute({
        "raw_idea": state["raw_idea"],
        "strategy": state.get("strategy", {}),
        "user_answers": state.get("user_answers", {}),
        "brand_profile": state.get("brand_profile", {}),
    })
    
    state["writer_output"] = result["output"]
    state["current_agent"] = "writer"
    state["execution_log"] = state.get("execution_log", []) + [result]
    
    if tracker:
        await tracker.agent_completed(
            "writer", 
            result.get("output", {}), 
            result.get("execution_time_ms", 0)
        )
    
    return state


async def visual_node(state: AgentState, tracker: ExecutionTracker | None = None) -> AgentState:
    """Run the visual specialist agent (for carousels only)."""
    if tracker:
        await tracker.agent_started("visual")
    
    result = await visual.execute({
        "raw_idea": state["raw_idea"],
        "writer_output": state.get("writer_output", {}),
        "brand_profile": state.get("brand_profile", {}),
    })
    
    state["visual_specs"] = result["output"]
    state["current_agent"] = "visual"
    state["execution_log"] = state.get("execution_log", []) + [result]
    
    if tracker:
        await tracker.agent_completed(
            "visual", 
            result.get("output", {}), 
            result.get("execution_time_ms", 0)
        )
    
    return state


async def optimize_node(state: AgentState, tracker: ExecutionTracker | None = None) -> AgentState:
    """Run the optimizer agent."""
    if tracker:
        await tracker.agent_started("optimizer")
    
    result = await optimizer.execute({
        "raw_idea": state["raw_idea"],
        "writer_output": state.get("writer_output", {}),
        "brand_profile": state.get("brand_profile", {}),
    })
    
    state["optimizer_output"] = result["output"]
    state["current_agent"] = "optimizer"
    state["execution_log"] = state.get("execution_log", []) + [result]
    
    if tracker:
        await tracker.agent_completed(
            "optimizer", 
            result.get("output", {}), 
            result.get("execution_time_ms", 0)
        )
    
    return state


async def finalize_node(state: AgentState) -> AgentState:
    """Compile final post from all agent outputs."""
    writer_out = state.get("writer_output", {})
    optimizer_out = state.get("optimizer_output", {})
    
    hooks = writer_out.get("hooks", [])
    best_hook = hooks[0] if hooks else {"text": "", "score": 0}
    
    state["final_post"] = {
        "format": state.get("format", "text"),
        "hook": best_hook,
        "body": writer_out.get("body_content", ""),
        "cta": writer_out.get("cta", ""),
        "hashtags": writer_out.get("hashtags", []),
        "visual_specs": state.get("visual_specs"),
        "quality_score": optimizer_out.get("quality_score", 0),
        "predicted_impressions": (
            optimizer_out.get("predicted_impressions_min", 0),
            optimizer_out.get("predicted_impressions_max", 0),
        ),
    }
    state["status"] = "completed"
    return state


# Routing functions
def route_after_validation(state: AgentState) -> str:
    """Route based on validator decision."""
    decision = state.get("validator_output", {}).get("decision", DECISION_APPROVE)
    if decision == DECISION_REJECT:
        return "end"
    return "strategize"


def route_after_writer(state: AgentState) -> str:
    """Route to visual agent if carousel, else to optimizer."""
    if state.get("format") == FORMAT_CAROUSEL:
        return "visual"
    return "optimize"


def route_after_optimizer(state: AgentState) -> str:
    """Route based on optimizer decision."""
    decision = state.get("optimizer_output", {}).get("decision", "APPROVE")
    revision = state.get("revision_count", 0)
    max_rev = state.get("max_revisions", 2)
    
    if decision == "REVISE" and revision < max_rev:
        state["revision_count"] = revision + 1
        return "write"
    return "finalize"


def build_workflow() -> StateGraph:
    """Build the LangGraph workflow."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("validate", validate_node)
    workflow.add_node("strategize", strategize_node)
    workflow.add_node("write", write_node)
    workflow.add_node("visual", visual_node)
    workflow.add_node("optimize", optimize_node)
    workflow.add_node("finalize", finalize_node)
    
    # Set entry point
    workflow.set_entry_point("validate")
    
    # Add edges
    workflow.add_conditional_edges("validate", route_after_validation, {
        "strategize": "strategize",
        "end": END,
    })
    workflow.add_edge("strategize", END)  # Pause for user answers
    workflow.add_conditional_edges("write", route_after_writer, {
        "visual": "visual",
        "optimize": "optimize",
    })
    workflow.add_edge("visual", "optimize")
    workflow.add_conditional_edges("optimize", route_after_optimizer, {
        "write": "write",
        "finalize": "finalize",
    })
    workflow.add_edge("finalize", END)
    
    return workflow


# Compiled workflow
_workflow = None


def get_workflow():
    """Get compiled workflow."""
    global _workflow
    if _workflow is None:
        _workflow = build_workflow().compile()
    return _workflow


async def run_generation(
    raw_idea: str,
    brand_profile: dict[str, Any] | None = None,
    user_id: str = "default",
) -> AgentState:
    """
    Run the full generation workflow.
    
    Returns state after strategist (awaiting_answers) or after completion.
    """
    workflow = get_workflow()
    
    initial_state: AgentState = {
        "raw_idea": raw_idea,
        "brand_profile": brand_profile or {},
        "user_id": user_id,
        "status": "processing",
        "revision_count": 0,
        "max_revisions": 2,
        "execution_log": [],
    }
    
    result = await workflow.ainvoke(initial_state)
    return result


async def continue_generation(
    state: AgentState,
    user_answers: dict[str, str],
    tracker: ExecutionTracker | None = None,
) -> AgentState:
    """
    Continue generation after user provides answers.
    
    Runs from writer through to completion.
    
    Args:
        state: Current agent state
        user_answers: Answers to clarifying questions
        tracker: Optional execution tracker for real-time events
    """
    state["user_answers"] = user_answers
    state["status"] = "processing"
    
    if tracker:
        await tracker.status_update("Starting content generation...", 35)
    
    # Run remaining nodes manually with tracker
    state = await write_node(state, tracker)
    
    if state.get("format") == FORMAT_CAROUSEL:
        state = await visual_node(state, tracker)
    
    state = await optimize_node(state, tracker)
    
    # Handle revisions
    revision_count = 0
    while (
        state.get("optimizer_output", {}).get("decision") == "REVISE"
        and state.get("revision_count", 0) < state.get("max_revisions", 2)
    ):
        revision_count += 1
        state["revision_count"] = state.get("revision_count", 0) + 1
        
        if tracker:
            await tracker.status_update(f"Revision {revision_count} - improving content...", 60)
        
        state = await write_node(state, tracker)
        if state.get("format") == FORMAT_CAROUSEL:
            state = await visual_node(state, tracker)
        state = await optimize_node(state, tracker)
    
    state = await finalize_node(state)
    
    if tracker:
        await tracker.complete(state.get("final_post"))
    
    return state


async def run_generation_with_tracking(
    raw_idea: str,
    post_id: str,
    brand_profile: dict[str, Any] | None = None,
    user_id: str = "default",
) -> tuple[AgentState, ExecutionTracker]:
    """
    Run generation with real-time execution tracking.
    
    Returns both the state and the tracker for accessing execution details.
    """
    tracker = get_tracker(post_id)
    
    initial_state: AgentState = {
        "raw_idea": raw_idea,
        "brand_profile": brand_profile or {},
        "user_id": user_id,
        "post_id": post_id,
        "status": "processing",
        "revision_count": 0,
        "max_revisions": 2,
        "execution_log": [],
    }
    
    await tracker.status_update("Starting idea validation...", 5)
    
    # Run validation and strategy with tracking
    state = await validate_node(initial_state, tracker)
    
    # Check for rejection
    validator_output = state.get("validator_output", {})
    if validator_output.get("decision") == DECISION_REJECT:
        state["status"] = "rejected"
        await tracker.status_update("Idea rejected - needs refinement", 100)
        return state, tracker
    
    state = await strategize_node(state, tracker)
    
    return state, tracker


async def continue_generation_with_tracking(
    state: AgentState,
    user_answers: dict[str, str],
    post_id: str,
) -> tuple[AgentState, ExecutionTracker]:
    """
    Continue generation with real-time execution tracking.
    
    Returns both the final state and the tracker.
    """
    tracker = get_tracker(post_id)
    
    result = await continue_generation(state, user_answers, tracker)
    
    return result, tracker

