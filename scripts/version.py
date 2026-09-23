"""
SecurityAgent version helpers: bump, validate, and tag.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Literal

import yaml

ROOT = Path(__file__).parent.parent
REGISTRY_FILE = ROOT / "registry" / "versions.yaml"

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.]+))?(?:\+([a-zA-Z0-9.]+))?$")

BumpType = Literal["major", "minor", "patch"]


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


def get_component_version(component_path: str) -> str:
    """Read version from registry by dotted path (e.g. 'tools.nmap')."""
    with REGISTRY_FILE.open() as f:
        registry = yaml.safe_load(f)
    keys = component_path.split(".")
    node = registry
    for key in keys:
        node = node[key]
    return node["version"]


def set_component_version(component_path: str, new_version: str) -> None:
    """Write updated version to registry."""
    if not is_valid_semver(new_version):
        raise ValueError(f"Invalid semver: {new_version!r}")
    with REGISTRY_FILE.open() as f:
        registry = yaml.safe_load(f)
    keys = component_path.split(".")
    node = registry
    for key in keys[:-1]:
        node = node[key]
    node[keys[-1]]["version"] = new_version
    with REGISTRY_FILE.open("w") as f:
        yaml.dump(registry, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def git_tag(tag: str, message: str = "") -> None:
    """Create a Git tag."""
    msg = message or f"Release {tag}"
    subprocess.run(["git", "tag", "-a", tag, "-m", msg], check=True, cwd=ROOT)
    print(f"[GIT] Tagged: {tag}")


def git_push_tags() -> None:
    subprocess.run(["git", "push", "--tags"], check=True, cwd=ROOT)
    print("[GIT] Tags pushed.")
