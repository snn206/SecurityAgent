#!/usr/bin/env python3
"""
SecurityAgent version helpers: bump, validate, and tag.
"""

from __future__ import annotations

import subprocess

from security_agent.core.paths import get_registry_path, get_repo_root
from security_agent.versioning.manager import (
    VersionManager,
    get_component_version,
    is_valid_semver,
)

ROOT = get_repo_root()
REGISTRY_FILE = get_registry_path("versions.yaml")


def set_component_version(component_path: str, new_version: str) -> None:
    """Write updated version to registry."""
    if not is_valid_semver(new_version):
        raise ValueError(f"Invalid semver: {new_version!r}")
    VersionManager().set_version(component_path, new_version)


def git_tag(tag: str, message: str = "") -> None:
    """Create a Git tag."""
    msg = message or f"Release {tag}"
    subprocess.run(["git", "tag", "-a", tag, "-m", msg], check=True, cwd=ROOT)
    print(f"[GIT] Tagged: {tag}")


def git_push_tags() -> None:
    subprocess.run(["git", "push", "--tags"], check=True, cwd=ROOT)
    print("[GIT] Tags pushed.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        print(f"Core version: {get_component_version('core')}")
    else:
        print("Usage: python scripts/version.py [info]")
