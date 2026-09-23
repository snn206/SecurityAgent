"""JEV Judge: Synthesizes verification and evaluation to render operational verdicts."""
from __future__ import annotations

from typing import Any
from security_agent.jev.verifier import Verifier
from security_agent.jev.evaluator import Evaluator


class Verdict:
    PASS = "PASS"
    RETRY = "RETRY"
    PIVOT = "PIVOT"
    FAIL = "FAIL"


class Judge:
    """Judges the outcome of an agent step and determines the operational next action."""

    def __init__(self, verifier: Verifier | None = None, evaluator: Evaluator | None = None) -> None:
        self.verifier = verifier or Verifier()
        self.evaluator = evaluator or Evaluator()

    def judge_step(
        self,
        agent_role: str,
        goal: str,
        tool_name: str | None,
        tool_output: str,
        duration_seconds: float = 0.0,
    ) -> dict[str, Any]:
        """Produce a complete JEV analysis and strategic verdict."""
        # 1. Verify
        verification = self.verifier.verify_tool_output(tool_name or "unknown", tool_output)

        # 2. Evaluate
        evaluation = self.evaluator.evaluate_step(
            agent_role=agent_role,
            goal=goal,
            tool_used=tool_name,
            verification_result=verification,
            duration_seconds=duration_seconds,
        )

        # 3. Judge verdict
        score = evaluation["score"]
        verified = verification["verified"]

        if verified and score >= 0.6:
            verdict = Verdict.PASS
            rationale = "Step produced verified security telemetry meeting standards."
            suggested_action = "PROCEED_TO_NEXT_STEP"
        elif not verified and ("timed out" in tool_output.lower() or "connection refused" in tool_output.lower()):
            verdict = Verdict.RETRY
            rationale = "Network timeout or rate-limiting detected. Recommend retry with adjusted timing/flags."
            suggested_action = "RETRY_WITH_ADAPTED_PARAMETERS"
        elif not verified and ("command not found" in tool_output.lower() or "blocked" in tool_output.lower()):
            verdict = Verdict.PIVOT
            rationale = "Target environment blocked tool or command is unavailable. Pivot to alternate vector."
            suggested_action = "SWITCH_TOOL_OR_TECHNIQUE"
        else:
            verdict = Verdict.PASS if score >= 0.5 else Verdict.FAIL
            rationale = "Step concluded with partial or unverified telemetry."
            suggested_action = "PROCEED_WITH_CAUTION" if score >= 0.5 else "ABORT_OR_ESCALATE"

        return {
            "verdict": verdict,
            "rationale": rationale,
            "suggested_action": suggested_action,
            "verification": verification,
            "evaluation": evaluation,
        }
