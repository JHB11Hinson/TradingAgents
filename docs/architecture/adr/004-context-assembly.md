# ADR-004: Layered context structure and the assembly pipeline

- Status: accepted (design; the assembler is not implemented yet)
- Date: 2026-10-30
- Deciders: the four team members
- Related: ADR-001, ADR-002, `D1-REQ-CTX-001`, `D1-REQ-CTX-002`, `D1-REQ-CTX-003`,
  `D1-REQ-COST-003`

## Context

Every model call in the inherited pipeline is assembled ad hoc: each agent builds a
`ChatPromptTemplate`, the graph supplies `state["messages"]`, and reports, memory and portfolio data
are interpolated by hand. Concretely:

- identity comes from `agents/context.py` (`instrument_context`, the language instruction) and from
  `state.py` (`company_of_interest`, `asset_type`, `trade_date`, `portfolio_context`);
- retrieved knowledge is the analyst reports and `past_context` (written by the Memory Log step);
- conversation history is `state["messages"]` plus the debate histories in `InvestDebateState` and
  `RiskDebateState`;
- resumable state is the LangGraph checkpoint and the memory log;
- the current task is the node's own instruction.

The course's D2.2 requires the design to be written down: the **layered structure** every call
receives, the **assembly pipeline**, the **token-budget cap with its compaction threshold**, and the
**policy for re-injecting critical constraints after compaction**.

Today there is no shared budget, no compaction and no re-injection. `max_tokens` in
`default_config.py` caps a model's *output*; it does not bound the context. A long debate can
therefore grow without a ceiling, and a truncation by the provider would silently drop constraints
rather than history.

## Decision

**1. Six layers, one assembler.** Every model call is assembled from exactly these layers, in this
order, by a single module (`src/tradingagents/context/`, planned):

| # | Layer | Content today | Status |
|---|---|---|---|
| 1 | Identity | `instrument_context`, ticker, asset type, trade date, `portfolio_context`, language instruction | exists (scattered) |
| 2 | Standing constraints | the agent's role prompt, the authority boundary, the required output lines (rating, final proposal), the "no data after the trade date" rule | exists (per agent) |
| 3 | Retrieved knowledge | analyst reports, `past_context`, vendor snapshots | exists |
| 4 | Conversation history | `state["messages"]`, bull/bear histories, risk histories | exists |
| 5 | Resumable state | checkpoint pointer, memory-log pointer | exists |
| 6 | Current task | the node's instruction for this turn | exists |

**2. Pipeline: dedupe → prioritize → budget → compact → assemble.**

- **Dedupe:** identity and each report appear once; repeated evidence is removed.
- **Prioritize:** `P0` = constraints, identity and the current task (never dropped); `P1` = retrieved
  knowledge; `P2` = conversation history; `P3` = resumable-state pointers.
- **Budget:** one shared cap, `context_budget_tokens`, default **50 000** (`D1-REQ-COST-003`).
  Per-layer ceilings: constraints 10%, identity 5%, retrieved 45%, history 30%, current task 10%.
- **Compact:** when the estimate exceeds **80%** of the budget, compact from the lowest priority
  upward; summarize history before trimming retrieved knowledge; never drop `P0`.
- **Assemble:** emit the layers in the order above.

**3. Token estimate.** Use a deterministic estimator (`characters / 4`) until a provider tokenizer is
integrated. The estimator is part of the contract: "assembled_tokens <= budget" is measured with it,
and it is recorded here so the number is reproducible on any machine.

**4. Re-injection after compaction.** After any compaction, the `P0` block (constraints, identity,
current task) is re-injected **verbatim**; a unit test hashes the block before and after and asserts
it is byte-identical. Compaction may change history and retrieved knowledge; it may never change the
constraints.

**5. Additive, no-op under budget.** If the assembled context is already within budget, the assembler
returns the same prompt the agent builds today. The change must not alter behaviour in the common
case; only over-budget calls change.

## Alternatives considered

- **Let each agent trim its own prompt.** Rejected: no shared ceiling, and every agent would
  re-implement the same truncation.
- **Rely on provider truncation.** Rejected: providers drop the oldest tokens, which can be the
  standing constraints — the opposite of the priority order.
- **Summarize everything with an LLM on every turn.** Rejected: cost and latency on every call, and a
  new source of non-determinism exactly where the budget is tight.
- **A fixed message-count window.** Rejected: message size varies by an order of magnitude, so a
  count is not a budget.
- **Put the budget only in the model configuration.** Rejected: `max_tokens` bounds output, not
  context; conflating them hides the problem.

## Consequences

- One module owns prompt assembly; agents stop hand-interpolating context.
- Cost becomes measurable and comparable against the baseline (`D1-REQ-COST-001`).
- Compaction can shorten useful history; the priority order and the re-injection test bound that
  risk.
- The assembler must be covered by six tests: layer presence, budget, compaction, byte-identical
  re-injection, the no-op-under-budget case, and a negative test that fails when the budget check is
  removed.
- Implementation order: `CTX-001` (structure) → `CTX-003` (budget and re-injection) → `CTX-002`
  (pipeline stages), each with its own tests before implementation.

## Reconsider if

- A provider exposes a stable, cheap tokenizer for every model in the catalog; replace the estimator.
- The graph is replaced by an event-driven design — an explicit non-goal (`AGENTS.md` §2), but if the
  decision reopens, this ADR reopens with it.
- The compaction test shows history compression changes decision quality below the evaluation
  threshold.
