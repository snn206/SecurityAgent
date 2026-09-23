"""FastAPI router for independent component version management and artifact installation."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from security_agent.versioning.manager import VersionManager

router = APIRouter(prefix="/versions", tags=["versions"])
vm = VersionManager()


class UpdateRequest(BaseModel):
    component: str = Field(default="all", description="Component path or 'all'")
    ref: str | None = Field(default=None, description="Optional Git tag / commit SHA or version")
    use_ssh: bool = Field(default=False, description="Use SSH for Git operations")


class RollbackRequest(BaseModel):
    component: str = Field(..., description="Component path ('core', 'providers.anthropic', etc.)")
    target: str = Field(..., description="Target Git ref or version")
    use_ssh: bool = Field(default=False, description="Use SSH for Git operations")


class InstallArtifactRequest(BaseModel):
    component: str = Field(..., description="Component path or identifier")
    artifact_source: str = Field(
        ..., description="URL to .zip, local archive path, git ref, or package version"
    )
    artifact_type: str | None = Field(
        default=None, description="Type: zip | git-tag | git-commit | pypi"
    )


@router.get("")
async def list_versions() -> dict[str, Any]:
    """List all independent system components, versions, and artifact types."""
    components = vm.list_components()
    categories = list({c["category"] for c in components})
    return {
        "status": "ok",
        "total": len(components),
        "categories": categories,
        "components": components,
    }


@router.get("/{component_path:path}")
async def get_component_info(component_path: str) -> dict[str, Any]:
    """Get metadata, changelog, and current version of a specific component."""
    try:
        entry, _ = vm.resolve_component(component_path)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Component '{component_path}' not found")

    changelog = vm.get_changelog(component_path)
    return {
        "status": "ok",
        "component": component_path,
        "entry": entry,
        "changelog": changelog,
    }


@router.post("/update")
async def update_component(req: UpdateRequest) -> dict[str, Any]:
    """Update a specific component or all components to latest."""
    if req.component in ("all", "core"):
        ok = vm.update_core_from_git(ref=req.ref, use_ssh=req.use_ssh)
        if req.component == "core":
            return {
                "status": "ok" if ok else "failed",
                "component": "core",
                "message": "Core updated from GitHub",
            }

    if req.component == "all":
        reg = vm.load_registry()
        for name, entry in reg.get("providers", {}).items():
            pkg = entry.get("package")
            if pkg:
                vm.update_pip_package(pkg, entry.get("min_package_version"))
        for name, entry in reg.get("tools", {}).items():
            vm.install_tool_in_sandbox(name, entry)

        return {"status": "ok", "component": "all", "message": "All components updated to latest"}

    try:
        entry, keys = vm.resolve_component(req.component)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Component '{req.component}' not found")

    sec = keys[0]
    name = keys[-1]

    if sec == "tools":
        ok = vm.install_tool_in_sandbox(name, entry)
        msg = (
            f"Tool '{name}' updated in sandbox" if ok else f"Tool '{name}' sandbox update triggered"
        )
    elif sec in ("providers", "packages"):
        pkg = entry.get("package") or name
        ok = vm.update_pip_package(pkg, entry.get("min_package_version"))
        msg = f"Package '{pkg}' updated" if ok else "Package update failed"
    else:
        msg = f"Component '{req.component}' update recorded"

    return {"status": "ok", "component": req.component, "message": msg}


@router.post("/rollback")
async def rollback_component(req: RollbackRequest) -> dict[str, Any]:
    """Roll back an independent component to a target Git ref, package version, or registry tag."""
    if req.component == "core":
        ok = vm.rollback_core_to_ref(req.target, use_ssh=req.use_ssh)
        if not ok:
            raise HTTPException(
                status_code=500, detail=f"Failed to rollback core to '{req.target}'"
            )
        return {
            "status": "ok",
            "component": "core",
            "target": req.target,
            "message": f"Core rolled back to {req.target}",
        }

    try:
        entry, keys = vm.resolve_component(req.component)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Component '{req.component}' not found")

    sec = keys[0]
    name = keys[-1]

    if sec in ("providers", "packages"):
        pkg = entry.get("package") or name
        vm.rollback_pip_package(pkg, req.target)
    vm.set_version(req.component, req.target)

    return {
        "status": "ok",
        "component": req.component,
        "target": req.target,
        "message": f"Component '{req.component}' rolled back/pinned to {req.target}",
    }


@router.post("/install-artifact")
async def install_artifact(req: InstallArtifactRequest) -> dict[str, Any]:
    """Download and install an artifact (.zip, git tag/commit, or package version) into the app."""
    ok, msg = vm.download_and_install_artifact(
        component_path=req.component,
        artifact_source=req.artifact_source,
        artifact_type=req.artifact_type,
    )
    if not ok:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "ok", "component": req.component, "message": msg}
