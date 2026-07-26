"""API contract tests, including the boundary enforcement of no-hallucination."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from paisai.api import create_app
from paisai.api.app import ProvenanceValidationMiddleware
from paisai.api.integrity_response import find_unprovenanced_numbers


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


# --- health -----------------------------------------------------------------


def test_health_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# --- calculations return provenanced values ---------------------------------


def test_savings_rate_endpoint(client):
    r = client.post("/v1/calc/savings-rate", json={"income": 100000, "expenses": 70000})
    assert r.status_code == 200
    payload = r.json()["savings_rate"]
    assert payload["provenance"] == "Calculated"
    assert abs(payload["value"] - 0.30) < 1e-9
    # The inputs are recorded for auditability.
    assert len(payload["inputs"]) == 2


def test_cagr_endpoint(client):
    r = client.post(
        "/v1/calc/cagr",
        json={"begin_value": 100, "end_value": 200, "years": 10},
    )
    assert r.status_code == 200
    assert r.json()["cagr"]["provenance"] == "Calculated"


def test_portfolio_weights_endpoint(client):
    r = client.post(
        "/v1/calc/portfolio-weights",
        json={"holdings": {"Equity": 600000, "Debt": 400000}},
    )
    assert r.status_code == 200
    weights = r.json()["weights"]
    assert abs(weights["Equity"]["value"] - 0.6) < 1e-9
    assert weights["Equity"]["provenance"] == "Calculated"


def test_undefined_calculation_returns_422(client):
    # CAGR with a zero beginning value is undefined — the engine refuses, and the
    # API surfaces that honestly instead of returning a fabricated number.
    r = client.post(
        "/v1/calc/cagr",
        json={"begin_value": 0, "end_value": 200, "years": 10},
    )
    assert r.status_code == 422
    assert r.json()["error"] == "integrity_error"


# --- missing market data is admitted, never invented ------------------------


def test_market_quote_is_unavailable_not_fabricated(client):
    r = client.get("/v1/market/quote", params={"symbol": "ACME"})
    assert r.status_code == 200
    quote = r.json()["quote"]
    assert quote["available"] is False
    assert "verified data" in quote["reason"].lower()


# --- the middleware actually blocks un-sourced numerics ---------------------


def test_middleware_blocks_unprovenanced_response():
    # A rogue endpoint that leaks a bare number must be caught at the boundary.
    app: FastAPI = create_app()

    @app.get("/v1/rogue")
    def rogue():  # pragma: no cover - exercised via the client
        return {"pe_ratio": 27.4}  # bare number, no provenance

    client = TestClient(app)
    r = client.get("/v1/rogue")
    assert r.status_code == 500
    assert r.json()["error"] == "integrity_violation"
    assert "$.pe_ratio" in r.json()["paths"]


def test_middleware_allows_clean_provenanced_response(client):
    r = client.post("/v1/calc/savings-rate", json={"income": 100000, "expenses": 70000})
    assert r.status_code == 200  # passes the boundary check untouched


# --- the serialized-form detector itself ------------------------------------


def test_detector_flags_bare_numbers():
    assert find_unprovenanced_numbers({"pe": 25.0}) == ["$.pe"]
    assert find_unprovenanced_numbers([1, 2]) == ["$[0]", "$[1]"]


def test_detector_accepts_provenance_envelope():
    ok = {"value": 100.0, "provenance": "Verified", "source": "feed"}
    assert find_unprovenanced_numbers(ok) == []


def test_detector_ignores_booleans_and_strings():
    assert find_unprovenanced_numbers({"available": False, "reason": "n/a"}) == []
