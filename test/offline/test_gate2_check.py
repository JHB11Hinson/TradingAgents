"""Contract tests for the gate-2 mypy quarantine guard (ADR-016).

The guard lives in .github/scripts/gate2_check.py because it is CI glue, not runtime
code.  It is loaded by path so the test suite does not need a package import.

The ratchet is one-way: the quarantine list docs/code-governance/mypy-legacy.txt may
shrink but must never grow.  A newly added path (compared to the base branch) is a
failed gate; removing a path, or not touching the file, passes.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".github" / "scripts" / "gate2_check.py"
QUARANTINE = "docs/code-governance/mypy-legacy.txt"

spec = importlib.util.spec_from_file_location("gate2_check", SCRIPT)
gate2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate2)


BASE = """\
# inherited modules quarantined (DEBT-009)
src/a.py
src/b.py
"""


class FakeGit:
    def __init__(self, blob):
        self._blob = blob

    def show(self, commit, path):
        if path != QUARANTINE:
            return None
        return self._blob.get(commit)


def run(base_text, head_text):
    git = FakeGit({"origin/main": base_text, "HEAD": head_text})
    return gate2.check(git, "origin/main", "HEAD")


def test_parse_ignores_blanks_and_comments():
    paths = gate2.quarantined_paths("# comment\n\nsrc/a.py\n  \nsrc/b.py\n")
    assert paths == {"src/a.py", "src/b.py"}


def test_adding_a_line_fails():
    head = BASE + "src/c.py\n"
    ok, reason = run(BASE, head)
    assert not ok
    assert "src/c.py" in reason


def test_removing_a_line_passes():
    head = "# inherited modules quarantined (DEBT-009)\nsrc/a.py\n"
    ok, reason = run(BASE, head)
    assert ok, reason


def test_no_change_passes():
    ok, reason = run(BASE, BASE)
    assert ok, reason


def test_comment_only_change_passes():
    head = "# updated note\nsrc/a.py\nsrc/b.py\n"
    ok, reason = run(BASE, head)
    assert ok, reason


def test_missing_base_file_passes():
    git = FakeGit({"origin/main": None, "HEAD": BASE})
    ok, reason = gate2.check(git, "origin/main", "HEAD")
    assert ok, reason


def test_both_missing_passes():
    git = FakeGit({"origin/main": None, "HEAD": None})
    ok, reason = gate2.check(git, "origin/main", "HEAD")
    assert ok, reason


def test_swap_reports_only_the_added_path():
    base = "# x\nsrc/a.py\n"
    head = "# x\nsrc/b.py\n"
    ok, reason = run(base, head)
    assert not ok
    assert "src/b.py" in reason
    assert "src/a.py" not in reason


def test_real_quarantine_file_is_readable():
    text = (ROOT / QUARANTINE).read_text(encoding="utf-8")
    paths = gate2.quarantined_paths(text)
    assert len(paths) == 26
    assert all(path.startswith("src/") and path.endswith(".py") for path in paths)


@pytest.mark.parametrize("bad", ["", "# only comments\n"])
def test_empty_list_is_stable(bad):
    ok, reason = run(bad, bad)
    assert ok, reason
