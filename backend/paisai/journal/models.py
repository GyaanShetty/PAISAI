"""The structured Decision Journal entry, captured at decision time.

Capturing assumptions, alternatives, emotional state, and market context *at the
moment of the decision* is what makes an honest later review possible. Memory
rewrites the past; the journal does not. See ``docs/DECISION_JOURNAL.md``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Any, Optional

from ..integrity.epistemics import Confidence
from ..integrity.provenance import Provenance, ProvenancedValue


class Action(str, Enum):
    """The financial action a journal entry records."""

    BUY = "Buy"
    SELL = "Sell"
    HOLD = "Hold"
    SIP = "SIP"
    WITHDRAWAL = "Withdrawal"
    LOAN = "Loan"
    INSURANCE = "Insurance"
    OTHER = "Other"


@dataclass(frozen=True)
class Assumption:
    """A premise the decision depended on, recorded so it can be tested later."""

    statement: str

    def __post_init__(self) -> None:
        if not self.statement.strip():
            raise ValueError("An assumption must have a statement.")


@dataclass(frozen=True)
class RiskFactor:
    """A risk identified at decision time, recorded so it can be checked later."""

    statement: str

    def __post_init__(self) -> None:
        if not self.statement.strip():
            raise ValueError("A risk factor must have a statement.")


@dataclass(frozen=True)
class Alternative:
    """An option that was considered, and why it was not chosen."""

    option: str
    rejection_reason: str

    def __post_init__(self) -> None:
        if not self.option.strip():
            raise ValueError("An alternative must name the option considered.")
        if not self.rejection_reason.strip():
            raise ValueError(
                "An alternative must record why it was rejected — an unexplained "
                "rejection cannot be reviewed honestly later."
            )


@dataclass
class DecisionEntry:
    """A single, structured record of a financial decision.

    ``expected_return`` — if the user supplies one — must be a ``User Provided``
    provenanced value, never a fabricated projection dressed up as the user's own
    expectation.
    """

    date: date
    asset: str
    action: Action
    thesis: str
    expected_outcome: str
    time_horizon: str
    review_date: date
    confidence: Confidence
    market_context: str = ""
    expected_return: Optional[ProvenancedValue] = None
    risk_factors: list[RiskFactor] = field(default_factory=list)
    assumptions: list[Assumption] = field(default_factory=list)
    alternatives: list[Alternative] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    emotional_state: Optional[str] = None  # optional and never required

    def __post_init__(self) -> None:
        for name, value in (
            ("asset", self.asset),
            ("thesis", self.thesis),
            ("expected_outcome", self.expected_outcome),
            ("time_horizon", self.time_horizon),
        ):
            if not str(value).strip():
                raise ValueError(f"A decision entry requires a non-empty {name}.")
        if self.review_date < self.date:
            raise ValueError("The review date cannot be before the decision date.")
        if self.expected_return is not None:
            if not isinstance(self.expected_return, ProvenancedValue):
                raise ValueError(
                    "expected_return must be a ProvenancedValue (User Provided)."
                )
            if self.expected_return.provenance is not Provenance.USER_PROVIDED:
                raise ValueError(
                    "expected_return is the user's own expectation and must be "
                    "provenance User Provided, not a fabricated projection."
                )

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.date.isoformat(),
            "asset": self.asset,
            "action": self.action.value,
            "thesis": self.thesis,
            "expected_outcome": self.expected_outcome,
            "time_horizon": self.time_horizon,
            "review_date": self.review_date.isoformat(),
            "confidence": self.confidence.value,
            "market_context": self.market_context,
            "expected_return": (
                self.expected_return.to_dict() if self.expected_return else None
            ),
            "risk_factors": [r.statement for r in self.risk_factors],
            "assumptions": [a.statement for a in self.assumptions],
            "alternatives": [
                {"option": a.option, "rejection_reason": a.rejection_reason}
                for a in self.alternatives
            ],
            "sources": list(self.sources),
            "emotional_state": self.emotional_state,
        }
