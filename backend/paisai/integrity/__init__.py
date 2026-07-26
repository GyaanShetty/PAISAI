"""The integrity core — the enforcement layer for PAISAI's data-integrity policy.

Everything a user sees passes through the vocabulary defined here:

- :class:`Provenance` — the six categories every value must belong to.
- :class:`ProvenancedValue` / :class:`Unavailable` — a number with its origin, or
  an honest statement that the number is not available.
- :class:`EpistemicLabel`, :class:`Confidence`, :class:`Answer` — the required
  anatomy of a substantive answer.
- :class:`IntegrityError` and :func:`ensure_provenanced` — the guardrail that
  rejects un-sourced numerics before they can reach a user.
"""

from .provenance import (
    IntegrityError,
    Provenance,
    ProvenancedValue,
    Unavailable,
    ensure_provenanced,
    unavailable,
)
from .epistemics import Answer, Confidence, EpistemicLabel

__all__ = [
    "Provenance",
    "ProvenancedValue",
    "Unavailable",
    "unavailable",
    "IntegrityError",
    "ensure_provenanced",
    "EpistemicLabel",
    "Confidence",
    "Answer",
]
