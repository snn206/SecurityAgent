"""Execution tracker and history store."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Float, JSON, DateTime, select, func

from security_agent.core.events import EventBus, EventType, AgentEvent


# ─── ORM Models ───────────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


class ExecutionRecord(Base):
    __tablename__ = "executions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    task_id: Mapped[str] = mapped_column(String, index=True)
    user_request: Mapped[str] = mapped_column(String)
    scope: Mapped[str] = mapped_column(String, default="")
    status: Mapped[str] = mapped_column(String, default="pending")
    plan: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    report: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    provider: Mapped[str] = mapped_column(String, default="")
    model: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                  default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)


class EventRecord(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id: Mapped[str] = mapped_column(String, index=True)
    event_type: Mapped[str] = mapped_column(String)
    agent_id: Mapped[str] = mapped_column(String, default="")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)


# ─── HistoryStore ─────────────────────────────────────────────────────────────

class HistoryStore:
    """Async persistence layer for execution history."""

    def __init__(self, database_url: str = "sqlite+aiosqlite:///./data/security_agent.db") -> None:
        self._engine = create_async_engine(database_url, echo=False)
        self._session_factory = async_sessionmaker(self._engine, expire_on_commit=False)

    async def initialize(self) -> None:
        """Create tables if they don't exist."""
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def create_execution(self, execution_id: str, task_id: str,
                                user_request: str, scope: str = "") -> ExecutionRecord:
        async with self._session_factory() as session:
            record = ExecutionRecord(
                id=execution_id, task_id=task_id,
                user_request=user_request, scope=scope, status="pending",
            )
            session.add(record)
            await session.commit()
            return record

    async def update_execution(self, execution_id: str, **kwargs: Any) -> None:
        async with self._session_factory() as session:
            record = await session.get(ExecutionRecord, execution_id)
            if record:
                for k, v in kwargs.items():
                    setattr(record, k, v)
                await session.commit()

    async def get_execution(self, execution_id: str) -> ExecutionRecord | None:
        async with self._session_factory() as session:
            return await session.get(ExecutionRecord, execution_id)

    async def list_executions(self, limit: int = 50, offset: int = 0) -> list[ExecutionRecord]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ExecutionRecord).order_by(ExecutionRecord.created_at.desc())
                .limit(limit).offset(offset)
            )
            return list(result.scalars().all())

    async def save_event(self, event: AgentEvent) -> None:
        async with self._session_factory() as session:
            record = EventRecord(
                id=event.event_id,
                execution_id=event.execution_id,
                event_type=event.event_type.value,
                agent_id=event.agent_id,
                timestamp=event.timestamp,
                payload=event.payload,
            )
            session.add(record)
            await session.commit()

    async def get_events(self, execution_id: str) -> list[EventRecord]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(EventRecord)
                .where(EventRecord.execution_id == execution_id)
                .order_by(EventRecord.timestamp)
            )
            return list(result.scalars().all())


# ─── ExecutionTracker ─────────────────────────────────────────────────────────

class ExecutionTracker:
    """Subscribes to EventBus and persists all events to HistoryStore."""

    def __init__(self, store: HistoryStore, event_bus: EventBus) -> None:
        self._store = store
        self._bus = event_bus
        self._bus.subscribe(self._handle_event)

    async def _handle_event(self, event: AgentEvent) -> None:
        await self._store.save_event(event)

        if event.event_type == EventType.TASK_COMPLETED:
            await self._store.update_execution(
                event.execution_id, status="done",
                completed_at=datetime.now(timezone.utc),
            )
        elif event.event_type == EventType.TASK_FAILED:
            await self._store.update_execution(event.execution_id, status="failed",
                                               completed_at=datetime.now(timezone.utc))
        elif event.event_type == EventType.PLAN_CREATED and event.payload.get("plan"):
            await self._store.update_execution(event.execution_id,
                                               plan=event.payload["plan"], status="executing")
        elif event.event_type == EventType.REPORT_GENERATED:
            await self._store.update_execution(event.execution_id, status="reporting")


_global_store: HistoryStore | None = None


def get_store() -> HistoryStore:
    """Singleton getter for HistoryStore."""
    global _global_store
    if _global_store is None:
        _global_store = HistoryStore()
    return _global_store
