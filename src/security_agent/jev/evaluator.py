"""JEV Evaluator: Quantitative assessment of agent steps and findings."""
from __future__ import annotations

from typing import Any


class Evaluator:
    """Evaluates agent step quality, tool choice efficiency, and output utility."""

    def evaluate_step(
        self,
        agent_role: str,
        goal: str,
        tool_used: str | None,
        verification_result: dict[str, Any],
        duration_seconds: float = 0.0,
    ) -> dict[str, Any]:
        """Score an agent step based on verification telemetry and goal progress."""
        is_verified = verification_result.get("verified", False)
        confidence = verification_result.get("confidence", 0.5)
        facts_count = verification_result.get("facts_count", 0)

        # Base score from verification
        base_score = 0.8 if is_verified else 0.2
        confidence_factor = confidence * 0.2
        facts_bonus = min(0.1, facts_count * 0.02)

        total_score = min(1.0, round(base_score + confidence_factor + facts_bonus, 2))

        # Check for latency penalty if step took excessive time
        latency_penalty = 0.0
        if duration_seconds > 120.0:
            latency_penalty = 0.1
            total_score = max(0.1, round(total_score - latency_penalty, 2))

        # Classify step quality
        if total_score >= 0.8:
            grade = "A"
        elif total_score >= 0.6:
            grade = "B"
        elif total_score >= 0.4:
            grade = "C"
        else:
            grade = "D"

        return {
            "score": total_score,
            "grade": grade,
            "agent_role": agent_role,
            "tool_used": tool_used,
            "facts_discovered": facts_count,
            "duration_seconds": duration_seconds,
            "is_effective": total_score >= 0.6,
        }
