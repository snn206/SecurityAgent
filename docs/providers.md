# Provider Guide

## Overview

All providers implement `BaseProvider` from `security_agent.core.base_provider`.
New providers can be added without modifying core agent logic.

## Supported Providers

| ID | Type | Auth | Tool Calling | Streaming | Reasoning |
|----|------|------|-------------|----------|----------|
| anthropic | Anthropic (Claude) | API Key | ✓ | ✓ | ✓ |
| openai | OpenAI | API Key | ✓ | ✓ | ✓ (o-series) |
| ollama | Local (Ollama) | None | ✓ | ✓ | — |
| mistral | Mistral | API Key | ✓ | ✓ | — |
| deepseek | DeepSeek | API Key | ✓ | ✓ | ✓ |
| nvidia_nim | NVIDIA NIM | API Key | ✓ | ✓ | — |
| qwen | Qwen | API Key | ✓ | ✓ | ✓ |
| opencode | OpenCode | API Key | ✓ | ✓ | — |
| kilo | Kilo | API Key | ✓ | ✓ | — |

## Configuration

Edit `config/providers.yaml`. Set `enabled: true` and provide API keys in `.env`.

## Adding a New Provider

1. Create `src/security_agent/providers/<name>/provider.py`
2. Subclass `BaseProvider`, implement `chat()`, `stream()`, `health_check()`
3. Register in `ProviderRegistry._create_provider()` (`providers/registry.py`)
4. Add to `config/providers.yaml`
5. Add to `registry/versions.yaml` under `providers:`
