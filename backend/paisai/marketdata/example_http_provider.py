"""A TEMPLATE HTTP market-data provider — not active by default.

This shows the shape of a real vendor adapter. It is intentionally **not**
registered and **not** imported anywhere: PAISAI must not ship a provider that
claims to return verified data against an API contract nobody has verified.

To turn it into a working provider:

1. Set ``base_url`` and the request path/params to match *your* vendor's API,
   confirmed against their official documentation.
2. Map the vendor's JSON response to a :class:`RawDatum` in ``_parse_*`` — in
   particular, extract the correct price/NAV field, the currency/unit, and the
   timestamp the vendor reports (``as_of``). Do not assume field names.
3. Provide the API key via an environment variable (never hardcode a secret).
4. Register it at startup::

       from paisai.marketdata import configure_provider
       configure_provider(ExampleHttpProvider(api_key=os.environ["MY_API_KEY"]))

Until every ``TODO`` below is resolved for a real vendor, this provider raises so
that it can never silently return an unverified number.
"""

from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timezone
from typing import Any, Optional

from .provider import MarketDataError, RawDatum


class ExampleHttpProvider:
    """Skeleton for an HTTP JSON market-data vendor. Fill in the TODOs."""

    name = "example-http"

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: str = "https://api.example-vendor.invalid",
        timeout: float = 5.0,
    ) -> None:
        self._api_key = api_key or os.environ.get("PAISAI_MARKETDATA_API_KEY")
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        if not self._api_key:
            raise MarketDataError(
                "No API key configured for ExampleHttpProvider. Set one before "
                "registering this provider — an unauthenticated data source is "
                "not a verified source."
            )

    # ------------------------------------------------------------------ #
    def get_quote(self, symbol: str) -> Optional[RawDatum]:
        raise MarketDataError(
            "ExampleHttpProvider is a template. Implement get_quote against your "
            "vendor's API and map the response in _parse_quote before use."
        )
        # Reference implementation once the vendor specifics are filled in:
        # data = self._get(f"/quote?symbol={symbol}&apikey={self._api_key}")
        # return self._parse_quote(data)

    def get_nav(self, scheme_code: str) -> Optional[RawDatum]:
        raise MarketDataError(
            "ExampleHttpProvider is a template. Implement get_nav against your "
            "vendor's API and map the response in _parse_nav before use."
        )

    # ------------------------------------------------------------------ #
    def _get(self, path: str) -> Any:
        url = f"{self._base_url}{path}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # network, decode, HTTP error
            raise MarketDataError(f"Request to {self._base_url} failed: {exc}") from exc

    def _parse_quote(self, data: Any) -> Optional[RawDatum]:
        # TODO: map to your vendor's fields. Example placeholder shape:
        #   return RawDatum(
        #       value=float(data["price"]),
        #       unit=data.get("currency", "INR"),
        #       source=self.name,
        #       as_of=datetime.fromisoformat(data["as_of"]),
        #   )
        raise MarketDataError("_parse_quote not implemented for a real vendor yet.")

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)
