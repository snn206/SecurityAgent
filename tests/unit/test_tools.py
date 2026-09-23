"""Unit tests for tool base classes."""
import pytest
from security_agent.core.base_tool import ToolConfig, ToolInput, ToolOutput


def test_tool_config_creation():
    cfg = ToolConfig(
        tool_id="nmap",
        name="Nmap",
        description="Port scanner",
        category="recon",
        command_template="nmap {flags} {target}",
    )
    assert cfg.tool_id == "nmap"
    assert cfg.timeout_seconds == 120


def test_tool_input_defaults():
    ti = ToolInput(tool_id="nmap", target="192.168.1.1")
    assert ti.flags == ""
    assert ti.extra == {}


def test_tool_output_success():
    to = ToolOutput(
        tool_id="nmap", target="192.168.1.1",
        command="nmap 192.168.1.1",
        stdout="PORT   STATE\n22/tcp open",
        stderr="", exit_code=0, duration_seconds=1.5, success=True,
    )
    assert to.success is True
    assert to.exit_code == 0
