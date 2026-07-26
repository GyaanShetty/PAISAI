# CLAUDE.md — Guidance for Engineers and AI Agents

This file governs how anyone — human or AI — contributes code to PAISAI. It exists
because PAISAI's value is **trust**, and trust is destroyed one careless line at a
time. Read the [founding principles](docs/FOUNDING_PRINCIPLES.md) before writing
code. They are not decoration; they are acceptance criteria.

---

## The one rule above all others

> If we don't know, we say we don't know. If we believe something, we explain
> exactly why. If we recommend something, we show the evidence, the risks, the
> alternatives, and the assumptions.

Any code, copy, chart, or model output that violates this does not ship, no matter
how polished it is otherwise.

---

## Non-negotiable engineering constraints

1. **Never fabricate financial data — in code or in output.**
   Prices, NAVs, returns, ratios, macro stats, regulations, and fundamentals come
   from the Market Data Gateway. Never hardcode a "reasonable" number, never let
   the model supply one from memory, never seed a demo with invented figures
   presented as real. When data is missing, render an honest "unavailable" state.
   See [`docs/DATA_INTEGRITY.md`](docs/DATA_INTEGRITY.md).

2. **Every displayed value carries exactly one provenance category.**
   Verified / Calculated / Estimated / Projected / User Provided / Assumed. If you
   add a field to the UI or an API response that shows a number, it carries its
   category. No exceptions.

3. **Deterministic math lives in the Calculation Engine, not in prose.**
   Numbers are produced or validated by tested code, so they are reproducible and
   auditable. The model explains; it does not compute figures freehand.

4. **Un-sourced numerics are rejected before the user sees them.**
   Respect the Provenance & Validation Middleware. Do not route around it. Tests
   must assert that un-sourced numerics are caught.

5. **Answers keep their anatomy.**
   Where the product surfaces AI reasoning, preserve evidence, assumptions, risks,
   alternatives, limitations, and confidence. Do not strip these for a "cleaner"
   UI — expose/collapse them, never delete them.

6. **No persuasion patterns.**
   No manufactured urgency, no engagement bait, no colour or copy designed to push
   a transaction. The interface informs; it does not sell.

7. **Security is a precondition, not a phase.**
   Follow [`docs/SECURITY.md`](docs/SECURITY.md). Never commit secrets. Validate
   input at every boundary. Fail honest, not silent.

---

## Working in this repository

- **Read the relevant `docs/` file before touching a subsystem.** The docs are the
  spec; the code implements them. If code and docs disagree, that is a bug in one
  of them — reconcile it, don't ignore it.
- **Keep the system prompt and the behaviour docs in sync.**
  [`docs/prompts/SYSTEM_PROMPT.md`](docs/prompts/SYSTEM_PROMPT.md) is the
  executable form of [`docs/AI_BEHAVIOR_CONTRACT.md`](docs/AI_BEHAVIOR_CONTRACT.md).
  A change to one is a change to both.
- **Tests are part of the change**, especially for anything numeric or
  data-integrity related. Golden/property tests for the Calculation Engine;
  contract tests for provenance and un-sourced-numeric rejection.
- **When uncertain about scope or a financial method, state the uncertainty** in
  the PR and ask — do not paper over it. The same honesty we demand of the product
  applies to how we build it.

---

## Definition of done for a feature

A feature is done when:

- [ ] Every value it displays has a provenance category.
- [ ] No number originates from model memory or a hardcoded guess.
- [ ] Missing data renders an honest "unavailable" state, not a fallback figure.
- [ ] AI output preserves evidence / assumptions / risks / alternatives / limits / confidence.
- [ ] There are no persuasion patterns.
- [ ] Security requirements in [`docs/SECURITY.md`](docs/SECURITY.md) are met.
- [ ] Tests cover the numeric and data-integrity behaviour.
- [ ] Docs are updated where behaviour changed.

Build for the user who will trust PAISAI with their financial life. Earn it every
commit.
