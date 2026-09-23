"""
SecurityAgent Update & Version Management CLI.

Usage:
    python scripts/update.py list
    python scripts/update.py update all
    python scripts/update.py update tools.nmap
    python scripts/update.py rollback providers.anthropic 1.2.0
    python scripts/update.py info tools.nmap
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

import typer
import yaml

ROOT = Path(__file__).parent.parent
REGISTRY_FILE = ROOT / "registry" / "versions.yaml"

app = typer.Typer(name="sa-update", help="SecurityAgent component version manager")


def _load_registry() -> dict[str, Any]:
    with REGISTRY_FILE.open() as f:
        return yaml.safe_load(f)


def _save_registry(data: dict[str, Any]) -> None:
    with REGISTRY_FILE.open("w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def _resolve_component(registry: dict[str, Any], component_path: str) -> tuple[dict, list[str]]:
    """Resolve 'tools.nmap' → (entry_dict, key_path)."""
    keys = component_path.split(".")
    node: Any = registry
    for key in keys:
        if not isinstance(node, dict) or key not in node:
            typer.echo(f"[ERROR] Component not found: {component_path}", err=True)
            raise typer.Exit(1)
        node = node[key]
    return node, keys


def _install_tool(name: str, entry: dict[str, Any]) -> None:
    """Install/update a tool inside the sandbox container."""
    install_cmd = entry.get("install_cmd")
    if not install_cmd:
        typer.echo(f"  [SKIP] No install_cmd for tool '{name}'")
        return

    typer.echo(f"  [TOOL] Installing '{name}' in sandbox: {install_cmd}")
    result = subprocess.run(
        ["docker", "exec", "security-agent-sandbox", "bash", "-c", install_cmd],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        typer.echo(f"  [OK] '{name}' installed successfully.")
    else:
        typer.echo(f"  [WARN] '{name}' install failed: {result.stderr.strip()}", err=True)


def _update_pip_package(package: str, min_version: str | None = None) -> None:
    """Update a pip package to latest."""
    pkg_spec = f"{package}>={min_version}" if min_version else package
    typer.echo(f"  [PKG] Updating pip package: {pkg_spec}")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", pkg_spec], check=False)


@app.command("list")
def cmd_list() -> None:
    """List all component versions."""
    registry = _load_registry()
    typer.echo(f"\n{'Component':<40} {'Version':<15} {'Artifact'}")
    typer.echo("-" * 70)

    def _print_section(section_name: str, section: dict) -> None:
        for name, entry in section.items():
            if isinstance(entry, dict) and "version" in entry:
                comp = f"{section_name}.{name}"
                typer.echo(f"{comp:<40} {entry['version']:<15} {entry.get('artifact', '—')}")

    for section_name in ("core", "providers", "agents", "tools", "packages", "extensions"):
        section = registry.get(section_name, {})
        if section_name == "core" and isinstance(section, dict) and "version" in section:
            typer.echo(f"{'core':<40} {section['version']:<15} {section.get('artifact', '—')}")
        elif isinstance(section, dict):
            _print_section(section_name, section)
    typer.echo()


@app.command("update")
def cmd_update(
    component: str = typer.Argument(help="Component path (e.g. 'tools.nmap') or 'all'"),
) -> None:
    """Update a component or all components to latest."""
    registry = _load_registry()

    if component == "all":
        typer.echo("[UPDATE] Updating all components...")
        # Update all pip-based providers
        providers = registry.get("providers", {})
        for name, entry in providers.items():
            pkg = entry.get("package")
            if pkg:
                _update_pip_package(pkg, entry.get("min_package_version"))

        # Update all tools in sandbox
        tools = registry.get("tools", {})
        for name, entry in tools.items():
            _install_tool(name, entry)

        typer.echo("\n[DONE] All components updated.")
        return

    entry, keys = _resolve_component(registry, component)
    section = keys[0]
    name = keys[-1]

    if section == "tools":
        _install_tool(name, entry)
    elif section == "providers":
        pkg = entry.get("package")
        if pkg:
            _update_pip_package(pkg, entry.get("min_package_version"))
        else:
            typer.echo(f"  [SKIP] No pip package for provider '{name}'")
    else:
        typer.echo(f"[INFO] Component '{component}' (type: {section}) — update not automated yet.")

    typer.echo(f"\n[DONE] '{component}' update complete.")


@app.command("rollback")
def cmd_rollback(
    component: str = typer.Argument(help="Component path (e.g. 'providers.anthropic')"),
    version: str = typer.Argument(help="Target version to roll back to"),
) -> None:
    """Roll back a component to a specific version."""
    registry = _load_registry()
    entry, keys = _resolve_component(registry, component)
    current = entry.get("version", "unknown")
    section = keys[0]
    name = keys[-1]

    typer.echo(f"[ROLLBACK] {component}: {current} → {version}")

    if section == "providers":
        pkg = entry.get("package")
        if pkg:
            typer.echo(f"  [PKG] Pinning {pkg}=={version}")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", f"{pkg}=={version}"], check=False
            )
        # Update registry
        node = registry
        for key in keys[:-1]:
            node = node[key]
        node[keys[-1]]["version"] = version
        _save_registry(registry)
        typer.echo(f"  [REGISTRY] Updated registry: {component} → {version}")

    elif section == "tools":
        typer.echo("  [WARN] Tool rollback requires manual Docker layer rebuild.")
        typer.echo(f"  Pinning version in registry to: {version}")
        node = registry
        for key in keys[:-1]:
            node = node[key]
        node[keys[-1]]["version"] = version
        _save_registry(registry)
    else:
        typer.echo(f"  [INFO] Recording rollback in registry for '{component}'.")
        node = registry
        for key in keys[:-1]:
            node = node[key]
        node[keys[-1]]["version"] = version
        _save_registry(registry)

    typer.echo(f"\n[DONE] Rollback of '{component}' to {version} complete.")


@app.command("info")
def cmd_info(component: str = typer.Argument(help="Component path")) -> None:
    """Show detailed info for a component."""
    registry = _load_registry()
    entry, _ = _resolve_component(registry, component)
    typer.echo(f"\n[{component}]")
    for k, v in entry.items():
        typer.echo(f"  {k}: {v}")
    typer.echo()


def main() -> None:
    app()


if __name__ == "__main__":
    main()
