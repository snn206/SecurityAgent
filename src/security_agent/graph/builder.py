"""LangGraph StateGraph builder for SecurityAgent."""
from __future__ import annotations

from langgraph.graph import StateGraph, END

from security_agent.core.state import AgentState
from .nodes import (
    planner_node,
    reasoner_node,
    tool_router_node,
    sandbox_executor_node,
    analyzer_node,
    reporter_node,
)
from .edges import (
    route_after_planning,
    route_after_tool,
    route_after_analysis,
)


def build_graph(checkpointer=None) -> StateGraph:
    """Build and compile the main SecurityAgent LangGraph."""

    graph = StateGraph(AgentState)

    # ── Nodes ─────────────────────────────────────────────────────────────────
    graph.add_node("planner", planner_node)
    graph.add_node("reasoner", reasoner_node)
    graph.add_node("tool_router", tool_router_node)
    graph.add_node("sandbox_executor", sandbox_executor_node)
    graph.add_node("analyzer", analyzer_node)
    graph.add_node("reporter", reporter_node)

    # ── Entry point ────────────────────────────────────────────────────────────
    graph.set_entry_point("planner")

    # ── Edges ─────────────────────────────────────────────────────────────────
    # After planning → decide: execute next step or reason
    graph.add_conditional_edges(
        "planner",
        route_after_planning,
        {
            "tool_router": "tool_router",
            "reasoner": "reasoner",
            "reporter": "reporter",
            END: END,
        },
    )

    # Reasoner always goes back to tool_router (picks next step)
    graph.add_edge("reasoner", "tool_router")

    # Tool router → sandbox
    graph.add_edge("tool_router", "sandbox_executor")

    # After sandbox execution → decide: analyze, or route next tool
    graph.add_conditional_edges(
        "sandbox_executor",
        route_after_tool,
        {
            "analyzer": "analyzer",
            "tool_router": "tool_router",
            "reporter": "reporter",
        },
    )

    # Analyzer → decide: more steps needed or report
    graph.add_conditional_edges(
        "analyzer",
        route_after_analysis,
        {
            "planner": "planner",     # re-plan if needed
            "tool_router": "tool_router",
            "reporter": "reporter",
        },
    )

    # Reporter is the terminal node
    graph.add_edge("reporter", END)

    return graph.compile(checkpointer=checkpointer)
