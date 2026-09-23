"""Sandbox manager — lifecycle management of Docker containers."""
from __future__ import annotations

import docker
from docker.models.containers import Container
from pathlib import Path
from typing import Any

import yaml

from security_agent.core.exceptions import SandboxError


class SandboxManager:
    """Manages the Docker sandbox container lifecycle."""

    def __init__(self, config_path: Path | None = None) -> None:
        cfg_path = config_path or (
            Path(__file__).parent.parent.parent.parent.parent / "config" / "sandbox.yaml"
        )
        if cfg_path.exists():
            with cfg_path.open() as f:
                self._cfg: dict[str, Any] = yaml.safe_load(f).get("sandbox", {})
        else:
            self._cfg = {}

        try:
            self._client = docker.from_env()
        except Exception as exc:
            raise SandboxError(f"Cannot connect to Docker daemon: {exc}") from exc

    def start(self, execution_id: str) -> Container:
        """Start a new sandbox container for the given execution."""
        image = self._cfg.get("image", "security-agent-sandbox:latest")
        name = f"{self._cfg.get('container_name_prefix', 'sa-sandbox')}-{execution_id[:8]}"
        resources = self._cfg.get("resources", {})

        try:
            container = self._client.containers.run(
                image=image,
                name=name,
                command="sleep infinity",
                detach=True,
                remove=self._cfg.get("auto_remove", True),
                network_mode=self._cfg.get("network_mode", "bridge"),
                mem_limit=resources.get("mem_limit", "2g"),
                cpu_count=resources.get("cpu_count", 2),
                cap_drop=self._cfg.get("cap_drop", ["ALL"]),
                cap_add=self._cfg.get("cap_add", ["NET_RAW"]),
                working_dir=self._cfg.get("workdir", "/workspace"),
                volumes=self._build_volumes(),
            )
            return container
        except Exception as exc:
            raise SandboxError(f"Failed to start sandbox container: {exc}") from exc

    def stop(self, container: Container) -> None:
        """Stop and remove a sandbox container."""
        try:
            container.stop(timeout=5)
        except Exception:
            pass

    def exec_command(self, container: Container, command: str) -> tuple[int, str]:
        """Execute a command in a running container. Returns (exit_code, output)."""
        try:
            exit_code, output = container.exec_run(
                cmd=["bash", "-c", command],
                demux=False,
            )
            return exit_code, (output or b"").decode("utf-8", errors="replace")
        except Exception as exc:
            raise SandboxError(f"exec_run failed: {exc}") from exc

    def _build_volumes(self) -> dict[str, dict[str, str]]:
        volumes_cfg = self._cfg.get("volumes", [])
        volumes: dict[str, dict[str, str]] = {}
        for v in volumes_cfg:
            host = str(Path(v["host"]).resolve())
            Path(host).mkdir(parents=True, exist_ok=True)
            volumes[host] = {"bind": v["container"], "mode": v.get("mode", "rw")}
        return volumes

    def pull_image(self) -> None:
        """Pull the sandbox Docker image."""
        image = self._cfg.get("image", "security-agent-sandbox:latest")
        self._client.images.pull(image)

    def is_healthy(self) -> bool:
        """Check if Docker daemon is reachable."""
        try:
            self._client.ping()
            return True
        except Exception:
            return False
