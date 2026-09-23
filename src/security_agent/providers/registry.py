"""Provider registry — loads providers from config/providers.yaml."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from security_agent.core.base_provider import BaseProvider, ProviderConfig
from security_agent.core.exceptions import ConfigError, ProviderError


class ProviderRegistry:
    """Loads and manages all provider instances from config."""

    def __init__(self, config_path: Path | None = None) -> None:
        self._providers: dict[str, BaseProvider] = {}
        self._config: dict[str, Any] = {}
        self._config_path = config_path or (
            Path(__file__).parent.parent.parent.parent.parent / "config" / "providers.yaml"
        )

    def load(self) -> None:
        """Load all enabled providers from config file."""
        if not self._config_path.exists():
            raise ConfigError(f"Providers config not found: {self._config_path}")

        with self._config_path.open() as f:
            raw = yaml.safe_load(f)

        self._config = raw
        providers_raw: dict[str, Any] = raw.get("providers", {})

        for provider_id, cfg in providers_raw.items():
            if not cfg.get("enabled", False):
                continue
            try:
                provider = self._create_provider(provider_id, cfg)
                self._providers[provider_id] = provider
            except Exception as exc:
                # Log and skip — don't crash startup due to missing optional provider
                import structlog
                structlog.get_logger().warning(
                    "provider_load_failed", provider_id=provider_id, error=str(exc)
                )

    def _create_provider(self, provider_id: str, cfg: dict[str, Any]) -> BaseProvider:
        """Instantiate the right provider class based on type."""
        provider_type = cfg.get("type", "openai_compatible")
        api_key = self._resolve_env(cfg.get("api_key", ""))
        base_url = self._resolve_env(cfg.get("base_url", ""))

        pconfig = ProviderConfig(
            provider_id=provider_id,
            provider_type=provider_type,
            api_key=api_key or None,
            base_url=base_url or None,
            default_model=cfg.get("default_model", ""),
            capabilities=cfg.get("capabilities", {}),
            extra=cfg,
        )

        match provider_type:
            case "anthropic":
                from security_agent.providers.anthropic.provider import AnthropicProvider
                return AnthropicProvider(pconfig)
            case "openai":
                from security_agent.providers.openai.provider import OpenAIProvider
                return OpenAIProvider(pconfig)
            case "openai_compatible":
                from security_agent.providers.openai.provider import OpenAIProvider
                return OpenAIProvider(pconfig)
            case "ollama":
                from security_agent.providers.ollama.provider import OllamaProvider
                return OllamaProvider(pconfig)
            case "mistral":
                from security_agent.providers.mistral.provider import MistralProvider
                return MistralProvider(pconfig)
            case "nvidia_nim":
                from security_agent.providers.nvidia_nim.provider import NvidiaNimProvider
                return NvidiaNimProvider(pconfig)
            case _:
                raise ProviderError(provider_id, f"Unknown provider type: {provider_type!r}")

    @staticmethod
    def _resolve_env(value: str) -> str:
        """Replace ${ENV_VAR} with actual environment variable values."""
        if value.startswith("${") and value.endswith("}"):
            var = value[2:-1]
            # Support default: ${VAR:-default}
            if ":-" in var:
                var_name, default = var.split(":-", 1)
                return os.environ.get(var_name, default)
            return os.environ.get(var, "")
        return value

    def get(self, provider_id: str) -> BaseProvider:
        if provider_id not in self._providers:
            raise ProviderError(provider_id, "Provider not loaded or not enabled")
        return self._providers[provider_id]

    def get_default(self) -> BaseProvider:
        default_id = self._config.get("default_provider", "")
        return self.get(default_id)

    def list(self) -> list[str]:
        return list(self._providers.keys())

    def all(self) -> dict[str, BaseProvider]:
        return dict(self._providers)


# Module-level singleton
_registry: ProviderRegistry | None = None


def get_registry() -> ProviderRegistry:
    global _registry
    if _registry is None:
        _registry = ProviderRegistry()
        _registry.load()
    return _registry
