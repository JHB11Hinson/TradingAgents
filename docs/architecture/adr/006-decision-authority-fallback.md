# ADR-006: Decision authority after a structured-output failure

- Status: **accepted** 2026-11-20. The non-author decision is the automated review on PR #40
  (`github-actions[bot]`, head `ea5a7f5`), requested by the owner; the owner directed the status flip
  when merging, and the flip lands in this same pull request before its final approval. The coding
  agent applied the edit, not the decision.
- Date: 2026-11-20
- Revision: **r5** (status flipped to `accepted` at the owner's direction; the implementation
  change no longer carries the flip)
- Earlier: r4 corrected the §10 repository-state premise, moved the debt id to `DEBT-013`, made the
  §Context quote verbatim and stated the flip sequence; r3 added the four failure identifiers, the
  T2/T7 test-role split and the ADR PR file scope.
- Deciders: the three active team members (`@JHB11Hinson`, `@AKAScarlett`, `@SY1433`)
- Change: `CHG-035` — ADR PR on branch `arch/CHG-035`, implementation PR on branch `feat/CHG-035`
- Related: ADR-001, ADR-003, `AGENTS.md` §7/§8/§11/§12, `D1-REQ-SAFE-002`, `D1-REQ-SAFE-003`,
  `D1-REQ-COST-003`, `INV-05`, `architecture-blueprint.md` §5,
  `docs/architecture/trace-matrix.md` (`SAFE-002` row), `docs/code-governance/verification-constraints.md`
  (`SAFE-002` row — see §10)

## Context

`D1-REQ-SAFE-002` is a `must` invariant:

> A decision whose schema fails validation must be rejected and degraded, never emitted as a
> tradeable action.

`architecture-blueprint.md` §5 states the boundary honestly: the portfolio-manager path *"still has a
free-text fallback after a structured-output failure; the fallback can parse a rating. `SAFE-002` is
therefore partial, not fully enforced."* `docs/architecture/invariants.md` INV-05 says the same.

The code matches that description.

1. `src/tradingagents/agents/managers/portfolio_manager.py` binds the schema once and, on a
   structured miss, does:

   ```python
   decision = invoke_structured(structured_llm, assembled.text, "Portfolio Manager")
   if decision is not None:
       final_trade_decision = render_pm_decision(decision)
       final_rating = decision.rating.value
   else:
       final_trade_decision = llm.invoke(assembled.text).content
       final_rating = parse_rating(final_trade_decision)
   ```

   `parse_rating` runs `extract_rating` over prose. A model that answers "**Rating**: Sell" in plain
   text therefore produces `final_rating = "Sell"` without any schema validation.

2. `src/tradingagents/agents/structured.py` collapses two different situations into the same
   `None`:

   - `bind_structured` catches `NotImplementedError` / `AttributeError` and returns `None` — the
     **provider cannot do structured output at all**;
   - `invoke_structured` catches **any** `Exception` (and a `None` parsed result) and returns `None`
     — **the call was made and its output was not a valid decision**.

   The caller cannot tell them apart, so it cannot choose a different response for each.

3. `RATING_REVIEW = "REVIEW"` (`agents/rating.py`) is already the sentinel for "no tradeable call".
   The CLI treats a REVIEW run as non-tradeable (`cli/run.py`, `is_review`), and the memory log
   stores the rating as given.

The result: after a schema failure, a prose answer can still become a tradeable action, which the
invariant forbids. INV-05 says: *"This is a known gap, not an accepted design; it must be fixed or
the invariant must be reworded with human approval."* This ADR chooses the first option.

## Decision

### 1. The only source of `final_rating` is a schema-valid `PortfolioDecision`

`final_rating` is `decision.rating.value` when a schema-valid `PortfolioDecision` was produced, and
`RATING_REVIEW` in every other outcome. No text-derived rating path remains in the portfolio-manager
node. The default outcome of a failed decision is `REVIEW`.

### 2. Structured failure and provider incapability are separate, named conditions

| Condition | Detected at | Signal | `structured_calls` | `text_calls` | Reason identifier | `final_rating` |
|---|---|---|---|---|---|---|
| **Provider unsupported** | `bind_structured` returns `None` | `NotImplementedError` / `AttributeError` at binding time | **0** | at most **1** | `provider_unsupported` | `REVIEW` |
| **Structured failure, retry succeeds** | `invoke_structured` fails once, second call valid | raised / `None` / invalid object | **2** | 0 | — (`ok`) | from the decision |
| **Structured failure, retry fails** | both calls fail | same | **2** (never a third) | at most **1** | `retry_failed` | `REVIEW` |
| **First structured call fails and the retry is not attempted** | `invoke_structured` fails, retry skipped | same | **1** | at most **1** | `structured_failure` | `REVIEW` |
| **Free-text aid failed** (any row above that called free text) | the free-text call raised / returned empty | `Exception` / empty content | as above | **1** (attempted) | `freetext_failed` | `REVIEW` |
| **Structured success** | first call valid | — | **1** | 0 | — (`ok`) | from the decision |

The loss of distinction in `structured.py` is the defect this ADR fixes.

### 3. Free text is an aid for the human reader, never the rating

When the structured path cannot produce a decision, the node **may call the provider exactly once in
free-text mode** to produce a reader-facing explanation, and that explanation is recorded as
`final_trade_decision`. The rating in that text is inert: `final_rating` stays `RATING_REVIEW`
whatever the prose says. The rule is stated once and applies to every failure cause:

> **A prose "Buy", "Overweight", "Hold", "Underweight" or "Sell" is never promoted to
> `final_rating`; only `PortfolioDecision.rating` can set it.**

This keeps a large class of local providers usable — the analyst still learns *why* the run could not
decide — while removing the tradeable consequence.

Free text remains unchanged for **advisory** agents (sentiment analyst, trader, research manager),
whose output is evidence, not the final action.

### 4. Retry policy: at most one structured retry

- A **provider-unsupported** condition is not retried: the binding could not be built, so a second
  attempt would fail identically. Free text (at most one call, §3) supplies the reader-facing text.
- A **structured failure** is retried **once** with the same binding and the same prompt. If the
  retry also fails there is no third attempt; free text (at most one call, §3) supplies the
  reader-facing text, and `final_rating` is `REVIEW` with reason `retry_failed`.
- The retry and the free-text call are **inside the node**; they add no graph step and cannot loop.

### 5. A failing free-text call is itself a safe outcome

The free-text call may raise (provider error, timeout, empty content). That must not raise out of the
node and must not produce a rating:

- the node catches the exception, **logs it as a warning** naming the agent and the original failure
  cause (so an outage and a model refusal are distinguishable in the log), and `final_rating` is
  `RATING_REVIEW`;
- `final_trade_decision` is a **module-level constant**, not assembled from model output, so it is
  produced even when nothing answered. It names **both** failures: the structured decision failure
  (with its reason identifier) and the failure of the explanatory text, and it carries the
  `freetext_failed` identifier;
- the constant is deterministic: the same failure inputs produce byte-identical text, which is what
  makes the test assertable.

Therefore **every** path of the node returns exactly one of: a schema-valid rating, or `REVIEW`.

### 6. Two counters, counted separately, observed through the public entry point

The node's behaviour exposes two independent counters, and they are **never summed into one "model
calls" figure**:

- `structured_calls` — calls made through the structured binding (`0`, `1` or `2`);
- `text_calls` — calls made in free-text mode (`0` or `1`, and counted as **attempted** when it
  raised).

**How they are observed (confirmed decision 2).** The counters are not added to the node's return
dict and not to `AgentState`: `agents/state.py` and the node's state shape are frozen by this ADR.
Tests read them from the two injected mocks through the public factory `create_portfolio_manager`:

- `structured_calls` ⇒ `llm.with_structured_output(...).invoke.call_count`;
- `text_calls` ⇒ `llm.invoke.call_count`.

Each mock entry point maps to exactly one counter, so the separation is testable without a new
public API, without a `decision_authority` key and without a state change. In telemetry both kinds of
call appear as model calls on the same span.

### 7. The retry must not enlarge the context

The retry and the free-text call reuse the already-assembled `assembled.text`; `assemble_context`
runs once per node call. `D1-REQ-COST-003` accounting is therefore unchanged, and neither call can
push the run over its budget. `ContextBudgetExceeded` before the first call still returns `REVIEW`
with no model call (existing behaviour, unchanged).

### 8. Test roles are split by contract

The two contracts must be tested by **different** tests, and neither test may assert the other's
contract:

- **Rating authority** — "a prose rating never becomes `final_rating`": tested with a single-failure
  scenario whose prose says a tradeable word, asserting only `final_rating == RATING_REVIEW` and the
  inertness of the prose.
- **Call budget** — "at most two structured calls and at most one free-text call": tested with
  scenarios whose prose content is irrelevant, asserting only the call counts.

A test that asserts both makes a failure ambiguous: a green count would hide a leaked rating. The
implementation tests that follow this rule are listed in the CHG-035 test design
(`test/offline/test_pm_decision_authority.py`).

### 9. Failure reason identifiers

Exactly four identifiers, used in the reader-facing REVIEW text (and only there — no new state key):

| Identifier | Meaning |
|---|---|
| `provider_unsupported` | the provider could not bind structured output at all |
| `structured_failure` | a structured call failed and no retry was attempted |
| `retry_failed` | the retry was attempted and also failed |
| `freetext_failed` | the reader-facing free-text call failed as well |

`provider_unsupported` and `retry_failed` / `freetext_failed` may co-occur in one text (e.g. a
provider that cannot bind *and* whose free-text call then raised). A reader can therefore tell which
decision path was taken from the text alone.

## Compatibility boundaries

### 10. Checkpoints, the memory log, and the documentation gap

- A checkpoint written by an **older version** may hold `final_trade_decision` without
  `final_rating`. `run_rating` (`agents/rating.py`) keeps its documented fallback of reading the
  rating from the decision text in that case. This ADR does **not** change `run_rating`; it changes
  only what the node writes for a *new* decision. The legacy path stays as the compatibility seam and
  is recorded in `INV-05` as such.
- `TradingMemoryLog.store_decision` (`memory/log.py`) keeps `rating = rating or parse_rating(...)`.
  The graph always passes the explicit rating, so that line is a legacy fallback for direct callers
  only. It is **not** changed by this ADR.
- **Documentation sequencing, recorded deliberately (review decision 3).**
  On `main` today all four records agree that `SAFE-002` is **partial**: `invariants.md` INV-05 says
  the free-text fallback can still parse a rating, `architecture-blueprint.md` §5 says "partial, not
  fully enforced", the `trace-matrix.md` SAFE-002 row lists the evidence without claiming
  enforcement, and `verification-constraints.md` §4 says partial. The implementation change
  (`feat/CHG-035`) flips the first three to **implemented** with the new tests; it does not edit
  `docs/code-governance/verification-constraints.md` in the same pass without an authorisation for
  that write-ask path, so that row is updated under **`DEBT-013`** with the trigger "after CHG-035
  merges". Until the follow-up lands, that one row is stale and says *partial* while the other three
  say *implemented* — this ADR is the reason why.
- A REVIEW decision is still written to memory with the REVIEW tag; settlement and reflection
  continue to work on it as today.

### 11. What this ADR explicitly does not change

- **`PortfolioDecision`** (`agents/schemas.py`) — no field added, removed or re-typed.
- **`PortfolioRating`** — unchanged.
- **`RATINGS_5_TIER`** — the five tiers and their order.
- **`RATING_REVIEW` and `is_review()`** — REVIEW stays the non-tradeable sentinel; it is not a sixth
  tier and is not added to `RATINGS_5_TIER`.
- **`extract_rating` / `parse_rating` / `run_rating`** — no behaviour change for existing callers.
- **Trader and Research Manager** — continue on `invoke_structured_or_freetext` with their current
  advisory free-text path. The sentiment analyst likewise.
- **`agents/state.py`** — no new state key; the reason identifiers travel inside
  `final_trade_decision`, so the state shape is untouched.
- **The node's return shape** — still exactly `risk_debate_state`, `final_trade_decision`,
  `final_rating`.
- **`docs/code-governance/verification-constraints.md`** — not modified (see §10; `DEBT-013`).
- **Every existing test file** — not modified.
- **`SAFE-003` position ceiling** (INV-06) — still not implemented; out of scope.

## Impact on existing providers

- **Working structured output** (the default catalog): no observable change; the retry never runs.
- **Intermittent failures** (thinking model answering in prose, transient parse miss): one extra
  structured attempt, then at most one free-text explanation, then `REVIEW`. The run completes and
  the memory log still records a decision.
- **No structured output** (older Ollama models, some OpenAI-compatible endpoints): the run still
  completes, the reader still gets an explanation, but `final_rating` is `REVIEW` and the CLI
  reports "no usable rating" (existing `is_review` behaviour). This behaviour change is recorded in
  `CHANGELOG.md`.
- **No configuration restores a tradeable prose rating.** That is deliberate.

## Consequences

- `INV-05` moves *Partial* → *Implemented* once the tests exist; blueprint §5 and the
  `trace-matrix.md` `SAFE-002` row follow in the implementation change. `verification-constraints.md`
  follows later under `DEBT-013`.
- The inherited test
  `test/offline/test_memory_log.py::test_pm_falls_back_to_freetext_when_structured_unavailable`
  asserts only `final_trade_decision`, which still equals the prose under §3 — it **stays green and
  is not touched**. Verified before implementation; if the verification disagreed, the change would
  stop for human review.
- A failed decision costs at most two structured calls and one free-text call.
- The retry and the free-text call appear in telemetry as extra model calls on the same span; no new
  event type is introduced.

## Alternatives considered

- **Keep the old fallback and reword INV-05.** Rejected: it turns a `must` invariant into a
  suggestion, and a prose "Sell" would stay reachable.
- **Drop providers without structured output.** Rejected: it would block a large class of local
  models; the explanation is still useful when the decision is `REVIEW`.
- **No free-text call at all after a failure.** Rejected: the operator loses the explanation of why
  the run could not decide, and it would break the inherited test above. The rating is protected
  without removing the explanation.
- **Validate prose with the schema instead of retrying.** Rejected: there is no deterministic
  text-to-`PortfolioDecision` mapping.
- **Retry until the schema validates.** Rejected: an unbounded retry is a termination hazard
  (`TERM-001`); the cost model assumes one assembly and a bounded number of calls.
- **Put the retry in the graph as a node.** Rejected: it would make the retry a debatable loop and
  change the graph shape.
- **Make `REVIEW` a sixth rating tier.** Rejected: it is a sentinel, not a position.
- **One combined "model calls" counter.** Rejected: it hides which contract failed.
- **A `decision_authority` key in the node's return dict.** Rejected (confirmed decision 2): it
  would change the node's return shape; the two mock entry points already observe both counters.
- **Edit `verification-constraints.md` in this change to avoid the stale row.** Rejected (confirmed
  decision 3): the path is write-ask; the gap is registered as `DEBT-013` instead.

## Reconsider if

- The evaluation set (`EVAL-001`, `DEBT-003`) shows that turning free-text decisions into REVIEW
  loses material quality on providers without structured output; then a stricter structured re-ask
  deserves its own ADR.
- A provider gains native structured output and the unsupported branch becomes dead code.
- `SAFE-003` (position ceiling) lands and must compose with this flow; the composition point is the
  same node and must be added here.
- `DEBT-013` is closed and the four documents agree; then §10's warning paragraph is removed.
