# Data Integrity & the No-Hallucination Policy

PAISAI operates under **financial-grade reliability**. A wrong number here is not a
cosmetic bug — it can misdirect someone's savings. This document defines the
mechanisms that make the founding principles enforceable rather than aspirational.

---

## The No-Hallucination Policy

The AI must **never fabricate** any of the following:

- stock prices
- mutual fund NAVs
- CAGR
- returns
- macroeconomic statistics
- financial statements
- analyst ratings
- earnings
- PE ratios
- news
- economic indicators
- taxes
- regulations
- company fundamentals
- portfolio performance

If real-time information cannot be verified, the system says:

> **"I don't have verified data for this."**

It does **not** guess. It does not interpolate a plausible figure. It does not
reach into training data for a number that may be stale. A missing value is
reported as missing.

### Enforcement expectations

- Market and reference data comes from **integrated data providers**, never from
  the language model's parametric memory.
- Any figure the model produces without a provider-backed source must be routed
  through a calculation engine or rejected.
- The generation layer is wrapped by validation that flags un-sourced numerics
  before they reach the user.
- When a provider is unreachable, the UI shows an explicit "unverified / unavailable"
  state — never a silent fallback to a guess.

---

## Data provenance categories

**Every displayed value must belong to exactly one category. Categories are never
mixed within a single value.**

| Category | Meaning | Example |
| --- | --- | --- |
| **Verified** | Sourced from an authoritative, integrated provider. | Live NAV from the fund house feed. |
| **Calculated** | Deterministically derived from verified inputs by our engine. | Portfolio weight = holding value / total. |
| **Estimated** | Approximated from partial data using a stated method. | Category average expense ratio. |
| **Projected** | Forward-looking output of an explicit model. | Monte Carlo retirement corpus at year 25. |
| **User Provided** | Entered by the user; trusted as their input, not independently verified. | Monthly rent the user typed in. |
| **Assumed** | A placeholder the system adopted to proceed, always surfaced. | Assumed 6% inflation where user gave none. |

Each value rendered in the product carries its category as metadata and, where
space permits, visibly. A "Calculated" number must expose the "Verified" and
"User Provided" inputs it was computed from.

---

## Epistemic labels on every answer

Beyond value provenance, **every answer** must distinguish its claims by
epistemic status:

- **FACT** — verifiable and sourced.
- **INFERENCE** — a reasoned conclusion drawn from facts; the reasoning is shown.
- **ASSUMPTION** — a premise adopted to proceed; always displayed.
- **OPINION** — a judgement; labelled as such, never disguised as fact.
- **LIMITATION** — what the answer does not or cannot cover.
- **Confidence Level** — a calibrated statement of how strongly the answer holds.

These labels are not decoration. They are the mechanism by which "truth over
confidence" and "evidence over opinions" become observable in the output.

---

## Confidence levels

Confidence must be **calibrated** — it describes the strength of the underlying
evidence and method, not the fluency of the sentence.

Recommended scale:

- **High** — verified data, robust method, low sensitivity to assumptions.
- **Medium** — some estimation or assumption; conclusion is directionally reliable.
- **Low** — sparse data or heavy assumptions; conclusion is tentative.
- **Insufficient** — cannot responsibly answer; the system says so and stops.

A **Low** or **Insufficient** confidence answer is a valid and expected outcome,
not a failure to be papered over.

---

## Practical checklist for any value or claim

Before anything reaches the user, it must be possible to answer:

1. Which **provenance category** does this value belong to?
2. If Verified — **what is the source**, and how fresh is it?
3. If Calculated — **what are the inputs**, and are they themselves clean?
4. If Estimated / Projected — **what method and what assumptions**?
5. What **epistemic label** applies (fact / inference / assumption / opinion)?
6. What is the **confidence level**, and what would change it?
7. What are the **limitations** — what is this value *not* saying?

If any of these cannot be answered, the value does not ship. It is replaced with
an honest statement of what is missing.
