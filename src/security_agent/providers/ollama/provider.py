"""Ollama (local) provider implementation."""
from __future__ import annotations

from typing import Any, AsyncIterator

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from security_agent.core.base_provider import (
    BaseProvider, ProviderConfig, ChatMessage, ChatResponse
)
from security_agent.core.exceptions import ProviderError


class OllamaProvider(BaseProvider):
    """Ollama local model provider via langchain-ollama."""

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(config)
        self._base_url = config.base_url or "http://localhost:11434"

    def _make_client(self, model: str | None, temperature: float, num_predict: int) -> ChatOllama:
        return ChatOllama(
            model=model or self.config.default_model,
            base_url=self._base_url,
            temperature=temperature,
            num_predict=num_predict,
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
            client = self._make_client(model, temperature, max_tokens)
            lc_messages = self._to_lc_messages(messages)
            if tools:
                response = await client.bind_tools(tools).ainvoke(lc_messages)
            else:
                response = await client.ainvoke(lc_messages)
            return ChatResponse(
                content=str(response.content),
                model=model or self.config.default_model,
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
            client = self._make_client(model, temperature, max_tokens)
            lc_messages = self._to_lc_messages(messages)
            async for chunk in client.astream(lc_messages):
                if chunk.content:
                    yield str(chunk.content)
        except Exception as exc:
            raise ProviderError(self.provider_id, str(exc)) from exc

    async def health_check(self) -> bool:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{self._base_url}/api/tags", timeout=5.0)
                return resp.status_code == 200
        except Exception:
            return False
