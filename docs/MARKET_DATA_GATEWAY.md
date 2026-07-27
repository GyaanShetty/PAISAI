# Market Data Gateway

All market and reference data (prices, NAVs, fundamentals, macro) enters PAISAI
through **one** component: the Market Data Gateway. This is the structural
enforcement of the No-Hallucination Policy — the language model never sources a
number from memory; every figure is either `Verified` from a provider (with its
source and freshness) or an explicit `Unavailable`.

Code: [`backend/paisai/marketdata/`](../backend/paisai/marketdata).

---

## Behaviour

| Situation | Result |
| --- | --- |
| No provider configured (default) | `Unavailable` — honest "no verified data". |
| Provider returns a datum | `Verified` value carrying `source` and `as_of`. |
| Provider has no value for the id | `Unavailable`. |
| Provider raises an error | `Unavailable` — **fails honest**, never a guess. |

Results are cached for a short TTL (default 60s) to avoid hammering the provider;
a cached value keeps its original `as_of`.

**No vendor is bundled.** Out of the box every lookup is `Unavailable`. That is
correct: PAISAI would rather say "I don't have verified data for this" than show a
number it cannot source.

---

## Wiring a provider

1. Implement the `MarketDataProvider` protocol (three things: a `name`, a
   `get_quote(symbol)`, and a `get_nav(scheme_code)`), returning a `RawDatum` or
   `None`. Raise `MarketDataError` on failure — never return a stale or guessed
   value.

2. Register it once at startup:

   ```python
   from paisai.marketdata import configure_provider
   from myproject.providers import AcmeMarketData

   configure_provider(AcmeMarketData(api_key=os.environ["ACME_API_KEY"]))
   ```

   After this, `GET /v1/market/quote`, `/v1/stock/{symbol}`, and `/v1/fund/{code}`
   return `Verified` values sourced from your provider.

A ready-to-fill starting point lives at
[`backend/paisai/marketdata/example_http_provider.py`](../backend/paisai/marketdata/example_http_provider.py).
It is a **template**, not an active provider: fill in your vendor's request URL
and response mapping (verified against *their* documentation — do not assume a
shape), supply the API key via an environment variable, and register it.

---

## Why the gateway, and not "just call an API in the endpoint"

- **Single choke point for provenance.** Every external number gets tagged in one
  place, so it is impossible to accidentally surface an un-sourced figure.
- **Honest failure is centralised.** Absence and errors both become `Unavailable`
  here, so no endpoint has to remember to handle them.
- **The model stays out of the number-sourcing business.** It explains figures the
  gateway produced; it never supplies them.

See [`DATA_INTEGRITY.md`](DATA_INTEGRITY.md) and [`ARCHITECTURE.md`](ARCHITECTURE.md).
