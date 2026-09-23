"""Conditional edge functions for the SecurityAgent LangGraph."""
from __future__ import annotations

from security_agent.core.state import AgentState


def route_after_planning(state: AgentState) -> str:
    """Route from planner node."""
    if state.get("status") == "failed":
        return "END"
    plan = state.get("plan") or {}
    steps = plan.get("steps", [])
    if not steps:
        return "reporter"
    current_step_id = state.get("current_step_id")
    if not current_step_id:
        return "reporter"
    return "tool_router"


def route_after_tool(state: AgentState) -> str:
    """Route after sandbox execution."""
    exit_code = state.get("sandbox_exit_code")
    # Always analyze — even if tool failed
    return "analyzer"


def route_after_analysis(state: AgentState) -> str:
    """Route after analysis: more steps or report."""
    current_step_id = state.get("current_step_id")
    if current_step_id:
        return "tool_router"
    return "reporter"
