"""Tool sync — auto-install/update tools inside the Docker sandbox."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .manager import SandboxManager
from security_agent.core.exceptions import SandboxError


class ToolSync:
    """Installs and updates tools inside the sandbox from registry/versions.yaml."""

    def __init__(self) -> None:
        self._manager = SandboxManager()
        from security_agent.core.paths import get_repo_root
        registry_path = get_repo_root() / "registry" / "versions.yaml"
        if registry_path.exists():
            with registry_path.open() as f:
                self._registry: dict[str, Any] = yaml.safe_load(f)
        else:
            self._registry = {}

    async def sync_all(self) -> dict[str, bool]:
        """Install/update all tools listed in the registry into the sandbox."""
        results: dict[str, bool] = {}
        tools = self._registry.get("tools", {})

        container = self._manager.start(execution_id="tool-sync")
        try:
            for tool_id, entry in tools.items():
                install_cmd = entry.get("install_cmd")
                if not install_cmd:
                    results[tool_id] = True
                    continue
                exit_code, output = self._manager.exec_command(container, install_cmd)
                results[tool_id] = (exit_code == 0)
        finally:
            self._manager.stop(container)

        return results

    async def sync_tool(self, tool_id: str) -> bool:
        """Install/update a single tool in the sandbox."""
        tools = self._registry.get("tools", {})
        if tool_id not in tools:
            raise SandboxError(f"Tool '{tool_id}' not found in registry")

        install_cmd = tools[tool_id].get("install_cmd")
        if not install_cmd:
            return True

        container = self._manager.start(execution_id=f"tool-sync-{tool_id}")
        try:
            exit_code, _ = self._manager.exec_command(container, install_cmd)
            return exit_code == 0
        finally:
            self._manager.stop(container)
