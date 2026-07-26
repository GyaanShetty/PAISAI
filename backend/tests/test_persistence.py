"""Persistence: audit-chain tamper-evidence and journal round-trips."""

from datetime import date

import pytest
from sqlalchemy import text

from paisai.integrity.epistemics import Confidence
from paisai.journal.models import Action, Assumption, DecisionEntry, RiskFactor
from paisai.persistence.audit import AuditLog, TamperError
from paisai.persistence.db import init_engine, get_sessionmaker
from paisai.persistence.journal_repository import JournalRepository


@pytest.fixture()
def sessions():
    # Isolated in-memory database per test.
    init_engine("sqlite+pysqlite:///:memory:")
    return get_sessionmaker()


# --- audit log --------------------------------------------------------------


def test_append_builds_a_verifiable_chain(sessions):
    log = AuditLog(sessions)
    log.append("user", "decision.recorded", "e1", {"asset": "Index fund"})
    log.append("system", "figure.served", "net_worth", {"provenance": "Calculated"})
    log.append("user", "sip.started", "e2", {"amount_provenance": "User Provided"})

    assert log.count() == 3
    assert log.verify_chain() is True

    records = log.records()
    assert [r.seq for r in records] == [1, 2, 3]
    # First record links to the genesis hash; each links to its predecessor.
    assert records[0].prev_hash == "0" * 64
    assert records[1].prev_hash == records[0].entry_hash
    assert records[2].prev_hash == records[1].entry_hash


def test_empty_chain_verifies(sessions):
    assert AuditLog(sessions).verify_chain() is True


def test_tampering_with_payload_is_detected(sessions):
    log = AuditLog(sessions)
    log.append("user", "decision.recorded", "e1", {"asset": "Index fund"})
    log.append("user", "decision.recorded", "e2", {"asset": "Bond fund"})

    # Alter a stored payload directly in the DB, behind the service's back.
    with sessions() as session:
        session.execute(
            text("UPDATE audit_log SET payload = :p WHERE seq = 1"),
            {"p": '{"asset":"Something else"}'},
        )
        session.commit()

    with pytest.raises(TamperError):
        log.verify_chain()


def test_deleting_a_record_breaks_the_chain(sessions):
    log = AuditLog(sessions)
    log.append("user", "a", "s1")
    log.append("user", "b", "s2")
    log.append("user", "c", "s3")

    with sessions() as session:
        session.execute(text("DELETE FROM audit_log WHERE seq = 2"))
        session.commit()

    # The sequence gap (1, 3) is caught.
    with pytest.raises(TamperError):
        log.verify_chain()


# --- journal repository -----------------------------------------------------


def _entry() -> DecisionEntry:
    return DecisionEntry(
        date=date(2026, 1, 1),
        asset="Broad-market index fund",
        action=Action.SIP,
        thesis="Low-cost core exposure.",
        expected_outcome="Compound near the market.",
        time_horizon="10+ years",
        review_date=date(2026, 7, 1),
        confidence=Confidence.MEDIUM,
        risk_factors=[RiskFactor("Equity drawdowns.")],
        assumptions=[Assumption("Costs stay low.")],
    )


def test_save_and_get_round_trip(sessions):
    repo = JournalRepository(sessions)
    entry_id = repo.save(_entry())
    stored = repo.get(entry_id)
    assert stored is not None
    assert stored["asset"] == "Broad-market index fund"
    assert stored["action"] == "SIP"
    assert stored["assumptions"] == ["Costs stay low."]


def test_get_missing_returns_none(sessions):
    repo = JournalRepository(sessions)
    assert repo.get("does-not-exist") is None


def test_saving_a_decision_writes_an_audit_event(sessions):
    audit = AuditLog(sessions)
    repo = JournalRepository(sessions, audit=audit)
    repo.save(_entry())
    records = audit.records()
    assert len(records) == 1
    assert records[0].action == "decision.recorded"
    assert audit.verify_chain() is True


def test_list_due_for_review(sessions):
    repo = JournalRepository(sessions)
    repo.save(_entry())  # review_date 2026-07-01
    assert len(repo.list_due_for_review("2026-07-01")) == 1
    assert len(repo.list_due_for_review("2026-06-30")) == 0
