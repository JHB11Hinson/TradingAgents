# Review memos (one file per pull request)

`docs/review-memo.md` is a **historical archive** through 2026-11-15. New review records go to:

```text
docs/review-memo/PR-<number>.md
```

## Why

The old single file was append-only, so two pull requests that both added a record conflicted at
the same end of the file. Resolving that conflict changed the reviewed head and dismissed the
approval. One file per PR removes the conflict: the reviewer creates a new file, and the PR branch
stays conflict-free when it is updated to the latest `main`.

## Rules

1. **One file per PR**, named with the pull-request number (`PR-32.md`).
2. **The reviewer writes it**, on the PR branch, **before** clicking Approve (manual 7.5/7.6).
3. It must contain at least:
   - `Reviewer:`
   - `Verdict: APPROVE | CHANGES REQUIRED | REJECT`
   - `Tests:` with the test paths that cover the change (inherited tests are allowed)
4. **Do not edit the archive.** `docs/review-memo.md` keeps its historical entries; only its header
   note may change.
5. A PR merge does not delete its record: the file stays as evidence.

## Shape

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
- Verdict: APPROVE
```

## Review order

1. `gh pr checkout <n>`
2. create `docs/review-memo/PR-<n>.md`
3. commit and push it to the PR branch
4. run the six-item review and post the verdict

The author must not push after the approval. If they do, the approval is stale and the reviewer
must decide again.
