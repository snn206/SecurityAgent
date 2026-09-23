"""Event system for SecurityAgent — real-time execution visibility."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Awaitable
import uuid


class EventType(str, Enum):
    # Task lifecycle
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_CANCELLED = "task.cancelled"

    # Agent activity
    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"
    AGENT_THINKING = "agent.thinking"

    # Planning
    PLAN_CREATED = "plan.created"
    PLAN_STEP_STARTED = "plan.step.started"
    PLAN_STEP_COMPLETED = "plan.step.completed"

    # Provider / model
    PROVIDER_REQUEST = "provider.request"
    PROVIDER_RESPONSE = "provider.response"
    PROVIDER_STREAM_CHUNK = "provider.stream.chunk"
    PROVIDER_TOKEN_USAGE = "provider.token_usage"

    # Tool selection & execution
    TOOL_SELECTED = "tool.selected"
    TOOL_STARTED = "tool.started"
    TOOL_COMPLETED = "tool.completed"
    TOOL_FAILED = "tool.failed"

    # Sandbox / Docker
    SANDBOX_STARTED = "sandbox.started"
    SANDBOX_COMMAND = "sandbox.command"
    SANDBOX_STDOUT = "sandbox.stdout"
    SANDBOX_STDERR = "sandbox.stderr"
    SANDBOX_EXIT = "sandbox.exit"

    # Results
    FINDING = "finding"
    ARTIFACT_CREATED = "artifact.created"
    REPORT_GENERATED = "report.generated"

    # Errors
    WARNING = "warning"
    ERROR = "error"


@dataclass
class AgentEvent:
    """A single timestamped execution event."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    execution_id: str = ""
    event_type: EventType = EventType.WARNING
    agent_id: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "execution_id": self.execution_id,
            "event_type": self.event_type.value,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp.isoformat(),
            "payload": self.payload,
        }


EventHandler = Callable[[AgentEvent], Awaitable[None]]


class EventBus:
    """Async in-process event bus. Subscribers receive events by execution_id or wildcard."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = {}  # execution_id → handlers
        self._global_handlers: list[EventHandler] = []

    def subscribe(self, handler: EventHandler, execution_id: str | None = None) -> None:
        """Subscribe to events. If execution_id is None, receives all events."""
        if execution_id is None:
            self._global_handlers.append(handler)
        else:
            self._handlers.setdefault(execution_id, []).append(handler)

    def unsubscribe(self, handler: EventHandler, execution_id: str | None = None) -> None:
        if execution_id is None:
            self._global_handlers = [h for h in self._global_handlers if h is not handler]
        else:
            handlers = self._handlers.get(execution_id, [])
            self._handlers[execution_id] = [h for h in handlers if h is not handler]

    async def emit(
        self,
        event_type: EventType,
        execution_id: str = "",
        agent_id: str = "",
        payload: dict[str, Any] | None = None,
    ) -> None:
        event = AgentEvent(
            execution_id=execution_id,
            event_type=event_type,
            agent_id=agent_id,
            payload=payload or {},
        )
        tasks: list[Awaitable[None]] = []
        for handler in self._global_handlers:
            tasks.append(handler(event))
        for handler in self._handlers.get(execution_id, []):
            tasks.append(handler(event))
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
