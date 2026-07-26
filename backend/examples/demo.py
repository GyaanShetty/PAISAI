"""A short, runnable demonstration of PAISAI's trust-enforcing core.

Run it from the backend directory:

    python examples/demo.py

It shows three things the founding principles demand:
  1. Numbers carry provenance and flow through deterministic math.
  2. Un-sourced numerics are refused before they could reach a user.
  3. When verified data is missing, the honest answer is "Unavailable" — not a guess.
"""

from paisai.engine import portfolio_weights, savings_rate
from paisai.integrity.epistemics import Answer, Confidence
from paisai.integrity.provenance import (
    IntegrityError,
    ensure_provenanced,
    unavailable,
    user_provided,
    verified,
)


def main() -> None:
    print("=== 1. Provenance flows through the math ===")
    income = user_provided(120_000.0, label="Monthly income", unit="INR")
    expenses = user_provided(84_000.0, label="Monthly expenses", unit="INR")
    rate = savings_rate(income, expenses)
    print(f"Savings rate: {rate.value:.1%}  [{rate.provenance.value}]")
    print(f"  derived from: {[i.label for i in rate.inputs]}")

    holdings = {
        "Equity": verified(600_000.0, source="broker statement", unit="INR"),
        "Debt": verified(300_000.0, source="broker statement", unit="INR"),
        "Gold": verified(100_000.0, source="broker statement", unit="INR"),
    }
    print("\nPortfolio weights:")
    for name, w in portfolio_weights(holdings).items():
        print(f"  {name:<7} {w.value:6.1%}  [{w.provenance.value}]")

    print("\n=== 2. Un-sourced numerics are refused ===")
    try:
        # Imagine a model tried to slip a P/E ratio straight to the UI.
        ensure_provenanced({"pe_ratio": 27.4}, context="stock_card")
    except IntegrityError as exc:
        print(f"Refused, as it should be:\n  {exc}")

    print("\n=== 3. Missing data is admitted, never invented ===")
    live_pe = unavailable(label="Live P/E")
    print(f"  {live_pe}")

    print("\n=== 4. An answer carries its honesty scaffolding ===")
    answer = Answer(
        summary=(
            "Dining is 38% of discretionary spending; at this rate, ~Rs 10.8L over "
            "five years assuming no behavioural change."
        ),
        evidence=["12 months of categorised transactions (User Provided)."],
        reasoning=["dining / discretionary = 0.38; projected flat for 60 months."],
        assumptions=["No behavioural change.", "No dining inflation."],
        risks=["Projection breaks if the spending pattern shifts."],
        alternatives=["Cap dining at 20%; redirect the difference to an index SIP."],
        limitations=["Excludes cash spend not captured by the linked account."],
        confidence=Confidence.MEDIUM,
        sources=["User's linked account statements."],
    ).validate()
    print(f"  summary   : {answer.summary}")
    print(f"  confidence: {answer.confidence.value}")
    print(f"  risks     : {answer.risks[0]}")


if __name__ == "__main__":
    main()
