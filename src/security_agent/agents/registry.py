"""Agent registry — loads agent configs from config/agents.yaml."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import yaml

class AgentRegistry:
    def __init__(self, config_path: Path | None = None) -> None:
        self._agents: dict[str, dict[str, Any]] = {}
        self._config_path = config_path or (
            Path(__file__).parent.parent.parent.parent.parent / "config" / "agents.yaml"
        )

    def load(self) -> None:
        if not self._config_path.exists():
            return
        with self._config_path.open() as f:
            raw = yaml.safe_load(f)
        self._agents = raw.get("agents", {})

    def get(self, agent_id: str) -> dict[str, Any]:
        return self._agents.get(agent_id, {})

    def list(self) -> list[str]:
        return list(self._agents.keys())
