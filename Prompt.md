# Prompt.md

Read `AGENTS.md` first; this is the one prompt to read after it. It is the **launch instruction for
the coding agent**. It is not a runtime prompt for the product's trading agents (those live in
`prompts/`), and it must never be used to run the agent unattended to completion.

---

## 1. Produce the execution plan first

Before generating any code, write an execution plan with these five parts, in this order:

1. **Traceability** — the requirement id(s) from `docs/req/requirements.yaml` this change serves, the
   change id (`CHG-xxx`), and the deliverables it touches. If no requirement covers it, say so and
   stop: register the requirement first.
2. **Interface contract** — the inputs, outputs and observable behaviour the change exposes or
   changes. Name every contract from `AGENTS.md` §8 that it touches.
3. **Scope boundaries** — the files and modules inside the change, and what is explicitly out.
4. **Testing strategy** — the tests to add, their tier (`test/offline/` or `test/live/`), the
   negative test for each new behaviour, and how each `fit_criterion` becomes checkable.
5. **Steps** — the ordered commits, with the tests-before-implementation split made explicit.

State the rollback at the end of the plan: how to undo this change through the normal pull-request
flow.

## 2. STOP for approval

Present the plan and **wait**.

Do not create a branch, write a file, install a dependency, or run a generator until a human
approves the plan. Approval is an explicit message from the human, not an inference from silence,
enthusiasm, or an earlier "go ahead".

If the plan changes after approval, stop and re-present the changed part.

## 3. Build in stages, with a human gate at each one

Follow the approved steps in order. At every stage:

- **Tests first.** Commit the tests before the implementation that makes them pass.
- **One change, one branch, one pull request.** Use the branch prefix from `AGENTS.md` §12 and carry
  the change id in the branch name, commit trailers and pull-request body.
- **Stop at every surprise.** A baseline that is not green, a file outside the approved scope, a test
  that cannot be made to pass, a contract that has to change: stop and ask.
- **Never self-approve or self-merge.** Open the pull request and hand it to a human reviewer.
- **Respect the one human-only file.** `.opencode/rules.md` is not writable by the agent
  (`AGENTS.md` §11). Everything else changes through a reviewed pull request.

## 4. Self-verify before asking for review

Run the verification in `AGENTS.md` §9 and put the evidence in the pull request:

- `ruff check` on the `src/**/*.py` files this change touches;
- `pytest -q` — the full offline suite, zero regressions against the 1262-passed baseline;
- `check-jsonschema --schemafile docs/req/req-schema.json docs/req/requirements.yaml` when the
  requirements change;
- a note on every gate in `AGENTS.md` §10 that is not online yet, and how a human covered it;
- one `docs/ai-use-log.yaml` entry (team policy: whenever the AI materially contributed);
- one `docs/review-memo.md` entry per pull request, written by the reviewer.

Report each command's result honestly. A red command is a finding to report, not something to
explain away or to make green by weakening a test.

## 5. What this prompt is not

- **Not a runtime prompt.** Trading strategy, analyst instructions and model behaviour do not belong
  here; they belong in `prompts/` and `src/`.
- **Not an autopilot.** The agent never runs from plan to merge without a human gate.
- **Not a substitute for `AGENTS.md`.** If the two disagree, `AGENTS.md` wins.
