"""Abstract base class for all tools."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolConfig:
    """Static tool config from config/tools.yaml."""
    tool_id: str
    name: str
    description: str
    category: str
    command_template: str
    default_flags: str = ""
    timeout_seconds: int = 120
    output_format: str = "text"
    restricted: bool = False
    allowed_flags: list[str] = field(default_factory=list)


@dataclass
class ToolInput:
    tool_id: str
    target: str
    flags: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolOutput:
    tool_id: str
    target: str
    command: str
    stdout: str
    stderr: str
    exit_code: int
    duration_seconds: float
    success: bool
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseTool(ABC):
    """Abstract tool. All built-in and extension tools must subclass this."""

    def __init__(self, config: ToolConfig) -> None:
        self.config = config

    @property
    def tool_id(self) -> str:
        return self.config.tool_id

    @property
    def description(self) -> str:
        return self.config.description

    @abstractmethod
    def build_command(self, tool_input: ToolInput) -> str:
        """Build the shell command string to execute in the sandbox."""
        ...

    @abstractmethod
    async def execute(self, tool_input: ToolInput) -> ToolOutput:
        """Execute the tool and return structured output."""
        ...

    def schema(self) -> dict[str, Any]:
        """Return JSON schema for tool calling (LangChain/OpenAI format)."""
        return {
            "type": "function",
            "function": {
                "name": self.config.tool_id,
                "description": self.config.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {"type": "string", "description": "Target host/URL/IP"},
                        "flags": {"type": "string", "description": "Additional flags"},
                    },
                    "required": ["target"],
                },
            },
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.tool_id!r})"
