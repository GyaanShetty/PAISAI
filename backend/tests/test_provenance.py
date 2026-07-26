"""Provenance invariants: an ill-formed value must be impossible to construct."""

import pytest

from paisai.integrity.provenance import (
    IntegrityError,
    Provenance,
    ProvenancedValue,
    Unavailable,
    assumed,
    ensure_provenanced,
    unavailable,
    user_provided,
    verified,
)


def test_verified_requires_source():
    with pytest.raises(IntegrityError):
        ProvenancedValue(value=100.0, provenance=Provenance.VERIFIED)


def test_verified_with_source_is_ok():
    v = verified(1234.5, source="NSE feed", label="NIFTY", unit="INR")
    assert v.provenance is Provenance.VERIFIED
    assert v.source == "NSE feed"
    assert v.as_of is not None


def test_calculated_requires_inputs():
    with pytest.raises(IntegrityError):
        ProvenancedValue(value=0.1, provenance=Provenance.CALCULATED)


def test_estimated_and_projected_require_method():
    with pytest.raises(IntegrityError):
        ProvenancedValue(value=0.06, provenance=Provenance.ESTIMATED)
    with pytest.raises(IntegrityError):
        ProvenancedValue(value=0.06, provenance=Provenance.PROJECTED)


def test_assumed_requires_note():
    with pytest.raises(IntegrityError):
        ProvenancedValue(value=0.06, provenance=Provenance.ASSUMED)
    ok = assumed(0.06, note="No inflation figure supplied; assuming 6%.")
    assert ok.note


def test_bool_is_not_a_financial_value():
    with pytest.raises(IntegrityError):
        ProvenancedValue(value=True, provenance=Provenance.USER_PROVIDED)  # type: ignore[arg-type]


def test_user_provided_needs_no_extra_justification():
    v = user_provided(50000.0, label="Monthly income", unit="INR")
    assert v.provenance is Provenance.USER_PROVIDED


def test_value_is_immutable():
    v = user_provided(10.0)
    with pytest.raises(Exception):
        v.value = 20.0  # type: ignore[misc]


def test_forward_looking_flag():
    assert assumed(0.06, note="assume").is_forward_looking
    assert not verified(1.0, source="x").is_forward_looking


def test_to_dict_carries_provenance():
    v = verified(99.0, source="provider", label="Price", unit="INR")
    d = v.to_dict()
    assert d["provenance"] == "Verified"
    assert d["source"] == "provider"


def test_unavailable_is_the_honest_default():
    u = unavailable(label="Live P/E")
    assert isinstance(u, Unavailable)
    assert "don't have verified data" in u.reason.lower()
    assert u.to_dict()["available"] is False


# --- the guardrail: un-sourced numerics never reach a user ------------------


def test_ensure_provenanced_rejects_bare_number():
    with pytest.raises(IntegrityError):
        ensure_provenanced(42.0, context="pe_ratio")


def test_ensure_provenanced_accepts_provenanced_value():
    ensure_provenanced(verified(1.0, source="x"))  # must not raise


def test_ensure_provenanced_accepts_unavailable():
    ensure_provenanced(unavailable())  # must not raise


def test_ensure_provenanced_recurses_into_containers():
    payload = {
        "price": verified(100.0, source="feed"),
        "nested": {"pe": 25.0},  # a bare number hiding one level down
    }
    with pytest.raises(IntegrityError):
        ensure_provenanced(payload)


def test_ensure_provenanced_allows_clean_container():
    payload = {
        "price": verified(100.0, source="feed"),
        "pe": unavailable(label="P/E"),
        "name": "ACME",  # non-numeric scalars are outside the guard
    }
    ensure_provenanced(payload)  # must not raise
