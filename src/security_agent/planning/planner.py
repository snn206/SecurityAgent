"""LangGraph-based planning agent — produces structured execution plans."""

from __future__ import annotations

import json
import uuid
from typing import Any

from security_agent.core.base_planner import BasePlanner, Plan, PlanStep
from security_agent.core.base_provider import ChatMessage
from security_agent.core.exceptions import PlanningError
from security_agent.providers.registry import get_registry

SYSTEM_PROMPT = """You are a security research planning agent.
Given a user objective, produce a detailed execution plan in JSON format.

The plan must be:
- Structured with numbered steps
- Each step has: step_id, description, agent_id, tools (list), depends_on (list of step_ids)
- Agent IDs: orchestrator, planner, reasoner, researcher, tool_router, analyzer, reporter
- Tool IDs: nmap, gobuster, sqlmap, nikto, whois, curl, shell

Return ONLY valid JSON. No explanation text outside the JSON.

JSON format:
{
  "plan_id": "<uuid>",
  "objective": "<user objective>",
  "scope": "<target scope>",
  "steps": [
    {
      "step_id": "step_1",
      "description": "...",
      "agent_id": "researcher",
      "tools": ["whois"],
      "depends_on": []
    }
  ],
  "constraints": ["..."]
}"""


class PlannerAgent(BasePlanner):
    """Creates execution plans using the configured planning provider."""

    strategy_name = "planner"

    def __init__(self, provider_id: str | None = None, model: str | None = None) -> None:
        self._provider_id = provider_id
        self._model = model

    def _get_provider(self):
        registry = get_registry()
        if self._provider_id:
            return registry.get(self._provider_id)
        return registry.get_default()

    async def create_plan(
        self,
        objective: str,
        context: dict[str, Any] | None = None,
    ) -> Plan:
        provider = self._get_provider()
        messages = [
            ChatMessage(role="system", content=SYSTEM_PROMPT),
            ChatMessage(
                role="user", content=f"Objective: {objective}\nContext: {json.dumps(context or {})}"
            ),
        ]
        try:
            response = await provider.chat(
                messages, model=self._model, temperature=0.1, max_tokens=4096
            )
            raw = response.content.strip()
            # Strip markdown code block if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            data = json.loads(raw)
            return self._parse_plan(data)
        except json.JSONDecodeError as exc:
            raise PlanningError(f"Planner returned invalid JSON: {exc}") from exc
        except Exception as exc:
            raise PlanningError(f"Planning failed: {exc}") from exc

    async def revise_plan(
        self,
        plan: Plan,
        feedback: str,
        context: dict[str, Any] | None = None,
    ) -> Plan:
        provider = self._get_provider()
        messages = [
            ChatMessage(role="system", content=SYSTEM_PROMPT),
            ChatMessage(
                role="user",
                content=(
                    f"Revise this plan based on feedback.\n\n"
                    f"Current plan:\n{json.dumps(plan.to_dict(), indent=2)}\n\n"
                    f"Feedback: {feedback}"
                ),
            ),
        ]
        response = await provider.chat(
            messages, model=self._model, temperature=0.1, max_tokens=4096
        )
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
        return self._parse_plan(data)

    @staticmethod
    def _parse_plan(data: dict[str, Any]) -> Plan:
        steps = [
            PlanStep(
                step_id=s.get("step_id", f"step_{i}"),
                description=s.get("description", ""),
                agent_id=s.get("agent_id", "tool_router"),
                tools=s.get("tools", []),
                depends_on=s.get("depends_on", []),
                metadata=s.get("metadata", {}),
            )
            for i, s in enumerate(data.get("steps", []))
        ]
        return Plan(
            plan_id=data.get("plan_id", str(uuid.uuid4())),
            objective=data.get("objective", ""),
            scope=data.get("scope", ""),
            steps=steps,
            constraints=data.get("constraints", []),
        )
