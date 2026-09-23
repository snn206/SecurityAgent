"""Unit tests for user agent memory management."""
import pytest
from security_agent.memory.manager import MemoryManager
from security_agent.storage.document_store import DocumentStore


@pytest.fixture
def temp_memory(tmp_path):
    store = DocumentStore(base_dir=tmp_path / "memory")
    return MemoryManager(doc_store=store)


def test_add_and_list_golden_rules(temp_memory):
    rule_id = temp_memory.add_memory(
        "golden_rules",
        {
            "title": "Stealth Subnet Policy",
            "rule": "Never exceed 100 packets/sec on production subnet 10.10.0.0/16",
            "target": "10.10.0.0/16",
            "category": "safety",
        }
    )
    assert rule_id is not None

    rules = temp_memory.list_memories("golden_rules")
    assert len(rules) == 1
    assert rules[0]["title"] == "Stealth Subnet Policy"


def test_update_memory(temp_memory):
    rule_id = temp_memory.add_memory(
        "golden_rules",
        {"title": "Initial Rule", "rule": "Old content"}
    )
    success = temp_memory.update_memory(
        "golden_rules",
        rule_id,
        {"rule": "Corrected and verified content", "title": "Updated Rule"}
    )
    assert success is True

    updated = temp_memory.get_memory("golden_rules", rule_id)
    assert updated["rule"] == "Corrected and verified content"
    assert updated["title"] == "Updated Rule"


def test_delete_memory(temp_memory):
    rule_id = temp_memory.add_memory(
        "golden_rules",
        {"title": "Temporary Rule", "rule": "To be forgotten"}
    )
    assert len(temp_memory.list_memories("golden_rules")) == 1

    deleted = temp_memory.delete_memory("golden_rules", rule_id)
    assert deleted is True
    assert len(temp_memory.list_memories("golden_rules")) == 0


def test_consolidated_context(temp_memory):
    temp_memory.add_memory("golden_rules", {"title": "No UDP scans", "rule": "Avoid UDP flood"})
    temp_memory.add_memory("lessons_learned", {
        "title": "Nmap timeout lesson",
        "target": "example.com",
        "insight": "Use -T2 on this host",
        "recommended_flags": "-T2",
    })

    context = temp_memory.get_consolidated_context("example.com")
    assert "GOLDEN RULES" in context
    assert "Avoid UDP flood" in context
    assert "DISTILLED EXPERIENCE" in context
    assert "Use -T2 on this host" in context
