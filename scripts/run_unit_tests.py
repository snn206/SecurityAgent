"""Fast test verification runner for DocumentStore, JEV, Memory, and Hierarchy."""

import asyncio
import sys
import tempfile
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from security_agent.jev.evaluator import Evaluator
from security_agent.jev.evolution import EvolutionEngine
from security_agent.jev.judge import Judge, Verdict
from security_agent.jev.verifier import Verifier
from security_agent.memory.manager import MemoryManager
from security_agent.orchestration.hierarchy import AgentRole, HierarchyManager
from security_agent.orchestration.task_queue import ParentTaskQueue
from security_agent.storage.document_store import DocumentStore


def test_document_store():
    print("[RUN] test_document_store...")
    with tempfile.TemporaryDirectory() as tmp:
        store = DocumentStore(base_dir=tmp)
        doc_id = store.insert_one("test", {"tool": "nmap", "port": 80})
        assert doc_id is not None

        found = store.find("test", {"tool": "nmap"})
        assert len(found) == 1
        assert found[0]["port"] == 80

        store.update_one("test", {"_id": doc_id}, {"port": 443})
        updated = store.find_one("test", {"_id": doc_id})
        assert updated["port"] == 443

        store.delete_one("test", {"_id": doc_id})
        assert store.count("test") == 0
    print("  [OK] DocumentStore passed!")


def test_jev():
    print("[RUN] test_jev...")
    with tempfile.TemporaryDirectory() as tmp:
        store = DocumentStore(base_dir=tmp)
        verifier = Verifier()
        evaluator = Evaluator()
        judge = Judge(verifier, evaluator)
        engine = EvolutionEngine(doc_store=store)

        nmap_out = "80/tcp open http Apache 2.4\n443/tcp open ssl"
        v_res = verifier.verify_tool_output("nmap", nmap_out)
        assert v_res["verified"] is True
        assert v_res["facts_count"] >= 2

        judgment = judge.judge_step("recon", "Port scan", "nmap", nmap_out)
        assert judgment["verdict"] == Verdict.PASS

        # Distill lesson
        lesson = engine.distill_lesson("10.0.0.1", "nmap", "recon", judgment, nmap_out)
        assert lesson is not None

        retrieved = engine.get_lessons_for_execution("10.0.0.1", "nmap")
        assert len(retrieved) >= 1
    print("  [OK] JEV (Verifier, Evaluator, Judge, Evolution) passed!")


def test_memory_manager():
    print("[RUN] test_memory_manager...")
    with tempfile.TemporaryDirectory() as tmp:
        store = DocumentStore(base_dir=tmp)
        mgr = MemoryManager(doc_store=store)

        rule_id = mgr.add_memory(
            "golden_rules",
            {
                "title": "Stealth Scan",
                "rule": "Always use -T2",
                "category": "recon",
            },
        )
        assert rule_id is not None
        assert len(mgr.list_memories("golden_rules")) == 1

        mgr.update_memory("golden_rules", rule_id, {"rule": "Always use -T2 with delay"})
        updated = mgr.get_memory("golden_rules", rule_id)
        assert updated["rule"] == "Always use -T2 with delay"

        ctx = mgr.get_consolidated_context("192.168.1.1")
        assert "Always use -T2 with delay" in ctx
    print("  [OK] MemoryManager (CRUD, search, consolidated context) passed!")


async def test_hierarchy_and_queue():
    print("[RUN] test_hierarchy_and_queue...")
    # 1. Hierarchy limits: 1 Ông, 3 Cha, 2 Con each -> max 10
    hm = HierarchyManager()
    assert hm.coordinator["role"] == AgentRole.COORDINATOR
    assert len(hm.parents) == 3
    assert hm.total_agent_count == 4

    c1 = hm.spawn_child("parent-recon", "Scanner 1", "Nmap port scan")
    c2 = hm.spawn_child("parent-recon", "Scanner 2", "DNS enum")
    assert hm.total_agent_count == 6

    # 3rd child must fail
    try:
        hm.spawn_child("parent-recon", "Scanner 3", "Over limit")
        raise AssertionError("Should have raised RuntimeError")
    except RuntimeError:
        pass

    topo = hm.get_topology()
    assert topo["total_agents"] == 6
    assert topo["max_limit"] == 10

    # 2. Task Queue: 3 parent slots max, overflow queued
    queue = ParentTaskQueue(max_parents=3)
    t1 = await queue.enqueue("T1", "G1", "10.0.0.1")
    t2 = await queue.enqueue("T2", "G2", "10.0.0.2")
    t3 = await queue.enqueue("T3", "G3", "10.0.0.3")
    assert t1["status"] == "active"
    assert t2["status"] == "active"
    assert t3["status"] == "active"

    t4 = await queue.enqueue("T4", "G4", "10.0.0.4")
    assert t4["status"] == "queued"
    assert queue.get_status()["queued_count"] == 1

    # Complete T1 -> T4 dequeues immediately
    await queue.complete_task(t1["id"])
    assert queue.get_status()["queued_count"] == 0
    assert queue.get_status()["active_count"] == 3
    print("  [OK] Hierarchy (10-agent cap) & ParentTaskQueue passed!")


async def main():
    test_document_store()
    test_jev()
    test_memory_manager()
    await test_hierarchy_and_queue()
    print("\n==============================================")
    print("ALL CORE TESTS PASSED WITH 100% SUCCESS!")
    print("==============================================")


if __name__ == "__main__":
    asyncio.run(main())
