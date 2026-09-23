"""Tool registry — loads tools from config/tools.yaml."""

from __future__ import annotations

from pathlib import Path

import yaml

from security_agent.core.base_tool import BaseTool, ToolConfig
from security_agent.core.exceptions import ToolError


class ToolRegistry:
    """Loads and manages tool instances from config."""

    def __init__(self, config_path: Path | None = None) -> None:
        self._tools: dict[str, BaseTool] = {}
        self._configs: dict[str, ToolConfig] = {}
        from security_agent.core.paths import get_config_path

        self._config_path = config_path or get_config_path("tools.yaml")

    def load(self) -> None:
        from security_agent.tools.builtin import (
            CurlTool,
            GobusterTool,
            NiktoTool,
            NmapTool,
            ShellTool,
            SqlmapTool,
            WhoisTool,
        )

        if not self._config_path.exists():
            return

        with self._config_path.open() as f:
            raw = yaml.safe_load(f)

        tool_classes = {
            "nmap": NmapTool,
            "gobuster": GobusterTool,
            "sqlmap": SqlmapTool,
            "nikto": NiktoTool,
            "whois": WhoisTool,
            "curl": CurlTool,
            "shell": ShellTool,
        }

        for tool_id, cfg in raw.get("tools", {}).items():
            config = ToolConfig(
                tool_id=tool_id,
                name=cfg.get("name", tool_id),
                description=cfg.get("description", ""),
                category=cfg.get("category", "utility"),
                command_template=cfg.get("command_template", ""),
                default_flags=cfg.get("default_flags", ""),
                timeout_seconds=cfg.get("timeout_seconds", 120),
                output_format=cfg.get("output_format", "text"),
                restricted=cfg.get("restricted", False),
                allowed_flags=cfg.get("allowed_flags", []),
            )
            self._configs[tool_id] = config
            if tool_id in tool_classes:
                self._tools[tool_id] = tool_classes[tool_id](config)

    def get(self, tool_id: str) -> BaseTool:
        if tool_id not in self._tools:
            raise ToolError(tool_id, "Tool not found in registry")
        return self._tools[tool_id]

    def list(self) -> list[str]:
        return list(self._tools.keys())
