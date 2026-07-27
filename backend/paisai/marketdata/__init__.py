"""The Market Data Gateway.

All market and reference data (prices, NAVs, fundamentals) must flow through this
single gateway — never from a language model's memory (see
``docs/ARCHITECTURE.md`` and ``docs/DATA_INTEGRITY.md``). The gateway:

- attaches **provenance** to every value it returns (``Verified`` with a source and
  an ``as_of`` timestamp), and
- returns an explicit **Unavailable** — never a fabricated figure — when no
  provider is configured or a provider cannot answer, and
- **fails honest**: if a provider errors, the result is Unavailable, not a guess.

No specific data vendor is bundled. Wire one by implementing
:class:`MarketDataProvider` and calling :func:`configure_provider`; until then
every lookup is honestly Unavailable.
"""

from .provider import (
    MarketDataError,
    MarketDataProvider,
    NullProvider,
    RawDatum,
)
from .gateway import MarketDataGateway, configure_provider, get_gateway
from .amfi import AmfiNavProvider

__all__ = [
    "RawDatum",
    "MarketDataProvider",
    "NullProvider",
    "MarketDataError",
    "MarketDataGateway",
    "configure_provider",
    "get_gateway",
    "AmfiNavProvider",
]

