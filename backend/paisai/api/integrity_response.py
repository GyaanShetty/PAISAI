"""Serialized-form enforcement of the no-hallucination policy.

The in-process guardrail (:func:`paisai.integrity.ensure_provenanced`) protects
Python objects. But by the time a response is JSON, provenanced values have been
flattened to ``{"value": 100.0, "provenance": "Verified", ...}``. This module
enforces the same policy on that serialized shape:

    **Every numeric leaf in a response must be the ``value`` of a dict that also
    carries a ``provenance`` tag. Any other bare number is a policy violation.**

This is what lets the middleware refuse — at the very last moment before bytes
leave the server — a response that would show a user a number of unknown origin.
"""

from __future__ import annotations

from typing import Any


def find_unprovenanced_numbers(node: Any, path: str = "$") -> list[str]:
    """Return JSON paths of every numeric not shielded by a provenance envelope.

    A number is legal only when it is the ``value`` field of a dict that also has
    a ``provenance`` key (the serialized form of a ``ProvenancedValue``). Booleans
    are flags, not financial quantities, and are ignored.
    """
    offenders: list[str] = []

    if isinstance(node, bool):
        return offenders
    if isinstance(node, (int, float)):
        # Reached a bare number directly — its parent did not shield it.
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
            offenders.extend(find_unprovenanced_numbers(value, f"{path}.{key}"))
        return offenders
    if isinstance(node, (list, tuple)):
        for i, value in enumerate(node):
            offenders.extend(find_unprovenanced_numbers(value, f"{path}[{i}]"))
        return offenders
    # Strings, None, and other non-numeric scalars are outside this policy.
    return offenders


def assert_response_provenanced(payload: Any) -> None:
    """Raise ``ValueError`` if any numeric in ``payload`` lacks provenance."""
    offenders = find_unprovenanced_numbers(payload)
    if offenders:
        raise ValueError(
            "Response contains un-sourced numeric(s) at: "
            + ", ".join(offenders)
            + ". Every number shown to a user must carry a provenance category, "
            "or be returned as an explicit 'unavailable' state."
        )
