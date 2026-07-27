"""Market Data Gateway: verified when a provider answers, honest otherwise."""

from datetime import datetime, timezone
from typing import Optional

import pytest

from paisai.integrity.provenance import Provenance, ProvenancedValue, Unavailable
from paisai.marketdata import (
    MarketDataError,
    MarketDataGateway,
    NullProvider,
    RawDatum,
)


class FakeProvider:
    name = "fake"

    def __init__(self, quote: Optional[RawDatum] = None, raise_on_quote: bool = False):
        self._quote = quote
        self._raise = raise_on_quote
        self.calls = 0

    def get_quote(self, symbol: str) -> Optional[RawDatum]:
        self.calls += 1
        if self._raise:
            raise MarketDataError("simulated upstream failure")
        return self._quote

    def get_nav(self, scheme_code: str) -> Optional[RawDatum]:
        return None


def _datum(value=100.0):
    return RawDatum(
        value=value, unit="INR", source="FakeExchange", as_of=datetime(2026, 1, 1, tzinfo=timezone.utc)
    )


# --- default (no provider) --------------------------------------------------


def test_null_provider_is_honest_unavailable():
    gw = MarketDataGateway(NullProvider())
    result = gw.quote("ACME")
    assert isinstance(result, Unavailable)
    assert "no verified data" in result.reason.lower()


def test_gateway_defaults_to_null_provider():
    gw = MarketDataGateway()
    assert gw.provider_name == "null"
    assert isinstance(gw.quote("ACME"), Unavailable)


# --- verified data ----------------------------------------------------------


def test_provider_datum_becomes_verified_value():
    gw = MarketDataGateway(FakeProvider(quote=_datum(2500.0)))
    result = gw.quote("RELIANCE")
    assert isinstance(result, ProvenancedValue)
    assert result.provenance is Provenance.VERIFIED
    assert result.value == 2500.0
    assert result.source == "FakeExchange"
    assert result.as_of is not None


def test_absent_datum_is_unavailable_not_zero():
    gw = MarketDataGateway(FakeProvider(quote=None))
    assert isinstance(gw.quote("UNKNOWN"), Unavailable)


# --- fail honest ------------------------------------------------------------


def test_provider_error_fails_honest():
    gw = MarketDataGateway(FakeProvider(raise_on_quote=True))
    result = gw.quote("ACME")
    assert isinstance(result, Unavailable)
    assert "could not return verified data" in result.reason.lower()


# --- caching ----------------------------------------------------------------


def test_results_are_cached_within_ttl():
    clock = {"t": 1000.0}
    provider = FakeProvider(quote=_datum())
    gw = MarketDataGateway(provider, cache_ttl_seconds=60, now=lambda: clock["t"])

    gw.quote("ACME")
    gw.quote("ACME")
    assert provider.calls == 1  # second call served from cache

    clock["t"] += 61  # advance past the TTL
    gw.quote("ACME")
    assert provider.calls == 2  # cache expired, provider queried again
