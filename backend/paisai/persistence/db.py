"""Database engine and session setup.

Defaults to a local SQLite database so the system runs and tests anywhere with no
external service. In production, set ``DATABASE_URL`` (e.g. a PostgreSQL DSN) per
``docs/ARCHITECTURE.md``; nothing else changes.
"""

from __future__ import annotations

import os
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    """Declarative base for all PAISAI ORM models."""


_engine: Optional[Engine] = None
_Session: Optional[sessionmaker] = None


def init_engine(url: Optional[str] = None, *, echo: bool = False) -> Engine:
    """Create (or recreate) the engine and the schema, returning the engine.

    ``url`` falls back to ``$DATABASE_URL`` and then to an on-disk SQLite file.
    Tests pass ``sqlite+pysqlite:///:memory:`` for an isolated database.
    """
    global _engine, _Session
    resolved = url or os.environ.get("DATABASE_URL") or "sqlite+pysqlite:///paisai.db"
    kwargs: dict = {"echo": echo, "future": True}
    if resolved.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
        # An in-memory database is per-connection; share one connection across
        # threads (e.g. the test client's worker) so the schema is visible.
        if ":memory:" in resolved:
            kwargs["poolclass"] = StaticPool
    _engine = create_engine(resolved, **kwargs)
    _Session = sessionmaker(bind=_engine, expire_on_commit=False, future=True)
    Base.metadata.create_all(_engine)
    return _engine


def get_sessionmaker() -> sessionmaker:
    """Return the configured sessionmaker, initialising a default engine if needed."""
    if _Session is None:
        init_engine()
    assert _Session is not None
    return _Session
