"""A real market-data provider: AMFI daily mutual-fund NAVs (India).

AMFI (the Association of Mutual Funds in India) publishes the official daily NAV
of every Indian mutual-fund scheme as a public, authoritative, keyless feed. That
makes it a legitimate `Verified` source under the No-Hallucination Policy — no
number is invented; each NAV comes straight from AMFI with the date AMFI reported
it.

This provider only answers `get_nav` (AMFI is funds, not equities); `get_quote`
returns ``None`` so the gateway renders equities as honestly unavailable.

Parsing is a pure function (:func:`parse_navall`) so it can be tested against a
fixture with no network. The provider caches the whole feed briefly (it is one
large document) and **fails honest** — any fetch/parse failure raises
:class:`MarketDataError`, which the gateway turns into an Unavailable, never a
guess.
"""

from __future__ import annotations

import time
import urllib.request
from datetime import datetime, timezone
from typing import Callable, Optional

from .provider import MarketDataError, RawDatum

AMFI_NAV_URL = "https://www.amfiindia.com/spages/NAVAll.txt"

# Feed columns are semicolon-delimited:
#   Scheme Code;ISIN Div Payout/ISIN Growth;ISIN Div Reinvestment;Scheme Name;NAV;Date
_MIN_COLS = 6
_SOURCE = "AMFI (amfiindia.com)"


def parse_navall(text: str) -> dict[str, RawDatum]:
    """Parse the AMFI NAVAll feed into ``{scheme_code: RawDatum}``.

    Header lines, category/AMC section headers, and rows whose NAV is not a
    number (e.g. "N.A.") are skipped — never coerced into a fabricated value.
    """
    table: dict[str, RawDatum] = {}
    for line in text.splitlines():
        parts = line.split(";")
        if len(parts) < _MIN_COLS:
            continue
        code = parts[0].strip()
        if not code.isdigit():  # skips the header row and section titles
            continue
        nav_str = parts[4].strip()
        date_str = parts[5].strip()
        try:
            nav = float(nav_str)
        except ValueError:
            continue  # "N.A." or blank — honestly omitted
        try:
            as_of = datetime.strptime(date_str, "%d-%b-%Y").replace(tzinfo=timezone.utc)
        except ValueError:
            continue  # unparseable date — omit rather than guess
        table[code] = RawDatum(value=nav, unit="INR", source=_SOURCE, as_of=as_of)
    return table


class AmfiNavProvider:
    """Serves verified mutual-fund NAVs from the AMFI public feed."""

    name = "amfi"

    def __init__(
        self,
        *,
        url: str = AMFI_NAV_URL,
        cache_ttl_seconds: float = 3600.0,
        timeout: float = 30.0,
        now: Callable[[], float] = time.monotonic,
        fetch: Optional[Callable[[], str]] = None,
    ) -> None:
        self._url = url
        self._ttl = cache_ttl_seconds
        self._timeout = timeout
        self._now = now
        self._fetch = fetch or self._http_fetch
        self._table: Optional[dict[str, RawDatum]] = None
        self._expiry = 0.0

    def get_quote(self, symbol: str) -> Optional[RawDatum]:
        # AMFI is a mutual-fund source, not an equities feed.
        return None

    def get_nav(self, scheme_code: str) -> Optional[RawDatum]:
        return self._get_table().get(scheme_code.strip())

    # ------------------------------------------------------------------ #
    def _get_table(self) -> dict[str, RawDatum]:
        if self._table is not None and self._expiry > self._now():
            return self._table
        text = self._fetch()
        table = parse_navall(text)
        if not table:
            raise MarketDataError(
                "AMFI feed parsed to zero schemes — the format may have changed; "
                "refusing to serve an empty/again-guessed table."
            )
        self._table = table
        self._expiry = self._now() + self._ttl
        return table

    def _http_fetch(self) -> str:
        req = urllib.request.Request(
            self._url, headers={"Accept": "text/plain", "User-Agent": "PAISAI/0.1"}
        )
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as exc:  # network/HTTP/decoding
            raise MarketDataError(f"Could not fetch the AMFI NAV feed: {exc}") from exc
