"""Persistence — durable storage for PAISAI, with auditability built in.

Trust depends on being able to reconstruct *what was decided and when*. This
package provides:

- :mod:`db` — the SQLAlchemy engine/session setup (SQLite for tests, Postgres in
  production via ``DATABASE_URL``).
- :mod:`audit` — an append-only, hash-chained audit log so that tampering with
  the record is *detectable*, not merely discouraged.
- :mod:`journal_repository` — storage for Decision Journal entries.
"""

from .db import Base, get_sessionmaker, init_engine
from .audit import AuditLog, AuditRecord, TamperError
from .journal_repository import JournalRepository

__all__ = [
    "Base",
    "init_engine",
    "get_sessionmaker",
    "AuditLog",
    "AuditRecord",
    "TamperError",
    "JournalRepository",
]
