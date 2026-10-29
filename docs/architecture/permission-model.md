# Permission model (default deny)

**Deliverable:** D2.6 / D3. **Requirement:** `D1-REQ-GOV-006`.
**Machine-readable source:** `.opencode/permissions.jsonc`. **Summary:** `AGENTS.md` §13.
**Decision record:** ADR-003.

This file, `.opencode/permissions.jsonc` and `AGENTS.md` §13 list the **same** whitelist. If any path
appears in one and not the others, the consistency check fails and the change is rejected.

---

## 1. Default and precedence

- **Default: deny.** Nothing is readable, writable or executable until a whitelist entry allows it.
- **Precedence: deny > ask > allow.** A narrower rule overrides a broader one; an unknown path or
  command is denied.
- A wildcard covers whole subtrees; an explicit path overrides a wildcard for the same subtree.

## 2. Roles

One whitelist, three modes. The role is chosen from the task, not from the `gh` account.

| Role | Read | Write | Commands |
|---|---|---|---|
| `plan` | the read whitelist | **deny** | read-only |
| `build` | the read whitelist | the write whitelist | the command whitelist |
| `review` | the read whitelist | `/tmp` drafts only | read-only |

## 3. Read whitelist

| Mode | Paths |
|---|---|
| **allow** | `AGENTS.md`, `Prompt.md`, `README.md`, `architecture-blueprint.md`, `Report.md`, `CHANGELOG.md`, `docs/**`, `src/**`, `test/**`, `prompts/**`, `eval/**`, `transcripts/**`, `.github/**`, `.agent/**`, `.opencode/rules.md`, `.opencode/tasks/**`, `pyproject.toml`, `requirements.txt`, `mypy.ini`, `Dockerfile`, `docker-compose.yml` |
| **deny** | `.env`, `.env.*`, `*.key`, `*.pem`, `*.p12`, `~/.ssh/**`, `~/.aws/**`, `~/.config/gh/**` |

## 4. Write whitelist

| Mode | Paths |
|---|---|
| **allow** | `src/**`, `test/**`, `docs/**`, `transcripts/**` (append-only), `prompts/**` (new versioned files only), `README.md`, `architecture-blueprint.md` |
| **ask** | `AGENTS.md`, `Prompt.md`, `.github/**`, `.agent/**`, `.opencode/**`, `pyproject.toml`, `requirements.txt`, `docs/req/req-schema.json`, `docs/code-governance/**`, `docs/architecture/permission-model.md` |
| **deny** | `.opencode/rules.md`, `.opencode/tasks/**`, `.opencode/git-gh-rules/**`, `.env`, `.env.*`, `*.key`, `*.pem`, `.git/**`, `.venv/**` |

`docs/**` is allowed, but `docs/code-governance/**` and `docs/architecture/permission-model.md` are
narrower **ask** entries and therefore win. `transcripts/**` is append-only; `prompts/**` accepts new
versioned files only.

## 5. Command whitelist

| Mode | Commands |
|---|---|
| **allow** | `git status`, `git diff`, `git log`, `git show`, `git fetch`, `git switch`, `git add`, `git commit`, `git branch`, `git push origin HEAD`, `git push --force-with-lease origin HEAD` (your own branch only), `gh pr list`, `gh pr view`, `gh pr diff`, `gh pr checks`, `gh pr create`, `gh run list`, `gh run view`, `gh api` (GET only), `pytest`, `python -m pytest`, `ruff`, `mypy`, `check-jsonschema`, `pip install`, `python -m build` |
| **ask** | `git commit --amend`, `git add -A`, `git add .`, `git push --force`, `git tag`, `git revert`, `gh pr review`, `gh pr comment`, `gh pr close`, `gh pr edit` |
| **deny** | `git push origin main`, `git push --force origin main`, `git push upstream`, `git reset --hard`, `git clean -fdx`, `git filter-repo`, `gh pr merge`, `gh api --method PUT`, `gh api --method POST`, `gh api --method PATCH`, `gh api --method DELETE` |

`gh api` with `-f` / `-F` is a write, not a GET, and is denied. `gh pr merge` is a human action.

## 6. Guard rules (always deny)

1. The most restrictive matching rule wins; an unknown path or command is denied.
2. `.opencode/rules.md` is human-only; no agent role may write it.
3. No secret, `.env`, key or token may be read, printed or committed.
4. Never push to `main` or `upstream`; never force-push or delete `main`.
5. No `gh api` write to branch protection, Actions, collaborators, secrets or webhooks.
6. No `gh pr merge` and no self-approval; a human merges.
7. No test weakening to make a gate pass.
8. No shared-history rewrite (`reset --hard`, `clean -fdx`, `filter-repo`, `-X ours/theirs`).

## 7. Authority boundary

Independent of the file whitelist, the product keeps one authority boundary: **model output is
advisory; deterministic code is authoritative.** Position size passes a deterministic ceiling, and a
decision whose schema fails validation is rejected and degraded to `REVIEW` rather than emitted
(`D1-REQ-SAFE-002`, `D1-REQ-SAFE-003`). No permission here lets model output bypass that code.

## 8. Enforcement

| Layer | Mechanism |
|---|---|
| Runtime | OpenCode permission settings derived from `.opencode/permissions.jsonc` (edit / bash / webfetch) |
| CI | `gate-3-schema`, `gate-5-regression`, `gate-6-ai-use-log`; further gates as they come online |
| Repository | branch protection on `main`: 1 approval, strict, `enforce_admins`, no force push, no deletion |
| Human | every pull request is reviewed; safety-critical changes need an ADR |

On violation: **stop**, report to the human, and record the incident in `docs/bug-diary.md`.

## 9. Consistency check

```bash
# the three sources must list the same allow/ask/deny sets
grep -o '`[^`]*`' AGENTS.md | sed -n '/^## 13\./,$p' | sort -u > /tmp/agents-paths.txt
python3 - <<'PY'
import json, re
src = open('.opencode/permissions.jsonc').read()
src = re.sub(r'(?m)^\s*//.*$', '', src)
m = json.loads(src)
for key in ('read', 'write'):
    for mode in ('allow', 'ask', 'deny'):
        print(key, mode, sorted(m[key].get(mode, [])))
PY
```

The check is a review step, not a gate yet; `verification-constraints.md` records it as a
`D1-REQ-GOV-006` check when that file lands.
