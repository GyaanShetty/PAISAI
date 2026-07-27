"""AMFI NAV provider: deterministic parsing and honest failure, no network."""

import pytest

from paisai.marketdata.amfi import AmfiNavProvider, parse_navall
from paisai.marketdata.gateway import MarketDataGateway
from paisai.marketdata.provider import MarketDataError
from paisai.integrity.provenance import Provenance, ProvenancedValue, Unavailable

# A trimmed sample in the exact AMFI NAVAll.txt shape.
SAMPLE = """Scheme Code;ISIN Div Payout/ ISIN Growth;ISIN Div Reinvestment;Scheme Name;Net Asset Value;Date

Open Ended Schemes(Equity Scheme - Large Cap Fund)

Aditya Birla Sun Life Mutual Fund

119551;INF209K01UN8;INF209K01UO6;Some Large Cap Fund - Growth;745.6789;25-Jul-2026
119552;INF209K01AA1;-;Some Fund With NA NAV;N.A.;25-Jul-2026
120503;INF090I01JL2;-;Another Fund - Direct Growth;58.2345;25-Jul-2026
"""


def test_parse_extracts_valid_rows():
    table = parse_navall(SAMPLE)
    assert set(table) == {"119551", "120503"}  # header + N.A. row skipped
    d = table["119551"]
    assert d.value == 745.6789
    assert d.unit == "INR"
    assert "AMFI" in d.source
    assert d.as_of.year == 2026 and d.as_of.month == 7 and d.as_of.day == 25


def test_parse_skips_na_and_headers():
    table = parse_navall(SAMPLE)
    assert "119552" not in table  # "N.A." is never coerced to a number


def test_provider_get_nav_with_injected_feed():
    provider = AmfiNavProvider(fetch=lambda: SAMPLE)
    datum = provider.get_nav("120503")
    assert datum is not None and datum.value == 58.2345
    assert provider.get_nav("does-not-exist") is None
    # AMFI is funds, not equities.
    assert provider.get_quote("RELIANCE") is None


def test_provider_caches_feed():
    calls = {"n": 0}

    def fetch():
        calls["n"] += 1
        return SAMPLE

    provider = AmfiNavProvider(fetch=fetch, cache_ttl_seconds=3600, now=lambda: 0.0)
    provider.get_nav("119551")
    provider.get_nav("120503")
    assert calls["n"] == 1  # single fetch serves many lookups


def test_provider_fails_honest_on_fetch_error():
    def boom():
        raise MarketDataError("network down")

    provider = AmfiNavProvider(fetch=boom)
    with pytest.raises(MarketDataError):
        provider.get_nav("119551")


def test_empty_feed_is_refused_not_served_empty():
    provider = AmfiNavProvider(fetch=lambda: "garbage with no valid rows")
    with pytest.raises(MarketDataError):
        provider.get_nav("119551")


def test_through_gateway_yields_verified_nav():
    gw = MarketDataGateway(AmfiNavProvider(fetch=lambda: SAMPLE))
    result = gw.nav("119551")
    assert isinstance(result, ProvenancedValue)
    assert result.provenance is Provenance.VERIFIED
    assert result.value == 745.6789
    assert "AMFI" in (result.source or "")
    # A missing scheme is honestly unavailable.
    assert isinstance(gw.nav("000000"), Unavailable)
