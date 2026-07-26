# Contributing to PAISAI

Thank you for helping build the most trustworthy AI-powered personal finance
platform. Contributions are welcome — but PAISAI holds a higher bar than most
projects, because a mistake here can misdirect someone's money.

Before anything else, read:

1. [`docs/FOUNDING_PRINCIPLES.md`](docs/FOUNDING_PRINCIPLES.md) — the six
   non-negotiable principles.
2. [`docs/DATA_INTEGRITY.md`](docs/DATA_INTEGRITY.md) — the no-hallucination policy
   and provenance model.
3. [`CLAUDE.md`](CLAUDE.md) — the engineering constraints and definition of done.

---

## Principles come first

Every contribution is evaluated against the founding principles before it is
evaluated for cleverness or polish. A feature that is elegant but violates
"truth over confidence" or the no-hallucination policy will be rejected.

The single governing rule:

> If we don't know, we say we don't know. If we believe something, we explain
> exactly why. If we recommend something, we show the evidence, the risks, the
> alternatives, and the assumptions.

---

## Workflow

1. **Branch** from the default branch for your change.
2. **Read the relevant `docs/` file** for the subsystem you're touching. The docs
   are the spec.
3. **Implement**, honouring the constraints in [`CLAUDE.md`](CLAUDE.md).
4. **Test** — include tests for numeric correctness and data-integrity behaviour
   (provenance tagging, rejection of un-sourced numerics).
5. **Update docs** where behaviour changed. If you change AI behaviour, update both
   [`docs/AI_BEHAVIOR_CONTRACT.md`](docs/AI_BEHAVIOR_CONTRACT.md) and
   [`docs/prompts/SYSTEM_PROMPT.md`](docs/prompts/SYSTEM_PROMPT.md).
6. **Open a PR** describing what changed and, explicitly, **how it upholds the
   founding principles.**

---

## Pull request expectations

A good PR for PAISAI answers:

- What does this change, and why?
- Does it display any values? If so, what provenance category does each carry?
- Could any number reach the user without a source? How is that prevented?
- What happens when data is unavailable — does it fail honest?
- What did you test, and what are the limitations of that testing?

Honesty about limitations in your PR is not a weakness — it is exactly the
discipline the product is built on. State what you're unsure about.

---

## Reporting security issues

Security issues should be reported privately to the maintainers, not in public
issues. See [`docs/SECURITY.md`](docs/SECURITY.md) for the security posture the
project holds itself to.
