"""Executions router — view execution trace and history."""
from __future__ import annotations
from typing import Any
from fastapi import APIRouter, HTTPException
from security_agent.api.app import get_store

router = APIRouter(tags=["executions"])

@router.get("/executions/{execution_id}")
async def get_execution(execution_id: str) -> dict[str, Any]:
    store = get_store()
    record = await store.get_execution(execution_id)
    if not record:
        raise HTTPException(status_code=404, detail="Execution not found")
    return {
        "execution_id": record.id,
        "task_id": record.task_id,
        "status": record.status,
        "user_request": record.user_request,
        "scope": record.scope,
        "plan": record.plan,
        "provider": record.provider,
        "model": record.model,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "completed_at": record.completed_at.isoformat() if record.completed_at else None,
        "duration_seconds": record.duration_seconds,
    }

@router.get("/executions/{execution_id}/events")
async def get_execution_events(execution_id: str) -> dict[str, Any]:
    store = get_store()
    events = await store.get_events(execution_id)
    return {
        "execution_id": execution_id,
        "events": [
            {
                "event_id": e.id,
                "event_type": e.event_type,
                "agent_id": e.agent_id,
                "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                "payload": e.payload,
            }
            for e in events
        ],
    }
