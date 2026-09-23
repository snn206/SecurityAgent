"""LangGraph node functions — each takes AgentState and returns state update dict."""

from __future__ import annotations

import uuid
from typing import Any

from security_agent.core.events import EventBus, EventType
from security_agent.core.state import AgentState
from security_agent.planning.planner import PlannerAgent
from security_agent.sandbox.executor import CommandExecutor

_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


async def planner_node(state: AgentState) -> dict[str, Any]:
    """Plan the task from the user request."""
    execution_id = state.get("execution_id", str(uuid.uuid4()))
    bus = get_event_bus()

    await bus.emit(EventType.AGENT_STARTED, execution_id=execution_id, agent_id="planner")
    await bus.emit(
        EventType.PLAN_CREATED,
        execution_id=execution_id,
        agent_id="planner",
        payload={"message": "Creating execution plan..."},
    )

    planner = PlannerAgent()

    # Inject user golden rules and past distilled lessons from memory
    from security_agent.memory.manager import get_memory_manager

    mem_mgr = get_memory_manager()
    memory_context = mem_mgr.get_consolidated_context(state.get("scope", ""))

    plan = await planner.create_plan(
        objective=state.get("user_request", ""),
        context={
            "scope": state.get("scope", ""),
            "memory_context": memory_context,
        },
    )

    await bus.emit(
        EventType.PLAN_CREATED,
        execution_id=execution_id,
        agent_id="planner",
        payload={"plan": plan.to_dict()},
    )

    return {
        "plan": plan.to_dict(),
        "current_step_id": plan.steps[0].step_id if plan.steps else None,
        "completed_steps": [],
        "status": "executing",
        "execution_id": execution_id,
    }


async def reasoner_node(state: AgentState) -> dict[str, Any]:
    """Evaluate intermediate results and decide next step."""
    execution_id = state.get("execution_id", "")
    bus = get_event_bus()
    await bus.emit(EventType.AGENT_STARTED, execution_id=execution_id, agent_id="reasoner")

    # Stub: pass through — extend with actual ReAct / ToT logic
    return {"status": "executing"}


async def tool_router_node(state: AgentState) -> dict[str, Any]:
    """Select the right tool for the current plan step."""
    execution_id = state.get("execution_id", "")
    bus = get_event_bus()
    await bus.emit(EventType.AGENT_STARTED, execution_id=execution_id, agent_id="tool_router")

    plan = state.get("plan") or {}
    current_step_id = state.get("current_step_id")
    steps = plan.get("steps", [])
    current_step = next((s for s in steps if s["step_id"] == current_step_id), None)

    if not current_step:
        return {"status": "reporting"}

    tools = current_step.get("tools", [])
    selected_tool = tools[0] if tools else "shell"

    await bus.emit(
        EventType.TOOL_SELECTED,
        execution_id=execution_id,
        agent_id="tool_router",
        payload={"tool_id": selected_tool, "step_id": current_step_id},
    )

    return {
        "pending_tool": selected_tool,
        "tool_input": {"tool_id": selected_tool, "target": state.get("scope", ""), "flags": ""},
    }


async def sandbox_executor_node(state: AgentState) -> dict[str, Any]:
    """Execute the selected tool in the Docker sandbox."""
    execution_id = state.get("execution_id", "")
    bus = get_event_bus()
    await bus.emit(EventType.SANDBOX_STARTED, execution_id=execution_id, agent_id="tool_router")

    tool_input = state.get("tool_input") or {}
    tool_id = tool_input.get("tool_id", "shell")
    target = tool_input.get("target", "")
    flags = tool_input.get("flags", "")

    # Build and execute command in sandbox
    executor = CommandExecutor()
    result = await executor.run(tool_id=tool_id, target=target, flags=flags)

    await bus.emit(
        EventType.SANDBOX_COMMAND,
        execution_id=execution_id,
        agent_id="tool_router",
        payload={"command": result.command},
    )
    await bus.emit(
        EventType.SANDBOX_STDOUT, execution_id=execution_id, payload={"stdout": result.stdout}
    )
    if result.stderr:
        await bus.emit(
            EventType.SANDBOX_STDERR, execution_id=execution_id, payload={"stderr": result.stderr}
        )
    await bus.emit(
        EventType.SANDBOX_EXIT,
        execution_id=execution_id,
        payload={"exit_code": result.exit_code, "duration": result.duration_seconds},
    )

    # Mark step complete
    completed_steps = list(state.get("completed_steps") or [])
    if state.get("current_step_id"):
        completed_steps.append(state["current_step_id"])

    # Find next step
    plan = state.get("plan") or {}
    steps = plan.get("steps", [])
    remaining = [s for s in steps if s["step_id"] not in completed_steps]
    next_step_id = remaining[0]["step_id"] if remaining else None

    return {
        "sandbox_command": result.command,
        "sandbox_stdout": result.stdout,
        "sandbox_stderr": result.stderr,
        "sandbox_exit_code": result.exit_code,
        "tool_output": {
            "tool_id": tool_id,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.exit_code,
        },
        "completed_steps": completed_steps,
        "current_step_id": next_step_id,
    }


async def analyzer_node(state: AgentState) -> dict[str, Any]:
    """Analyze tool output and extract findings."""
    execution_id = state.get("execution_id", "")
    bus = get_event_bus()
    await bus.emit(EventType.AGENT_STARTED, execution_id=execution_id, agent_id="analyzer")

    # JEV (Judge / Evaluator / Verifier) Harness & Evolution
    from security_agent.jev.evolution import EvolutionEngine
    from security_agent.jev.judge import Judge

    judge = Judge()
    evolution = EvolutionEngine()

    tool_output = state.get("tool_output") or {}
    findings = list(state.get("findings") or [])
    jev_judgments = list(state.get("jev_judgments") or [])

    if tool_output:
        tool_id = tool_output.get("tool_id", "unknown")
        stdout = tool_output.get("stdout", "")
        target = state.get("scope", "")

        # 1. Run JEV Judgment
        judgment = judge.judge_step(
            agent_role="analyzer",
            goal=state.get("user_request", ""),
            tool_name=tool_id,
            tool_output=stdout,
        )
        jev_judgments.append(judgment)

        # 2. Distill lessons learned from this run (evolution)
        lesson = evolution.distill_lesson(
            target=target,
            tool_name=tool_id,
            agent_role="analyzer",
            judgment=judgment,
            raw_output=stdout,
        )

        # 3. Verified finding extraction
        findings.append(
            {
                "tool_id": tool_id,
                "stdout": stdout[:2000],
                "exit_code": tool_output.get("exit_code"),
                "jev_score": judgment["evaluation"]["score"],
                "jev_grade": judgment["evaluation"]["grade"],
                "verdict": judgment["verdict"],
                "facts_count": judgment["verification"].get("facts_count", 0),
            }
        )

    await bus.emit(
        EventType.FINDING,
        execution_id=execution_id,
        agent_id="analyzer",
        payload={"findings_count": len(findings)},
    )

    return {"findings": findings, "jev_judgments": jev_judgments}


async def reporter_node(state: AgentState) -> dict[str, Any]:
    """Generate the final report."""
    execution_id = state.get("execution_id", "")
    bus = get_event_bus()
    await bus.emit(EventType.AGENT_STARTED, execution_id=execution_id, agent_id="reporter")

    report = {
        "execution_id": execution_id,
        "objective": (state.get("plan") or {}).get("objective", state.get("user_request", "")),
        "scope": state.get("scope", ""),
        "findings": state.get("findings", []),
        "artifacts": state.get("artifacts", []),
        "status": "complete",
    }

    await bus.emit(
        EventType.REPORT_GENERATED,
        execution_id=execution_id,
        agent_id="reporter",
        payload={"report_id": execution_id},
    )
    await bus.emit(EventType.TASK_COMPLETED, execution_id=execution_id, agent_id="reporter")

    return {"report": report, "status": "done"}
