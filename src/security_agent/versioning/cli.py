"""CLI for SecurityAgent component version manager (sa-update)."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from security_agent.versioning.manager import VersionManager

app = typer.Typer(name="sa-update", help="SecurityAgent component version manager")
console = Console()


@app.command("list")
def cmd_list() -> None:
    """List all component versions, artifact types, and references."""
    vm = VersionManager()
    registry = vm.load_registry()

    table = Table(
        title="SecurityAgent Component Versions", show_header=True, header_style="bold magenta"
    )
    table.add_column("Component", style="cyan")
    table.add_column("Version", style="green")
    table.add_column("Artifact Type", style="yellow")
    table.add_column("Reference / Package", style="dim")

    # Core
    core = registry.get("core", {})
    if isinstance(core, dict):
        table.add_row(
            "core",
            str(core.get("version", "—")),
            str(core.get("artifact", "git-tag")),
            str(core.get("ref", "main")),
        )

    # Sections
    for section_name in ("providers", "agents", "tools", "packages", "extensions"):
        section = registry.get(section_name, {})
        if isinstance(section, dict):
            for name, entry in section.items():
                if isinstance(entry, dict) and "version" in entry:
                    comp = f"{section_name}.{name}"
                    ref_or_pkg = (
                        entry.get("package") or entry.get("ref") or entry.get("install_cmd", "—")
                    )
                    table.add_row(
                        comp,
                        str(entry["version"]),
                        str(entry.get("artifact", "—")),
                        str(ref_or_pkg),
                    )

    console.print(table)


@app.command("info")
def cmd_info(
    component: str = typer.Argument(
        ..., help="Component path (e.g. 'core' or 'providers.anthropic')"
    ),
) -> None:
    """Show detailed metadata and changelog for a component."""
    vm = VersionManager()
    try:
        entry, _ = vm.resolve_component(component)
    except KeyError:
        console.print(f"[red]Error: Component '{component}' not found in registry.[/red]")
        raise typer.Exit(1)

    console.print(f"\n[bold cyan]Component:[/] {component}")
    for k, v in entry.items():
        console.print(f"  [yellow]{k}:[/] {v}")
    console.print()


@app.command("update")
def cmd_update(
    component: str = typer.Argument(
        "all", help="Component path ('core', 'tools.nmap', etc.) or 'all'"
    ),
    ssh: bool = typer.Option(False, "--ssh", help="Use SSH (git@github.com:...) instead of HTTPS"),
) -> None:
    """Update a specific component or all components to latest version."""
    vm = VersionManager()
    registry = vm.load_registry()

    if component in ("all", "core"):
        console.print("[cyan][*] Updating core from GitHub repository...[/cyan]")
        ok = vm.update_core_from_git(use_ssh=ssh)
        if ok:
            console.print("[green][✓] Core updated to latest version from GitHub.[/green]")
        else:
            console.print("[yellow][!] Core update check finished.[/yellow]")
        if component == "core":
            return

    if component == "all":
        # Update providers
        for name, entry in registry.get("providers", {}).items():
            pkg = entry.get("package")
            if pkg:
                console.print(f"[cyan][*] Updating provider: {name} ({pkg})...[/cyan]")
                vm.update_pip_package(pkg, entry.get("min_package_version"))

        # Update tools in sandbox
        for name, entry in registry.get("tools", {}).items():
            console.print(f"[cyan][*] Updating sandbox tool: {name}...[/cyan]")
            vm.install_tool_in_sandbox(name, entry)

        console.print("\n[bold green][✓] All components updated to latest.[/bold green]")
        return

    # Specific component
    try:
        entry, keys = vm.resolve_component(component)
    except KeyError:
        console.print(f"[red]Error: Component '{component}' not found.[/red]")
        raise typer.Exit(1)

    section = keys[0]
    name = keys[-1]

    if section == "tools":
        console.print(f"[cyan][*] Updating tool '{name}' in sandbox...[/cyan]")
        if vm.install_tool_in_sandbox(name, entry):
            console.print(f"[green][✓] Tool '{name}' updated successfully.[/green]")
        else:
            console.print(
                "[yellow][!] Could not execute update in sandbox (is container running?).[/yellow]"
            )
    elif section == "providers":
        pkg = entry.get("package")
        if pkg:
            console.print(f"[cyan][*] Updating provider package '{pkg}'...[/cyan]")
            vm.update_pip_package(pkg, entry.get("min_package_version"))
            console.print(f"[green][✓] Provider '{name}' package updated.[/green]")
        else:
            console.print(f"[yellow]No external pip package for provider '{name}'.[/yellow]")
    else:
        console.print(f"[dim]Component '{component}' has no automated update hook.[/dim]")

    console.print(f"\n[bold green][✓] Update finished for '{component}'.[/bold green]")


@app.command("rollback")
def cmd_rollback(
    component: str = typer.Argument(
        ..., help="Component path ('core', 'providers.anthropic', etc.)"
    ),
    target: str = typer.Argument(..., help="Target Git tag / commit SHA or SemVer"),
    ssh: bool = typer.Option(False, "--ssh", help="Use SSH for Git operations"),
) -> None:
    """Roll back a component independently to a specific Git tag, commit SHA, or version."""
    vm = VersionManager()

    if component == "core":
        console.print(f"[cyan][*] Rolling back core to Git ref: {target}...[/cyan]")
        ok = vm.rollback_core_to_ref(target, use_ssh=ssh)
        if ok:
            console.print(f"[green][✓] Core rolled back to Git ref '{target}'.[/green]")
        else:
            console.print(
                f"[red][✗] Failed to rollback core to '{target}'. Check your internet connection or git ref.[/red]"
            )
            raise typer.Exit(1)
        return

    try:
        entry, keys = vm.resolve_component(component)
    except KeyError:
        console.print(f"[red]Error: Component '{component}' not found.[/red]")
        raise typer.Exit(1)

    section = keys[0]
    name = keys[-1]

    if section == "providers":
        pkg = entry.get("package")
        if pkg:
            console.print(
                f"[cyan][*] Rolling back provider package '{pkg}' to version {target}...[/cyan]"
            )
            vm.rollback_pip_package(pkg, target)
        vm.set_version(component, target)
        console.print(
            f"[green][✓] Provider '{name}' pinned to version {target} in registry.[/green]"
        )
    else:
        vm.set_version(component, target)
        console.print(
            f"[green][✓] Recorded rollback for '{component}' to version {target}.[/green]"
        )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
