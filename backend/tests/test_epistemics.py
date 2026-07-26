"""Answer anatomy: a substantive answer cannot be stripped of its honesty."""

import pytest

from paisai.integrity.epistemics import (
    Answer,
    Confidence,
    EpistemicLabel,
    InvestmentRecommendation,
)


def _full_answer(**overrides):
    base = dict(
        summary="Dining is 38% of discretionary spending.",
        evidence=["12 months of categorised transactions."],
        reasoning=["Dining total / discretionary total = 0.38."],
        assumptions=["No behavioural change over the horizon."],
        risks=["Projection fails if spending pattern shifts."],
        alternatives=["Cap dining at 20% and redirect the difference to SIP."],
        limitations=["Excludes cash spend not captured by the bank feed."],
        confidence=Confidence.MEDIUM,
        sources=["User's linked account statements."],
    )
    base.update(overrides)
    return Answer(**base)


def test_full_answer_validates():
    _full_answer().validate()


def test_substantive_answer_missing_sections_fails():
    with pytest.raises(ValueError):
        _full_answer(evidence=[], risks=[]).validate()


def test_summary_required():
    with pytest.raises(ValueError):
        Answer(summary="   ").validate(substantive=False)


def test_insufficient_confidence_must_state_limitation():
    # "I can't answer" is valid — but only if it says why.
    bad = Answer(summary="No verified data.", confidence=Confidence.INSUFFICIENT)
    with pytest.raises(ValueError):
        bad.validate()
    good = Answer(
        summary="I don't have verified data for this fund's live NAV.",
        confidence=Confidence.INSUFFICIENT,
        limitations=["The NAV provider was unreachable at query time."],
    )
    good.validate()  # must not raise


def test_non_substantive_answer_is_lenient():
    Answer(summary="Rounded to nearest rupee for display.").validate(substantive=False)


def test_answer_serialises_all_sections():
    d = _full_answer().to_dict()
    for key in (
        "evidence",
        "reasoning",
        "assumptions",
        "risks",
        "alternatives",
        "limitations",
        "confidence",
        "sources",
    ):
        assert key in d


def test_epistemic_labels_available():
    assert {l.value for l in EpistemicLabel} == {
        "Fact",
        "Inference",
        "Assumption",
        "Opinion",
        "Limitation",
    }


# --- investment recommendation ----------------------------------------------


def _full_reco(**overrides):
    base = dict(
        asset="Broad-market index fund",
        thesis="Low-cost broad exposure fits a long-horizon core allocation.",
        supporting_evidence=["Expense ratio below category median (verified)."],
        risks=["Full exposure to equity-market drawdowns."],
        counterarguments=["An investor near a goal date may want less equity."],
        assumptions=["Horizon of 10+ years; no near-term liquidity need."],
        portfolio_role="Core equity holding.",
        time_horizon="10+ years.",
        exit_conditions=["Horizon shortens materially or costs rise above peers."],
        confidence=Confidence.MEDIUM,
    )
    base.update(overrides)
    return InvestmentRecommendation(**base)


def test_full_recommendation_validates():
    _full_reco().validate()


def test_recommendation_missing_parts_fails():
    with pytest.raises(ValueError):
        _full_reco(risks=[], exit_conditions=[]).validate()


def test_recommendation_rejects_certainty_language():
    with pytest.raises(ValueError):
        _full_reco(thesis="This fund will go up over time.").validate()
    with pytest.raises(ValueError):
        _full_reco(
            supporting_evidence=["Returns are basically guaranteed."]
        ).validate()
