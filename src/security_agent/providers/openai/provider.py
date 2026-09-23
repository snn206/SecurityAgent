"""OpenAI + OpenAI-compatible provider implementation."""
from __future__ import annotations

from typing import Any, AsyncIterator

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from security_agent.core.base_provider import (
    BaseProvider, ProviderConfig, ChatMessage, ChatResponse
)
from security_agent.core.exceptions import ProviderError


class OpenAIProvider(BaseProvider):
    """OpenAI provider — also used for any OpenAI-compatible API (DeepSeek, Qwen, etc.)."""

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(config)
        self._client = ChatOpenAI(
            api_key=config.api_key or "not-set",
            model=config.default_model,
            base_url=config.base_url or None,
        )

    def _to_lc_messages(self, messages: list[ChatMessage]) -> list[Any]:
        result = []
        for m in messages:
            if m.role == "system":
                result.append(SystemMessage(content=m.content))
            elif m.role == "user":
                result.append(HumanMessage(content=m.content))
            elif m.role == "assistant":
                result.append(AIMessage(content=m.content))
        return result

    async def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> ChatResponse:
        try:
            client = ChatOpenAI(
                api_key=self.config.api_key or "not-set",
                model=model or self.config.default_model,
                temperature=temperature,
                max_tokens=max_tokens,
                base_url=self.config.base_url or None,
            )
            lc_messages = self._to_lc_messages(messages)
            if tools:
                response = await client.bind_tools(tools).ainvoke(lc_messages)
            else:
                response = await client.ainvoke(lc_messages)

            usage = None
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                usage = {
                    "input_tokens": response.usage_metadata.get("input_tokens", 0),
                    "output_tokens": response.usage_metadata.get("output_tokens", 0),
                }

            return ChatResponse(
                content=str(response.content),
                model=model or self.config.default_model,
                usage=usage,
                tool_calls=getattr(response, "tool_calls", None),
            )
        except Exception as exc:
            raise ProviderError(self.provider_id, str(exc)) from exc

    async def stream(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        try:
            client = ChatOpenAI(
                api_key=self.config.api_key or "not-set",
                model=model or self.config.default_model,
                temperature=temperature,
                max_tokens=max_tokens,
                base_url=self.config.base_url or None,
            )
            lc_messages = self._to_lc_messages(messages)
            async for chunk in client.astream(lc_messages):
                if chunk.content:
                    yield str(chunk.content)
        except Exception as exc:
            raise ProviderError(self.provider_id, str(exc)) from exc

    async def health_check(self) -> bool:
        try:
            await self._client.ainvoke([HumanMessage(content="ping")])
            return True
        except Exception:
            return False
