"""Verifies D1-REQ-GOV-001: the README states how to run the offline, the live and the full suite.

CHG-052 adds the troubleshooting section for the one failure mode a fresh checkout hits: the
offline tests run against `src/` because `pyproject.toml` sets `pythonpath = ["src"]`, while the
evaluator is invoked as a subprocess (`python -m eval.run`) and therefore imports whatever the
**installed** package resolves to. Two checkouts that share one editable install can disagree, and
the evaluator test fails with a `ModuleNotFoundError` that `pip install -e ".[dev]"` fixes.

The tests pin the section's presence and the commands it names, not its wording, so a future edit
can rephrase it without breaking the suite.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
README = REPO / "README.md"
PYPROJECT = REPO / "pyproject.toml"


@pytest.fixture(scope="module")
def readme() -> str:
    return README.read_text(encoding="utf-8")


@pytest.mark.unit
def test_the_readme_has_a_troubleshooting_section(readme: str) -> None:
    assert re.search(r"(?m)^## \d+\. Troubleshooting", readme), (
        "README must carry a numbered Troubleshooting section so the evaluator failure is findable"
    )


@pytest.mark.unit
def test_the_troubleshooting_section_names_the_editable_install(readme: str) -> None:
    section = _section(readme, "Troubleshooting")
    assert 'pip install -e ".[dev]"' in section, (
        "the fix a reader needs is `pip install -e \".[dev]\"`; the section must name it verbatim"
    )


@pytest.mark.unit
def test_the_troubleshooting_section_names_the_installed_package_rule(readme: str) -> None:
    section = _section(readme, "Troubleshooting")
    assert "python -m eval.run" in section, (
        "the section must point at the evaluator, the only command that runs as a subprocess"
    )
    assert re.search(r"installed", section, re.IGNORECASE), (
        "the section must explain that the subprocess uses the installed package"
    )


@pytest.mark.unit
def test_the_offline_tests_scope_is_stated(readme: str) -> None:
    section = _section(readme, "Run the tests")
    assert "pytest -q test/offline" in section
    assert "pytest -q -m integration" in section, (
        "GOV-001 requires the README to state how to run the live suite"
    )


@pytest.mark.unit
def test_the_pythonpath_setting_explains_why_tests_and_the_subprocess_differ() -> None:
    """The README's explanation is only true while pyproject keeps `pythonpath = ["src"]`."""
    pyproject = PYPROJECT.read_text(encoding="utf-8")
    assert re.search(r'(?m)^pythonpath = \["src"\]$', pyproject), (
        "the README's rule depends on pytest importing from src/; update both together"
    )


def _section(readme: str, title: str) -> str:
    """Return the body of the numbered `## N. <title>` section, up to the next `## N.` heading."""
    match = re.search(
        rf"(?ms)^## \d+\. {re.escape(title)}\n(.*?)(?=^## \d+\. |\Z)",
        readme,
    )
    assert match is not None, f"README is missing the '{title}' section"
    return match.group(1)
