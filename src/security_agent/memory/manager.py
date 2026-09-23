"""Agent Memory and Brain Manager.

Provides comprehensive memory storage and user management for:
- Auto-distilled JEV lessons learned
- User-injected Golden Rules & policy constraints
- Target profiles & cross-mission intelligence
"""
from __future__ import annotations

import re
from typing import Any
from security_agent.storage.document_store import DocumentStore, get_document_store


class MemoryManager:
    """Manages agent brain memory with full user inspection and editing capabilities."""

    COLLECTIONS = ["lessons_learned", "golden_rules", "target_knowledge"]

    def __init__(self, doc_store: DocumentStore | None = None) -> None:
        self.doc_store = doc_store or get_document_store()

    def list_memories(
        self,
        collection: str = "lessons_learned",
        category: str | None = None,
        search_query: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """List and search memories with optional category and keyword filtering."""
        filter_dict: dict[str, Any] = {}
        if category and category.lower() != "all":
            filter_dict["category"] = category

        docs = self.doc_store.find(collection, filter_dict=filter_dict, sort_by="updated_at", limit=limit)

        if search_query and search_query.strip():
            q = search_query.lower().strip()
            docs = [
                d for d in docs
                if q in str(d.get("title", "")).lower()
                or q in str(d.get("insight", "")).lower()
                or q in str(d.get("target", "")).lower()
                or q in str(d.get("rule", "")).lower()
            ]

        return docs

    def get_memory(self, collection: str, memory_id: str) -> dict[str, Any] | None:
        """Retrieve a specific memory document by its _id."""
        return self.doc_store.find_one(collection, {"_id": memory_id})

    def add_memory(self, collection: str, document: dict[str, Any]) -> str:
        """Add a new memory or user-specified Golden Rule."""
        doc = dict(document)
        if collection not in self.COLLECTIONS:
            collection = "golden_rules"
        if "source" not in doc:
            doc["source"] = "USER_INJECTED"
        return self.doc_store.insert_one(collection, doc)

    def update_memory(
        self, collection: str, memory_id: str, updates: dict[str, Any]
    ) -> bool:
        """Update/edit an existing memory (e.g. user correcting agent knowledge)."""
        clean_updates = {k: v for k, v in updates.items() if k not in ("_id", "created_at")}
        return self.doc_store.update_one(collection, {"_id": memory_id}, clean_updates)

    def delete_memory(self, collection: str, memory_id: str) -> bool:
        """Delete/forget a memory item."""
        return self.doc_store.delete_one(collection, {"_id": memory_id})

    def reset_collection(self, collection: str) -> None:
        """Purge all memories from a collection."""
        self.doc_store.clear_collection(collection)

    def reset_all(self) -> None:
        """Purge all memory collections."""
        for col in self.COLLECTIONS:
            self.doc_store.clear_collection(col)

    def get_consolidated_context(self, target: str, tools: list[str] | None = None) -> str:
        """Assemble relevant memory (rules + lessons) to inject into agent prompt."""
        # 1. Fetch user golden rules
        rules = self.doc_store.find("golden_rules", limit=15)
        # 2. Fetch past lessons for this target or general tools
        lessons = self.doc_store.find("lessons_learned", limit=20)
        target_lessons = [l for l in lessons if l.get("target") == target]
        general_lessons = [l for l in lessons if l.get("target") != target][:5]

        parts: list[str] = []

        if rules:
            parts.append("### USER GOLDEN RULES & CONSTRAINTS:")
            for r in rules:
                rule_text = r.get("rule") or r.get("insight") or r.get("title")
                parts.append(f"- {rule_text}")

        relevant_lessons = target_lessons + general_lessons
        if relevant_lessons:
            parts.append("\n### DISTILLED EXPERIENCE & PAST LESSONS:")
            for l in relevant_lessons:
                title = l.get("title", "")
                insight = l.get("insight", "")
                flags = l.get("recommended_flags", "")
                flags_str = f" [Recommended flags: {flags}]" if flags else ""
                parts.append(f"- {title}: {insight}{flags_str}")

        return "\n".join(parts) if parts else ""


_global_memory_manager: MemoryManager | None = None


def get_memory_manager() -> MemoryManager:
    """Singleton getter for MemoryManager."""
    global _global_memory_manager
    if _global_memory_manager is None:
        _global_memory_manager = MemoryManager()
    return _global_memory_manager
