"""The Personal Decision Quality Score.

This score measures the **quality of decision-making, not portfolio returns**. A
well-reasoned, appropriately hedged, correctly sized decision scores well even if
it lost money; a lucky, poorly-reasoned one does not. See
``docs/DECISION_JOURNAL.md``.

The score is a transparent, rule-based heuristic — deliberately simple and fully
inspectable, never an opaque black box. It is labelled ``Estimated`` (a heuristic
index, not a verified measurement), and it always ships with its component
breakdown and its limitations, so the user can see exactly how it was formed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from ..integrity.epistemics import Confidence
from ..integrity.provenance import Provenance, ProvenancedValue
from .models import DecisionEntry
from .review import ReviewResult

# What a well-recorded decision contains. Presence of each is a process signal —
# it says the decision was made deliberately, not impulsively.
_COMPLETENESS_CHECKS = (
    "thesis",
    "expected_outcome",
    "time_horizon",
    "assumptions",
    "risk_factors",
    "alternatives",
    "sources",
)

# How much accuracy each confidence level implicitly claims, used only to check
# calibration against observed outcomes. These are transparent anchors, not
# empirical constants dressed up as fact.
_CONFIDENCE_TARGET = {
    Confidence.HIGH: 0.85,
    Confidence.MEDIUM: 0.60,
    Confidence.LOW: 0.40,
    Confidence.INSUFFICIENT: 0.25,
}


@dataclass
class DecisionQualityScore:
    """A process-quality score in [0, 1] with its components and limitations."""

    overall: ProvenancedValue
    completeness: float
    calibration: Optional[float]
    components: dict[str, bool]
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall": self.overall.to_dict(),
            "completeness": self.completeness,
            "calibration": self.calibration,
            "components": self.components,
            "limitations": list(self.limitations),
        }


def _completeness(entry: DecisionEntry) -> tuple[float, dict[str, bool]]:
    present: dict[str, bool] = {}
    for name in _COMPLETENESS_CHECKS:
        value = getattr(entry, name)
        if isinstance(value, str):
            present[name] = bool(value.strip())
        else:  # list-valued anatomy (assumptions, risks, alternatives, sources)
            present[name] = len(value) > 0
    score = sum(present.values()) / len(_COMPLETENESS_CHECKS)
    return score, present


def _calibration(entry: DecisionEntry, review: ReviewResult) -> Optional[float]:
    resolved = len(review.assumptions_held) + len(review.assumptions_failed)
    if resolved == 0:
        return None  # nothing was observable yet — calibration is unknown, not 0
    actual_accuracy = len(review.assumptions_held) / resolved
    target = _CONFIDENCE_TARGET[entry.confidence]
    # 1.0 when stated confidence matched what actually happened; falls off linearly.
    return max(0.0, 1.0 - abs(target - actual_accuracy))


def score_decision_quality(
    entry: DecisionEntry,
    review: Optional[ReviewResult] = None,
) -> DecisionQualityScore:
    """Compute the process-quality score for a decision.

    Without a review, only the completeness of the recorded reasoning can be
    assessed. With a review, calibration (did stated confidence match observed
    outcomes?) is folded in. Returns are never an input — by design.
    """
    completeness, components = _completeness(entry)
    limitations = [
        "Measures decision *process*, not returns — a sound decision can still "
        "lose money, and a lucky one can still be poor.",
        "Completeness rewards recording the reasoning; it cannot judge whether the "
        "reasoning was correct.",
    ]

    calibration: Optional[float] = None
    if review is not None:
        calibration = _calibration(entry, review)
        if calibration is None:
            limitations.append(
                "No assumptions were observable at review, so calibration is "
                "unknown and excluded from the score."
            )

    if calibration is None:
        overall_value = completeness
        method = "overall = completeness (no calibration data available yet)"
    else:
        overall_value = 0.6 * completeness + 0.4 * calibration
        method = "overall = 0.6 * completeness + 0.4 * calibration"

    limitations.append(
        "This is a transparent heuristic index, not an empirically validated "
        "metric; treat it as directional."
    )

    overall = ProvenancedValue(
        value=round(overall_value, 4),
        provenance=Provenance.ESTIMATED,
        label="Decision Quality Score",
        unit="index[0-1]",
        method=method,
    )
    return DecisionQualityScore(
        overall=overall,
        completeness=round(completeness, 4),
        calibration=None if calibration is None else round(calibration, 4),
        components=components,
        limitations=limitations,
    )
