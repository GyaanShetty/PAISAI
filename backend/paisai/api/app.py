"""The PAISAI FastAPI application.

Endpoints are intentionally thin: they translate user input into provenanced
values, delegate the arithmetic to the tested Calculation Engine, and return
values with their provenance intact. The Provenance & Validation Middleware sits
in front of everything and refuses to emit a response that carries an un-sourced
number — the no-hallucination policy, enforced at the wire.

Where a real data provider would be consulted (e.g. a live quote), there is no
Market Data Gateway wired in this foundational build, so the API returns an honest
``unavailable`` state rather than inventing a figure.
"""

from __future__ import annotations

import json
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .. import __version__
from ..engine import cagr, emergency_fund_months, portfolio_weights, savings_rate
from ..integrity.provenance import IntegrityError, unavailable, user_provided
from .integrity_response import find_unprovenanced_numbers


# --------------------------------------------------------------------------- #
# Provenance & Validation Middleware
# --------------------------------------------------------------------------- #
class ProvenanceValidationMiddleware(BaseHTTPMiddleware):
    """Refuse to send a JSON response that shows a user an un-sourced number.

    Applies to data routes (``/v1/…``). If a numeric escapes without a provenance
    envelope, the middleware fails honest — a 500 stating the integrity breach —
    rather than letting a number of unknown origin reach the client.
    """

    PROTECTED_PREFIX = "/v1/"

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        path = request.url.path
        if not path.startswith(self.PROTECTED_PREFIX):
            return response
        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
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
                            "Every displayed number must carry a provenance "
                            "category or be an explicit unavailable state."
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


def _integrity_error(exc: IntegrityError) -> JSONResponse:
    """A calculation refused because its inputs were undefined/contaminated."""
    return JSONResponse(
        status_code=422,
        content={"error": "integrity_error", "detail": str(exc)},
    )


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

    @app.get("/health")
    def health() -> dict[str, str]:
        # Strings only — no financial numerics — so nothing to provenance here.
        return {"status": "ok", "service": "paisai-api", "version": __version__}

    @app.post("/v1/calc/savings-rate")
    def calc_savings_rate(req: SavingsRateRequest) -> Any:
        income = user_provided(req.income, label="Income", unit="currency")
        expenses = user_provided(req.expenses, label="Expenses", unit="currency")
        try:
            result = savings_rate(income, expenses)
        except IntegrityError as exc:
            return _integrity_error(exc)
        return {"savings_rate": result.to_dict()}

    @app.post("/v1/calc/cagr")
    def calc_cagr(req: CagrRequest) -> Any:
        begin = user_provided(req.begin_value, label="Beginning value")
        end = user_provided(req.end_value, label="Ending value")
        years = user_provided(req.years, label="Years")
        try:
            result = cagr(begin, end, years)
        except IntegrityError as exc:
            return _integrity_error(exc)
        return {"cagr": result.to_dict()}

    @app.post("/v1/calc/emergency-fund")
    def calc_emergency_fund(req: EmergencyFundRequest) -> Any:
        savings = user_provided(req.liquid_savings, label="Liquid savings")
        expenses = user_provided(req.monthly_expenses, label="Monthly expenses")
        try:
            result = emergency_fund_months(savings, expenses)
        except IntegrityError as exc:
            return _integrity_error(exc)
        return {"emergency_fund_months": result.to_dict()}

    @app.post("/v1/calc/portfolio-weights")
    def calc_portfolio_weights(req: PortfolioWeightsRequest) -> Any:
        holdings = {
            name: user_provided(value, label=name)
            for name, value in req.holdings.items()
        }
        try:
            weights = portfolio_weights(holdings)
        except IntegrityError as exc:
            return _integrity_error(exc)
        return {"weights": {name: pv.to_dict() for name, pv in weights.items()}}

    @app.get("/v1/market/quote")
    def market_quote(symbol: str) -> Any:
        # No Market Data Gateway is wired in this foundational build. The honest
        # answer is "unavailable" — never a fabricated price. When a verified
        # provider is integrated, this returns a Verified ProvenancedValue.
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
