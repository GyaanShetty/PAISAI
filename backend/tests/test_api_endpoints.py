"""Product endpoints: dashboard, decision journal, audit, market data — end to end."""

from datetime import datetime, timezone
from typing import Optional

import pytest
from fastapi.testclient import TestClient

from paisai.api import create_app
from paisai.marketdata import RawDatum, configure_provider
from paisai.persistence.db import init_engine


@pytest.fixture()
def client() -> TestClient:
    # Isolated in-memory database so journal/audit routes persist within the test.
    init_engine("sqlite+pysqlite:///:memory:")
    return TestClient(create_app())


@pytest.fixture(autouse=True)
def _reset_provider():
    # Ensure no provider leaks between tests; default is honest-unavailable.
    configure_provider(None)
    yield
    configure_provider(None)


class _FakeProvider:
    name = "fake"

    def get_quote(self, symbol: str) -> Optional[RawDatum]:
        return RawDatum(2500.0, "INR", "FakeExchange", datetime(2026, 1, 1, tzinfo=timezone.utc))

    def get_nav(self, scheme_code: str) -> Optional[RawDatum]:
        return None


def _entry_payload(**overrides) -> dict:
    base = {
        "date": "2026-01-01",
        "asset": "Broad-market index fund",
        "action": "SIP",
        "thesis": "Low-cost core exposure for a long horizon.",
        "expected_outcome": "Compound near the market over 10+ years.",
        "time_horizon": "10+ years",
        "review_date": "2026-07-01",
        "confidence": "Medium",
        "risk_factors": ["Equity drawdowns."],
        "assumptions": ["Costs stay low."],
        "alternatives": [
            {"option": "Active fund", "rejection_reason": "Higher fee, no edge."}
        ],
        "sources": ["Fund factsheet"],
    }
    base.update(overrides)
    return base


# --- dashboard --------------------------------------------------------------


def test_dashboard_computes_provided_and_admits_missing(client):
    r = client.post(
        "/v1/dashboard",
        json={
            "assets": 5_000_000,
            "liabilities": 720_000,
            "monthly_income": 120_000,
            "monthly_expenses": 84_000,
            "holdings": {"Equity": 600000, "Debt": 400000},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["net_worth"]["provenance"] == "Calculated"
    assert body["net_worth"]["value"] == 4_280_000
    assert body["savings_rate"]["provenance"] == "Calculated"
    # No liquid_savings provided -> emergency fund is honestly unavailable.
    assert body["emergency_fund_months"]["available"] is False
    assert body["portfolio_weights"]["Equity"]["provenance"] == "Calculated"


def test_dashboard_all_missing_is_all_unavailable(client):
    r = client.post("/v1/dashboard", json={})
    assert r.status_code == 200
    body = r.json()
    assert body["net_worth"]["available"] is False
    assert body["savings_rate"]["available"] is False
    assert body["portfolio_weights"]["available"] is False


# --- decision journal -------------------------------------------------------


def test_journal_create_get_roundtrip(client):
    created = client.post("/v1/journal", json=_entry_payload())
    assert created.status_code == 201
    entry_id = created.json()["id"]

    fetched = client.get(f"/v1/journal/{entry_id}")
    assert fetched.status_code == 200
    assert fetched.json()["entry"]["asset"] == "Broad-market index fund"


def test_journal_get_missing_is_404(client):
    r = client.get("/v1/journal/does-not-exist")
    assert r.status_code == 404


def test_journal_rejects_invalid_entry(client):
    # review_date before decision date must be rejected with a 422.
    r = client.post("/v1/journal", json=_entry_payload(review_date="2025-12-01"))
    assert r.status_code == 422
    assert r.json()["error"] == "validation_error"


def test_journal_review_due(client):
    client.post("/v1/journal", json=_entry_payload())  # review_date 2026-07-01
    due = client.get("/v1/journal/review-due", params={"on_or_before": "2026-07-01"})
    assert due.status_code == 200
    assert due.json()["count"] == 1
    not_yet = client.get(
        "/v1/journal/review-due", params={"on_or_before": "2026-06-30"}
    )
    assert not_yet.json()["count"] == 0


# --- audit ------------------------------------------------------------------


def test_audit_verify_reflects_journal_writes(client):
    # Empty log verifies.
    first = client.get("/v1/audit/verify")
    assert first.status_code == 200
    assert first.json()["intact"] is True
    assert first.json()["records_checked"] == 0

    # Recording a decision writes an audit event.
    client.post("/v1/journal", json=_entry_payload())
    after = client.get("/v1/audit/verify")
    assert after.json()["intact"] is True
    assert after.json()["records_checked"] == 1


# --- market data through the gateway ----------------------------------------


def test_market_quote_unavailable_without_provider(client):
    r = client.get("/v1/market/quote", params={"symbol": "ACME"})
    assert r.status_code == 200
    assert r.json()["quote"]["available"] is False


def test_stock_endpoint_unavailable_without_provider(client):
    r = client.get("/v1/stock/RELIANCE")
    assert r.status_code == 200
    body = r.json()
    assert body["quote"]["available"] is False
    assert body["fundamentals"]["available"] is False


def test_stock_endpoint_verified_with_provider(client):
    configure_provider(_FakeProvider())
    r = client.get("/v1/stock/RELIANCE")
    assert r.status_code == 200
    quote = r.json()["quote"]
    assert quote["provenance"] == "Verified"
    assert quote["value"] == 2500.0
    assert quote["source"] == "FakeExchange"


def test_fund_endpoint_unavailable_without_provider(client):
    r = client.get("/v1/fund/120503")
    assert r.status_code == 200
    assert r.json()["nav"]["available"] is False


def test_structural_counts_pass_the_boundary_middleware(client):
    # 'count' and 'records_checked' are structural metadata, not financial numbers,
    # so they are not blocked by the provenance middleware.
    assert client.get("/v1/audit/verify").status_code == 200
    assert (
        client.get(
            "/v1/journal/review-due", params={"on_or_before": "2026-01-01"}
        ).status_code
        == 200
    )
