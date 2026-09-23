"""Report exporters — Markdown, JSON, HTML, PDF."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import markdown as md_lib


class MarkdownExporter:
    def export(self, report: dict[str, Any]) -> str:
        meta = report.get("metadata", {})
        findings = report.get("findings", [])
        tools = report.get("tools_used", [])
        commands = report.get("commands", [])

        lines = [
            "# Security Assessment Report",
            "",
            f"**Report ID:** `{report.get('report_id', '')}`  ",
            f"**Execution ID:** `{report.get('execution_id', '')}`  ",
            f"**Generated:** {report.get('generated_at', '')}  ",
            f"**Provider:** {meta.get('provider', '—')} / {meta.get('model', '—')}  ",
            f"**Duration:** {meta.get('duration_seconds', '—')}s  ",
            "",
            "---",
            "",
            "## Summary",
            "",
            report.get("summary", ""),
            "",
            "## Objective",
            "",
            report.get("objective", ""),
            "",
            "## Scope",
            "",
            report.get("scope", "—"),
            "",
            "## Tools Used",
            "",
            *(([f"- `{t}`" for t in tools]) or ["- None"]),
            "",
            "## Actions Performed",
            "",
            *(([f"- {a}" for a in report.get("actions_performed", [])]) or ["- None"]),
            "",
            "## Findings",
            "",
        ]

        if findings:
            for i, finding in enumerate(findings, 1):
                lines += [
                    f"### Finding {i}: {finding.get('tool_id', 'Unknown')}",
                    "",
                    "```",
                    (finding.get("stdout") or "")[:2000],
                    "```",
                    "",
                    f"**Exit code:** `{finding.get('exit_code', '?')}`",
                    "",
                ]
        else:
            lines.append("No findings recorded.")

        lines += ["", "## Commands Executed", ""]
        for cmd in commands:
            if cmd.get("command"):
                lines += ["```bash", cmd["command"], "```", ""]

        lines += [
            "## Recommendations",
            "",
            *[f"- {r}" for r in report.get("recommendations", [])],
            "",
            "## Artifacts",
            "",
            *(([f"- `{a}`" for a in report.get("artifacts", [])]) or ["- None"]),
        ]

        return "\n".join(lines)


class JSONExporter:
    def export(self, report: dict[str, Any]) -> str:
        return json.dumps(report, indent=2, default=str)


class HTMLExporter:
    def export(self, report: dict[str, Any]) -> str:
        md_content = MarkdownExporter().export(report)
        body = md_lib.markdown(md_content, extensions=["fenced_code", "tables"])
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Security Assessment Report — {report.get('execution_id', '')}</title>
<style>
  body {{ font-family: 'Segoe UI', sans-serif; max-width: 960px; margin: 40px auto; padding: 0 20px; }}
  pre {{ background: #1d1d2e; color: #a8dadc; padding: 16px; border-radius: 6px; overflow-x: auto; }}
</style>
</head>
<body>{body}</body>
</html>"""


class PDFExporter:
    def export(self, report: dict[str, Any], output_path: Path) -> Path:
        try:
            import weasyprint  # type: ignore
            html = HTMLExporter().export(report)
            weasyprint.HTML(string=html).write_pdf(str(output_path))
            return output_path
        except ImportError:
            raise RuntimeError("Install weasyprint: pip install weasyprint")
