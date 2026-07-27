# PAISAI

**PAISA + AI — Your AI Financial Operating System.**

The "AI" lives inside the word PAISA. That is not a marketing flourish; it is the
entire thesis. PAISAI exists to put disciplined artificial intelligence at the
core of personal wealth — not to make it flashier, but to make it **trustworthy**.

> **Mission:** Build the most trustworthy AI-powered personal finance platform ever
> created. Not the smartest. Not the flashiest. The most trustworthy.

---

## What PAISAI is

PAISAI feels less like a chatbot and more like sitting beside an exceptionally
disciplined financial mentor — one whose reasoning is always visible, whose
confidence is always calibrated, and whose advice is grounded in verifiable
evidence rather than persuasion.

Every conclusion the system produces is designed to be:

- **Transparent** — the reasoning is shown, never hidden.
- **Evidence-backed** — claims are tied to verifiable sources.
- **Explainable** — every number can be traced to how it was produced.
- **Auditable** — decisions and their rationale are recorded over time.
- **Educational** — every recommendation can teach you why it exists.
- **Conservative under uncertainty** — when we don't know, we say we don't know.

---

## The founding principles

PAISAI is built around six non-negotiable principles. They are documented in full
in [`docs/FOUNDING_PRINCIPLES.md`](docs/FOUNDING_PRINCIPLES.md).

1. **Truth over confidence.**
2. **Evidence over opinions.**
3. **Transparency over persuasion.**
4. **Education over prediction.**
5. **Long-term wealth over short-term excitement.**
6. **Honesty over completeness.**

If the system cannot answer something confidently, it must explicitly admit
uncertainty. If data is unavailable, it says so. If assumptions are made, it
displays every assumption. It never invents information to produce an answer.

---

## The documentation constitution

This branch establishes the foundation of PAISAI: the canonical documents that
govern every future feature, response, calculation, chart, and simulation.

| Document | Purpose |
| --- | --- |
| [`docs/FOUNDING_PRINCIPLES.md`](docs/FOUNDING_PRINCIPLES.md) | The six principles and what they obligate. |
| [`docs/DATA_INTEGRITY.md`](docs/DATA_INTEGRITY.md) | No-hallucination policy, data provenance categories, epistemic labels. |
| [`docs/AI_BEHAVIOR_CONTRACT.md`](docs/AI_BEHAVIOR_CONTRACT.md) | AI personality, communication style, the anatomy of every answer. |
| [`docs/MODULES.md`](docs/MODULES.md) | The eleven product modules and their responsibilities. |
| [`docs/DECISION_JOURNAL.md`](docs/DECISION_JOURNAL.md) | The signature feature: recording, reviewing, and scoring decisions. |
| [`docs/MARKET_INTELLIGENCE.md`](docs/MARKET_INTELLIGENCE.md) | Explaining market events, not just reporting them. |
| [`docs/DESIGN_LANGUAGE.md`](docs/DESIGN_LANGUAGE.md) | Bloomberg Terminal meets Apple — the visual and interaction system. |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Engineering stack, service topology, observability, testing. |
| [`docs/SECURITY.md`](docs/SECURITY.md) | Regulated-grade security and privacy requirements. |
| [`docs/prompts/SYSTEM_PROMPT.md`](docs/prompts/SYSTEM_PROMPT.md) | The operational system prompt that encodes the principles for the AI layer. |
| [`CLAUDE.md`](CLAUDE.md) | Binding guidance for any engineer or AI agent contributing code. |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | How changes are proposed, reviewed, and merged. |

---

## Product modules (at a glance)

1. **Dashboard** — net worth, cash flow, financial health, FI progress.
2. **Expense Intelligence** — categorisation, lifestyle-inflation and leakage detection.
3. **Investment Planner** — portfolios built from age, income, risk, tax and goals.
4. **Portfolio Analysis** — diversification, correlation, concentration, drawdown, valuation.
5. **Stock Analysis** — fundamentals, valuation, capital allocation, moat, macro context.
6. **Mutual Fund Analysis** — costs, rolling returns, tracking error, tax efficiency.
7. **Tax Planner** — country-specific, legal optimisation and scenario planning.
8. **Retirement Planning** — Monte Carlo simulation with probability of success.
9. **Financial Twin** — a living simulation of the user's financial life.
10. **Financial Education** — adaptive learning across finance and economics.
11. **AI Professor** — every recommendation is teachable at four depths.

Full detail in [`docs/MODULES.md`](docs/MODULES.md).

---

## Technology (intended)

- **Frontend:** Next.js, React, TypeScript, Tailwind CSS, shadcn/ui, Framer Motion.
- **Backend:** FastAPI, Python, PostgreSQL, Redis, a vector database, Celery, WebSockets.
- **Platform:** Docker, Kubernetes-ready, with logging, metrics, tracing and CI/CD.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full design.

---

## Project status

**Foundational, with the trust core in code.** This branch commits the founding
principles, the documentation constitution, and the first executable layer of the
backend: the integrity core and deterministic calculation engine that make "no
hallucination" and provenance *structural*.

- [`backend/`](backend) — the trust-enforcing core and API (tested: `97 passed`).
  See [`backend/README.md`](backend/README.md).
  - `paisai.integrity` — provenance categories, `ProvenancedValue` / `Unavailable`,
    the `ensure_provenanced()` guardrail that refuses un-sourced numerics, and the
    required anatomy of an `Answer`.
  - `paisai.engine` — deterministic financial math; provenance flows through every
    calculation, and undefined cases raise rather than return a misleading number.
  - `paisai.api` — FastAPI service with the **Provenance & Validation Middleware**
    that fails honest if any numeric would leave the server un-sourced; missing
    market data returns an explicit "unavailable" state, never a fabricated price.
  - `paisai.journal` — the **Decision Journal** signature feature: structured
    entries, thesis-vs-reality review that never guesses an unobserved outcome,
    and a transparent, process-based Decision Quality Score (judgement, not
    returns).
  - `paisai.persistence` — SQLAlchemy storage (SQLite for tests, Postgres in
    prod) with an **append-only, hash-chained audit log**: altering any past
    record breaks the chain, so tampering is *detectable*, not just discouraged.
  - `paisai.marketdata` — the **Market Data Gateway**: the single choke point
    through which all external prices/NAVs flow, tagged `Verified` with source and
    freshness. No vendor is bundled, so lookups are honestly `Unavailable` until a
    provider is wired (see [`docs/MARKET_DATA_GATEWAY.md`](docs/MARKET_DATA_GATEWAY.md));
    it fails honest on provider errors, never a fabricated figure.
- CI ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) — every change is
  gated by the backend integrity tests and the frontend production build.
- [`frontend/`](frontend) — the Next.js + TypeScript + Tailwind web client,
  Vercel-deployable, embodying the design language (production build verified).
  See [`frontend/README.md`](frontend/README.md). A **Dashboard** page (inputs →
  provenanced results) and a **Decision Journal** page are wired to the API;
  provenance chips make fact vs. forecast visible and missing data renders as an
  honest "No verified data."
- Run tooling — [`docker-compose.yml`](docker-compose.yml) (Postgres + API +
  frontend) and [`scripts/dev.sh`](scripts/dev.sh) for a no-Docker local run.

Every future module inherits these contracts. Nothing ships that violates them.

---

## Run the product locally

The backend and frontend run together as a working application. A user can enter
their figures and see a dashboard where **every value carries its provenance**,
record decisions in the **Decision Journal**, and verify the **audit chain** — and
anything requiring live market data renders as an honest "unavailable", never a
fabricated number.

**Option A — one command (Docker):**

```bash
docker compose up --build
# frontend → http://localhost:3000   API → http://localhost:8000
```

This brings up PostgreSQL, the FastAPI backend, and the Next.js frontend together;
the audit log and journal persist across restarts.

**Option B — no Docker (SQLite):**

```bash
./scripts/dev.sh          # starts backend (:8000) and frontend (:3000)
```

**Or run each side yourself:**

```bash
# backend
cd backend && pip install -e ".[api]" && uvicorn paisai.api.app:app --port 8000
# frontend (separate shell)
cd frontend && npm install && NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

Key endpoints: `POST /v1/dashboard`, `POST /v1/journal`, `GET /v1/journal/review-due`,
`GET /v1/audit/verify`, `GET /v1/market/quote` (honest "unavailable").

> The `Dockerfile`/`docker-compose.yml` are provided for one-command runs; they
> were not executed in the authoring environment (no Docker daemon there). The
> local path (`scripts/dev.sh` / `uvicorn` + `npm`) was verified end to end against
> a running backend.

---

## The one principle that governs all others

> If we don't know, we say we don't know.
> If we believe something, we explain exactly why.
> If we recommend something, we show the evidence, the risks, the alternatives,
> and the assumptions.

The defining feature of PAISAI is not intelligence. It is **trust**.
