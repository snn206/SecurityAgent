"""Abstract base class for all provider implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProviderConfig:
    """Runtime config for a provider instance."""

    provider_id: str
    provider_type: str
    api_key: str | None = None
    base_url: str | None = None
    default_model: str = ""
    capabilities: dict[str, bool] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatMessage:
    role: str  # "system" | "user" | "assistant" | "tool"
    content: str
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None


@dataclass
class ChatResponse:
    content: str
    model: str
    usage: dict[str, int] | None = None
    tool_calls: list[dict[str, Any]] | None = None
    finish_reason: str = "stop"
    reasoning: str | None = None  # extended thinking / reasoning trace


class BaseProvider(ABC):
    """Abstract provider. All provider implementations must subclass this."""

    def __init__(self, config: ProviderConfig) -> None:
        self.config = config

    @property
    def provider_id(self) -> str:
        return self.config.provider_id

    @property
    def supports_tool_calling(self) -> bool:
        return self.config.capabilities.get("tool_calling", False)

    @property
    def supports_streaming(self) -> bool:
        return self.config.capabilities.get("streaming", False)

    @property
    def supports_reasoning(self) -> bool:
        return self.config.capabilities.get("reasoning", False)

    @abstractmethod
    async def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> ChatResponse:
        """Send a chat completion request."""
        ...

    @abstractmethod
    async def stream(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream a chat completion response token by token."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is reachable."""
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.provider_id!r}, model={self.config.default_model!r})"
