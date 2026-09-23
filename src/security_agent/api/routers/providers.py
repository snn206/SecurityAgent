"""Providers router — list available and configured LLM providers."""
from __future__ import annotations

import os
from typing import Any
from fastapi import APIRouter
import yaml

from security_agent.core.paths import get_config_path

router = APIRouter(tags=["providers"])


@router.get("/providers")
async def list_providers() -> list[dict[str, Any]]:
    """Return all providers configured in config/providers.yaml."""
    cfg_path = get_config_path("providers.yaml")
    if not cfg_path.exists():
        return []

    try:
        with cfg_path.open() as f:
            data = yaml.safe_load(f)

        providers_dict = data.get("providers", {})
        result = []
        for pid, pcfg in providers_dict.items():
            api_key_spec = pcfg.get("api_key", "")
            # Check if environment key is populated
            has_key = True
            if api_key_spec.startswith("${") and api_key_spec.endswith("}"):
                env_name = api_key_spec[2:-1]
                has_key = bool(os.environ.get(env_name))
            elif not api_key_spec and pcfg.get("type") not in ("ollama", "mock"):
                has_key = False

            result.append({
                "name": pid,
                "type": pcfg.get("type", "openai_compatible"),
                "default_model": pcfg.get("default_model", ""),
                "enabled": pcfg.get("enabled", True),
                "configured": has_key or pcfg.get("type") in ("ollama", "mock"),
                "env_var": api_key_spec[2:-1] if (api_key_spec.startswith("${") and api_key_spec.endswith("}")) else None,
                "capabilities": pcfg.get("capabilities", {}),
            })
        return result
    except Exception:
        return []
