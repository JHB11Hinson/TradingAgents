"""Verifies D1-REQ-GOV-009: an accepted ADR cites a pull request that exists.

An `accepted` record is evidence that a decision was reviewed. When the record names the pull
request that carried it, that number must resolve to a review record under `docs/review-memo/`;
otherwise the traceability chain is broken and a reader cannot follow it.

The guard lives in `.github/scripts/adr_status_check.py` because it is CI glue, not runtime code.
It is loaded by path so the suite does not need a package import, the same way
`test_gate2_check.py` loads `gate2_check.py`.

The check is deliberately narrow, because the real corpus is irregular:

* only `accepted` ADRs are checked; a `proposed` record may cite a pull request that is still
  open, so its number is not verified;
* an `accepted` ADR that names no pull request at all is **exempt**, not broken: the inherited
  records predate the per-PR record convention;
* a citation must use the project's explicit forms, `PR #<n>` or `PR-<n>`; a bare number is not a
  citation.

The PR-existence predicate is a parameter, so the tests inject a set of known numbers instead of
calling GitHub. The tracked corpus is checked against the repository's own `docs/review-memo/`
directory, which is the same evidence a reader would use.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".github" / "scripts" / "adr_status_check.py"
ADR_DIR = ROOT / "docs" / "architecture" / "adr"

spec = importlib.util.spec_from_file_location("adr_status_check", SCRIPT)
adr_status = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adr_status)


# --- the tracked corpus ---------------------------------------------------------------------


@pytest.mark.unit
def test_every_adr_has_a_known_status() -> None:
    for number, _path, text in adr_status.read_adrs(ADR_DIR):
        status = adr_status.status_of(text)
        assert status is not None, f"ADR-{number} has no parseable status line"
        assert status in adr_status.KNOWN_STATUSES, f"ADR-{number} has unknown status {status!r}"


@pytest.mark.unit
def test_every_accepted_adr_that_cites_a_pr_cites_a_recorded_one() -> None:
    problems = adr_status.check(adr_status.read_adrs(ADR_DIR), adr_status.memo_exists_factory(ROOT))
    assert not problems, "ADR/PR traceability is broken:\n  " + "\n  ".join(problems)


@pytest.mark.unit
def test_the_corpus_actually_exercises_the_check() -> None:
    """A green result must come from real citations, not from parsing nothing."""
    cited = [
        number
        for number, _path, text in adr_status.read_adrs(ADR_DIR)
        if adr_status.status_of(text) == "accepted" and adr_status.cited_prs(text)
    ]
    assert cited, "no accepted ADR cites a PR; the corpus-level test would pass vacuously"


# --- R1: accepted ADR citing a real PR -------------------------------------------------------


@pytest.mark.unit
def test_r1_an_accepted_adr_citing_a_real_pr_passes() -> None:
    text = "# ADR-900: x\n\n- Status: accepted by the review on PR #40\n"
    assert adr_status.check([("900", Path("900-x.md"), text)], lambda n: n == 40) == []


# --- R2: accepted ADR citing a missing PR ----------------------------------------------------


@pytest.mark.unit
def test_r2_an_accepted_adr_citing_a_missing_pr_fails() -> None:
    text = "# ADR-900: x\n\n- Status: accepted by the review on PR #9999\n"
    problems = adr_status.check([("900", Path("900-x.md"), text)], lambda _n: False)
    assert len(problems) == 1
    assert "ADR-900" in problems[0] and "#9999" in problems[0]


# --- R5b: a proposed ADR is not verified -----------------------------------------------------


@pytest.mark.unit
def test_r5b_a_proposed_adr_does_not_trigger_the_pr_check() -> None:
    text = "# ADR-900: x\n\n- **Status:** proposed (PR-9999, 2026-11-23)\n"
    assert adr_status.check([("900", Path("900-x.md"), text)], lambda _n: False) == []


# --- negative: a bare number is not a citation -----------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    "line",
    [
        "CHG-049 finished on day 42 of the sprint.",
        "See item 58 in the list below.",
        "The only change was the 2026-11-22 release.",
        "A PR without a number is not a citation.",
    ],
)
def test_a_bare_number_is_not_parsed_as_a_pr_citation(line: str) -> None:
    assert adr_status.cited_prs(line) == []


@pytest.mark.unit
def test_the_two_supported_forms_are_both_parsed() -> None:
    assert adr_status.cited_prs("reviewed on PR #40 and earlier on PR-58") == [40, 58]


@pytest.mark.unit
def test_every_citation_is_verified_not_only_the_first() -> None:
    text = "# ADR-900: x\n\n- Status: accepted\n- Reviewed on PR #40 and PR #9999\n"
    problems = adr_status.check([("900", Path("900-x.md"), text)], lambda n: n == 40)
    assert len(problems) == 1 and "#9999" in problems[0]


# --- exemption: an accepted ADR with no citation ---------------------------------------------


@pytest.mark.unit
def test_exemption_an_accepted_adr_without_a_citation_passes() -> None:
    text = "# ADR-900: x\n\n- Status: accepted, implemented in CHG-033\n"
    assert adr_status.check([("900", Path("900-x.md"), text)], lambda _n: False) == []


@pytest.mark.unit
def test_unreferenced_accepted_adrs_are_exempt_not_broken() -> None:
    """The inherited records predate the per-PR convention; naming no PR is allowed.

    This is the corpus-level form of the exemption: even when *no* PR exists at all, an accepted
    ADR that cites nothing must not be reported.
    """
    adrs = adr_status.read_adrs(ADR_DIR)
    exempt = [
        number
        for number, _path, text in adrs
        if adr_status.status_of(text) == "accepted" and not adr_status.cited_prs(text)
    ]
    assert exempt, "the exemption is only meaningful while such records exist"
    problems = adr_status.check(adrs, lambda _number: False)
    for number in exempt:
        assert not any(problem.startswith(f"ADR-{number}:") for problem in problems), (
            f"ADR-{number} names no PR and must be exempt, not reported"
        )


@pytest.mark.unit
def test_the_status_parser_handles_every_shape_in_the_corpus() -> None:
    assert adr_status.status_of("- Status: accepted") == "accepted"
    assert adr_status.status_of("- Status: accepted, implemented in CHG-033") == "accepted"
    assert adr_status.status_of("- Status: **accepted** 2026-11-20. The decision") == "accepted"
    assert adr_status.status_of("- **Status:** accepted (CHG-042, 2026-11-21). Approved") == "accepted"
    assert adr_status.status_of("- **Status:** proposed (PR-3, 2026-11-23) — awaiting") == "proposed"


@pytest.mark.unit
def test_a_missing_status_line_is_reported() -> None:
    problems = adr_status.check([("900", Path("900-x.md"), "# ADR-900: x\n\nno status\n")], lambda _n: True)
    assert problems and "no status line" in problems[0]
