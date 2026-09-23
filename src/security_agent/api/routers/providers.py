"""Providers router — list available providers."""
from __future__ import annotations
from fastapi import APIRouter
from security_agent.providers.registry import get_registry

router = APIRouter(tags=["providers"])

@router.get("/providers")
async def list_providers() -> dict:
    try:
        registry = get_registry()
        return {"providers": registry.list()}
    except Exception as exc:
        return {"providers": [], "error": str(exc)}
