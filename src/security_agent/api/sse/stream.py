"""SSE stream endpoint — server-sent events for execution monitoring."""
from __future__ import annotations

import asyncio
import json
from typing import AsyncGenerator

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from security_agent.core.events import EventBus, AgentEvent
from security_agent.graph.nodes import get_event_bus

sse_router = APIRouter()


async def _event_generator(execution_id: str) -> AsyncGenerator[dict, None]:
    bus = get_event_bus()
    queue: asyncio.Queue[AgentEvent] = asyncio.Queue()

    async def enqueue(event: AgentEvent) -> None:
        await queue.put(event)

    bus.subscribe(enqueue, execution_id=execution_id)

    try:
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield {
                    "event": event.event_type.value,
                    "data": json.dumps(event.to_dict(), default=str),
                    "id": event.event_id,
                }
                if event.event_type.value in ("task.completed", "task.failed", "task.cancelled"):
                    break
            except asyncio.TimeoutError:
                yield {"event": "ping", "data": "keepalive"}
    finally:
        bus.unsubscribe(enqueue, execution_id=execution_id)


@sse_router.get("/stream/{execution_id}")
async def sse_stream(execution_id: str) -> EventSourceResponse:
    """SSE endpoint — stream execution events."""
    return EventSourceResponse(_event_generator(execution_id))
