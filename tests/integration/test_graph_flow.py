"""Integration tests for LangGraph workflow.
These tests use mocked providers to avoid real API calls.
"""
import pytest
from unittest.mock import AsyncMock, patch
from security_agent.graph.edges import route_after_planning, route_after_tool, route_after_analysis


def test_route_after_planning_no_steps():
    state = {"plan": {"steps": []}, "status": "executing"}
    assert route_after_planning(state) == "reporter"


def test_route_after_planning_has_steps():
    state = {
        "plan": {"steps": [{"step_id": "s1", "description": "scan"}]},
        "current_step_id": "s1",
        "status": "executing"
    }
    assert route_after_planning(state) == "tool_router"


def test_route_after_tool_always_analyzes():
    state = {"sandbox_exit_code": 0}
    assert route_after_tool(state) == "analyzer"


def test_route_after_analysis_more_steps():
    state = {"current_step_id": "s2"}
    assert route_after_analysis(state) == "tool_router"


def test_route_after_analysis_done():
    state = {"current_step_id": None}
    assert route_after_analysis(state) == "reporter"
