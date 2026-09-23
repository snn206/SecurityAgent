"""Test configuration and shared fixtures for SecurityAgent tests."""
from __future__ import annotations

import pytest
import pytest_asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from security_agent.core.base_provider import ProviderConfig, ChatResponse
from security_agent.core.events import EventBus


@pytest.fixture
def provider_config() -> ProviderConfig:
    return ProviderConfig(
        provider_id="test_provider",
        provider_type="openai",
        api_key="test-key",
        default_model="gpt-4o",
        capabilities={"tool_calling": True, "streaming": True},
    )


@pytest.fixture
def mock_chat_response() -> ChatResponse:
    return ChatResponse(
        content='{"plan_id":"test","objective":"test","scope":"","steps":[],"constraints":[]}',
        model="gpt-4o",
        usage={"input_tokens": 100, "output_tokens": 50},
    )


@pytest.fixture
def event_bus() -> EventBus:
    return EventBus()


@pytest.fixture
def config_dir() -> Path:
    return Path(__file__).parent.parent / "config"


@pytest_asyncio.fixture
async def test_history_store():
    from security_agent.execution.history import HistoryStore
    store = HistoryStore("sqlite+aiosqlite:///:memory:")
    await store.initialize()
    return store
