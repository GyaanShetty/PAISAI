"""Provenance: every value belongs to exactly one category, or is Unavailable.

This module is the executable form of ``docs/DATA_INTEGRITY.md``. Its central
claim is simple and absolute: **a number may not reach a user unless the system
can say where it came from.** A value is either a :class:`ProvenancedValue` (a
number tagged with its origin and the metadata that origin requires) or an
:class:`Unavailable` (an honest "I don't have verified data for this").

The invariants below are what make the no-hallucination policy structural: you
cannot even *construct* a ``Verified`` value without a source, so a fabricated
figure has no legal representation in the system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, Sequence


class IntegrityError(Exception):
    """Raised when a value would violate the data-integrity policy.

    This is not an ordinary bug — it means something tried to present a number
    to a user without honest provenance. It should fail loudly, never silently
    degrade into a guess.
    """


class Provenance(str, Enum):
    """The six — and only six — categories a displayed value may belong to.

    Categories are never mixed within a single value. See ``docs/DATA_INTEGRITY.md``.
    """

    VERIFIED = "Verified"          # From an authoritative, integrated provider.
    CALCULATED = "Calculated"      # Deterministically derived from verified inputs.
    ESTIMATED = "Estimated"        # Approximated from partial data via a stated method.
    PROJECTED = "Projected"        # Forward-looking output of an explicit model.
    USER_PROVIDED = "User Provided"  # Entered by the user; trusted as input, not verified.
    ASSUMED = "Assumed"            # A placeholder adopted to proceed, always surfaced.


@dataclass(frozen=True)
class ProvenancedValue:
    """A number that knows where it came from.

    The constructor enforces the metadata each provenance category requires, so
    an ill-formed value cannot exist:

    - ``VERIFIED`` requires a ``source``.
    - ``CALCULATED`` requires the ``inputs`` it was derived from.
    - ``ESTIMATED`` / ``PROJECTED`` require a ``method``.
    - ``ASSUMED`` requires a ``note`` explaining the assumption.
    - ``USER_PROVIDED`` needs no extra justification (the user is the source).
    """

    value: float
    provenance: Provenance
    label: str = ""
    unit: str = ""
    source: Optional[str] = None
    as_of: Optional[datetime] = None
    method: Optional[str] = None
    note: Optional[str] = None
    inputs: Sequence["ProvenancedValue"] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.value, (int, float)) or isinstance(self.value, bool):
            raise IntegrityError(
                f"ProvenancedValue.value must be a real number, got {self.value!r}"
            )

        p = self.provenance
        if p is Provenance.VERIFIED and not self.source:
            raise IntegrityError(
                "A Verified value must cite a source. If you cannot, it is not "
                "verified — use Unavailable instead of inventing one."
            )
        if p is Provenance.CALCULATED and not self.inputs:
            raise IntegrityError(
                "A Calculated value must record the inputs it was derived from, "
                "so the number stays reproducible and auditable."
            )
        if p in (Provenance.ESTIMATED, Provenance.PROJECTED) and not self.method:
            raise IntegrityError(
                f"An {p.value} value must state the method behind it."
            )
        if p is Provenance.ASSUMED and not self.note:
            raise IntegrityError(
                "An Assumed value must surface the assumption via `note`; "
                "assumptions are never hidden."
            )
        # Freeze inputs to a tuple so the value stays immutable and hashable.
        object.__setattr__(self, "inputs", tuple(self.inputs))

    @property
    def is_forward_looking(self) -> bool:
        """True for values that describe the future (Projected/Estimated/Assumed)."""
        return self.provenance in (
            Provenance.PROJECTED,
            Provenance.ESTIMATED,
            Provenance.ASSUMED,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialise with provenance intact — the tag travels with the value."""
        data: dict[str, Any] = {
            "value": self.value,
            "provenance": self.provenance.value,
        }
        if self.label:
            data["label"] = self.label
        if self.unit:
            data["unit"] = self.unit
        if self.source:
            data["source"] = self.source
        if self.as_of:
            data["as_of"] = self.as_of.isoformat()
        if self.method:
            data["method"] = self.method
        if self.note:
            data["note"] = self.note
        if self.inputs:
            data["inputs"] = [i.to_dict() for i in self.inputs]
        return data

    def __str__(self) -> str:
        rendered = f"{self.value:g}{(' ' + self.unit) if self.unit else ''}"
        return f"{rendered} [{self.provenance.value}]"


@dataclass(frozen=True)
class Unavailable:
    """The honest alternative to a fabricated number.

    When verified data cannot be obtained, the system yields an ``Unavailable``
    rather than a guess. This is the canonical rendering of
    "I don't have verified data for this."
    """

    label: str = ""
    reason: str = "I don't have verified data for this."

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {"available": False, "reason": self.reason}
        if self.label:
            data["label"] = self.label
        return data

    def __str__(self) -> str:
        prefix = f"{self.label}: " if self.label else ""
        return f"{prefix}{self.reason}"


def unavailable(label: str = "", reason: Optional[str] = None) -> Unavailable:
    """Convenience constructor for an honest "no verified data" result."""
    if reason is None:
        return Unavailable(label=label)
    return Unavailable(label=label, reason=reason)


def verified(
    value: float,
    source: str,
    *,
    label: str = "",
    unit: str = "",
    as_of: Optional[datetime] = None,
) -> ProvenancedValue:
    """Build a Verified value. Raises if no source is given."""
    return ProvenancedValue(
        value=value,
        provenance=Provenance.VERIFIED,
        label=label,
        unit=unit,
        source=source,
        as_of=as_of or datetime.now(timezone.utc),
    )


def user_provided(
    value: float, *, label: str = "", unit: str = ""
) -> ProvenancedValue:
    """Build a User Provided value (the user is the source of truth for it)."""
    return ProvenancedValue(
        value=value,
        provenance=Provenance.USER_PROVIDED,
        label=label,
        unit=unit,
    )


def assumed(
    value: float, note: str, *, label: str = "", unit: str = ""
) -> ProvenancedValue:
    """Build an Assumed value; the assumption is required and always surfaced."""
    return ProvenancedValue(
        value=value,
        provenance=Provenance.ASSUMED,
        label=label,
        unit=unit,
        note=note,
    )


def ensure_provenanced(value: Any, *, context: str = "") -> None:
    """Guardrail: reject any bare numeric trying to reach a user un-sourced.

    The Provenance & Validation Middleware (see ``docs/ARCHITECTURE.md``) calls
    this on anything bound for the user. A raw ``int``/``float`` is exactly the
    shape a hallucinated figure takes, so it is refused: numbers must arrive as
    a :class:`ProvenancedValue` or be declared :class:`Unavailable`.
    """
    if isinstance(value, (ProvenancedValue, Unavailable)):
        return
    if isinstance(value, bool):
        return  # booleans are flags, not financial quantities
    if isinstance(value, (int, float)):
        where = f" ({context})" if context else ""
        raise IntegrityError(
            f"Un-sourced numeric {value!r}{where} cannot be shown to a user. "
            "Wrap it in a ProvenancedValue with a category, or return "
            "Unavailable — never present a bare number of unknown origin."
        )
    # Recurse into common containers so nested bare numerics are also caught.
    if isinstance(value, dict):
        for k, v in value.items():
            ensure_provenanced(v, context=f"{context}.{k}" if context else str(k))
        return
    if isinstance(value, (list, tuple, set)):
        for i, v in enumerate(value):
            ensure_provenanced(v, context=f"{context}[{i}]" if context else f"[{i}]")
        return
    # Strings and other non-numeric scalars are outside this guard's scope.
