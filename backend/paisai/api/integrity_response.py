"""Serialized-form enforcement of the no-hallucination policy.

The in-process guardrail (:func:`paisai.integrity.ensure_provenanced`) protects
Python objects. But by the time a response is JSON, provenanced values have been
flattened to ``{"value": 100.0, "provenance": "Verified", ...}``. This module
enforces the same policy on that serialized shape:

    **Every *financial* numeric leaf in a response must be the ``value`` of a dict
    that also carries a ``provenance`` tag. Any other bare number is a policy
    violation.**

The policy is about the numbers that inform financial decisions — prices, NAVs,
ratios, projections. A response also carries *structural metadata* that is plainly
not a financial quantity: how many records were returned, an audit sequence
number, a page index. Those live under an explicit, small allowlist of keys
(:data:`STRUCTURAL_KEYS`). A field carrying money or a rate must never be named
one of those — the allowlist is deliberately kept to unambiguous metadata names
(note that "total", which is often a financial sum, is intentionally *not* in it).

This is what lets the middleware refuse — at the very last moment before bytes
leave the server — a response that would show a user a financial number of unknown
origin.
"""

from __future__ import annotations

from typing import Any

# Keys permitted to carry a bare integer because they are structural metadata,
# never a financial quantity. Kept intentionally small and unambiguous.
STRUCTURAL_KEYS = frozenset(
    {
        "count",
        "records_checked",
        "seq",
        "page",
        "per_page",
        "limit",
        "offset",
        "index",
    }
)


def find_unprovenanced_numbers(
    node: Any,
    path: str = "$",
    *,
    _key: str | None = None,
) -> list[str]:
    """Return JSON paths of every financial numeric not shielded by provenance.

    A number is legal when it is either (a) the ``value`` field of a dict that
    also has a ``provenance`` key (the serialized form of a ``ProvenancedValue``),
    or (b) the value of a key in :data:`STRUCTURAL_KEYS` (structural metadata).
    Booleans are flags, not quantities, and are ignored.
    """
    offenders: list[str] = []

    if isinstance(node, bool):
        return offenders
    if isinstance(node, (int, float)):
        if _key in STRUCTURAL_KEYS:
            return offenders  # structural metadata, not a financial quantity
        offenders.append(path)
        return offenders
    if isinstance(node, dict):
        has_provenance = "provenance" in node and bool(node["provenance"])
        for key, value in node.items():
            if (
                key == "value"
                and isinstance(value, (int, float))
                and not isinstance(value, bool)
                and has_provenance
            ):
                continue  # a legitimately provenanced value
            offenders.extend(
                find_unprovenanced_numbers(value, f"{path}.{key}", _key=key)
            )
        return offenders
    if isinstance(node, (list, tuple)):
        for i, value in enumerate(node):
            # List elements inherit no structural exemption from their key.
            offenders.extend(find_unprovenanced_numbers(value, f"{path}[{i}]"))
        return offenders
    # Strings, None, and other non-numeric scalars are outside this policy.
    return offenders


def assert_response_provenanced(payload: Any) -> None:
    """Raise ``ValueError`` if any financial numeric in ``payload`` lacks provenance."""
    offenders = find_unprovenanced_numbers(payload)
    if offenders:
        raise ValueError(
            "Response contains un-sourced numeric(s) at: "
            + ", ".join(offenders)
            + ". Every financial number shown to a user must carry a provenance "
            "category, or be returned as an explicit 'unavailable' state."
        )
