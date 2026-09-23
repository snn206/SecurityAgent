"""Abstract base class for planning strategies."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PlanStep:
    """A single step in an execution plan."""

    step_id: str
    description: str
    agent_id: str
    tools: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Plan:
    """A structured execution plan produced by the Planner."""

    plan_id: str
    objective: str
    steps: list[PlanStep]
    scope: str = ""
    constraints: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "objective": self.objective,
            "scope": self.scope,
            "steps": [
                {
                    "step_id": s.step_id,
                    "description": s.description,
                    "agent_id": s.agent_id,
                    "tools": s.tools,
                    "depends_on": s.depends_on,
                }
                for s in self.steps
            ],
            "constraints": self.constraints,
        }


class BasePlanner(ABC):
    """Abstract planner. Planning strategies must subclass this."""

    strategy_name: str

    @abstractmethod
    async def create_plan(
        self,
        objective: str,
        context: dict[str, Any] | None = None,
    ) -> Plan:
        """Generate an execution plan from an objective."""
        ...

    @abstractmethod
    async def revise_plan(
        self,
        plan: Plan,
        feedback: str,
        context: dict[str, Any] | None = None,
    ) -> Plan:
        """Revise an existing plan given feedback."""
        ...
