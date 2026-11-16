# Merge train — serial integration without stale approvals

> **Requirement:** `D1-REQ-GOV-002` (coding governance), `D1-REQ-GOV-010` (review records).
> **Status:** active. **Owner:** `@JHB11Hinson`. **Reviewers:** the active team members.
> This runbook is the project's procedure for landing a queue of pull requests on `main` without
> losing approvals to avoidable rebases.

---

## 1. Why this runbook exists

`main` requires a strict up-to-date branch, one approving review and
`dismiss_stale_reviews: true` (`docs/code-governance/protection.json`). That combination is
deliberate: an approval must cover the exact content that lands. The cost is that some pushes after
approval require a second review.

The protection is **not** the thing to change. The cost is removed by ordering the work so that the
final push happens **before** the approval that is used to merge.

Observed behaviour on this repository (2026-11-14):

| Situation | Action | Approval after the action |
|---|---|---|
| Branch is behind `main`, no conflict | `git merge main` on the PR branch | **preserved** (PR #31) |
| Branch conflicts with `main` | resolve the conflict, commit, push | **dismissed** (PR #27) |

GitHub preserves an approval when the pull request's own diff is unchanged; a conflict resolution
introduces new content, so the approval is treated as stale. Treat the second case as a new review,
not as a bug.

## 2. Non-negotiable rules

1. **Never push after the approval you intend to merge on.** If you must push, the approval is gone;
   request a fresh one.
2. **Write the review record on the pull request's own branch**, before the reviewer approves
   (`docs/review-memo/PR-<n>.md`, manual 7.5/7.6). Do not open a separate "batch of review records"
   pull request: it appends to the same file as the PRs it records and conflicts by construction.
3. **One approval per pull request, from someone other than its author.** Never disable
   `dismiss_stale_reviews`, lower the approval count, add an admin bypass, or merge without review.
   That evidence is graded (D7).
4. **A red gate is not negotiated.** Fix the content; never weaken a check, add `skip`, or use
   `|| true`.
5. **After a merge, sync `main` and re-run the preflight** before touching the next PR.

## 2.1 The merge lock — one conflicting approval in flight

The append-only records are sharded by member (`docs/ai-use-log/<member>.yaml`) and by PR
(`docs/review-memo/PR-<n>.md`), so a pull request that is behind `main` can be updated with
`git merge main` without a conflict. A conflict-free update normally preserves the approval.

The lock is therefore narrower than "one approval total":

1. **Clean pull requests may be batch-approved.** After each merge, update the rest with
   `git merge main` and check `reviewDecision` still says `APPROVED`.
2. **A pull request whose update conflicts must be resolved and approved again.** Serialize only
   those: one conflicting approval in flight.
3. The reviewer approves only when the merger is available for the next few minutes.
4. The merger merges immediately after the approval, then releases the lock.
5. If an update is not conflict-free, treat the approval as gone and request a fresh one. Do not
   merge on the old approval.

The lock is a queue discipline, not a GitHub setting. It is what turns "resolve conflicts before
approval" from advice into a guarantee without forcing a single approval at a time.

## 3. Classify the queue

Run the preflight (§6) and put every open PR in one of four buckets:

| Bucket | GitHub state | Action |
|---|---|---|
| Ready | `CLEAN` + `APPROVED` | merge now (`gh pr merge <n> --squash --delete-branch`) |
| Behind, clean | `BEHIND`/`MERGEABLE` + `APPROVED` | `git merge main`, push once, wait for checks, merge; approval normally survives |
| Conflicting | `DIRTY`/`CONFLICTING` | resolve, push once, run local verification, then request **one** approval and merge immediately |
| Waiting | `BLOCKED`, `REVIEW_REQUIRED` | do not merge; wait for a reviewer or split the work |

A PR that is `BEHIND` but whose diff conflicts with `main` is in the **Conflicting** bucket; the
`mergeable` field is the authority, not `mergeStateStatus`.

## 4. Ordering a batch

1. Build the conflict graph (§6). Two PRs that edit the same append-only region conflict with each
   other even when each is clean against `main`.
2. Merge the independent, already-approved PRs first. They do not invalidate the others.
3. For a conflicting pair, choose the one that must land first (dependency or the PR whose approval
   is still valid), merge it, then update the second.
4. Never approve two conflicting PRs "in parallel" and hope to merge both. The second will need a
   push, and a push after approval is exactly the cost this runbook removes.
5. If a batch of review records is needed, put each record on its own PR branch as step 2 of §2.

## 5. Procedure

```text
1. Sync main and freeze pushes:      git switch main && git pull --ff-only
2. Preflight the queue:              §6
3. Merge the first Ready PR (human): gh pr merge <n> --squash --delete-branch
4. Sync main:                        git switch main && git pull --ff-only
5. For the next PR:
   a. clean-behind:                  git switch <branch> && git merge main && git push
   b. conflicting:                   git switch <branch> && git merge main
                                     resolve the union, run local verification, git push
6. Wait for the gates:               gh pr checks <n>
7. Request the one approval:         reviewer reads, pushes the record if needed, approves
8. Merge immediately:                gh pr merge <n> --squash --delete-branch
9. Delete the local branch:          git branch -d <branch>
10. Repeat from step 4.
```

**Local verification before the final push** (the same three tiers the gates use):

```bash
.venv/bin/python -m pytest -q
.venv/bin/ruff check src
.venv/bin/check-jsonschema --schemafile docs/req/req-schema.json docs/req/requirements.yaml
```

## 6. Preflight (read-only)

Run from the repository root. It does not write to GitHub or to the repository.

```bash
# 1. Fetch and show the queue
git fetch origin --prune
gh pr list --state open --limit 50 \
  --json number,title,headRefName,mergeable,mergeStateStatus,reviewDecision,isDraft \
  --jq '.[] | [.number,.mergeStateStatus,.mergeable,.reviewDecision,.isDraft,.headRefName] | @tsv'

# 2. Conflicts against main, and pairwise conflicts
for b in $(gh pr list --state open --limit 50 --json headRefName --jq '.[].headRefName'); do
  ref="origin/$b"
  git rev-parse --verify --quiet "$ref" >/dev/null || { echo "missing $ref"; continue; }
  base=$(git merge-base origin/main "$ref")
  n=$(git merge-tree "$base" origin/main "$ref" | grep -c '^<<<<<<<\|^+<<<<<<<')
  printf '%s\t%s\n' "$n" "$b"
done | sort -n

# 3. Gate status for the head of each PR
for n in $(gh pr list --state open --limit 50 --json number --jq '.[].number'); do
  printf 'PR %s: ' "$n"
  gh pr checks "$n" 2>/dev/null | awk '{print $2}' | sort -u | tr '\n' ' '
  echo
done

# 4. The merge lock: this must print zero or one PR
gh pr list --state open --limit 50 --json number,reviewDecision \
  --jq '.[] | select(.reviewDecision=="APPROVED") | .number'
```

Interpretation of step 4: an empty result means no approval is waiting. One or more numbers are
allowed when their updates are conflict-free: merge them in order, updating each with
`git merge main` and checking `reviewDecision` after every update. A conflicting approved PR must
be resolved and re-approved; do not batch those.

Interpretation:

- `0` conflicts and `APPROVED` → Ready.
- `0` conflicts and `BEHIND` → Behind, clean; update with `git merge main`.
- More than `0` conflicts → Conflicting; resolve before asking for the final approval.
- `REVIEW_REQUIRED` → Waiting; do not weaken the branch protection to skip it.

## 7. Review record shape

The reviewer creates one file per PR, `docs/review-memo/PR-<n>.md`:

```text
### PR-<n> — <CHG-id> <title>
- Reviewer: <handle>
- Specification: ...
- Architecture: ...
- Code and tests: ...
- Runtime metadata: ...
- Safety and efficiency: ...
- Record truth: ...
- Tests: test/offline/test_foo.py, test/offline/test_bar.py
- Verdict: APPROVE | CHANGES REQUIRED | REJECT
```

Recommended command sequence for the reviewer:

```bash
gh pr checkout <n>
mkdir -p docs/review-memo
# create docs/review-memo/PR-<n>.md with the record above
git add docs/review-memo/PR-<n>.md
git commit -m "docs: record the review of PR #<n> under CHG-<id>"
git push
gh pr review <n> --approve --body "Review record pushed; gates green."
```

The author must not push after this approval. If they do, the approval is stale and the reviewer
must decide again.

## 8. Rollback

- A bad merge on `main`: open a `fix/` PR that reverts the squash commit; review and merge it. Never
  force-push or rewrite `main`.
- A wrongly resolved conflict before merge: `git merge --abort` (or reset the local merge commit),
  fix it, and re-run the local verification. Do not merge a branch whose conflict resolution was not
  reviewed.
- A dismissed approval: request a new review. Do not disable `dismiss_stale_reviews`; that setting
  protects the relationship between the approval and the content.

## 9. Evidence

Record the train run where it can be audited:

- the pull request body states the order and the dependencies;
- the review memo carries the per-PR verdict and the head SHA;
- `docs/ai-use-log/<member>.yaml` records the agent's contribution (the legacy
  `docs/ai-use-log.yaml` is an archive);
- the session transcript is append-only.

This runbook is itself a change: it follows the same branch, PR, review and merge rules it
describes.
