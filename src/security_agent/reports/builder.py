"""Report builder — aggregates execution data into a structured report."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ReportBuilder:
    """Builds a structured report from execution data."""

    def build(
        self,
        execution_id: str,
        user_request: str,
        scope: str,
        plan: dict[str, Any] | None,
        findings: list[dict[str, Any]],
        events: list[Any],
        artifacts: list[str],
        provider: str = "",
        model: str = "",
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
    ) -> dict[str, Any]:
        """Build and return the full report as a dict."""

        # Timeline from events
        timeline = [
            {
                "timestamp": getattr(e, "timestamp", datetime.now(timezone.utc)).isoformat()
                if hasattr(e, "timestamp") else str(e.get("timestamp", "")),
                "event_type": getattr(e, "event_type", "").value
                if hasattr(getattr(e, "event_type", None), "value")
                else str(getattr(e, "event_type", e.get("event_type", ""))),
                "agent_id": getattr(e, "agent_id", e.get("agent_id", "")),
                "payload": getattr(e, "payload", e.get("payload", {})),
            }
            for e in events
        ]

        # Commands from timeline
        commands = [
            {
                "command": ev["payload"].get("command", ""),
                "stdout": ev["payload"].get("stdout", ""),
                "exit_code": ev["payload"].get("exit_code"),
            }
            for ev in timeline
            if ev["event_type"] in ("sandbox.command", "sandbox.exit")
        ]

        duration = None
        if started_at and completed_at:
            duration = (completed_at - started_at).total_seconds()

        return {
            "report_id": str(uuid.uuid4()),
            "execution_id": execution_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "metadata": {
                "provider": provider,
                "model": model,
                "duration_seconds": duration,
                "started_at": started_at.isoformat() if started_at else None,
                "completed_at": completed_at.isoformat() if completed_at else None,
            },
            "summary": self._generate_summary(user_request, findings),
            "objective": user_request,
            "scope": scope,
            "execution_timeline": timeline,
            "actions_performed": [
                s["description"] for s in (plan or {}).get("steps", [])
            ],
            "tools_used": list({
                f["tool_id"] for f in findings if f.get("tool_id")
            }),
            "findings": findings,
            "commands": commands,
            "artifacts": artifacts,
            "recommendations": self._generate_recommendations(findings),
        }

    @staticmethod
    def _generate_summary(objective: str, findings: list[dict[str, Any]]) -> str:
        count = len(findings)
        return (
            f"Security assessment completed for objective: {objective}. "
            f"{count} finding(s) recorded."
        )

    @staticmethod
    def _generate_recommendations(findings: list[dict[str, Any]]) -> list[str]:
        if not findings:
            return ["No findings to report. Consider broadening scope."]
        return [
            "Review all open ports and services identified.",
            "Patch or restrict access to vulnerable endpoints.",
            "Apply principle of least privilege where possible.",
        ]
