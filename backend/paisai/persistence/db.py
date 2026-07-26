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
    connect_args = {"check_same_thread": False} if resolved.startswith("sqlite") else {}
    _engine = create_engine(resolved, echo=echo, future=True, connect_args=connect_args)
    _Session = sessionmaker(bind=_engine, expire_on_commit=False, future=True)
    Base.metadata.create_all(_engine)
    return _engine


def get_sessionmaker() -> sessionmaker:
    """Return the configured sessionmaker, initialising a default engine if needed."""
    if _Session is None:
        init_engine()
    assert _Session is not None
    return _Session
