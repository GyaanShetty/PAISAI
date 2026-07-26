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

- [`backend/`](backend) — the trust-enforcing core (standard-library only, fully
  tested: `41 passed`). See [`backend/README.md`](backend/README.md).
  - `paisai.integrity` — provenance categories, `ProvenancedValue` / `Unavailable`,
    the `ensure_provenanced()` guardrail that refuses un-sourced numerics, and the
    required anatomy of an `Answer`.
  - `paisai.engine` — deterministic financial math; provenance flows through every
    calculation, and undefined cases raise rather than return a misleading number.
- [`frontend/`](frontend) — the Next.js + TypeScript + Tailwind web client,
  Vercel-deployable, embodying the design language (production build verified).
  See [`frontend/README.md`](frontend/README.md). Provenance chips make fact vs.
  forecast visible; missing data renders as an honest "No verified data."

Every future module inherits these contracts. Nothing ships that violates them.

---

## The one principle that governs all others

> If we don't know, we say we don't know.
> If we believe something, we explain exactly why.
> If we recommend something, we show the evidence, the risks, the alternatives,
> and the assumptions.

The defining feature of PAISAI is not intelligence. It is **trust**.
