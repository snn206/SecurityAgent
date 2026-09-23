"""Unit tests for embedded zero-install DocumentStore."""
import pytest
from security_agent.storage.document_store import DocumentStore


@pytest.fixture
def temp_store(tmp_path):
    return DocumentStore(base_dir=tmp_path / "memory")


def test_insert_and_find(temp_store):
    doc_id = temp_store.insert_one("test_col", {"name": "nmap_rule", "level": 1})
    assert doc_id is not None

    found = temp_store.find("test_col", {"name": "nmap_rule"})
    assert len(found) == 1
    assert found[0]["name"] == "nmap_rule"
    assert found[0]["_id"] == doc_id


def test_find_one(temp_store):
    temp_store.insert_one("test_col", {"tool": "gobuster", "status": "active"})
    doc = temp_store.find_one("test_col", {"tool": "gobuster"})
    assert doc is not None
    assert doc["status"] == "active"


def test_update_one(temp_store):
    doc_id = temp_store.insert_one("test_col", {"target": "10.0.0.1", "ports": [80]})
    success = temp_store.update_one(
        "test_col",
        {"_id": doc_id},
        {"$set": {"ports": [80, 443]}}
    )
    assert success is True

    updated = temp_store.find_one("test_col", {"_id": doc_id})
    assert updated["ports"] == [80, 443]


def test_delete_one(temp_store):
    doc_id = temp_store.insert_one("test_col", {"target": "192.168.1.50"})
    assert temp_store.count("test_col") == 1

    deleted = temp_store.delete_one("test_col", {"_id": doc_id})
    assert deleted is True
    assert temp_store.count("test_col") == 0


def test_clear_collection(temp_store):
    temp_store.insert_many("test_col", [{"i": 1}, {"i": 2}, {"i": 3}])
    assert temp_store.count("test_col") == 3

    temp_store.clear_collection("test_col")
    assert temp_store.count("test_col") == 0
