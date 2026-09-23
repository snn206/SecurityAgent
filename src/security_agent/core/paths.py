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


def get_config_path(filename: str = "") -> Path:
    """Get absolute path to a configuration file inside config/."""
    root_cfg = get_repo_root() / "config"
    if (root_cfg / filename).exists() if filename else root_cfg.exists():
        return root_cfg / filename if filename else root_cfg

    pkg_cfg = Path(__file__).resolve().parent.parent / "config"
    if (pkg_cfg / filename).exists() if filename else pkg_cfg.exists():
        return pkg_cfg / filename if filename else pkg_cfg

    return root_cfg / filename if filename else root_cfg


def get_registry_path(filename: str = "") -> Path:
    """Get absolute path to registry/ directory or a file inside registry/."""
    root_reg = get_repo_root() / "registry"
    if (root_reg / filename).exists() if filename else root_reg.exists():
        return root_reg / filename if filename else root_reg

    pkg_reg = Path(__file__).resolve().parent.parent / "registry"
    if (pkg_reg / filename).exists() if filename else pkg_reg.exists():
        return pkg_reg / filename if filename else pkg_reg

    return root_reg / filename if filename else root_reg
