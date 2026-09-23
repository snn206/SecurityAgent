"""Unit tests for planning layer."""
import pytest
from security_agent.core.base_planner import Plan, PlanStep


def test_plan_creation():
    step = PlanStep(step_id="s1", description="Scan", agent_id="tool_router", tools=["nmap"])
    plan = Plan(plan_id="p1", objective="Test scan", steps=[step])
    assert len(plan.steps) == 1
    assert plan.steps[0].tools == ["nmap"]


def test_plan_to_dict():
    plan = Plan(plan_id="p1", objective="Test", steps=[
        PlanStep(step_id="s1", description="Recon", agent_id="researcher")
    ])
    d = plan.to_dict()
    assert d["plan_id"] == "p1"
    assert len(d["steps"]) == 1
    assert d["steps"][0]["agent_id"] == "researcher"
