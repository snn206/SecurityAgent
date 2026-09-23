"""Abstract base class for all SecurityAgent agents."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .state import AgentState
from .events import EventBus


class BaseAgent(ABC):
    """Abstract base for all agents.

    Agents are LangGraph nodes. They receive the current AgentState,
    perform their task, and return a state update dict.
    """

    agent_id: str
    agent_name: str

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._event_bus = event_bus or EventBus()

    @abstractmethod
    async def run(self, state: AgentState) -> dict[str, Any]:
        """Execute agent logic. Returns a partial state update."""
        ...

    async def emit(self, event_type: str, payload: dict[str, Any]) -> None:
        """Emit an execution event."""
        await self._event_bus.emit(
            execution_id=str(state_execution_id := payload.get("execution_id", "")),
            event_type=event_type,
            agent_id=self.agent_id,
            payload=payload,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.agent_id!r})"
