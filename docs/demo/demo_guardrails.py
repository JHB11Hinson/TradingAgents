"""Demo: deterministic position ceiling and REVIEW fallback. Run from the repo root."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from tradingagents.agents.schemas import PortfolioDecision
from tradingagents.guardrails.decisions import review_decision, validate_free_text_decision
from tradingagents.guardrails.positions import enforce_position_ceiling

decision = PortfolioDecision(
    rating="Overweight",
    executive_summary="Build slowly.",
    investment_thesis="Demand is strong.",
    position_pct=50.0,
)
clipped, warning = enforce_position_ceiling(decision, 10.0)
print(f"claimed {decision.position_pct:g}% -> enforced {clipped.position_pct:g}%")
print(warning)

print("\n--- free-text decision ---")
print("clean:", validate_free_text_decision("Rating: Overweight\nFINAL TRANSACTION PROPOSAL: **BUY**"))
print("malformed:", validate_free_text_decision("I kind of like it, maybe."))
print(review_decision("schema failed"))
