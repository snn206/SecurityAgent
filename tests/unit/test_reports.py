"""Unit tests for report builder and exporters."""
import pytest
from security_agent.reports.builder import ReportBuilder
from security_agent.reports.exporters import MarkdownExporter, JSONExporter


def test_report_builder():
    builder = ReportBuilder()
    report = builder.build(
        execution_id="exec-1",
        user_request="Scan target",
        scope="192.168.1.1",
        plan=None,
        findings=[{"tool_id": "nmap", "stdout": "22/tcp open", "exit_code": 0}],
        events=[],
        artifacts=[],
    )
    assert report["execution_id"] == "exec-1"
    assert len(report["findings"]) == 1
    assert "nmap" in report["tools_used"]


def test_markdown_exporter():
    builder = ReportBuilder()
    report = builder.build("exec-1", "Test", "192.168.1.1", None, [], [], [])
    md = MarkdownExporter().export(report)
    assert "# Security Assessment Report" in md
    assert "exec-1" in md


def test_json_exporter():
    import json
    builder = ReportBuilder()
    report = builder.build("exec-1", "Test", "", None, [], [], [])
    output = JSONExporter().export(report)
    parsed = json.loads(output)
    assert parsed["execution_id"] == "exec-1"
