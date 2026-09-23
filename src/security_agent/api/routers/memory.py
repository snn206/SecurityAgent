"""API router for User Memory & Brain Management."""
from __future__ import annotations

from typing import Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from security_agent.memory.manager import get_memory_manager

router = APIRouter(prefix="/memory", tags=["memory"])


class MemoryCreateRequest(BaseModel):
    collection: str = Field(default="golden_rules", description="Collection: golden_rules, lessons_learned, target_knowledge")
    title: str = Field(..., description="Short summary / title of the rule or lesson")
    content: str = Field(..., description="Guideline, rule body, or insight")
    target: str | None = Field(default=None, description="Optional target or subnet scope")
    category: str | None = Field(default="general", description="Category: recon, vuln, exploit, safety, general")
    recommended_flags: str | None = Field(default=None, description="Tool flags or parameters")


class MemoryUpdateRequest(BaseModel):
    title: str | None = None
    content: str | None = None
    category: str | None = None
    recommended_flags: str | None = None


class ResetRequest(BaseModel):
    collection: str | None = None  # None resets all


@router.get("")
async def list_memories(
    collection: str = Query(default="lessons_learned"),
    category: str | None = Query(default=None),
    search: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict[str, Any]:
    """List memories for user inspection with optional search and category filters."""
    mgr = get_memory_manager()
    items = mgr.list_memories(collection=collection, category=category, search_query=search, limit=limit)
    return {
        "collection": collection,
        "count": len(items),
        "items": items,
    }


@router.post("", status_code=201)
async def create_memory(req: MemoryCreateRequest) -> dict[str, Any]:
    """Add a new User Golden Rule or manual memory item."""
    mgr = get_memory_manager()
    doc = {
        "title": req.title,
        "insight": req.content,
        "rule": req.content,
        "target": req.target,
        "category": req.category or "general",
        "recommended_flags": req.recommended_flags,
        "source": "USER_INJECTED",
    }
    doc_id = mgr.add_memory(req.collection, doc)
    return {"status": "created", "_id": doc_id, "collection": req.collection}


@router.get("/{collection}/{memory_id}")
async def get_memory(collection: str, memory_id: str) -> dict[str, Any]:
    """Fetch a single memory document."""
    mgr = get_memory_manager()
    doc = mgr.get_memory(collection, memory_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Memory not found")
    return doc


@router.put("/{collection}/{memory_id}")
async def update_memory(
    collection: str, memory_id: str, req: MemoryUpdateRequest
) -> dict[str, Any]:
    """Edit or correct an existing memory document."""
    mgr = get_memory_manager()
    updates: dict[str, Any] = {}
    if req.title is not None:
        updates["title"] = req.title
    if req.content is not None:
        updates["insight"] = req.content
        updates["rule"] = req.content
    if req.category is not None:
        updates["category"] = req.category
    if req.recommended_flags is not None:
        updates["recommended_flags"] = req.recommended_flags

    success = mgr.update_memory(collection, memory_id, updates)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"status": "updated", "_id": memory_id}


@router.delete("/{collection}/{memory_id}")
async def delete_memory(collection: str, memory_id: str) -> dict[str, Any]:
    """Delete a memory item."""
    mgr = get_memory_manager()
    success = mgr.delete_memory(collection, memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"status": "deleted", "_id": memory_id}


@router.post("/reset")
async def reset_memory(req: ResetRequest) -> dict[str, Any]:
    """Reset/purge memory collections."""
    mgr = get_memory_manager()
    if req.collection:
        mgr.reset_collection(req.collection)
        return {"status": "reset", "collection": req.collection}
    else:
        mgr.reset_all()
        return {"status": "reset_all"}
