"""Unit tests for execution history store."""
import pytest


@pytest.mark.asyncio
async def test_create_and_get_execution(test_history_store):
    store = test_history_store
    record = await store.create_execution("exec-1", "task-1", "Scan 192.168.1.1", "192.168.1.1")
    assert record.id == "exec-1"
    assert record.status == "pending"

    fetched = await store.get_execution("exec-1")
    assert fetched is not None
    assert fetched.user_request == "Scan 192.168.1.1"


@pytest.mark.asyncio
async def test_update_execution(test_history_store):
    store = test_history_store
    await store.create_execution("exec-2", "task-2", "Test", "")
    await store.update_execution("exec-2", status="done")
    record = await store.get_execution("exec-2")
    assert record.status == "done"
