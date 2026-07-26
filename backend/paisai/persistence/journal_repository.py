"""Storage for Decision Journal entries.

Entries are persisted in their serialized (``to_dict``) form together with a few
indexed columns for querying. Recording a decision also writes an audit-log event,
so the *act* of journalling is itself part of the auditable history.
"""

from __future__ import annotations

import json
import uuid
from typing import Any, Optional

from sqlalchemy import String, Text, select
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker

from ..journal.models import DecisionEntry
from .audit import AuditLog
from .db import Base, get_sessionmaker


class DecisionEntryORM(Base):
    __tablename__ = "decision_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    decision_date: Mapped[str] = mapped_column(String(10), index=True)
    asset: Mapped[str] = mapped_column(String(255), index=True)
    action: Mapped[str] = mapped_column(String(32), index=True)
    review_date: Mapped[str] = mapped_column(String(10), index=True)
    data: Mapped[str] = mapped_column(Text)  # full serialized entry


class JournalRepository:
    """Persist and retrieve Decision Journal entries, auditing each write."""

    def __init__(
        self,
        session_factory: Optional[sessionmaker] = None,
        audit: Optional[AuditLog] = None,
    ) -> None:
        self._sessions = session_factory or get_sessionmaker()
        self._audit = audit if audit is not None else AuditLog(self._sessions)

    def save(self, entry: DecisionEntry, *, actor: str = "user") -> str:
        """Persist an entry, write an audit event, and return the new id."""
        entry_id = str(uuid.uuid4())
        data = entry.to_dict()
        with self._sessions() as session:
            session.add(
                DecisionEntryORM(
                    id=entry_id,
                    decision_date=entry.date.isoformat(),
                    asset=entry.asset,
                    action=entry.action.value,
                    review_date=entry.review_date.isoformat(),
                    data=json.dumps(data),
                )
            )
            session.commit()
        self._audit.append(
            actor=actor,
            action="decision.recorded",
            subject=entry_id,
            payload={"asset": entry.asset, "action": entry.action.value},
        )
        return entry_id

    def get(self, entry_id: str) -> Optional[dict[str, Any]]:
        """Return the stored (serialized) entry, or ``None`` if not found."""
        with self._sessions() as session:
            row = session.get(DecisionEntryORM, entry_id)
            return json.loads(row.data) if row is not None else None

    def list_due_for_review(self, on_or_before: str) -> list[dict[str, Any]]:
        """Return entries whose review date has arrived (ISO ``YYYY-MM-DD``)."""
        with self._sessions() as session:
            rows = session.execute(
                select(DecisionEntryORM)
                .where(DecisionEntryORM.review_date <= on_or_before)
                .order_by(DecisionEntryORM.review_date.asc())
            ).scalars().all()
            return [json.loads(r.data) for r in rows]
