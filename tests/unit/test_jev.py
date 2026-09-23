"""Unit tests for JEV (Judge / Evaluator / Verifier) and Evolution Engine."""
import pytest
from security_agent.jev.verifier import Verifier
from security_agent.jev.evaluator import Evaluator
from security_agent.jev.judge import Judge, Verdict
from security_agent.jev.evolution import EvolutionEngine
from security_agent.storage.document_store import DocumentStore


@pytest.fixture
def temp_store(tmp_path):
    return DocumentStore(base_dir=tmp_path / "memory")


def test_verifier_nmap():
    verifier = Verifier()
    sample_output = """
    Starting Nmap 7.94
    Nmap scan report for 10.0.2.15
    PORT     STATE SERVICE VERSION
    22/tcp   open  ssh     OpenSSH 8.9p1
    80/tcp   open  http    Apache httpd 2.4.52
    Nmap done: 1 IP address (1 host up) scanned in 2.15 seconds
    """
    res = verifier.verify_tool_output("nmap", sample_output)
    assert res["verified"] is True
    assert res["facts_count"] >= 2
    assert any("22/tcp open" in f for f in res["extracted_facts"])


def test_verifier_finding_without_proof():
    verifier = Verifier()
    finding = {"title": "Remote Code Execution", "severity": "critical", "proof": ""}
    res = verifier.verify_finding(finding)
    assert res["verified"] is False
    assert res["requires_validation"] is True


def test_evaluator_step():
    evaluator = Evaluator()
    v_res = {"verified": True, "confidence": 0.9, "facts_count": 3}
    score = evaluator.evaluate_step(
        agent_role="recon",
        goal="Discover open ports",
        tool_used="nmap",
        verification_result=v_res,
        duration_seconds=5.0,
    )
    assert score["score"] >= 0.8
    assert score["is_effective"] is True


def test_judge_verdict():
    judge = Judge()
    nmap_success = "80/tcp open http Apache\n443/tcp open ssl"
    judgment = judge.judge_step("recon", "Scan ports", "nmap", nmap_success)
    assert judgment["verdict"] == Verdict.PASS

    nmap_timeout = "Connection timed out after 30 seconds"
    judgment_timeout = judge.judge_step("recon", "Scan ports", "nmap", nmap_timeout)
    assert judgment_timeout["verdict"] == Verdict.RETRY


def test_evolution_distill_and_retrieve(temp_store):
    engine = EvolutionEngine(doc_store=temp_store)
    judgment = {
        "verdict": Verdict.RETRY,
        "evaluation": {"score": 0.4},
        "verification": {"verified": False},
    }
    raw_output = "Note: Host seems down. If it is really up, but blocking our ping probes, try -Pn"

    lesson = engine.distill_lesson(
        target="10.0.0.5",
        tool_name="nmap",
        agent_role="recon",
        judgment=judgment,
        raw_output=raw_output,
    )

    assert lesson is not None
    assert "-Pn" in lesson["insight"] or "-Pn" in lesson["recommended_flags"]

    retrieved = engine.get_lessons_for_execution("10.0.0.5", "nmap")
    assert len(retrieved) >= 1
    assert retrieved[0]["tool_name"] == "nmap"
