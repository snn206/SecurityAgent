"""Unit tests for event system."""
import pytest
import asyncio
from security_agent.core.events import EventBus, EventType, AgentEvent


@pytest.mark.asyncio
async def test_event_bus_subscribe():
    bus = EventBus()
    received = []

    async def handler(event: AgentEvent):
        received.append(event)

    bus.subscribe(handler)
    await bus.emit(EventType.TASK_STARTED, execution_id="exec-1", agent_id="test")
    assert len(received) == 1
    assert received[0].event_type == EventType.TASK_STARTED


@pytest.mark.asyncio
async def test_event_bus_execution_scoped():
    bus = EventBus()
    received = []

    async def handler(event: AgentEvent):
        received.append(event)

    bus.subscribe(handler, execution_id="exec-1")
    await bus.emit(EventType.AGENT_STARTED, execution_id="exec-2")  # Different ID
    assert len(received) == 0
    await bus.emit(EventType.AGENT_STARTED, execution_id="exec-1")
    assert len(received) == 1
