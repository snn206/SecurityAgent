"""Custom exceptions for SecurityAgent."""

from __future__ import annotations


class SecurityAgentError(Exception):
    """Base exception for all SecurityAgent errors."""


class ConfigError(SecurityAgentError):
    """Invalid or missing configuration."""


class ProviderError(SecurityAgentError):
    """Provider API or connectivity error."""

    def __init__(self, provider_id: str, message: str) -> None:
        self.provider_id = provider_id
        super().__init__(f"[Provider:{provider_id}] {message}")


class ToolError(SecurityAgentError):
    """Tool execution error."""

    def __init__(self, tool_id: str, message: str) -> None:
        self.tool_id = tool_id
        super().__init__(f"[Tool:{tool_id}] {message}")


class SandboxError(SecurityAgentError):
    """Docker sandbox error."""

    def __init__(self, message: str, container_id: str | None = None) -> None:
        self.container_id = container_id
        super().__init__(f"[Sandbox] {message}")


class PlanningError(SecurityAgentError):
    """Planning or reasoning error."""


class ExecutionError(SecurityAgentError):
    """Agent execution error."""


class ReportError(SecurityAgentError):
    """Report generation error."""


class VersionError(SecurityAgentError):
    """Version registry error."""
