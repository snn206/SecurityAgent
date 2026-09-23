"""JEV Evolution Engine: Distills lessons learned from successes and failures.

Enables agents to learn from experience, evolve tactics, and avoid repeating mistakes
by querying past lessons stored in the embedded document store.
"""
from __future__ import annotations

import re
from typing import Any
from security_agent.storage.document_store import DocumentStore, get_document_store


class EvolutionEngine:
    """Extracts lessons, manages agent evolutionary knowledge, and provides retrieval."""

    def __init__(self, doc_store: DocumentStore | None = None) -> None:
        self.doc_store = doc_store or get_document_store()
        self.collection = "lessons_learned"

    def distill_lesson(
        self,
        target: str,
        tool_name: str | None,
        agent_role: str,
        judgment: dict[str, Any],
        raw_output: str = "",
    ) -> dict[str, Any] | None:
        """Extract a structured lesson from a JEV judgment and save to document store."""
        verdict = judgment.get("verdict")
        evaluation = judgment.get("evaluation", {})
        score = evaluation.get("score", 0.5)

        lesson_type = "OPTIMIZATION" if score >= 0.8 else ("RECOVERY" if verdict in ("RETRY", "PIVOT") else "OBSERVATION")
        title = ""
        insight = ""
        recommended_flags = ""

        lower_out = raw_output.lower()

        if "host seems down" in lower_out or "0 hosts up" in lower_out:
            title = f"{tool_name or 'Scanner'} blocked by ping probe filtering"
            insight = f"Target {target} drops ICMP echo requests. Always supply -Pn to skip host discovery."
            recommended_flags = "-Pn -sT"
            lesson_type = "RECOVERY"
        elif "rate limit" in lower_out or "429 too many requests" in lower_out:
            title = f"Rate-limiting detected on {target}"
            insight = f"Target {target} implements active request rate throttling. Reduce threads and inject delays."
            recommended_flags = "--scan-delay 200ms --max-rate 50"
            lesson_type = "RECOVERY"
        elif "waf" in lower_out or "cloudflare" in lower_out or "forbidden (403)" in lower_out:
            title = f"WAF/Defense blocking on {target}"
            insight = f"Target {target} is shielded by WAF. Standard wordlists trigger 403. Use randomized headers."
            recommended_flags = "-H 'User-Agent: Mozilla/5.0...'"
            lesson_type = "RECOVERY"
        elif score >= 0.8 and tool_name:
            facts = judgment.get("verification", {}).get("facts_count", 0)
            title = f"High-yield configuration for {tool_name}"
            insight = f"Tool {tool_name} successfully extracted {facts} verified security facts against {target}."
            recommended_flags = "standard_optimized"

        if not title:
            return None

        lesson_doc = {
            "title": title,
            "target": target,
            "tool_name": tool_name or "general",
            "agent_role": agent_role,
            "lesson_type": lesson_type,
            "insight": insight,
            "recommended_flags": recommended_flags,
            "verdict": verdict,
            "score": score,
            "source": "JEV_AUTO_EVOLUTION",
        }

        # Check if identical lesson already exists to prevent duplicate noise
        existing = self.doc_store.find_one(
            self.collection,
            {"target": target, "tool_name": tool_name or "general", "title": title}
        )
        if not existing:
            doc_id = self.doc_store.insert_one(self.collection, lesson_doc)
            lesson_doc["_id"] = doc_id
        else:
            self.doc_store.update_one(
                self.collection,
                {"_id": existing["_id"]},
                {"$set": {"updated_at": lesson_doc.get("created_at"), "score": score}}
            )
            lesson_doc["_id"] = existing["_id"]

        return lesson_doc

    def get_lessons_for_execution(
        self, target: str, tool_name: str | None = None
    ) -> list[dict[str, Any]]:
        """Retrieve relevant past lessons for a target or tool to guide current execution."""
        filter_criteria: dict[str, Any] = {"target": target}
        lessons = self.doc_store.find(self.collection, filter_criteria, limit=10)

        # Also find general tool lessons
        if tool_name:
            tool_lessons = self.doc_store.find(self.collection, {"tool_name": tool_name}, limit=5)
            # Merge without duplicates
            seen_ids = {l.get("_id") for l in lessons}
            for tl in tool_lessons:
                if tl.get("_id") not in seen_ids:
                    lessons.append(tl)

        return lessons
