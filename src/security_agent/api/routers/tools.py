"""Tools router — list available tools."""
from __future__ import annotations
from pathlib import Path
from fastapi import APIRouter
import yaml

router = APIRouter(tags=["tools"])

@router.get("/tools")
async def list_tools() -> dict:
    cfg_path = Path(__file__).parent.parent.parent.parent.parent.parent / "config" / "tools.yaml"
    if cfg_path.exists():
        with cfg_path.open() as f:
            data = yaml.safe_load(f)
        return {"tools": list(data.get("tools", {}).keys())}
    return {"tools": []}
