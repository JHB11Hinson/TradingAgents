# Risk list (D2.10)

**Status:** accepted 2026-11-20. **Owner:** `@JHB11Hinson`, reviewed by the team.
**Requirement:** `D1-REQ-GOV-009` (D2.10). **This artifact is optional** in the course; it is kept
because the project's remaining work is exactly the set of assumptions below.

An assumption that could become a defect, with the review trigger that turns it into one. A risk
without a trigger is a worry; this list has no worries.

| # | Assumption | If it is wrong | Trigger to review | Mitigation / owner |
|---|---|---|---|---|
| R-01 | The 120,000-token baseline is representative of an inherited run | `COST-001`'s 0.374 overstates the saving | before quoting a cost figure in `Report.md`; when a key is available | add a live mode and re-measure (`DEBT-011`) — admin |
| R-02 | Fixed vendor payloads are representative enough for the fixed set | the evaluation passes while a real run behaves differently | when the set grows or a real run contradicts a replay | grow the set from recorded runs — admin + member 3 |
| R-03 | An analysis fits the 50,000 run cap after compaction | a run whose analysis needs far more fails mid-flight (only the PM degrades) | the first real run that exhausts the analysis budget | `DEBT-012`; degrade every agent — admin |
| R-04 | The 2,500-token decision reserve is enough | the PM returns `REVIEW` on a case with a larger decision prompt | a case with a large portfolio context | make the reserve proportional — admin |
| R-05 | The provider price table stays current | the manifest's `est_cost` drifts from the bill | a provider price change; a model added to the catalog | update `telemetry/pricing.py`; `DEBT-003` follow-up — admin |
| R-06 | The 26 quarantined inherited modules stay untouched | a type regression in one of them is not caught | any change to a quarantined module | shrink `mypy-legacy.txt` (`DEBT-009`) — module owner |
| R-07 | GitHub Actions keeps running on the fork | every gate silently stops running | `gh pr checks` is empty | re-enable in the Actions tab (`BUG-004`) — admin |
| R-08 | The memory log's markdown format stays readable | an old log is misparsed after a format change | any change to the entry tag | a format change is a new ADR — admin |
| R-09 | The structured-debate contract can be added without changing the inherited debate | `DEBATE-001/002` slips past the freeze | before the freeze review | `verification-constraints.md` §4 marks it planned — member 1 |
| R-10 | The evaluation thresholds are strict enough | a quality regression passes | whenever the review rate or structured-output rate moves | E-005 in the logbook — admin |

**Review cadence:** the admin checks this list at each sprint review and before the freeze. A risk
whose trigger fired becomes a bug-diary entry, not a line that stays here.
