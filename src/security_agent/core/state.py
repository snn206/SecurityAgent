"""LangGraph state definition for the SecurityAgent workflow."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Annotated
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict, total=False):
    """Full workflow state passed between LangGraph nodes."""

    # Identifiers
    execution_id: str
    task_id: str

    # User request
    user_request: str
    scope: str

    # Messages (LangGraph-managed — uses add_messages reducer)
    messages: Annotated[list[BaseMessage], add_messages]

    # Planning
    plan: dict[str, Any] | None         # serialized Plan
    current_step_id: str | None
    completed_steps: list[str]

    # Provider/model in use
    active_provider: str
    active_model: str

    # Tool execution
    pending_tool: str | None
    tool_input: dict[str, Any] | None
    tool_output: dict[str, Any] | None

    # Sandbox
    sandbox_container_id: str | None
    sandbox_command: str | None
    sandbox_stdout: str | None
    sandbox_stderr: str | None
    sandbox_exit_code: int | None

    # Results
    findings: list[dict[str, Any]]
    artifacts: list[str]

    # Report
    report: dict[str, Any] | None

    # Status
    status: str   # pending | planning | executing | analyzing | reporting | done | failed
    error: str | None
