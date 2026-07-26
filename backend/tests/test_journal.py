"""Decision Journal: honest capture, honest review, process-based scoring."""

from datetime import date

import pytest

from paisai.integrity.epistemics import Confidence
from paisai.integrity.provenance import Provenance, assumed, user_provided
from paisai.journal import (
    Action,
    Alternative,
    Assumption,
    AssumptionStatus,
    DecisionEntry,
    Observation,
    RiskFactor,
    RiskStatus,
    ThesisStatus,
    review_entry,
    score_decision_quality,
)


def _entry(**overrides) -> DecisionEntry:
    base = dict(
        date=date(2026, 1, 1),
        asset="Broad-market index fund",
        action=Action.SIP,
        thesis="Low-cost broad exposure for a long-horizon core allocation.",
        expected_outcome="Compound near the market over 10+ years.",
        time_horizon="10+ years",
        review_date=date(2026, 7, 1),
        confidence=Confidence.MEDIUM,
        market_context="Elevated valuations; rates plateauing.",
        risk_factors=[RiskFactor("Full exposure to equity drawdowns.")],
        assumptions=[
            Assumption("Costs stay below category median."),
            Assumption("Horizon remains 10+ years."),
        ],
        alternatives=[Alternative("Active fund", "Higher fee, no edge shown.")],
        sources=["Fund factsheet"],
    )
    base.update(overrides)
    return DecisionEntry(**base)


# --- models -----------------------------------------------------------------


def test_entry_builds_and_serialises():
    e = _entry()
    d = e.to_dict()
    assert d["action"] == "SIP"
    assert d["assumptions"] == [
        "Costs stay below category median.",
        "Horizon remains 10+ years.",
    ]


def test_review_date_before_decision_is_rejected():
    with pytest.raises(ValueError):
        _entry(review_date=date(2025, 12, 1))


def test_missing_thesis_rejected():
    with pytest.raises(ValueError):
        _entry(thesis="   ")


def test_alternative_requires_rejection_reason():
    with pytest.raises(ValueError):
        Alternative("Some option", "")


def test_expected_return_must_be_user_provided():
    ok = _entry(expected_return=user_provided(0.11, label="Expected return"))
    assert ok.expected_return.provenance is Provenance.USER_PROVIDED
    # A fabricated projection dressed up as the user's expectation is refused.
    with pytest.raises(ValueError):
        _entry(expected_return=assumed(0.11, note="model guess"))


# --- review -----------------------------------------------------------------


def test_review_reconciles_recorded_observations():
    e = _entry()
    result = review_entry(
        e,
        observations=[
            Observation("Costs stay below category median.", AssumptionStatus.HELD),
            Observation("Horizon remains 10+ years.", AssumptionStatus.FAILED),
            Observation(
                "Full exposure to equity drawdowns.", RiskStatus.MATERIALISED
            ),
        ],
        thesis_status=ThesisStatus.WEAKENED,
    )
    assert result.assumptions_held == ["Costs stay below category median."]
    assert result.assumptions_failed == ["Horizon remains 10+ years."]
    assert result.risks_materialised == ["Full exposure to equity drawdowns."]


def test_review_never_guesses_unobserved_assumptions():
    e = _entry()
    # Only one of two assumptions observed; the other must be UNKNOWN, not assumed.
    result = review_entry(
        e,
        observations=[
            Observation("Costs stay below category median.", AssumptionStatus.HELD),
        ],
    )
    assert result.assumptions_held == ["Costs stay below category median."]
    assert result.assumptions_unknown == ["Horizon remains 10+ years."]
    assert result.risks_unknown == ["Full exposure to equity drawdowns."]


def test_review_surfaces_unmatched_observations():
    e = _entry()
    result = review_entry(
        e,
        observations=[Observation("Some unrelated claim", AssumptionStatus.HELD)],
    )
    assert "Some unrelated claim" in result.unmatched_observations


def test_should_reconsider_only_on_evidence():
    e = _entry()
    # No observations -> all unknown -> must NOT recommend reconsidering.
    calm = review_entry(e, observations=[])
    assert calm.should_reconsider is False
    # A broken thesis -> reconsider.
    broken = review_entry(e, observations=[], thesis_status=ThesisStatus.BROKEN)
    assert broken.should_reconsider is True


# --- quality score ----------------------------------------------------------


def test_quality_score_rewards_completeness():
    full = score_decision_quality(_entry())
    sparse = score_decision_quality(
        _entry(assumptions=[], risk_factors=[], alternatives=[], sources=[])
    )
    assert full.completeness > sparse.completeness
    assert full.overall.provenance is Provenance.ESTIMATED
    assert full.overall.value <= 1.0
    # The score always ships with its honest caveats.
    assert any("not returns" in l for l in full.limitations)


def test_quality_calibration_uses_review_when_present():
    e = _entry(confidence=Confidence.HIGH)
    # High confidence but both assumptions failed -> poor calibration.
    review = review_entry(
        e,
        observations=[
            Observation("Costs stay below category median.", AssumptionStatus.FAILED),
            Observation("Horizon remains 10+ years.", AssumptionStatus.FAILED),
        ],
    )
    scored = score_decision_quality(e, review)
    assert scored.calibration is not None
    assert scored.calibration < 0.5


def test_quality_calibration_unknown_when_nothing_observed():
    e = _entry()
    review = review_entry(e, observations=[])
    scored = score_decision_quality(e, review)
    assert scored.calibration is None
    assert any("calibration is" in l.lower() for l in scored.limitations)
