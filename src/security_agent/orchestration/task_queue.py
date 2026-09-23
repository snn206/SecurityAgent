"""Task Queue for Parent Agents.

Limits concurrent active parent tasks to 3. Excess tasks are held in an
ordered priority queue and dispatched immediately when a parent becomes idle.
"""
from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any, Callable, Coroutine


class ParentTaskQueue:
    """Manages task scheduling and queuing for up to 3 parent domain leads."""

    MAX_CONCURRENT_PARENTS = 3

    def __init__(self, max_parents: int = MAX_CONCURRENT_PARENTS) -> None:
        self.max_parents = max_parents
        self._active_tasks: dict[str, dict[str, Any]] = {}
        self._queue: list[dict[str, Any]] = []
        self._completed_tasks: dict[str, dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        self._listeners: list[Callable[[dict[str, Any]], Coroutine[Any, Any, None]]] = []

    def on_task_dispatched(self, listener: Callable[[dict[str, Any]], Coroutine[Any, Any, None]]) -> None:
        """Register a callback when a task is dispatched from the queue."""
        self._listeners.append(listener)

    async def enqueue(
        self,
        title: str,
        goal: str,
        target: str,
        domain: str = "general",
        priority: int = 1,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Enqueue or immediately dispatch a parent task."""
        async with self._lock:
            task_id = f"ptask-{uuid.uuid4().hex[:8]}"
            task = {
                "id": task_id,
                "title": title,
                "goal": goal,
                "target": target,
                "domain": domain,
                "priority": priority,
                "status": "pending",
                "enqueued_at": time.time(),
                "assigned_parent": None,
                "metadata": metadata or {},
            }

            if len(self._active_tasks) < self.max_parents:
                # Immediate dispatch
                slot_index = len(self._active_tasks) + 1
                task["status"] = "active"
                task["assigned_parent"] = f"parent-{domain}-{slot_index}"
                task["started_at"] = time.time()
                self._active_tasks[task_id] = task
                await self._notify_dispatch(task)
            else:
                # Put in queue
                task["status"] = "queued"
                self._queue.append(task)
                # Sort by priority (higher priority number first)
                self._queue.sort(key=lambda t: t.get("priority", 1), reverse=True)

            return task

    async def complete_task(self, task_id: str, result: dict[str, Any] | None = None) -> dict[str, Any] | None:
        """Complete an active parent task and dispatch the next queued task if available."""
        async with self._lock:
            if task_id not in self._active_tasks:
                return None

            task = self._active_tasks.pop(task_id)
            task["status"] = "completed"
            task["completed_at"] = time.time()
            task["result"] = result or {}
            self._completed_tasks[task_id] = task

            # Dequeue next task if queue has items
            if self._queue and len(self._active_tasks) < self.max_parents:
                next_task = self._queue.pop(0)
                slot_index = len(self._active_tasks) + 1
                next_task["status"] = "active"
                next_task["assigned_parent"] = f"parent-{next_task.get('domain', 'lead')}-{slot_index}"
                next_task["started_at"] = time.time()
                self._active_tasks[next_task["id"]] = next_task
                await self._notify_dispatch(next_task)

            return task

    async def _notify_dispatch(self, task: dict[str, Any]) -> None:
        for listener in self._listeners:
            try:
                await listener(task)
            except Exception:
                pass

    def get_status(self) -> dict[str, Any]:
        """Get live metrics on queue state."""
        return {
            "max_parent_slots": self.max_parents,
            "active_count": len(self._active_tasks),
            "queued_count": len(self._queue),
            "active_tasks": list(self._active_tasks.values()),
            "queued_tasks": list(self._queue),
            "completed_count": len(self._completed_tasks),
        }


_global_task_queue: ParentTaskQueue | None = None


def get_task_queue() -> ParentTaskQueue:
    """Singleton getter for ParentTaskQueue."""
    global _global_task_queue
    if _global_task_queue is None:
        _global_task_queue = ParentTaskQueue()
    return _global_task_queue
