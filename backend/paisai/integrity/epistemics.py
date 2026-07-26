"""Epistemic labelling and the required anatomy of a substantive answer.

``docs/AI_BEHAVIOR_CONTRACT.md`` says every substantive answer must carry its
evidence, reasoning, assumptions, risks, alternatives, limitations, confidence,
and sources. This module makes that anatomy a type: an :class:`Answer` that is
missing its material parts is not "a bit thin" — it is invalid.

Nothing here fabricates content. It only guarantees that when the AI layer
produces an answer, the honest scaffolding travels with it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Sequence


class EpistemicLabel(str, Enum):
    """How a given claim relates to the truth. See ``docs/DATA_INTEGRITY.md``."""

    FACT = "Fact"              # Verifiable and sourced.
    INFERENCE = "Inference"    # A reasoned conclusion; the reasoning is shown.
    ASSUMPTION = "Assumption"  # A premise adopted to proceed; always displayed.
    OPINION = "Opinion"        # A judgement, labelled as such.
    LIMITATION = "Limitation"  # What the answer does not or cannot cover.


class Confidence(str, Enum):
    """Calibrated to the strength of evidence and method — never to tone.

    ``INSUFFICIENT`` is a valid, expected outcome: it means the system cannot
    responsibly answer and says so, rather than papering over the gap.
    """

    HIGH = "High"                  # Verified data, robust method, low sensitivity.
    MEDIUM = "Medium"              # Some estimation/assumption; directionally reliable.
    LOW = "Low"                    # Sparse data or heavy assumptions; tentative.
    INSUFFICIENT = "Insufficient"  # Cannot responsibly answer.


@dataclass(frozen=True)
class Claim:
    """A single statement carrying its epistemic label."""

    text: str
    label: EpistemicLabel

    def to_dict(self) -> dict[str, Any]:
        return {"text": self.text, "label": self.label.value}


@dataclass
class Answer:
    """A substantive answer with its honesty scaffolding attached.

    ``summary`` is the headline; the surrounding fields are the reasoning made
    visible. :meth:`validate` enforces that a non-trivial answer is not stripped
    of the parts that make it trustworthy.
    """

    summary: str
    evidence: list[str] = field(default_factory=list)
    reasoning: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    alternatives: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    confidence: Confidence = Confidence.INSUFFICIENT
    sources: list[str] = field(default_factory=list)
    claims: list[Claim] = field(default_factory=list)

    def validate(self, *, substantive: bool = True) -> "Answer":
        """Check the answer honours the behaviour contract; returns self.

        For a substantive answer (a recommendation or analysis) the material
        sections may be terse but must not be empty. The one honest exception:
        an answer may legitimately report that it cannot answer, in which case
        its confidence is ``INSUFFICIENT`` and its limitation explains why.
        """
        if not self.summary.strip():
            raise ValueError("An answer must have a summary.")

        if not substantive:
            return self

        if self.confidence is Confidence.INSUFFICIENT:
            # "I can't responsibly answer" is valid — but it must say why.
            if not self.limitations:
                raise ValueError(
                    "An Insufficient-confidence answer must state the limitation "
                    "that prevents a fuller answer."
                )
            return self

        missing = [
            name
            for name, seq in (
                ("evidence", self.evidence),
                ("reasoning", self.reasoning),
                ("risks", self.risks),
                ("assumptions", self.assumptions),
                ("limitations", self.limitations),
            )
            if not seq
        ]
        if missing:
            raise ValueError(
                "A substantive answer is missing required sections: "
                + ", ".join(missing)
                + ". Do not drop them for a cleaner UI — collapse, never delete."
            )
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "evidence": list(self.evidence),
            "reasoning": list(self.reasoning),
            "assumptions": list(self.assumptions),
            "risks": list(self.risks),
            "alternatives": list(self.alternatives),
            "limitations": list(self.limitations),
            "confidence": self.confidence.value,
            "sources": list(self.sources),
            "claims": [c.to_dict() for c in self.claims],
        }


@dataclass
class InvestmentRecommendation:
    """The mandatory anatomy of an investment recommendation.

    ``docs/AI_BEHAVIOR_CONTRACT.md`` forbids recommending anything on the basis
    of hype and requires each of these components. The system never states an
    asset *will* rise; the phrasing is conditional and assumption-bound.
    """

    asset: str
    thesis: str
    supporting_evidence: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    counterarguments: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    portfolio_role: str = ""
    time_horizon: str = ""
    exit_conditions: list[str] = field(default_factory=list)
    confidence: Confidence = Confidence.INSUFFICIENT

    _FORBIDDEN = ("will go up", "will rise", "guaranteed", "can't lose", "sure thing")

    def validate(self) -> "InvestmentRecommendation":
        required: Sequence[tuple[str, Any]] = (
            ("thesis", self.thesis),
            ("supporting_evidence", self.supporting_evidence),
            ("risks", self.risks),
            ("counterarguments", self.counterarguments),
            ("assumptions", self.assumptions),
            ("portfolio_role", self.portfolio_role),
            ("time_horizon", self.time_horizon),
            ("exit_conditions", self.exit_conditions),
        )
        missing = [name for name, val in required if not val]
        if missing:
            raise ValueError(
                "An investment recommendation is incomplete: missing "
                + ", ".join(missing)
                + ". Never recommend without evidence, risks, counterarguments, "
                "assumptions, role, horizon, and exit conditions."
            )
        blob = (self.thesis + " " + " ".join(self.supporting_evidence)).lower()
        hit = next((p for p in self._FORBIDDEN if p in blob), None)
        if hit:
            raise ValueError(
                f"Forbidden certainty phrasing detected: {hit!r}. State that the "
                "investment 'appears suitable under these assumptions', never that "
                "it will rise or is guaranteed."
            )
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset": self.asset,
            "thesis": self.thesis,
            "supporting_evidence": list(self.supporting_evidence),
            "risks": list(self.risks),
            "counterarguments": list(self.counterarguments),
            "assumptions": list(self.assumptions),
            "portfolio_role": self.portfolio_role,
            "time_horizon": self.time_horizon,
            "exit_conditions": list(self.exit_conditions),
            "confidence": self.confidence.value,
        }
