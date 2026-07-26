"""The Decision Journal — PAISAI's signature feature.

Most finance tools track *what you own*. The Decision Journal tracks *how you
decided*, then compares the original thesis against what actually happened. Its
objective is to improve judgement, not to maximise profit — so a good decision
that lost money scores well, and a lucky bad decision does not.

This module implements the parts that can be computed honestly from recorded
data:

- :mod:`models` — the structured entry captured at decision time.
- :mod:`review` — the thesis-vs-reality reconciliation at the review date.
- :mod:`quality` — a transparent, process-based Decision Quality Score.

Where a capability would require behavioural data the journal does not yet
capture, it is declared explicitly rather than faked (see ``review`` and the
notes on bias detection) — consistent with "evidence over opinions".
"""

from .models import (
    Action,
    Alternative,
    Assumption,
    DecisionEntry,
    RiskFactor,
)
from .review import (
    AssumptionStatus,
    Observation,
    ReviewResult,
    RiskStatus,
    ThesisStatus,
    review_entry,
)
from .quality import DecisionQualityScore, score_decision_quality

__all__ = [
    "Action",
    "Assumption",
    "Alternative",
    "RiskFactor",
    "DecisionEntry",
    "Observation",
    "AssumptionStatus",
    "RiskStatus",
    "ThesisStatus",
    "ReviewResult",
    "review_entry",
    "DecisionQualityScore",
    "score_decision_quality",
]
