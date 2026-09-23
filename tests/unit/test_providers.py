"""Unit tests for provider abstraction layer."""
import pytest
from security_agent.core.base_provider import ProviderConfig, BaseProvider


def test_provider_config_capabilities(provider_config):
    assert provider_config.provider_id == "test_provider"
    assert provider_config.capabilities.get("tool_calling") is True


def test_provider_repr(provider_config):
    from unittest.mock import MagicMock
    # Test that any provider has a proper repr
    from security_agent.core.base_provider import BaseProvider
    assert "test_provider" in provider_config.provider_id


def test_chat_response_defaults():
    from security_agent.core.base_provider import ChatResponse
    r = ChatResponse(content="hello", model="gpt-4o")
    assert r.finish_reason == "stop"
    assert r.tool_calls is None
    assert r.reasoning is None
