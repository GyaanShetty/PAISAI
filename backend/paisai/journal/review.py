"""Thesis-vs-reality reconciliation at the review date.

At each review date, PAISAI compares the original thesis against what actually
happened. This module performs that comparison **only from observations that are
explicitly recorded** — it never guesses what became of an assumption or a risk.
An un-observed assumption is reported as ``UNKNOWN``, not silently assumed correct.
That honesty is the whole point of the exercise.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .models import DecisionEntry


class AssumptionStatus(str, Enum):
    HELD = "Held"
    FAILED = "Failed"
    UNKNOWN = "Unknown"  # not yet observable; never guessed


class RiskStatus(str, Enum):
    MATERIALISED = "Materialised"
    DID_NOT = "Did not materialise"
    UNKNOWN = "Unknown"


class ThesisStatus(str, Enum):
    HOLDS = "Still holds"
    WEAKENED = "Weakened"
    BROKEN = "Broken"
    UNKNOWN = "Unknown"


@dataclass
class Observation:
    """What was actually observed for one assumption or risk by the review date.

    ``key`` must match an assumption statement or risk statement in the entry.
    """

    key: str
    status: object  # AssumptionStatus | RiskStatus
    note: str = ""


@dataclass
class ReviewResult:
    """The outcome of a review: what held, what failed, what remains unknown.

    ``should_reconsider`` is a conservative flag, true only when there is recorded
    evidence that the thesis is broken or that failed assumptions outnumber those
    that held. It is never triggered by unknowns.
    """

    entry_asset: str
    thesis_status: ThesisStatus
    assumptions_held: list[str] = field(default_factory=list)
    assumptions_failed: list[str] = field(default_factory=list)
    assumptions_unknown: list[str] = field(default_factory=list)
    risks_materialised: list[str] = field(default_factory=list)
    risks_avoided: list[str] = field(default_factory=list)
    risks_unknown: list[str] = field(default_factory=list)
    unmatched_observations: list[str] = field(default_factory=list)
    should_reconsider: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_asset": self.entry_asset,
            "thesis_status": self.thesis_status.value,
            "assumptions_held": self.assumptions_held,
            "assumptions_failed": self.assumptions_failed,
            "assumptions_unknown": self.assumptions_unknown,
            "risks_materialised": self.risks_materialised,
            "risks_avoided": self.risks_avoided,
            "risks_unknown": self.risks_unknown,
            "unmatched_observations": self.unmatched_observations,
            "should_reconsider": self.should_reconsider,
        }


def review_entry(
    entry: DecisionEntry,
    observations: list[Observation],
    thesis_status: ThesisStatus = ThesisStatus.UNKNOWN,
) -> ReviewResult:
    """Reconcile a decision's assumptions and risks against recorded observations.

    Assumptions and risks with no matching observation are reported ``UNKNOWN`` —
    the review does not invent an outcome for them. Observations that match no
    assumption or risk in the entry are surfaced under ``unmatched_observations``
    rather than dropped.
    """
    obs_by_key = {o.key: o for o in observations}
    used_keys: set[str] = set()

    result = ReviewResult(entry_asset=entry.asset, thesis_status=thesis_status)

    for assumption in entry.assumptions:
        obs = obs_by_key.get(assumption.statement)
        if obs is None:
            result.assumptions_unknown.append(assumption.statement)
            continue
        used_keys.add(assumption.statement)
        if obs.status is AssumptionStatus.HELD:
            result.assumptions_held.append(assumption.statement)
        elif obs.status is AssumptionStatus.FAILED:
            result.assumptions_failed.append(assumption.statement)
        else:
            result.assumptions_unknown.append(assumption.statement)

    for risk in entry.risk_factors:
        obs = obs_by_key.get(risk.statement)
        if obs is None:
            result.risks_unknown.append(risk.statement)
            continue
        used_keys.add(risk.statement)
        if obs.status is RiskStatus.MATERIALISED:
            result.risks_materialised.append(risk.statement)
        elif obs.status is RiskStatus.DID_NOT:
            result.risks_avoided.append(risk.statement)
        else:
            result.risks_unknown.append(risk.statement)

    result.unmatched_observations = [
        o.key for o in observations if o.key not in used_keys
    ]

    # Conservative: only recommend reconsideration on recorded evidence, never
    # on unknowns.
    result.should_reconsider = thesis_status is ThesisStatus.BROKEN or (
        len(result.assumptions_failed) > len(result.assumptions_held)
        and len(result.assumptions_failed) > 0
    )
    return result
