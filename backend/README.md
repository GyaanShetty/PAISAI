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
│   └── engine/
│       └── calculations.py # deterministic math; provenance flows through it
├── tests/                  # 41 tests covering the invariants above
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

## Run it

```bash
cd backend

# Tests (installs nothing beyond pytest)
python -m pip install pytest
python -m pytest

# The demo
PYTHONPATH=. python examples/demo.py
```

Expected: `41 passed`, and a demo that shows provenance flowing through
calculations, an un-sourced number being refused, and missing data admitted
rather than invented.
