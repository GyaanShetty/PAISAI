"""The PAISAI FastAPI application.

Endpoints are intentionally thin: they translate user input into provenanced
values, delegate the arithmetic to the tested Calculation Engine, persist through
the repositories, and return values with their provenance intact. The Provenance &
Validation Middleware sits in front of every ``/v1/`` route and refuses to emit a
response that carries an un-sourced financial number — the no-hallucination policy,
enforced at the wire.

Where a real data provider would be consulted (e.g. a live quote), there is no
Market Data Gateway wired in this build, so the API returns an honest
``unavailable`` state rather than inventing a figure.
"""

from __future__ import annotations

import json
import os
from datetime import date
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .. import __version__
from ..dashboard import DashboardInput, build_dashboard
from ..engine import cagr, emergency_fund_months, portfolio_weights, savings_rate
from ..integrity.epistemics import Confidence
from ..integrity.provenance import IntegrityError, unavailable, user_provided
from ..journal.models import Action, Alternative, Assumption, DecisionEntry, RiskFactor
from ..persistence.audit import AuditLog, TamperError
from ..persistence.journal_repository import JournalRepository
from .integrity_response import find_unprovenanced_numbers


# --------------------------------------------------------------------------- #
# Provenance & Validation Middleware
# --------------------------------------------------------------------------- #
class ProvenanceValidationMiddleware(BaseHTTPMiddleware):
    """Refuse to send a JSON response that shows a user an un-sourced number.

    Applies to data routes (``/v1/…``). If a financial numeric escapes without a
    provenance envelope, the middleware fails honest — a 500 stating the integrity
    breach — rather than letting a number of unknown origin reach the client.
    """

    PROTECTED_PREFIX = "/v1/"

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if not request.url.path.startswith(self.PROTECTED_PREFIX):
            return response
        if "application/json" not in response.headers.get("content-type", ""):
            return response

        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        try:
            payload = json.loads(body) if body else None
        except json.JSONDecodeError:
            payload = None

        if payload is not None:
            offenders = find_unprovenanced_numbers(payload)
            if offenders:
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "integrity_violation",
                        "detail": (
                            "Blocked a response containing un-sourced numeric(s). "
                            "Every displayed financial number must carry a "
                            "provenance category or be an explicit unavailable state."
                        ),
                        "paths": offenders,
                    },
                )

        return Response(
            content=body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )


# --------------------------------------------------------------------------- #
# Request models
# --------------------------------------------------------------------------- #
class SavingsRateRequest(BaseModel):
    income: float = Field(..., description="Monthly (or periodic) income.")
    expenses: float = Field(..., description="Expenses over the same period.")


class CagrRequest(BaseModel):
    begin_value: float
    end_value: float
    years: float


class EmergencyFundRequest(BaseModel):
    liquid_savings: float
    monthly_expenses: float


class PortfolioWeightsRequest(BaseModel):
    holdings: Dict[str, float] = Field(
        ..., description="Map of holding name to its current value."
    )


class DashboardRequest(BaseModel):
    assets: Optional[float] = None
    liabilities: Optional[float] = None
    monthly_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    liquid_savings: Optional[float] = None
    holdings: Optional[Dict[str, float]] = None


class AlternativeModel(BaseModel):
    option: str
    rejection_reason: str


class JournalEntryRequest(BaseModel):
    date: date
    asset: str
    action: Action
    thesis: str
    expected_outcome: str
    time_horizon: str
    review_date: date
    confidence: Confidence
    market_context: str = ""
    expected_return: Optional[float] = None
    risk_factors: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    alternatives: List[AlternativeModel] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    emotional_state: Optional[str] = None


def _integrity_error(exc: IntegrityError) -> JSONResponse:
    """A calculation refused because its inputs were undefined/contaminated."""
    return JSONResponse(
        status_code=422, content={"error": "integrity_error", "detail": str(exc)}
    )


def _validation_error(exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=422, content={"error": "validation_error", "detail": str(exc)}
    )


def _cors_origins() -> list[str]:
    raw = os.environ.get("PAISAI_CORS_ORIGINS", "http://localhost:3000")
    return [o.strip() for o in raw.split(",") if o.strip()]


# --------------------------------------------------------------------------- #
# Application factory
# --------------------------------------------------------------------------- #
def create_app() -> FastAPI:
    app = FastAPI(
        title="PAISAI API",
        version=__version__,
        description=(
            "The trust-enforcing API of PAISAI. Numbers come from a tested "
            "calculation engine, carry provenance, and are validated at the "
            "boundary. Missing data is admitted, never invented."
        ),
    )
    app.add_middleware(ProvenanceValidationMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    # -- health ------------------------------------------------------------- #
    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "paisai-api", "version": __version__}

    # -- calculations ------------------------------------------------------- #
    @app.post("/v1/calc/savings-rate")
    def calc_savings_rate(req: SavingsRateRequest) -> Any:
        try:
            result = savings_rate(
                user_provided(req.income, label="Income", unit="currency"),
                user_provided(req.expenses, label="Expenses", unit="currency"),
            )
        except IntegrityError as exc:
            return _integrity_error(exc)
        return {"savings_rate": result.to_dict()}

    @app.post("/v1/calc/cagr")
    def calc_cagr(req: CagrRequest) -> Any:
        try:
            result = cagr(
                user_provided(req.begin_value, label="Beginning value"),
                user_provided(req.end_value, label="Ending value"),
                user_provided(req.years, label="Years"),
            )
        except IntegrityError as exc:
            return _integrity_error(exc)
        return {"cagr": result.to_dict()}

    @app.post("/v1/calc/emergency-fund")
    def calc_emergency_fund(req: EmergencyFundRequest) -> Any:
        try:
            result = emergency_fund_months(
                user_provided(req.liquid_savings, label="Liquid savings"),
                user_provided(req.monthly_expenses, label="Monthly expenses"),
            )
        except IntegrityError as exc:
            return _integrity_error(exc)
        return {"emergency_fund_months": result.to_dict()}

    @app.post("/v1/calc/portfolio-weights")
    def calc_portfolio_weights(req: PortfolioWeightsRequest) -> Any:
        try:
            weights = portfolio_weights(
                {n: user_provided(v, label=n) for n, v in req.holdings.items()}
            )
        except IntegrityError as exc:
            return _integrity_error(exc)
        return {"weights": {n: pv.to_dict() for n, pv in weights.items()}}

    # -- dashboard ---------------------------------------------------------- #
    @app.post("/v1/dashboard")
    def dashboard(req: DashboardRequest) -> Any:
        try:
            result = build_dashboard(
                DashboardInput(
                    assets=req.assets,
                    liabilities=req.liabilities,
                    monthly_income=req.monthly_income,
                    monthly_expenses=req.monthly_expenses,
                    liquid_savings=req.liquid_savings,
                    holdings=req.holdings,
                )
            )
        except IntegrityError as exc:
            return _integrity_error(exc)
        return result.to_dict()

    # -- decision journal --------------------------------------------------- #
    @app.post("/v1/journal", status_code=201)
    def create_journal_entry(req: JournalEntryRequest) -> Any:
        try:
            entry = DecisionEntry(
                date=req.date,
                asset=req.asset,
                action=req.action,
                thesis=req.thesis,
                expected_outcome=req.expected_outcome,
                time_horizon=req.time_horizon,
                review_date=req.review_date,
                confidence=req.confidence,
                market_context=req.market_context,
                expected_return=(
                    user_provided(req.expected_return, label="Expected return")
                    if req.expected_return is not None
                    else None
                ),
                risk_factors=[RiskFactor(r) for r in req.risk_factors],
                assumptions=[Assumption(a) for a in req.assumptions],
                alternatives=[
                    Alternative(a.option, a.rejection_reason) for a in req.alternatives
                ],
                sources=req.sources,
                emotional_state=req.emotional_state,
            )
        except (ValueError, IntegrityError) as exc:
            return _validation_error(exc)
        entry_id = JournalRepository().save(entry)
        return {"id": entry_id, "entry": entry.to_dict()}

    @app.get("/v1/journal/review-due")
    def journal_review_due(on_or_before: date) -> Any:
        entries = JournalRepository().list_due_for_review(on_or_before.isoformat())
        return {"count": len(entries), "entries": entries}

    @app.get("/v1/journal/{entry_id}")
    def get_journal_entry(entry_id: str) -> Any:
        entry = JournalRepository().get(entry_id)
        if entry is None:
            return JSONResponse(
                status_code=404, content={"error": "not_found", "id": entry_id}
            )
        return {"id": entry_id, "entry": entry}

    # -- audit -------------------------------------------------------------- #
    @app.get("/v1/audit/verify")
    def audit_verify() -> Any:
        log = AuditLog()
        try:
            log.verify_chain()
        except TamperError as exc:
            return JSONResponse(
                status_code=409,
                content={"intact": False, "detail": str(exc)},
            )
        return {"intact": True, "records_checked": log.count()}

    # -- market data (honest unavailable) ----------------------------------- #
    @app.get("/v1/market/quote")
    def market_quote(symbol: str) -> Any:
        return {
            "symbol": symbol,
            "quote": unavailable(
                label=f"Live quote for {symbol}",
                reason=(
                    "No verified market-data provider is connected in this build; "
                    "I don't have verified data for this."
                ),
            ).to_dict(),
        }

    return app


app = create_app()
