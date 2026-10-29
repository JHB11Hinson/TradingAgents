# Always-on rules for the coding agent

> **Human-only file (course D3).** A human changes this file through a reviewed pull request; the
> agent must not write it. The human is the author of record: an agent typing at their direction is
> transcription, not authorship. These rules apply to every session, in addition to `AGENTS.md` and
> `Prompt.md`.

---

## 1. Authority order

1. The course PDFs are the final requirement.
2. The team's process manuals (workspace-only, `.opencode/manual/`) are the authority for team
   workflow; this file restates the parts the agent must obey.
3. `AGENTS.md` is the repository's single entry point; `Prompt.md` is the launch instruction.
4. `docs/code-governance/protection.json`, `.github/workflows/ci.yml` and `.github/CODEOWNERS` are
   the repository's real state — verify them, never assume.
5. This file maps the layers above into agent behaviour. It adds nothing and relaxes nothing.

If two layers disagree, or a situation is not covered, **stop and ask** (§8).

## 2. The three human gates (never signed by the agent)

| Gate | What the human decides | The agent's job |
|---|---|---|
| Plan approval | the approach, before any code | prepare the plan, then stop |
| Test approval | the tests, before the implementation | commit `test/**`, then stop |
| PR approval | the merge | prepare the evidence, then stop |

An explicit human statement is the only approval. Silence, enthusiasm, an earlier "go ahead", or the
`gh` account having admin rights are not approval.

## 3. Standard sequence

```text
sync main → branch (<type>/CHG-xxx-…): requirement, change card, plan (approve)
→ tests only (approve) → implementation + records → local three-tier verification
→ open PR → gates → review (the reviewer pushes the record, then approves)
→ squash merge + delete branch → sync main
```

Branch prefixes: `feat/`, `fix/`, `refactor/`, `test/`, `docs/`, `req/`, `arch/`, `gov/`, `ci/`.
A branch lives at most **3 days** and **5 commits**; past that, split it or rebuild it from `main`.

## 4. Git and GitHub: auto / ask / forbidden

### Auto — in the authorized scope, reversible, on this branch only

- read-only: `git status|diff|log|show|fetch|ls-remote`, `gh pr list|view|diff|checks`,
  `gh run list|view`, `gh api` GET
- `git switch -c <type>/CHG-xxx-…`, `git switch <branch>`, `git add <explicit paths>`, `git commit`
- push **your own** feature branch to `origin`; `--force-with-lease` on your own branch after a rebase
- `gh pr create --base main`; add a reviewer other than yourself
- append to `docs/ai-use-log.yaml` and `transcripts/`; draft a review memo in `/tmp`
- mechanical conflict resolution per file; `git rebase --abort`; `git restore --staged`

### Ask — state the facts, at least two options and a recommendation, then wait

- `git commit --amend` (pushed or not); `git add -A` / `git add .`; `--force` on any branch;
  pushing a shared or someone else's branch; deleting a remote branch (except `--delete-branch` at merge)
- a branch older than 3 days or longer than 5 commits, when it needs splitting or rebuilding
- changing test assertions, thresholds, `skip`, or deleting cases
- `pyproject.toml`, dependencies, `docs/req/req-schema.json`, requirement-id rules
- `AGENTS.md`, `.github/**`, `.github/CODEOWNERS`, `docs/code-governance/**`
- posting a review verdict, commenting on a pull request, pushing a record to someone else's branch
- tags, releases, `git revert` of a merged commit
- anything outside the authorized scope

### Forbidden — the agent must not execute, even if told "just do it"

- `git push` to `main`; force-push or delete `main`; push to `upstream`; edit the `upstream` push URL
- disable or loosen branch protection; remove a check from `contexts`; set `enforce_admins: false`
- `gh pr merge` (the human author merges once someone else has approved); approve your own pull
  request; sign a human verdict
- `gh api` writes to protection, Actions, collaborators, secrets or webhooks
- `git reset --hard`, `git clean -fdx`, `git filter-repo`, or any shared-history rewrite
- `-X ours` / `-X theirs` to resolve a conflict wholesale
- commit a secret, `.env`, key or token; delete someone else's branch, tag or release
- edit `.opencode/rules.md`, `.opencode/tasks/**`, or `.opencode/git-gh-rules/**`

## 5. Development discipline

1. **Requirement first.** Cite `D1-REQ-…` in the change card; register it first if it is missing.
2. **Tests first, and one negative test per feature.** Tests and implementation never share a commit.
3. **Do not hand-edit generated code.** Ask the agent to change it, so the session record keeps the
   provenance.
4. **Never make a gate green by weakening it** — no loosened assertions, no `skip`, no
   `continue-on-error`, no `|| true` to pass.
5. **Conflicts take the union.** Never choose one side wholesale; if the meaning is unclear, abort
   and ask.
6. **Secrets: revoke first, clean second.** Stop pushing immediately and tell a human.
7. **Never push to `main`.** Branch protection blocks it too; do not test it.

## 6. Records

Every change carries the change card in the pull-request body; the change id in the branch name and
the commit trailers (`Refs:`, `Agent-Session:`, `AI-Use-Log:`, `Test-Approval:`); one
`docs/review-memo.md` entry per pull request (the reviewer writes it, after pushing); one
`docs/ai-use-log.yaml` entry whenever the AI materially contributed; transcripts append-only.

## 7. Evidence before claims

Quote the command and its output from this session for anything you claim: "gates are green" needs
`gh pr checks`; "tests pass" needs `pytest -q`; gate names, paths and line numbers must come from the
files, not from memory. If you did not run it, write "not run".

## 8. Stop and ask

Stop before: touching `main`, branch protection, gates, secrets or a safety-critical path; changing a
test criterion; resolving a conflict whose meaning is unclear; acting outside the authorized scope;
when two instructions conflict; when a rule does not cover the case.

Ask with the facts, at least two options, a recommendation and a rollback — then wait. A stopped
session costs minutes; an unreviewed merge costs the evidence the course grades.
