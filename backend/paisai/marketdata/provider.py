"""The market-data provider contract.

A provider is the *only* place a real, external number enters PAISAI. Its job is
narrow: given an identifier, return the verified datum from an authoritative
source — or ``None`` if it genuinely does not have it. It never invents a value.

The gateway (not the provider) is responsible for turning a :class:`RawDatum` into
a provenanced value and for handling absence and errors honestly. Keeping the
provider dumb makes vendor adapters small and easy to audit.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Protocol, runtime_checkable


class MarketDataError(Exception):
    """A provider failed to fulfil a request (network, auth, bad response).

    The gateway catches this and returns an honest Unavailable — it must never be
    swallowed into a fabricated number.
    """


@dataclass(frozen=True)
class RawDatum:
    """A single verified datum from an authoritative source.

    ``as_of`` is when the source reported it — carried through so the user can see
    how fresh a Verified value is.
    """

    value: float
    unit: str
    source: str
    as_of: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.value, (int, float)) or isinstance(self.value, bool):
            raise MarketDataError(f"RawDatum.value must be numeric, got {self.value!r}")
        if not self.source:
            raise MarketDataError(
                "RawDatum must name its source — an unsourced datum is not verified."
            )


@runtime_checkable
class MarketDataProvider(Protocol):
    """The interface a data vendor adapter implements.

    Return the datum, or ``None`` when the provider legitimately has no value for
    the identifier. Raise :class:`MarketDataError` on failure — do not return a
    stale or guessed value.
    """

    name: str

    def get_quote(self, symbol: str) -> Optional[RawDatum]:
        """Latest price for an equity/index ``symbol``."""
        ...

    def get_nav(self, scheme_code: str) -> Optional[RawDatum]:
        """Latest NAV for a mutual-fund ``scheme_code``."""
        ...


class NullProvider:
    """The default provider: it has no data, and says so.

    With no vendor configured, every lookup returns ``None`` and the gateway
    renders an honest Unavailable. This is the correct behaviour of the system
    before a real provider (and its credentials) are wired in.
    """

    name = "null"

    def get_quote(self, symbol: str) -> Optional[RawDatum]:
        return None

    def get_nav(self, scheme_code: str) -> Optional[RawDatum]:
        return None
