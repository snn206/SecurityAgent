"""Provider stub — extend with langchain integration."""

from __future__ import annotations

from collections.abc import AsyncIterator

from security_agent.core.base_provider import (
    BaseProvider,
    ChatResponse,
)
from security_agent.core.exceptions import ProviderError


class MistralProvider(BaseProvider):
    async def chat(
        self, messages, model=None, temperature=0.2, max_tokens=4096, tools=None, **kwargs
    ) -> ChatResponse:
        raise ProviderError(self.provider_id, "Not yet implemented — extend this stub.")

    async def stream(
        self, messages, model=None, temperature=0.2, max_tokens=4096, **kwargs
    ) -> AsyncIterator[str]:
        raise ProviderError(self.provider_id, "Not yet implemented — extend this stub.")
        yield ""  # make it a generator

    async def health_check(self) -> bool:
        return False
