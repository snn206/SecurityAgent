"""Repository path discovery utilities."""
from __future__ import annotations

import os
from pathlib import Path


def get_repo_root() -> Path:
    """Find repository root by traversing upward for pyproject.toml or config."""
    # Check if SA_ROOT is set in environment
    if "SA_ROOT" in os.environ:
        return Path(os.environ["SA_ROOT"])

    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists() or (parent / "config").exists():
            return parent
    return Path.cwd()


def get_config_path(filename: str) -> Path:
    """Get absolute path to a configuration file inside config/."""
    return get_repo_root() / "config" / filename
