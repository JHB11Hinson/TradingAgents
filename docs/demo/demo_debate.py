"""Demo: free prose vs a schema-bound debate turn. Run from the repo root with the venv active."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from tradingagents.agents.debate import DebateTurnError, parse_debate_turn, render_debate_turn

PROSE = "I think the stock goes up because guidance was strong. The bear is wrong."

STRUCTURED = (
    '{"claim":"Guidance raise supports a long.",'
    '"evidence":[{"source":"10-Q","quote":"FY26 guidance raised 8%."}],'
    '"rebuttal":"The margin concern is already priced.","confidence":"medium",'
    '"diverge":"Weighed margin risk against the guidance raise.",'
    '"converge":"Both sides agree demand is strong; valuation is the disagreement."}'
)

print("--- legacy free prose ---")
print(render_debate_turn(parse_debate_turn(PROSE, side="Bull", opponent="Bear"), "Bull"))

print("\n--- structured DebateTurn ---")
print(render_debate_turn(parse_debate_turn(STRUCTURED, side="Bull", opponent="Bear"), "Bull"))

print("\n--- malformed JSON rejected ---")
try:
    parse_debate_turn('{"claim":"only a claim"}', side="Bull")
except DebateTurnError as exc:
    print(type(exc).__name__)
    print(str(exc))
