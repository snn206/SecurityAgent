"""Unit tests for 10-Agent Hierarchy and Parent Task Queue."""
import pytest
from security_agent.orchestration.hierarchy import HierarchyManager, AgentRole
from security_agent.orchestration.task_queue import ParentTaskQueue


def test_hierarchy_structure_and_limits():
    hm = HierarchyManager()

    # Verify 1 Coordinator
    assert hm.coordinator["role"] == AgentRole.COORDINATOR
    assert hm.coordinator["name"] == "Grandparent Coordinator"

    # Verify 3 Default Parents
    assert len(hm.parents) == 3
    for p in hm.parents.values():
        assert p["role"] == AgentRole.PARENT

    # Total agents initially: 1 (ông) + 3 (cha) = 4
    assert hm.total_agent_count == 4

    # Spawn 2 children under parent-recon
    c1 = hm.spawn_child("parent-recon", "Scanner 1", "Scan subnet")
    c2 = hm.spawn_child("parent-recon", "Scanner 2", "Scan DNS")
    assert c1["role"] == AgentRole.CHILD
    assert c2["role"] == AgentRole.CHILD
    assert hm.total_agent_count == 6

    # Attempting to spawn 3rd active child under same parent should raise RuntimeError
    with pytest.raises(RuntimeError):
        hm.spawn_child("parent-recon", "Scanner 3", "Exceed limit")

    # Retiring child frees slot
    hm.complete_child(c1["id"])
    c3 = hm.spawn_child("parent-recon", "Scanner 3", "Replacement worker")
    assert c3 is not None


@pytest.mark.asyncio
async def test_parent_task_queue_slot_limit_and_overflow():
    queue = ParentTaskQueue(max_parents=3)

    # Dispatch first 3 tasks — should all be active immediately
    t1 = await queue.enqueue("Task 1", "Goal 1", "10.0.0.1", domain="recon")
    t2 = await queue.enqueue("Task 2", "Goal 2", "10.0.0.2", domain="vuln")
    t3 = await queue.enqueue("Task 3", "Goal 3", "10.0.0.3", domain="exploit")

    assert t1["status"] == "active"
    assert t2["status"] == "active"
    assert t3["status"] == "active"

    status = queue.get_status()
    assert status["active_count"] == 3
    assert status["queued_count"] == 0

    # 4th task exceeds parent slots -> must be queued
    t4 = await queue.enqueue("Task 4", "Goal 4", "10.0.0.4", domain="recon")
    assert t4["status"] == "queued"

    status = queue.get_status()
    assert status["active_count"] == 3
    assert status["queued_count"] == 1

    # Complete Task 1 -> should automatically dequeue Task 4 into active!
    completed = await queue.complete_task(t1["id"], result={"output": "done"})
    assert completed["status"] == "completed"

    status_after = queue.get_status()
    assert status_after["active_count"] == 3
    assert status_after["queued_count"] == 0
    # Task 4 is now active
    active_ids = [t["id"] for t in status_after["active_tasks"]]
    assert t4["id"] in active_ids
