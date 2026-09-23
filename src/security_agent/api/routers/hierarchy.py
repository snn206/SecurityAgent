"""API router for Multi-Agent Hierarchy and Parent Task Queue."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from security_agent.orchestration.hierarchy import get_hierarchy_manager
from security_agent.orchestration.task_queue import get_task_queue

router = APIRouter(prefix="/hierarchy", tags=["hierarchy"])


class EnqueueTaskRequest(BaseModel):
    title: str
    goal: str
    target: str
    domain: str = Field(default="recon", description="recon, vuln, exploit, or general")
    priority: int = Field(default=1, ge=1, le=10)


@router.get("")
async def get_hierarchy_topology() -> dict[str, Any]:
    """Retrieve full live 1-3-2 agent hierarchy topology."""
    mgr = get_hierarchy_manager()
    return mgr.get_topology()


@router.get("/queue")
async def get_queue_status() -> dict[str, Any]:
    """Retrieve Parent Task Queue metrics and pending tasks."""
    queue = get_task_queue()
    return queue.get_status()


@router.post("/queue", status_code=201)
async def enqueue_parent_task(req: EnqueueTaskRequest) -> dict[str, Any]:
    """Manually enqueue or dispatch a task to the parent agents."""
    queue = get_task_queue()
    task = await queue.enqueue(
        title=req.title,
        goal=req.goal,
        target=req.target,
        domain=req.domain,
        priority=req.priority,
    )
    return {"status": "enqueued", "task": task}
