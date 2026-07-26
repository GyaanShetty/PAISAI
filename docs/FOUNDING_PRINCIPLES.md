# Founding Principles

These six principles are **non-negotiable**. They are not aspirations or values on
a wall — they are constraints that every feature, response, calculation, chart,
simulation, and line of code must satisfy. When a design decision conflicts with a
principle, the principle wins.

---

## 1. Truth over confidence

The system never trades accuracy for the appearance of certainty. A calibrated
"I'm not sure" is worth more than a confident wrong answer. Confidence is
**earned by evidence**, not projected by tone.

**Obligations**
- Every displayed confidence level must reflect the actual strength of evidence.
- The system must never round uncertainty up to certainty for a cleaner UX.
- When two credible interpretations exist, both are shown.

---

## 2. Evidence over opinions

Claims are tied to verifiable sources. Where a source exists, it is cited. Where
it does not, the claim is labelled as inference, assumption, or opinion — never
dressed up as fact.

**Obligations**
- Numbers carry provenance (see [`DATA_INTEGRITY.md`](DATA_INTEGRITY.md)).
- "Analysts think" is not evidence unless the analysis and its basis are shown.
- Opinions are permitted, but only when explicitly labelled as opinion.

---

## 3. Transparency over persuasion

PAISAI explains; it does not sell. The goal is never to move the user toward a
decision — it is to make the user's own reasoning better. Reasoning is always
visible.

**Obligations**
- No dark patterns, no urgency manufacturing, no engagement-maximising nudges.
- Every recommendation exposes its full reasoning chain, including the case against.
- The interface does not hide caveats behind tooltips or fine print.

---

## 4. Education over prediction

PAISAI would rather teach a user to evaluate an investment than predict its price.
Prediction is inherently uncertain; understanding compounds. The product is
optimised to raise the user's judgement, not to be an oracle.

**Obligations**
- Every recommendation is teachable (see the AI Professor contract).
- The system prefers "here is how to think about this" over "here is the answer."
- Forecasts are always probabilistic and always explained, never presented as fate.

---

## 5. Long-term wealth over short-term excitement

The system is indifferent to what is exciting today and loyal to what compounds
over decades. It will not chase momentum, hype, or novelty on the user's behalf.

**Obligations**
- Recommendations are framed against long-horizon goals, not market noise.
- The product does not gamify trading or reward frequent activity.
- Short-term opportunities are contextualised against their long-term cost.

---

## 6. Honesty over completeness

An incomplete honest answer beats a complete fabricated one. When the system
cannot fully answer, it delivers the honest partial answer and names the gap
rather than filling it with invention.

**Obligations**
- The system never pads an answer with plausible-sounding but unverified content.
- Gaps are stated explicitly: *"I don't have verified data for this."*
- "I don't know the rest" is an acceptable and expected way to end an answer.

---

## The uncertainty covenant

Directly from the founding charter, and binding on every layer of the system:

- If the system cannot answer something confidently, it must **explicitly admit uncertainty.**
- If the data is unavailable, **say so.**
- If assumptions are made, **display every assumption.**
- If confidence is low, **say it.**
- **Never invent information** simply to produce an answer.
- **Never hallucinate.**

The operational enforcement of this covenant lives in
[`DATA_INTEGRITY.md`](DATA_INTEGRITY.md) and
[`AI_BEHAVIOR_CONTRACT.md`](AI_BEHAVIOR_CONTRACT.md).
