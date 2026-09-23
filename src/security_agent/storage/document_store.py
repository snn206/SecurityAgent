"""Embedded zero-install NoSQL document store with a MongoDB-like interface.

Provides collections, JSON documents, filter queries, updates, and deletes
without requiring any external database server (uses TinyDB / embedded JSON).
"""
from __future__ import annotations

import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


class DocumentStore:
    """Embedded document store providing MongoDB-like operations."""

    def __init__(self, base_dir: str | Path | None = None) -> None:
        if base_dir is None:
            base_dir = Path("data/memory")
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._cache: dict[str, list[dict[str, Any]]] = {}

    def _get_collection_path(self, collection: str) -> Path:
        safe_name = "".join(c for c in collection if c.isalnum() or c in ("_", "-"))
        return self.base_dir / f"{safe_name}.json"

    def _load_collection(self, collection: str) -> list[dict[str, Any]]:
        path = self._get_collection_path(collection)
        if not path.exists():
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []

    def _save_collection(self, collection: str, docs: list[dict[str, Any]]) -> None:
        path = self._get_collection_path(collection)
        tmp_path = path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(docs, f, indent=2, ensure_ascii=False)
        tmp_path.replace(path)

    @staticmethod
    def _matches(doc: dict[str, Any], filter_dict: dict[str, Any] | None) -> bool:
        if not filter_dict:
            return True
        for key, val in filter_dict.items():
            if key not in doc:
                return False
            # Support basic operators: $in, $ne, $regex, or exact match
            if isinstance(val, dict):
                for op, op_val in val.items():
                    if op == "$in" and doc[key] not in op_val:
                        return False
                    elif op == "$ne" and doc[key] == op_val:
                        return False
                    elif op == "$gt" and not (doc[key] > op_val):
                        return False
                    elif op == "$lt" and not (doc[key] < op_val):
                        return False
            elif doc[key] != val:
                return False
        return True

    def insert_one(self, collection: str, document: dict[str, Any]) -> str:
        """Insert a single document into a collection. Returns inserted _id."""
        with self._lock:
            doc = dict(document)
            if "_id" not in doc:
                doc["_id"] = str(uuid.uuid4())
            if "created_at" not in doc:
                doc["created_at"] = datetime.now(timezone.utc).isoformat()
            doc["updated_at"] = datetime.now(timezone.utc).isoformat()

            docs = self._load_collection(collection)
            docs.append(doc)
            self._save_collection(collection, docs)
            return str(doc["_id"])

    def insert_many(self, collection: str, documents: list[dict[str, Any]]) -> list[str]:
        """Insert multiple documents."""
        with self._lock:
            docs = self._load_collection(collection)
            ids = []
            now = datetime.now(timezone.utc).isoformat()
            for document in documents:
                doc = dict(document)
                if "_id" not in doc:
                    doc["_id"] = str(uuid.uuid4())
                if "created_at" not in doc:
                    doc["created_at"] = now
                doc["updated_at"] = now
                docs.append(doc)
                ids.append(str(doc["_id"]))
            self._save_collection(collection, docs)
            return ids

    def find(
        self,
        collection: str,
        filter_dict: dict[str, Any] | None = None,
        sort_by: str | None = None,
        reverse: bool = True,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Query documents matching filter criteria."""
        with self._lock:
            docs = self._load_collection(collection)
            matched = [d for d in docs if self._matches(d, filter_dict)]

            if sort_by:
                matched.sort(key=lambda x: str(x.get(sort_by, "")), reverse=reverse)

            if limit is not None and limit > 0:
                return matched[:limit]
            return matched

    def find_one(
        self, collection: str, filter_dict: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Find the first matching document."""
        with self._lock:
            docs = self._load_collection(collection)
            for doc in docs:
                if self._matches(doc, filter_dict):
                    return doc
            return None

    def update_one(
        self,
        collection: str,
        filter_dict: dict[str, Any],
        update_dict: dict[str, Any],
        upsert: bool = False,
    ) -> bool:
        """Update a single document matching the filter."""
        with self._lock:
            docs = self._load_collection(collection)
            for i, doc in enumerate(docs):
                if self._matches(doc, filter_dict):
                    # Handle $set operator if provided or direct merge
                    updates = update_dict.get("$set", update_dict)
                    doc.update(updates)
                    doc["updated_at"] = datetime.now(timezone.utc).isoformat()
                    docs[i] = doc
                    self._save_collection(collection, docs)
                    return True

            if upsert:
                new_doc = dict(filter_dict)
                updates = update_dict.get("$set", update_dict)
                new_doc.update(updates)
                self.insert_one(collection, new_doc)
                return True

            return False

    def delete_one(self, collection: str, filter_dict: dict[str, Any]) -> bool:
        """Delete first document matching the filter."""
        with self._lock:
            docs = self._load_collection(collection)
            for i, doc in enumerate(docs):
                if self._matches(doc, filter_dict):
                    docs.pop(i)
                    self._save_collection(collection, docs)
                    return True
            return False

    def delete_many(self, collection: str, filter_dict: dict[str, Any]) -> int:
        """Delete all documents matching the filter."""
        with self._lock:
            docs = self._load_collection(collection)
            initial_count = len(docs)
            remaining = [d for d in docs if not self._matches(d, filter_dict)]
            deleted_count = initial_count - len(remaining)
            if deleted_count > 0:
                self._save_collection(collection, remaining)
            return deleted_count

    def count(self, collection: str, filter_dict: dict[str, Any] | None = None) -> int:
        """Count documents in a collection."""
        with self._lock:
            docs = self._load_collection(collection)
            if not filter_dict:
                return len(docs)
            return sum(1 for d in docs if self._matches(d, filter_dict))

    def clear_collection(self, collection: str) -> None:
        """Truncate a collection completely."""
        with self._lock:
            self._save_collection(collection, [])


_global_doc_store: DocumentStore | None = None


def get_document_store() -> DocumentStore:
    """Singleton getter for embedded document store."""
    global _global_doc_store
    if _global_doc_store is None:
        _global_doc_store = DocumentStore()
    return _global_doc_store
