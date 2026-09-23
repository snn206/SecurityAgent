"""Core version manager for SecurityAgent components."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Literal

import yaml

from security_agent.core.paths import get_registry_path

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.]+))?(?:\+([a-zA-Z0-9.]+))?$")
BumpType = Literal["major", "minor", "patch"]
GIT_REPO_URL_DEFAULT = "git+https://github.com/snn206/SecurityAgent.git"
GIT_REPO_SSH_DEFAULT = "git+ssh://git@github.com/snn206/SecurityAgent.git"


def parse_semver(version: str) -> tuple[int, int, int]:
    m = SEMVER_RE.match(version)
    if not m:
        raise ValueError(f"Invalid semver: {version!r}")
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def bump_version(current: str, bump: BumpType) -> str:
    major, minor, patch = parse_semver(current)
    match bump:
        case "major":
            return f"{major + 1}.0.0"
        case "minor":
            return f"{major}.{minor + 1}.0"
        case "patch":
            return f"{major}.{minor}.{patch + 1}"


def is_valid_semver(version: str) -> bool:
    return bool(SEMVER_RE.match(version))


class VersionManager:
    """Manages version inspection, updates, rollbacks, and GitHub installations."""

    def __init__(self, registry_file: Path | None = None) -> None:
        self.registry_file = registry_file or get_registry_path("versions.yaml")

    def load_registry(self) -> dict[str, Any]:
        if not self.registry_file.exists():
            return {}
        with self.registry_file.open(encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def save_registry(self, data: dict[str, Any]) -> None:
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        with self.registry_file.open("w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def resolve_component(self, component_path: str) -> tuple[dict[str, Any], list[str]]:
        registry = self.load_registry()
        keys = component_path.split(".")
        node: Any = registry
        for key in keys:
            if not isinstance(node, dict) or key not in node:
                raise KeyError(f"Component not found in registry: {component_path}")
            node = node[key]
        return node, keys

    def get_version(self, component_path: str) -> str:
        entry, _ = self.resolve_component(component_path)
        return str(entry.get("version", "unknown"))

    def set_version(self, component_path: str, new_version: str) -> None:
        registry = self.load_registry()
        keys = component_path.split(".")
        node: Any = registry
        for key in keys[:-1]:
            node = node[key]
        if keys[-1] in node and isinstance(node[keys[-1]], dict):
            node[keys[-1]]["version"] = new_version
        else:
            node[keys[-1]] = {"version": new_version}
        self.save_registry(registry)

    def update_core_from_git(self, ref: str | None = None, use_ssh: bool = False) -> bool:
        """Update core SecurityAgent directly from GitHub via uv or pip."""
        repo_base = GIT_REPO_SSH_DEFAULT if use_ssh else GIT_REPO_URL_DEFAULT
        target = f"{repo_base}@{ref}" if ref else repo_base

        # Determine installer: prefer uv if available, fallback to sys.executable -m pip
        uv_path = shutil.which("uv")
        if uv_path:
            cmd = [uv_path, "pip", "install", "--upgrade", target]
        else:
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade", target]

        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode == 0:
            if ref:
                self.set_version("core", ref)
            return True
        return False

    def rollback_core_to_ref(self, ref: str, use_ssh: bool = False) -> bool:
        """Rollback core SecurityAgent to a specific Git tag or commit SHA."""
        return self.update_core_from_git(ref=ref, use_ssh=use_ssh)

    def update_pip_package(self, package: str, min_version: str | None = None) -> bool:
        """Update a provider or utility Python package."""
        pkg_spec = f"{package}>={min_version}" if min_version else package
        uv_path = shutil.which("uv")
        if uv_path:
            cmd = [uv_path, "pip", "install", "--upgrade", pkg_spec]
        else:
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade", pkg_spec]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        return proc.returncode == 0

    def rollback_pip_package(self, package: str, version: str) -> bool:
        """Pin a pip package to a specific version."""
        pkg_spec = f"{package}=={version}"
        uv_path = shutil.which("uv")
        if uv_path:
            cmd = [uv_path, "pip", "install", pkg_spec]
        else:
            cmd = [sys.executable, "-m", "pip", "install", pkg_spec]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        return proc.returncode == 0

    def install_tool_in_sandbox(self, name: str, entry: dict[str, Any]) -> bool:
        """Run install/update command inside Kali Docker sandbox."""
        install_cmd = entry.get("install_cmd")
        if not install_cmd:
            return False
        docker_path = shutil.which("docker")
        if not docker_path:
            return False
        proc = subprocess.run(
            [docker_path, "exec", "security-agent-sandbox", "bash", "-c", install_cmd],
            capture_output=True,
            text=True,
        )
        return proc.returncode == 0


def get_component_version(component_path: str) -> str:
    return VersionManager().get_version(component_path)
