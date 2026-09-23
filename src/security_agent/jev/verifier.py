"""JEV Verifier: Empirically verifies security findings, evidence, and tool outputs."""

from __future__ import annotations

import re
from typing import Any


class Verifier:
    """Verifies that reported findings and tool outputs meet empirical proof standards."""

    def verify_tool_output(self, tool_name: str, raw_output: str) -> dict[str, Any]:
        """Verify if a tool executed correctly and yielded valid security telemetry."""
        if not raw_output or not raw_output.strip():
            return {
                "verified": False,
                "reason": "Empty tool output received",
                "extracted_facts": [],
            }

        extracted_facts: list[str] = []

        if tool_name.lower() == "nmap":
            # Check for open ports pattern e.g. "80/tcp open http"
            open_ports = re.findall(r"(\d+/(?:tcp|udp)\s+open\s+[\w\.\-]+)", raw_output)
            if open_ports:
                extracted_facts.extend([f"Port open: {' '.join(p.split())}" for p in open_ports])
                return {
                    "verified": True,
                    "confidence": 0.95,
                    "facts_count": len(open_ports),
                    "extracted_facts": extracted_facts,
                    "evidence_snippet": open_ports[:5],
                }
            elif "0 hosts up" in raw_output or "Host seems down" in raw_output:
                return {
                    "verified": True,
                    "confidence": 0.9,
                    "reason": "Host appears down or blocking ICMP ping probes",
                    "extracted_facts": ["Target host is down or unresponsive"],
                }

        elif tool_name.lower() in ("gobuster", "dirb", "ffuf"):
            # Check for discovered endpoints e.g. "--> /admin (Status: 200)"
            paths = re.findall(r"(/[a-zA-Z0-9_\-\.\/]+)\s+\(Status:\s*(\d+)\)", raw_output)
            if paths:
                extracted_facts.extend([f"Path discovered: {p[0]} (HTTP {p[1]})" for p in paths])
                return {
                    "verified": True,
                    "confidence": 0.9,
                    "facts_count": len(paths),
                    "extracted_facts": extracted_facts,
                    "evidence_snippet": [f"{p[0]} [{p[1]}]" for p in paths[:5]],
                }

        elif tool_name.lower() in ("nuclei", "nikto"):
            # Check for vulnerability detection indicators
            vulns = re.findall(
                r"\[(critical|high|medium|low|info)\]\s+\[([\w\-]+)\]", raw_output, re.IGNORECASE
            )
            if vulns:
                extracted_facts.extend([f"Vuln template matched: {v[1]} ({v[0]})" for v in vulns])
                return {
                    "verified": True,
                    "confidence": 0.85,
                    "facts_count": len(vulns),
                    "extracted_facts": extracted_facts,
                    "evidence_snippet": [f"{v[1]} [{v[0]}]" for v in vulns[:5]],
                }

        # Generic output verification
        has_error = bool(
            re.search(r"\b(error|fatal|command not found|timed out)\b", raw_output, re.IGNORECASE)
        )
        return {
            "verified": not has_error,
            "confidence": 0.7 if not has_error else 0.2,
            "reason": "Command executed without fatal errors"
            if not has_error
            else "Tool reported execution error",
            "extracted_facts": extracted_facts,
        }

    def verify_finding(self, finding: dict[str, Any]) -> dict[str, Any]:
        """Verify if a security finding contains sufficient verifiable proof."""
        title = finding.get("title", "")
        proof = finding.get("proof") or finding.get("evidence") or ""
        severity = (finding.get("severity") or "info").lower()

        if not title:
            return {"verified": False, "score": 0.0, "reason": "Missing finding title"}

        # Critical and high severity findings require non-empty empirical proof
        if severity in ("critical", "high"):
            if not proof or len(str(proof).strip()) < 10:
                return {
                    "verified": False,
                    "score": 0.3,
                    "reason": f"High/Critical finding '{title}' lacks empirical proof/payload evidence",
                    "requires_validation": True,
                }

        return {
            "verified": True,
            "score": 0.9,
            "reason": "Finding satisfies empirical validation checks",
            "requires_validation": False,
        }
