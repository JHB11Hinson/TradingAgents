# MCP and tool manifest (tools × roles)

**Deliverable:** D3. **Requirement:** `D1-REQ-GOV-005`.
**Machine-readable permissions:** `.opencode/permissions.jsonc`. **Prose:** `docs/architecture/permission-model.md`.
**Roles:** the same three as the permission model — `plan`, `build`, `review`.

This file names **every tool the coding agent can call** and **which role may call it**. A tool that
is not listed here is denied. If a role/tool pair disagrees with `.opencode/permissions.jsonc` or
`docs/architecture/permission-model.md`, the change is rejected.

---

## 1. MCP servers

**None.** No MCP server is configured for this repository; the agent's MCP resource list is empty.

| Server | Status |
|---|---|
| — | none configured |

If an MCP server is added later, this table gains one row per server, the permission model gains the
corresponding paths/tools, and both changes land in the same pull request.

## 2. Native tools

The coding agent's native tools, as observed in this workspace:

| # | Tool | What it does |
|---|---|---|
| 1 | `read` | read a file or directory |
| 2 | `write` | create or overwrite a file |
| 3 | `edit` | targeted replacement inside a file |
| 4 | `grep` | search file contents |
| 5 | `glob` | find paths by pattern |
| 6 | `shell` | run a shell command |
| 7 | `webfetch` | fetch an HTTP(S) URL |
| 8 | `websearch` | search the web |
| 9 | `skill` | load a skill's instructions |
| 10 | `question` | ask the human a multiple-choice question |
| 11 | `subagent` | start a child agent with its own context |
| 12 | `execute` | run the confined Code Mode runtime (calls the tools above) |
| 13 | `search` | discover tools inside Code Mode |
| 14 | `browser` | open, read, navigate and preview pages in a desktop browser |
| 15 | `opencode` | inspect/rename/move sessions, list models, read MCP resources |
| 16 | `cmd_plan_summary` | report the current account/plan (read-only) |

## 3. Tool × role matrix

| Tool | `plan` | `build` | `review` | Notes |
|---|---|---|---|---|
| `read`, `grep`, `glob` | allow | allow | allow | the **read whitelist** applies; `.env*`, keys and `~/.ssh` stay denied |
| `write`, `edit` | **deny** | allow | **deny** | the **write whitelist** and its ask tier apply; `review` may only draft under `/tmp` |
| `shell` | read-only | allow | read-only | the **command whitelist** applies (allow / ask / deny) |
| `webfetch`, `websearch` | allow | allow | allow | read-only; never place a secret in a URL; no authenticated endpoint |
| `skill` | allow | allow | allow | loads local instructions only |
| `question` | allow | allow | allow | human-facing; carries no write |
| `subagent` | deny | **ask** | deny | a subagent inherits this manifest and the same role |
| `execute`, `search` | allow | allow | allow | only the tools listed here are reachable |
| `browser` | ask | ask | ask | read-only browsing; never submit a form, log in, or enter credentials |
| `opencode` | allow | allow | allow | `session_move` / `session_rename` are **ask**; the rest is read-only |
| `cmd_plan_summary` | allow | allow | allow | read-only |

**Unknown tool → deny.** **Deny wins over ask, ask over allow** — the same precedence as the
permission model.

## 4. Notes that keep this manifest honest

1. `write` / `edit` never bypass the write whitelist: the tool is allowed, the **path** decides.
2. `shell` never bypasses the command tiers: `git push --force`, `gh pr merge`, `gh api` writes and
   history rewrites stay denied even though `shell` itself is allowed.
3. `webfetch` / `websearch` / `browser` are the only network-capable tools; none of them may carry a
   credential, and none is used to reach an authenticated API. Runtime data access happens in the
   product (`src/tradingagents/dataflows/`), not through the coding agent.
4. `subagent` is `ask` because a child agent could otherwise accumulate permissions the parent
   presented to the human; the child inherits the same role and whitelist.
5. This manifest is documentation of the tool surface, not a runtime policy engine. The runtime layer
   is the OpenCode permission settings derived from `.opencode/permissions.jsonc`.

## 5. Consistency check

```bash
# every tool named in the permission model must be named here, and vice versa
grep -oE '`(read|write|edit|grep|glob|shell|webfetch|websearch|skill|question|subagent|execute|search|browser|opencode|cmd_plan_summary)`' \
  .opencode/permissions.jsonc docs/architecture/permission-model.md | sort -u
grep -oE '^\| `[a-z_, `]+`' docs/code-governance/mcp-tool-manifest.md | sort -u
```

A mismatch is a review blocker for any change touching the tool surface.
