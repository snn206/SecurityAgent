"""10-Agent Hierarchical Topology Manager.

Strictly enforces:
- 1 Grandparent Coordinator Agent ("Ông")
- Up to 3 Parent Agents ("Cha")
- Up to 2 Child Agents per Parent ("Con")
- Global maximum limit of 10 agents active across the system.
"""
from __future__ import annotations

import time
import uuid
from typing import Any


class AgentRole:
    COORDINATOR = "coordinator"  # Ông (1 max)
    PARENT = "parent"            # Cha (3 max)
    CHILD = "child"              # Con (2 per parent max)


class HierarchyManager:
    """Manages creation, lifecycle, and limits of the 1-3-2 agent tree."""

    MAX_COORDINATOR = 1
    MAX_PARENTS = 3
    MAX_CHILDREN_PER_PARENT = 2
    MAX_TOTAL_AGENTS = 10

    def __init__(self) -> None:
        self.coordinator: dict[str, Any] = {
            "id": "agent-root-coordinator",
            "name": "Grandparent Coordinator",
            "role": AgentRole.COORDINATOR,
            "status": "active",
            "current_mission": None,
            "created_at": time.time(),
        }
        self.parents: dict[str, dict[str, Any]] = {}
        self.children: dict[str, dict[str, Any]] = {}

        # Initialize default 3 Parent domain leads
        self._init_default_parents()

    def _init_default_parents(self) -> None:
        default_specs = [
            ("parent-recon", "Recon Lead Agent", "Reconnaissance, surface mapping, DNS and port scanning"),
            ("parent-vuln", "Vulnerability Lead Agent", "Web application audit, service inspection, CVE correlation"),
            ("parent-exploit", "Exploit Lead Agent", "PoC validation, sandbox verification, payload verification"),
        ]
        for pid, name, domain in default_specs:
            self.parents[pid] = {
                "id": pid,
                "name": name,
                "domain": domain,
                "role": AgentRole.PARENT,
                "status": "idle",
                "assigned_task": None,
                "created_at": time.time(),
                "children_ids": [],
            }

    @property
    def total_agent_count(self) -> int:
        return 1 + len(self.parents) + len(self.children)

    def spawn_child(self, parent_id: str, name: str, task: str) -> dict[str, Any]:
        """Spawn a child worker under a specified parent agent.

        Enforces MAX_CHILDREN_PER_PARENT (2) and MAX_TOTAL_AGENTS (10).
        """
        if parent_id not in self.parents:
            raise ValueError(f"Parent agent '{parent_id}' does not exist.")

        parent = self.parents[parent_id]
        current_children = parent.get("children_ids", [])

        if len(current_children) >= self.MAX_CHILDREN_PER_PARENT:
            # Check if any existing child has finished, retire it to make room
            retire_candidate = None
            for cid in current_children:
                if self.children.get(cid, {}).get("status") in ("completed", "idle"):
                    retire_candidate = cid
                    break

            if retire_candidate:
                self.retire_child(retire_candidate)
            else:
                raise RuntimeError(
                    f"Parent '{parent['name']}' already has {self.MAX_CHILDREN_PER_PARENT} active child workers."
                )

        if self.total_agent_count >= self.MAX_TOTAL_AGENTS:
            raise RuntimeError(
                f"Global system agent ceiling reached ({self.MAX_TOTAL_AGENTS} agents max)."
            )

        child_id = f"child-{uuid.uuid4().hex[:6]}"
        child_doc = {
            "id": child_id,
            "parent_id": parent_id,
            "name": name,
            "task": task,
            "role": AgentRole.CHILD,
            "status": "working",
            "created_at": time.time(),
        }

        self.children[child_id] = child_doc
        parent["children_ids"].append(child_id)
        parent["status"] = "supervising_children"
        return child_doc

    def complete_child(self, child_id: str, result: Any = None) -> None:
        """Mark a child worker as completed."""
        if child_id in self.children:
            self.children[child_id]["status"] = "completed"
            self.children[child_id]["result"] = result

    def retire_child(self, child_id: str) -> None:
        """Retire and de-register a completed child agent to free slots."""
        if child_id in self.children:
            child = self.children.pop(child_id)
            pid = child.get("parent_id")
            if pid and pid in self.parents:
                if child_id in self.parents[pid]["children_ids"]:
                    self.parents[pid]["children_ids"].remove(child_id)
                if not self.parents[pid]["children_ids"]:
                    self.parents[pid]["status"] = "idle"

    def get_topology(self) -> dict[str, Any]:
        """Return the complete hierarchical agent tree with live status."""
        tree_parents = []
        for pid, pdata in self.parents.items():
            p_copy = dict(pdata)
            p_children = [self.children[cid] for cid in pdata["children_ids"] if cid in self.children]
            p_copy["children"] = p_children
            tree_parents.append(p_copy)

        return {
            "total_agents": self.total_agent_count,
            "max_limit": self.MAX_TOTAL_AGENTS,
            "coordinator": self.coordinator,
            "parents": tree_parents,
        }


_global_hierarchy_manager: HierarchyManager | None = None


def get_hierarchy_manager() -> HierarchyManager:
    """Singleton getter for HierarchyManager."""
    global _global_hierarchy_manager
    if _global_hierarchy_manager is None:
        _global_hierarchy_manager = HierarchyManager()
    return _global_hierarchy_manager
