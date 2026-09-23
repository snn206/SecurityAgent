"""FastAPI application factory for SecurityAgent."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from security_agent.api.middleware.logging import LoggingMiddleware
from security_agent.api.routers import (
    executions,
    health,
    hierarchy,
    memory,
    providers,
    reports,
    tasks,
    tools,
)
from security_agent.api.websocket.manager import ConnectionManager
from security_agent.execution.history import HistoryStore

# Module-level singletons
_store: HistoryStore | None = None
_ws_manager: ConnectionManager | None = None


def get_store() -> HistoryStore:
    global _store
    if _store is None:
        _store = HistoryStore()
    return _store


def get_ws_manager() -> ConnectionManager:
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = ConnectionManager()
    return _ws_manager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup / shutdown lifecycle."""
    store = get_store()
    await store.initialize()
    yield
    # Cleanup on shutdown
    ws_manager = get_ws_manager()
    await ws_manager.close_all()


def create_app() -> FastAPI:
    app = FastAPI(
        title="SecurityAgent API",
        description="Multi-Agent Security Research System",
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # ── Middleware ──────────────────────────────────────────────────────────────
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ────────────────────────────────────────────────────────────────
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(tasks.router, prefix="/api/v1")
    app.include_router(executions.router, prefix="/api/v1")
    app.include_router(reports.router, prefix="/api/v1")
    app.include_router(providers.router, prefix="/api/v1")
    app.include_router(tools.router, prefix="/api/v1")
    app.include_router(memory.router, prefix="/api/v1")
    app.include_router(hierarchy.router, prefix="/api/v1")

    # ── WebSocket ──────────────────────────────────────────────────────────────
    from security_agent.api.websocket.events import ws_router

    app.include_router(ws_router)

    # ── SSE ────────────────────────────────────────────────────────────────────
    from security_agent.api.sse.stream import sse_router

    app.include_router(sse_router)

    # ── Static UI ─────────────────────────────────────────────────────────────
    dist_dir = Path(__file__).parent.parent / "ui" / "dist"
    static_dir = Path(__file__).parent.parent / "ui" / "static"
    ui_dir = dist_dir if dist_dir.exists() else (static_dir if static_dir.exists() else None)
    if ui_dir is not None:
        app.mount("/", StaticFiles(directory=str(ui_dir), html=True), name="ui")

    return app


def main() -> None:
    import uvicorn

    uvicorn.run(
        "security_agent.api.app:create_app",
        factory=True,
        host="0.0.0.0",
        port=8080,
        reload=False,
    )


if __name__ == "__main__":
    main()
