"""Calculation engine: correct math, and provenance that flows through it."""

import math

import pytest

from paisai.engine import (
    cagr,
    emergency_fund_months,
    portfolio_weights,
    savings_rate,
)
from paisai.integrity.provenance import (
    IntegrityError,
    Provenance,
    assumed,
    user_provided,
    verified,
)


def _num(x, label=""):
    return user_provided(x, label=label)


# --- CAGR -------------------------------------------------------------------


def test_cagr_doubles_over_ten_years():
    # 100 -> 200 over 10y is 2 ** (1/10) - 1 ≈ 7.177%.
    result = cagr(_num(100.0), _num(200.0), _num(10.0))
    assert math.isclose(result.value, 2 ** 0.1 - 1, rel_tol=1e-12)
    assert result.provenance is Provenance.CALCULATED
    assert len(result.inputs) == 3  # inputs recorded for auditability


def test_cagr_flat_is_zero():
    result = cagr(_num(500.0), _num(500.0), _num(5.0))
    assert math.isclose(result.value, 0.0, abs_tol=1e-12)


def test_cagr_can_be_negative():
    # A real loss produces an honest negative CAGR, not a floored zero.
    result = cagr(_num(200.0), _num(100.0), _num(4.0))
    assert result.value < 0


def test_cagr_undefined_inputs_raise():
    with pytest.raises(IntegrityError):
        cagr(_num(0.0), _num(100.0), _num(5.0))
    with pytest.raises(IntegrityError):
        cagr(_num(100.0), _num(200.0), _num(0.0))


def test_cagr_rejects_forward_looking_input():
    # An Assumed input would contaminate a "Calculated" result.
    with pytest.raises(IntegrityError):
        cagr(_num(100.0), assumed(200.0, note="hoped-for value"), _num(10.0))


def test_cagr_rejects_bare_number_input():
    with pytest.raises(IntegrityError):
        cagr(100.0, 200.0, 10.0)  # type: ignore[arg-type]


# --- savings rate -----------------------------------------------------------


def test_savings_rate_basic():
    result = savings_rate(_num(100000.0), _num(70000.0))
    assert math.isclose(result.value, 0.30, rel_tol=1e-12)
    assert result.provenance is Provenance.CALCULATED


def test_savings_rate_negative_when_overspending():
    result = savings_rate(_num(50000.0), _num(65000.0))
    assert result.value < 0  # honest: spending exceeds income


def test_savings_rate_requires_positive_income():
    with pytest.raises(IntegrityError):
        savings_rate(_num(0.0), _num(1000.0))


# --- portfolio weights ------------------------------------------------------


def test_portfolio_weights_sum_to_one():
    holdings = {
        "Equity": verified(600000.0, source="broker"),
        "Debt": verified(300000.0, source="broker"),
        "Gold": verified(100000.0, source="broker"),
    }
    weights = portfolio_weights(holdings)
    assert math.isclose(sum(w.value for w in weights.values()), 1.0, rel_tol=1e-12)
    assert math.isclose(weights["Equity"].value, 0.6, rel_tol=1e-12)
    # Each weight records the holding and the computed total.
    assert all(w.provenance is Provenance.CALCULATED for w in weights.values())
    assert len(weights["Equity"].inputs) == 2


def test_portfolio_weights_empty_raises():
    with pytest.raises(IntegrityError):
        portfolio_weights({})


def test_portfolio_weights_zero_total_raises():
    with pytest.raises(IntegrityError):
        portfolio_weights({"a": _num(0.0), "b": _num(0.0)})


def test_portfolio_weights_reject_negative_holding():
    with pytest.raises(IntegrityError):
        portfolio_weights({"a": _num(-100.0), "b": _num(200.0)})


# --- emergency fund ---------------------------------------------------------


def test_emergency_fund_months():
    result = emergency_fund_months(_num(300000.0), _num(50000.0))
    assert math.isclose(result.value, 6.0, rel_tol=1e-12)
    assert result.unit == "months"


def test_emergency_fund_requires_positive_expenses():
    with pytest.raises(IntegrityError):
        emergency_fund_months(_num(100000.0), _num(0.0))
