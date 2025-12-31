"""
LangGraph workflow for LinkedIn content generation.

Orchestrates the 5 agents in sequence with conditional routing.
"""

import logging
from typing import Any
from langgraph.graph import StateGraph, END

from src.orchestration.state import AgentState
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


async def validate_node(state: AgentState) -> AgentState:
    """Run the validator agent."""
    result = await validator.execute({
        "raw_idea": state["raw_idea"],
        "brand_profile": state.get("brand_profile", {}),
    })
    
    state["validator_output"] = result["output"]
    state["current_agent"] = "validator"
    state["execution_log"] = state.get("execution_log", []) + [result]
    return state


async def strategize_node(state: AgentState) -> AgentState:
    """Run the strategist agent."""
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
    return state


async def write_node(state: AgentState) -> AgentState:
    """Run the writer agent."""
    result = await writer.execute({
        "raw_idea": state["raw_idea"],
        "strategy": state.get("strategy", {}),
        "user_answers": state.get("user_answers", {}),
        "brand_profile": state.get("brand_profile", {}),
    })
    
    state["writer_output"] = result["output"]
    state["current_agent"] = "writer"
    state["execution_log"] = state.get("execution_log", []) + [result]
    return state


async def visual_node(state: AgentState) -> AgentState:
    """Run the visual specialist agent (for carousels only)."""
    result = await visual.execute({
        "raw_idea": state["raw_idea"],
        "writer_output": state.get("writer_output", {}),
        "brand_profile": state.get("brand_profile", {}),
    })
    
    state["visual_specs"] = result["output"]
    state["current_agent"] = "visual"
    state["execution_log"] = state.get("execution_log", []) + [result]
    return state


async def optimize_node(state: AgentState) -> AgentState:
    """Run the optimizer agent."""
    result = await optimizer.execute({
        "raw_idea": state["raw_idea"],
        "writer_output": state.get("writer_output", {}),
        "brand_profile": state.get("brand_profile", {}),
    })
    
    state["optimizer_output"] = result["output"]
    state["current_agent"] = "optimizer"
    state["execution_log"] = state.get("execution_log", []) + [result]
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
) -> AgentState:
    """
    Continue generation after user provides answers.
    
    Runs from writer through to completion.
    """
    state["user_answers"] = user_answers
    state["status"] = "processing"
    
    # Run remaining nodes manually
    state = await write_node(state)
    
    if state.get("format") == FORMAT_CAROUSEL:
        state = await visual_node(state)
    
    state = await optimize_node(state)
    
    # Handle revisions
    while (
        state.get("optimizer_output", {}).get("decision") == "REVISE"
        and state.get("revision_count", 0) < state.get("max_revisions", 2)
    ):
        state["revision_count"] = state.get("revision_count", 0) + 1
        state = await write_node(state)
        if state.get("format") == FORMAT_CAROUSEL:
            state = await visual_node(state)
        state = await optimize_node(state)
    
    state = await finalize_node(state)
    return state
