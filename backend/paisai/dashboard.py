"""Dashboard composition.

Given the user's own inputs, compute the headline figures — net worth, savings
rate, emergency-fund coverage, portfolio weights — each as a provenanced value.
Where an input is missing, the figure is rendered as an honest ``Unavailable``
rather than guessed. Nothing here reaches for a number the user did not provide.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Union

from .engine import (
    emergency_fund_months,
    net_worth,
    portfolio_weights,
    savings_rate,
)
from .integrity.provenance import ProvenancedValue, Unavailable, unavailable, user_provided

Figure = Union[ProvenancedValue, Unavailable]


@dataclass
class DashboardInput:
    """User-provided financial inputs. Every field is optional and untrusted-as-
    verified: what the user typed is ``User Provided``, not independently checked."""

    assets: Optional[float] = None
    liabilities: Optional[float] = None
    monthly_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    liquid_savings: Optional[float] = None
    holdings: Optional[Mapping[str, float]] = None


@dataclass
class Dashboard:
    net_worth: Figure
    savings_rate: Figure
    emergency_fund_months: Figure
    portfolio_weights: Union[dict[str, ProvenancedValue], Unavailable]
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        pw: Any
        if isinstance(self.portfolio_weights, Unavailable):
            pw = self.portfolio_weights.to_dict()
        else:
            pw = {k: v.to_dict() for k, v in self.portfolio_weights.items()}
        return {
            "net_worth": self.net_worth.to_dict(),
            "savings_rate": self.savings_rate.to_dict(),
            "emergency_fund_months": self.emergency_fund_months.to_dict(),
            "portfolio_weights": pw,
            "notes": list(self.notes),
        }


def build_dashboard(inp: DashboardInput) -> Dashboard:
    """Compose the dashboard, computing only what the inputs support."""
    notes: list[str] = []

    if inp.assets is not None and inp.liabilities is not None:
        nw: Figure = net_worth(
            user_provided(inp.assets, label="Total assets", unit="currency"),
            user_provided(inp.liabilities, label="Total liabilities", unit="currency"),
        )
    else:
        nw = unavailable(
            label="Net worth",
            reason="Provide total assets and total liabilities to compute net worth.",
        )

    if inp.monthly_income is not None and inp.monthly_expenses is not None:
        sr: Figure = savings_rate(
            user_provided(inp.monthly_income, label="Monthly income", unit="currency"),
            user_provided(inp.monthly_expenses, label="Monthly expenses", unit="currency"),
        )
    else:
        sr = unavailable(
            label="Savings rate",
            reason="Provide monthly income and expenses to compute the savings rate.",
        )

    if inp.liquid_savings is not None and inp.monthly_expenses is not None:
        ef: Figure = emergency_fund_months(
            user_provided(inp.liquid_savings, label="Liquid savings", unit="currency"),
            user_provided(inp.monthly_expenses, label="Monthly expenses", unit="currency"),
        )
    else:
        ef = unavailable(
            label="Emergency fund coverage",
            reason="Provide liquid savings and monthly expenses to compute coverage.",
        )

    pw: Union[dict[str, ProvenancedValue], Unavailable]
    if inp.holdings:
        pw = portfolio_weights(
            {name: user_provided(value, label=name) for name, value in inp.holdings.items()}
        )
    else:
        pw = unavailable(
            label="Portfolio weights",
            reason="Provide holdings (name -> value) to compute allocation weights.",
        )

    notes.append(
        "All figures are Calculated from your own User Provided inputs; none are "
        "independently verified market data."
    )
    return Dashboard(
        net_worth=nw,
        savings_rate=sr,
        emergency_fund_months=ef,
        portfolio_weights=pw,
        notes=notes,
    )
