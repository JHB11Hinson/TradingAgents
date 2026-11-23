"""Contract tests for the gate-2 safety-path guard (ADR-018).

The guard lives in .github/scripts/gate2_safety_check.py because it is CI glue. It is
loaded by path so the suite needs no package import.

Rule: a pull request that changes a safety-critical path (listed in
docs/code-governance/safety-paths.txt) must also add or modify an ADR under
docs/architecture/adr/ in the same diff. A PR that touches no safety path, or one that
touches a safety path and carries an ADR, passes.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".github" / "scripts" / "gate2_safety_check.py"
SAFETY_FILE = "docs/code-governance/safety-paths.txt"

spec = importlib.util.spec_from_file_location("gate2_safety_check", SCRIPT)
safety = importlib.util.module_from_spec(spec)
spec.loader.exec_module(safety)


class FakeGit:
    def __init__(self, changed):
        self._changed = changed

    def changed_files(self, base, head):
        return list(self._changed)


def run(changed, base="origin/main", head="HEAD"):
    return safety.check(FakeGit(changed), base, head)


PATHS = "# safety-critical paths\nsrc/tradingagents/default_config.py\nsrc/tradingagents/guardrails/\n"


def test_parse_safety_paths_ignores_blanks_and_comments():
    assert safety.parse_safety_paths(PATHS) == [
        "src/tradingagents/default_config.py",
        "src/tradingagents/guardrails/",
    ]


def test_missing_safety_file_is_a_failure(tmp_path):
    ok, reason = safety.check(FakeGit([]), "origin/main", "HEAD", safety_file=tmp_path / "absent.txt")
    assert not ok


def test_safety_path_change_without_adr_fails(tmp_path):
    path = tmp_path / "safety.txt"
    path.write_text("src/tradingagents/default_config.py\n", encoding="utf-8")
    ok, reason = run(["src/tradingagents/default_config.py"], safety_file=path)
    assert not ok
    assert "ADR" in reason


def test_safety_path_change_with_adr_passes(tmp_path):
    path = tmp_path / "safety.txt"
    path.write_text("src/tradingagents/default_config.py\n", encoding="utf-8")
    ok, reason = run(
        ["src/tradingagents/default_config.py", "docs/architecture/adr/018-x.md"],
        safety_file=path,
    )
    assert ok, reason


def test_no_safety_path_change_passes(tmp_path):
    path = tmp_path / "safety.txt"
    path.write_text("src/tradingagents/default_config.py\n", encoding="utf-8")
    ok, reason = run(["src/tradingagents/dataflows/date_window.py"], safety_file=path)
    assert ok, reason


def test_directory_prefix_matches(tmp_path):
    path = tmp_path / "safety.txt"
    path.write_text("src/tradingagents/guardrails/\n", encoding="utf-8")
    ok, reason = run(["src/tradingagents/guardrails/positions.py"], safety_file=path)
    assert not ok


def test_directory_prefix_without_adr_and_with_other_files_still_fails(tmp_path):
    path = tmp_path / "safety.txt"
    path.write_text("src/tradingagents/guardrails/\n", encoding="utf-8")
    ok, _ = run(
        ["README.md", "src/tradingagents/guardrails/instructions.py"],
        safety_file=path,
    )
    assert not ok


def test_real_safety_file_is_readable_and_named():
    paths = safety.parse_safety_paths((ROOT / SAFETY_FILE).read_text(encoding="utf-8"))
    assert paths
    assert any("default_config" in path for path in paths)
    assert any("guardrails" in path for path in paths)


def test_real_safety_file_change_without_adr_fails():
    paths = safety.parse_safety_paths((ROOT / SAFETY_FILE).read_text(encoding="utf-8"))
    touched = paths[0].rstrip("/")
    ok, _ = safety.check(FakeGit([touched]), "origin/main", "HEAD")
    assert not ok
