"""Deterministic financial calculations.

Each function here embodies two rules from the founding documents:

1. **Numbers come from math, not memory.** Results are computed from the inputs,
   never recalled by a model.
2. **Provenance flows through the math.** Inputs must themselves be
   :class:`ProvenancedValue` (Verified, User Provided, or Calculated), and the
   result is tagged ``Calculated`` with those inputs recorded — so any figure can
   be traced back to clean data.

The functions raise :class:`IntegrityError` rather than returning a misleading
number when the inputs make the calculation undefined.
"""

from __future__ import annotations

from typing import Mapping

from ..integrity.provenance import (
    IntegrityError,
    Provenance,
    ProvenancedValue,
)

# Inputs to a calculation must carry one of these provenance categories. An
# Estimated/Projected/Assumed input would silently contaminate a "Calculated"
# result, so calculations refuse them unless a caller opts in explicitly.
_CLEAN_INPUTS = (
    Provenance.VERIFIED,
    Provenance.USER_PROVIDED,
    Provenance.CALCULATED,
)


def _require_clean(*values: ProvenancedValue) -> None:
    for v in values:
        if not isinstance(v, ProvenancedValue):
            raise IntegrityError(
                "Calculation inputs must be ProvenancedValue, so provenance "
                f"flows through the math; got {type(v).__name__}."
            )
        if v.provenance not in _CLEAN_INPUTS:
            raise IntegrityError(
                f"Input {v.label or v.value!r} is {v.provenance.value}; a "
                "Calculated result may only derive from Verified, User Provided, "
                "or Calculated inputs. Present forward-looking figures as "
                "Projected/Estimated explicitly instead."
            )


def cagr(
    begin_value: ProvenancedValue,
    end_value: ProvenancedValue,
    years: ProvenancedValue,
    *,
    label: str = "CAGR",
) -> ProvenancedValue:
    """Compound Annual Growth Rate, returned as a decimal fraction (0.12 = 12%).

    CAGR = (end / begin) ** (1 / years) - 1.

    Undefined cases (non-positive begin value or non-positive horizon) raise
    rather than returning a fabricated-looking zero.
    """
    _require_clean(begin_value, end_value, years)
    b, e, y = begin_value.value, end_value.value, years.value
    if b <= 0:
        raise IntegrityError("CAGR is undefined for a non-positive beginning value.")
    if y <= 0:
        raise IntegrityError("CAGR is undefined for a non-positive number of years.")
    if e < 0:
        raise IntegrityError("CAGR is undefined for a negative ending value.")
    result = (e / b) ** (1.0 / y) - 1.0
    return ProvenancedValue(
        value=result,
        provenance=Provenance.CALCULATED,
        label=label,
        unit="fraction",
        method="CAGR = (end / begin) ** (1 / years) - 1",
        inputs=(begin_value, end_value, years),
    )


def savings_rate(
    income: ProvenancedValue,
    expenses: ProvenancedValue,
    *,
    label: str = "Savings rate",
) -> ProvenancedValue:
    """Savings rate as a fraction of income: (income - expenses) / income.

    Can be negative (spending exceeds income) — that is a real, honest result and
    is returned as-is, not floored to zero.
    """
    _require_clean(income, expenses)
    inc, exp = income.value, expenses.value
    if inc <= 0:
        raise IntegrityError(
            "Savings rate is undefined without positive income."
        )
    result = (inc - exp) / inc
    return ProvenancedValue(
        value=result,
        provenance=Provenance.CALCULATED,
        label=label,
        unit="fraction",
        method="savings_rate = (income - expenses) / income",
        inputs=(income, expenses),
    )


def portfolio_weights(
    holdings: Mapping[str, ProvenancedValue],
) -> dict[str, ProvenancedValue]:
    """Portfolio weights (each a fraction of total) from per-holding values.

    Returns a mapping of the same keys to ``Calculated`` weights that record both
    the holding value and the computed total as inputs. Requires a positive total.
    """
    if not holdings:
        raise IntegrityError("Cannot compute weights for an empty portfolio.")
    values = list(holdings.values())
    _require_clean(*values)
    if any(v.value < 0 for v in values):
        raise IntegrityError("Holding values must be non-negative to weight them.")

    total_amount = sum(v.value for v in values)
    if total_amount <= 0:
        raise IntegrityError(
            "Portfolio total is zero; weights are undefined."
        )
    total = ProvenancedValue(
        value=total_amount,
        provenance=Provenance.CALCULATED,
        label="Portfolio total",
        method="total = sum(holding values)",
        inputs=tuple(values),
    )
    weights: dict[str, ProvenancedValue] = {}
    for name, holding in holdings.items():
        weights[name] = ProvenancedValue(
            value=holding.value / total_amount,
            provenance=Provenance.CALCULATED,
            label=f"{name} weight",
            unit="fraction",
            method="weight = holding value / portfolio total",
            inputs=(holding, total),
        )
    return weights


def emergency_fund_months(
    liquid_savings: ProvenancedValue,
    monthly_expenses: ProvenancedValue,
    *,
    label: str = "Emergency fund coverage",
) -> ProvenancedValue:
    """How many months of expenses the liquid savings cover."""
    _require_clean(liquid_savings, monthly_expenses)
    if monthly_expenses.value <= 0:
        raise IntegrityError(
            "Emergency-fund coverage is undefined without positive monthly expenses."
        )
    if liquid_savings.value < 0:
        raise IntegrityError("Liquid savings cannot be negative.")
    result = liquid_savings.value / monthly_expenses.value
    return ProvenancedValue(
        value=result,
        provenance=Provenance.CALCULATED,
        label=label,
        unit="months",
        method="months = liquid savings / monthly expenses",
        inputs=(liquid_savings, monthly_expenses),
    )
