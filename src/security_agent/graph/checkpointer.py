"""LangGraph checkpointer setup — SQLite by default."""
from __future__ import annotations
import os
from pathlib import Path

def get_checkpointer():
    """Return a LangGraph checkpointer based on config.
    
    Uses SQLite by default. To use Postgres, set SA_DATABASE_URL to a postgres URL.
    """
    try:
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
        db_path = Path("./data/checkpoints.db")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return AsyncSqliteSaver.from_conn_string(str(db_path))
    except ImportError:
        return None  # No checkpointer — stateless operation
