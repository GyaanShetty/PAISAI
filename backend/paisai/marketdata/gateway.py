"""The gateway: provenance, caching, and honest failure around a provider."""

from __future__ import annotations

import time
from typing import Callable, Optional

from ..integrity.provenance import Provenance, ProvenancedValue, Unavailable, unavailable
from .provider import MarketDataError, MarketDataProvider, NullProvider, RawDatum

Result = ProvenancedValue | Unavailable


class MarketDataGateway:
    """Wraps a provider with provenance tagging, TTL caching, and honest failure.

    - A datum from the provider becomes a ``Verified`` value carrying the source
      and ``as_of``.
    - Absence (``None``) becomes an honest Unavailable.
    - A provider error becomes an honest Unavailable — never a fabricated value.
    - Results are cached briefly (``cache_ttl_seconds``) to avoid hammering the
      provider; the cached value keeps its original ``as_of``.
    """

    def __init__(
        self,
        provider: Optional[MarketDataProvider] = None,
        *,
        cache_ttl_seconds: float = 60.0,
        now: Callable[[], float] = time.monotonic,
    ) -> None:
        self._provider: MarketDataProvider = provider or NullProvider()
        self._ttl = cache_ttl_seconds
        self._now = now
        self._cache: dict[tuple[str, str], tuple[float, ProvenancedValue]] = {}

    @property
    def provider_name(self) -> str:
        return self._provider.name

    def quote(self, symbol: str) -> Result:
        return self._lookup("quote", symbol, self._provider.get_quote, f"Live quote for {symbol}")

    def nav(self, scheme_code: str) -> Result:
        return self._lookup("nav", scheme_code, self._provider.get_nav, f"NAV for {scheme_code}")

    # ------------------------------------------------------------------ #
    def _lookup(
        self,
        kind: str,
        key: str,
        fetch: Callable[[str], Optional[RawDatum]],
        label: str,
    ) -> Result:
        cache_key = (kind, key)
        cached = self._cache.get(cache_key)
        if cached is not None and cached[0] > self._now():
            return cached[1]

        try:
            datum = fetch(key)
        except MarketDataError as exc:
            # Fail honest: a provider error is not a reason to invent a number.
            return unavailable(
                label=label,
                reason=(
                    f"The market-data provider ({self._provider.name}) could not "
                    f"return verified data: {exc}"
                ),
            )

        if datum is None:
            return unavailable(
                label=label,
                reason=(
                    "No verified data is available for this from the configured "
                    f"provider ({self._provider.name})."
                ),
            )

        value = ProvenancedValue(
            value=datum.value,
            provenance=Provenance.VERIFIED,
            label=label,
            unit=datum.unit,
            source=datum.source,
            as_of=datum.as_of,
        )
        self._cache[cache_key] = (self._now() + self._ttl, value)
        return value


# --------------------------------------------------------------------------- #
# Configuration — no vendor is bundled; wire one here.
# --------------------------------------------------------------------------- #
_configured_provider: Optional[MarketDataProvider] = None


def configure_provider(provider: Optional[MarketDataProvider]) -> None:
    """Register the process-wide market-data provider (or ``None`` to clear it).

    A deployment wires its vendor adapter here at startup — typically reading an
    API key from the environment. Until this is called, the gateway uses the
    NullProvider and every lookup is honestly Unavailable.
    """
    global _configured_provider
    _configured_provider = provider


def get_gateway(**kwargs) -> MarketDataGateway:
    """Build a gateway around the configured provider (NullProvider if none)."""
    return MarketDataGateway(_configured_provider, **kwargs)
