"""Sandbox CommandExecutor — runs commands in Docker (Kali Linux) container."""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from security_agent.core.exceptions import SandboxError


@dataclass
class ExecutionResult:
    command: str
    stdout: str
    stderr: str
    exit_code: int
    duration_seconds: float
    success: bool = True
    container_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class CommandExecutor:
    """Executes commands inside a Docker sandbox container."""

    def __init__(self, config_path: Path | None = None) -> None:
        from security_agent.core.paths import get_config_path
        cfg_path = config_path or get_config_path("sandbox.yaml")
        if cfg_path.exists():
            with cfg_path.open() as f:
                self._cfg: dict[str, Any] = yaml.safe_load(f).get("sandbox", {})
        else:
            self._cfg = {}

    def _get_image(self) -> str:
        return self._cfg.get("image", "security-agent-sandbox:latest")

    def _get_timeout(self, tool_id: str) -> int:
        # Per-tool timeout from tools.yaml would be loaded here
        return self._cfg.get("default_timeout", 300)

    async def run(
        self,
        tool_id: str,
        target: str,
        flags: str = "",
        command: str | None = None,
        timeout: int | None = None,
    ) -> ExecutionResult:
        """Run a command inside the Docker sandbox container.

        If `command` is provided directly, it's used as-is.
        Otherwise, builds from tool_id + target + flags.
        """
        if command is None:
            command = self._build_command(tool_id, target, flags)

        effective_timeout = timeout or self._get_timeout(tool_id)

        docker_cmd = [
            "docker", "run", "--rm",
            "--network", self._cfg.get("network_mode", "bridge"),
            "--memory", self._cfg.get("resources", {}).get("mem_limit", "2g"),
            "--cpus", str(self._cfg.get("resources", {}).get("cpu_count", 2)),
            self._get_image(),
            "bash", "-c", command,
        ]

        start = time.monotonic()
        try:
            proc = await asyncio.create_subprocess_exec(
                *docker_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout_b, stderr_b = await asyncio.wait_for(
                    proc.communicate(), timeout=effective_timeout
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.communicate()
                raise SandboxError(f"Command timed out after {effective_timeout}s")

            duration = time.monotonic() - start
            return ExecutionResult(
                command=command,
                stdout=stdout_b.decode("utf-8", errors="replace"),
                stderr=stderr_b.decode("utf-8", errors="replace"),
                exit_code=proc.returncode or 0,
                duration_seconds=round(duration, 2),
                success=(proc.returncode == 0),
            )
        except SandboxError:
            raise
        except Exception as exc:
            raise SandboxError(f"Docker execution failed: {exc}") from exc

    @staticmethod
    def _build_command(tool_id: str, target: str, flags: str) -> str:
        """Build shell command from tool template — simplified version."""
        templates = {
            "nmap": f"nmap {flags} {target}",
            "gobuster": f"gobuster dir -u {target} -w /wordlists/common.txt {flags}",
            "sqlmap": f"sqlmap -u {target} {flags} --batch",
            "nikto": f"nikto -h {target} {flags}",
            "whois": f"whois {target}",
            "curl": f"curl -sS -L --max-time 30 {flags} {target}",
            "shell": f"{target} {flags}",  # target = actual command for shell tool
        }
        return templates.get(tool_id, f"{tool_id} {target} {flags}").strip()
