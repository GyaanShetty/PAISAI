# Decision Journal — the Signature Feature

Most finance apps track *what you own*. PAISAI's Decision Journal tracks *how you
decide*. It is the feature that most directly serves the mission: it improves
**judgement**, not merely returns.

Every financial decision the user makes is recorded as a structured entry. At each
decision's review date, PAISAI compares the original thesis against what actually
happened — surfacing which assumptions held, which failed, and what that says
about the user's decision-making over time.

> **The objective is to improve judgement, not to maximise profit.**

---

## When an entry is created

A Decision Journal entry is created for every material financial action,
including but not limited to:

- Investment purchase
- SIP (start / modify / stop)
- Withdrawal
- Sale
- Loan
- Insurance purchase
- Any other major financial action

---

## Entry schema

Each entry must capture:

| Field | Description |
| --- | --- |
| **Date** | When the decision was made. |
| **Asset or decision** | What the decision concerns. |
| **Action** | Buy, Sell, Hold, SIP, Loan, etc. |
| **Original investment thesis** | Why the user made this decision. |
| **Expected outcome** | What the user expected to happen. |
| **Time horizon** | Over what period the thesis should play out. |
| **Expected return** | If the user provides one *(User Provided)*. |
| **Risk factors identified** | Risks recognised at the time. |
| **Key assumptions** | Premises the decision depended on. |
| **Alternative options considered** | What else was on the table. |
| **Why alternatives were rejected** | The reasoning against them. |
| **Emotional state** | Optional — how the user felt at the time. |
| **Market context** | Conditions at the time of the decision. |
| **Confidence level** | How sure the user was. |
| **Sources consulted** | What informed the decision. |
| **Review date** | When to revisit — e.g. 3, 6, or 12 months. |

Capturing assumptions, alternatives, emotional state, and market context *at the
time* is what makes an honest later review possible. Memory rewrites the past;
the journal does not.

---

## The review

At each review date, PAISAI automatically compares:

**Original thesis  →  What actually happened.**

It highlights:

- Which assumptions were **correct**
- Which assumptions **failed**
- Which risks **materialised**
- Which risks **never occurred**
- Whether the investment thesis **still holds**
- Whether the position **should be reconsidered**

The review is evidence-based and non-judgemental in tone — consistent with the
behaviour contract. It reports what happened and what it implies; it does not
scold.

---

## Behavioural bias detection

Across many entries and reviews, the journal detects recurring biases:

- **Overconfidence**
- **Confirmation bias**
- **Recency bias**
- **Anchoring**
- **Loss aversion**
- **FOMO**
- **Sunk cost fallacy**
- **Survivorship bias**

Detection is pattern-based and always explained: the system shows the entries that
evidence a bias rather than merely asserting it. This is behavioural finance made
personal — and it, too, must never fabricate a pattern that the data does not
support.

---

## Personal Decision Quality Score

The journal generates a **Personal Decision Quality Score** that measures the
**quality of decision-making, not portfolio returns.**

This distinction is the heart of the feature:

- A *good decision* is one that was well-reasoned, appropriately hedged, and
  correctly sized given the information available at the time — **even if it lost
  money.**
- A *bad decision* is one that was poorly reasoned, over-concentrated, or driven
  by bias — **even if it made money.**

Rewarding sound process over lucky outcomes is how PAISAI raises a user's
long-term judgement. Outcome and process are scored separately and shown
separately, so luck is never mistaken for skill.
