"""Tasks router — submit and monitor tasks."""
from __future__ import annotations

import uuid
import asyncio
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from security_agent.execution.history import HistoryStore, get_store  # type: ignore[attr-defined]
from security_agent.graph.builder import build_graph
from security_agent.graph.nodes import get_event_bus

router = APIRouter(tags=["tasks"])


class TaskRequest(BaseModel):
    user_request: str = Field(..., description="The security task to perform")
    scope: str = Field(default="", description="Target scope (IP, domain, URL range)")
    provider: str = Field(default="", description="Override default provider")
    model: str = Field(default="", description="Override default model")


class TaskResponse(BaseModel):
    task_id: str
    execution_id: str
    status: str
    created_at: str


async def _run_graph(execution_id: str, task_id: str, request: TaskRequest) -> None:
    """Background task: run the LangGraph workflow."""
    from security_agent.execution.history import get_store
    from security_agent.api.app import get_ws_manager

    store = get_store()
    bus = get_event_bus()

    # Wire event bus → WebSocket broadcaster
    ws_manager = get_ws_manager()

    async def broadcast_event(event: Any) -> None:
        await ws_manager.broadcast(execution_id, event.to_dict())

    bus.subscribe(broadcast_event, execution_id=execution_id)

    try:
        await store.update_execution(execution_id, status="running")
        graph = build_graph()
        initial_state = {
            "execution_id": execution_id,
            "task_id": task_id,
            "user_request": request.user_request,
            "scope": request.scope,
            "status": "planning",
            "messages": [],
            "findings": [],
            "artifacts": [],
            "completed_steps": [],
        }
        async for event in graph.astream(initial_state, config={"configurable": {"thread_id": execution_id}}):
            pass  # Events emitted via EventBus
    except Exception as exc:
        await store.update_execution(
            execution_id, status="failed",
            completed_at=datetime.now(timezone.utc),
        )
    finally:
        bus.unsubscribe(broadcast_event, execution_id=execution_id)


@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    request: TaskRequest,
    background_tasks: BackgroundTasks,
) -> TaskResponse:
    """Submit a new security task."""
    store = get_store()
    task_id = str(uuid.uuid4())
    execution_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    await store.create_execution(
        execution_id=execution_id,
        task_id=task_id,
        user_request=request.user_request,
        scope=request.scope,
    )

    background_tasks.add_task(_run_graph, execution_id, task_id, request)

    return TaskResponse(
        task_id=task_id,
        execution_id=execution_id,
        status="pending",
        created_at=now.isoformat(),
    )


@router.get("/tasks/{task_id}")
async def get_task(task_id: str) -> dict[str, Any]:
    """Get task status."""
    store = get_store()
    # Find by task_id
    executions = await store.list_executions(limit=1000)
    record = next((e for e in executions if e.task_id == task_id), None)
    if not record:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "task_id": record.task_id,
        "execution_id": record.id,
        "status": record.status,
        "user_request": record.user_request,
        "scope": record.scope,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "completed_at": record.completed_at.isoformat() if record.completed_at else None,
    }


@router.get("/tasks")
async def list_tasks(limit: int = 20, offset: int = 0) -> dict[str, Any]:
    """List recent tasks."""
    store = get_store()
    records = await store.list_executions(limit=limit, offset=offset)
    return {
        "tasks": [
            {
                "task_id": r.task_id,
                "execution_id": r.id,
                "status": r.status,
                "user_request": r.user_request[:100],
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records
        ],
        "total": len(records),
    }
