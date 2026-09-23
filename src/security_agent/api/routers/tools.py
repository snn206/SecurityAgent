"""Tools router — list available sandbox tools."""
from __future__ import annotations

from typing import Any
from fastapi import APIRouter
import yaml

from security_agent.core.paths import get_config_path

router = APIRouter(tags=["tools"])


@router.get("/tools")
async def list_tools() -> list[dict[str, Any]]:
    """Return all tools configured in config/tools.yaml."""
    cfg_path = get_config_path("tools.yaml")
    if not cfg_path.exists():
        return []

    try:
        with cfg_path.open() as f:
            data = yaml.safe_load(f)

        tools_dict = data.get("tools", {})
        result = []
        for tid, tcfg in tools_dict.items():
            result.append({
                "id": tid,
                "name": tcfg.get("name", tid),
                "description": tcfg.get("description", ""),
                "category": tcfg.get("category", "general"),
                "command_template": tcfg.get("command_template", ""),
                "container": "kali-sandbox",
                "risk": "HIGH" if tid in ("sqlmap", "metasploit") else ("MEDIUM" if tid == "nuclei" else "LOW"),
            })
        return result
    except Exception:
        return []
