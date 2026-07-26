"""An append-only, hash-chained audit log.

Auditability is one of the trust properties PAISAI promises. This log records
financially material events (a decision recorded, a figure served, a data source
consulted) so the history can be reconstructed. Each record is linked to the one
before it by a SHA-256 hash of its contents, forming a chain: altering any past
record breaks every hash after it, so tampering is **detectable**, not merely
discouraged.

The service exposes only ``append``, reads, and ``verify_chain`` — there is no
update or delete. Fail honest: if the chain does not verify, that is surfaced as
a :class:`TamperError`, never swallowed.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import Integer, String, Text, func, select
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker

from .db import Base, get_sessionmaker

GENESIS_HASH = "0" * 64


class TamperError(Exception):
    """Raised when the audit chain fails verification — the record was altered."""


class AuditRecordORM(Base):
    __tablename__ = "audit_log"

    seq: Mapped[int] = mapped_column(Integer, primary_key=True)  # monotonic, 1-based
    timestamp: Mapped[str] = mapped_column(String(40))
    actor: Mapped[str] = mapped_column(String(255))
    action: Mapped[str] = mapped_column(String(255))
    subject: Mapped[str] = mapped_column(String(255))
    payload: Mapped[str] = mapped_column(Text)  # canonical JSON
    prev_hash: Mapped[str] = mapped_column(String(64))
    entry_hash: Mapped[str] = mapped_column(String(64))


@dataclass(frozen=True)
class AuditRecord:
    seq: int
    timestamp: str
    actor: str
    action: str
    subject: str
    payload: dict[str, Any]
    prev_hash: str
    entry_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "seq": self.seq,
            "timestamp": self.timestamp,
            "actor": self.actor,
            "action": self.action,
            "subject": self.subject,
            "payload": self.payload,
            "prev_hash": self.prev_hash,
            "entry_hash": self.entry_hash,
        }


def _canonical(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def compute_hash(
    seq: int,
    timestamp: str,
    actor: str,
    action: str,
    subject: str,
    payload: Any,
    prev_hash: str,
) -> str:
    """Deterministic SHA-256 over a record's content and its predecessor's hash."""
    material = _canonical(
        {
            "seq": seq,
            "timestamp": timestamp,
            "actor": actor,
            "action": action,
            "subject": subject,
            "payload": payload,
            "prev_hash": prev_hash,
        }
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


class AuditLog:
    """Service for appending to and verifying the audit chain."""

    def __init__(self, session_factory: Optional[sessionmaker] = None) -> None:
        self._sessions = session_factory or get_sessionmaker()

    def append(
        self,
        actor: str,
        action: str,
        subject: str,
        payload: Optional[dict[str, Any]] = None,
    ) -> AuditRecord:
        """Append one event to the log and return the sealed record."""
        payload = payload or {}
        with self._sessions() as session:
            last = session.execute(
                select(AuditRecordORM).order_by(AuditRecordORM.seq.desc()).limit(1)
            ).scalar_one_or_none()
            seq = 1 if last is None else last.seq + 1
            prev_hash = GENESIS_HASH if last is None else last.entry_hash
            timestamp = datetime.now(timezone.utc).isoformat()
            entry_hash = compute_hash(
                seq, timestamp, actor, action, subject, payload, prev_hash
            )
            row = AuditRecordORM(
                seq=seq,
                timestamp=timestamp,
                actor=actor,
                action=action,
                subject=subject,
                payload=_canonical(payload),
                prev_hash=prev_hash,
                entry_hash=entry_hash,
            )
            session.add(row)
            session.commit()
            return AuditRecord(
                seq=seq,
                timestamp=timestamp,
                actor=actor,
                action=action,
                subject=subject,
                payload=payload,
                prev_hash=prev_hash,
                entry_hash=entry_hash,
            )

    def records(self) -> list[AuditRecord]:
        with self._sessions() as session:
            rows = session.execute(
                select(AuditRecordORM).order_by(AuditRecordORM.seq.asc())
            ).scalars().all()
            return [
                AuditRecord(
                    seq=r.seq,
                    timestamp=r.timestamp,
                    actor=r.actor,
                    action=r.action,
                    subject=r.subject,
                    payload=json.loads(r.payload),
                    prev_hash=r.prev_hash,
                    entry_hash=r.entry_hash,
                )
                for r in rows
            ]

    def count(self) -> int:
        with self._sessions() as session:
            return session.execute(
                select(func.count()).select_from(AuditRecordORM)
            ).scalar_one()

    def verify_chain(self) -> bool:
        """Recompute the chain; raise :class:`TamperError` at the first break.

        Returns ``True`` for an intact (or empty) chain.
        """
        with self._sessions() as session:
            rows = session.execute(
                select(AuditRecordORM).order_by(AuditRecordORM.seq.asc())
            ).scalars().all()

            expected_prev = GENESIS_HASH
            expected_seq = 1
            for r in rows:
                if r.seq != expected_seq:
                    raise TamperError(
                        f"Audit sequence gap: expected {expected_seq}, found {r.seq}."
                    )
                if r.prev_hash != expected_prev:
                    raise TamperError(
                        f"Audit chain broken at seq {r.seq}: prev_hash does not "
                        "match the previous record."
                    )
                recomputed = compute_hash(
                    r.seq,
                    r.timestamp,
                    r.actor,
                    r.action,
                    r.subject,
                    json.loads(r.payload),
                    r.prev_hash,
                )
                if recomputed != r.entry_hash:
                    raise TamperError(
                        f"Audit record at seq {r.seq} was altered: content hash "
                        "does not match its stored hash."
                    )
                expected_prev = r.entry_hash
                expected_seq += 1
            return True
