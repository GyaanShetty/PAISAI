# Product Modules

PAISAI is composed of eleven modules plus two cross-cutting systems (the Decision
Journal and Market Intelligence). Every module inherits the data-integrity and
behaviour contracts — no module is exempt. Where a module displays a number, that
number carries a provenance category. Where it draws a conclusion, that conclusion
carries evidence, assumptions, risks, and a confidence level.

The Decision Journal and Market Intelligence have their own documents
([`DECISION_JOURNAL.md`](DECISION_JOURNAL.md),
[`MARKET_INTELLIGENCE.md`](MARKET_INTELLIGENCE.md)).

---

## 1. Dashboard

The single pane of financial truth. Displays:

- Net Worth, Assets, Liabilities, Cash
- Emergency Fund status
- Savings Rate
- Financial Health Score
- Monthly Cash Flow
- Investment Allocation
- Debt overview
- Insurance coverage
- Goal Tracking
- Future Net Worth Projection *(Projected — model and assumptions shown)*
- Financial Independence Progress

Every metric is traceable to its inputs. The Financial Health Score exposes its
components rather than presenting an opaque number.

---

## 2. Expense Intelligence

Automatically categorises expenses and **detects patterns**, not just totals:

- Lifestyle inflation
- Subscription leakage
- Impulse spending
- Overspending
- Recurring expenses

Generates monthly insights and quarterly/annual trends, and — critically —
**explains mathematically how today's behaviour affects future wealth** (the
dining-out example in the behaviour contract is the canonical pattern).

---

## 3. Investment Planner

Builds portfolios from the user's full context:

- Age, Income, Risk tolerance
- Country and Tax Rules
- Goals, Emergency Fund, Existing Assets
- Investment Horizon

Generates allocations and **always explains WHY, never only WHAT.** An allocation
without its rationale is a violation of the transparency principle.

---

## 4. Portfolio Analysis

Analyses an existing portfolio across:

- Diversification, Correlation, Concentration
- Sector Allocation, Geographic Allocation
- Risk, Volatility, Drawdown
- Valuation, Expected Return *(Projected)*, Historical Performance *(Verified/Calculated)*

**Every metric is explained** — the user learns what "correlation" or "max
drawdown" means for their money, not just its value.

---

## 5. Stock Analysis

Fundamental analysis across:

- Revenue, Margins, Cash Flow
- ROE, ROCE, Debt
- Valuation, Management quality, Capital Allocation
- Competitive Advantage (moat), Industry, Macro environment
- DCF assumptions *(Assumed/Projected — every input shown)*
- Comparable valuation

**Never produces unsupported conclusions.** A DCF is only as honest as its
assumptions, so every assumption is displayed and its sensitivity noted.

---

## 6. Mutual Fund Analysis

Compares funds across:

- Expense Ratio, Tracking Error
- Rolling Returns *(Verified/Calculated)*
- Fund Manager, AUM, Benchmark
- Risk Metrics, Portfolio Holdings
- Turnover, Exit Load, Tax Efficiency

---

## 7. Tax Planner

Country-specific and **legal only.** Provides optimisation and scenario planning
within the law. It assists with legitimate tax efficiency and refuses to help with
evasion. Regulations are treated as reference data — never fabricated (see the
No-Hallucination Policy).

---

## 8. Retirement Planning

**Monte Carlo simulation** producing a **probability of success**, not a single
deterministic number. Inputs modelled:

- Inflation, Salary Growth, Expenses
- Investment Returns, Withdrawal Rate
- Healthcare Costs, Unexpected Events

Output is a distribution with an explicit success probability and the assumptions
that drive it.

---

## 9. Financial Twin

A **living financial model** of the user, continuously simulating life events:

- House Purchase, Marriage, Children
- Job Change, Promotion, Layoff
- Inflation Shock, Market Crash
- Business, Large Purchases, Early Retirement

Shows **probability distributions, never deterministic predictions.** The Twin is
where "education over prediction" is most visible: it teaches the user how ranges
of outcomes respond to their choices.

---

## 10. Financial Education

Adaptive learning across:

- Accounting, Economics, Investing
- Corporate Finance, Behavioural Finance
- Risk, Taxation, Valuation
- Derivatives, Macroeconomics

Difficulty adapts to the learner. Education content is clearly separated from
personalised guidance.

---

## 11. AI Professor

Makes every recommendation teachable. Each recommendation exposes:

- **Teach Me**
- **Explain Like I'm 15**
- **Intermediate**
- **Advanced**
- **Show Formula**
- **Worked Example**
- **Historical Context**
- **Opposing View**

The AI Professor is the mechanism by which "education over prediction" is
delivered at the point of every decision.

---

## Cross-cutting systems

- **[Decision Journal](DECISION_JOURNAL.md)** — the signature feature. Records
  every financial decision, reviews it against reality, and scores decision
  *quality* rather than returns.
- **[Market Intelligence](MARKET_INTELLIGENCE.md)** — explains market events and
  their transmission into the user's own portfolio.
