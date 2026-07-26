# PAISAI Backend

The trust-enforcing core of PAISAI. This package turns the founding principles
(see the repository [`docs/`](../docs)) into code: provenance is a type, the
no-hallucination policy is a guardrail, and financial math is deterministic and
auditable.

> The integrity core and calculation engine depend only on the Python standard
> library, so they run and test anywhere. API/runtime dependencies (FastAPI,
> Postgres, Redis, Celery, …) are layered on as those services are built — see
> [`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md).

## Layout

```
backend/
├── paisai/
│   ├── integrity/          # the enforcement layer
│   │   ├── provenance.py   # Provenance categories, ProvenancedValue, Unavailable,
│   │   │                   #   ensure_provenanced() — rejects un-sourced numerics
│   │   └── epistemics.py   # EpistemicLabel, Confidence, Answer, InvestmentRecommendation
│   ├── engine/
│   │   └── calculations.py # deterministic math; provenance flows through it
│   ├── api/                # FastAPI service layer
│   │   ├── app.py          # endpoints + Provenance & Validation Middleware
│   │   └── integrity_response.py  # serialized-form no-hallucination guard
│   ├── journal/            # the Decision Journal (models, review, quality score)
│   └── persistence/        # SQLAlchemy storage
│       ├── db.py           # engine/session (SQLite for tests, Postgres in prod)
│       ├── audit.py        # append-only, hash-chained, tamper-evident audit log
│       └── journal_repository.py  # entry storage; audits every write
├── tests/                  # 72 tests covering the invariants above
├── examples/demo.py        # runnable tour of the core
└── pyproject.toml
```

## What the core guarantees

- **No number without an origin.** A value is either a `ProvenancedValue` tagged
  with one of six categories (Verified / Calculated / Estimated / Projected /
  User Provided / Assumed) or an explicit `Unavailable`. You cannot construct a
  `Verified` value without a source, or a `Calculated` value without recording
  its inputs.
- **Un-sourced numerics are refused.** `ensure_provenanced()` — the
  Provenance & Validation Middleware in miniature — raises on any bare number
  bound for a user, recursing into dicts and lists so nothing hides.
- **Math, not memory.** Calculations take provenanced inputs and return
  `Calculated` results that record those inputs, so every figure is reproducible.
  Undefined cases raise instead of returning a misleading zero.
- **Answers keep their anatomy.** A substantive `Answer` must carry evidence,
  reasoning, assumptions, risks, and limitations, with a calibrated confidence.
  "I can't answer" is valid — but only when it states the limitation and marks
  confidence `Insufficient`.

## The API layer

`paisai.api` exposes the core over HTTP (FastAPI) and enforces the
no-hallucination policy at the boundary:

- Endpoints translate user input into provenanced values and delegate the
  arithmetic to the tested engine; results are returned with provenance intact.
- **Provenance & Validation Middleware** inspects every `/v1/…` JSON response and
  refuses (fails honest with a 500) if any numeric escapes without a provenance
  envelope — the serialized-form guard in `integrity_response.py`.
- `GET /v1/market/quote` has no data provider wired in this build, so it returns
  an explicit *unavailable* state rather than a fabricated price.

## Run it

```bash
cd backend

# Full suite (integrity core + engine + API)
python -m pip install -e ".[dev]"
python -m pytest                      # -> 72 passed

# The core-only demo (standard library, no install needed)
PYTHONPATH=. python examples/demo.py

# The API
python -m pip install -e ".[api]"
uvicorn paisai.api.app:app --reload   # http://127.0.0.1:8000/health
#   POST /v1/calc/savings-rate   {"income": 100000, "expenses": 70000}
#   POST /v1/calc/cagr           {"begin_value": 100, "end_value": 200, "years": 10}
#   POST /v1/calc/portfolio-weights  {"holdings": {"Equity": 600000, "Debt": 400000}}
#   GET  /v1/market/quote?symbol=ACME   -> honest "unavailable"
```

Expected: `72 passed`, a demo that shows provenance flowing through calculations
(an un-sourced number refused, missing data admitted rather than invented), and an
API that returns provenanced figures — or an honest 500 if anything tries to leak
a bare number.
