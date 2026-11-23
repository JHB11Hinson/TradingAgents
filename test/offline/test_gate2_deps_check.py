"""Contract tests for the gate-2 dependency-declaration checker (ADR-018).

The checker lives in .github/scripts/gate2_deps_check.py because it is CI glue, and it
uses only the standard library: the tool that detects undeclared dependencies must not
itself be an undeclared dependency.

Rule: every top-level import in src/**/*.py must resolve to the standard library,
first-party code (`tradingagents`, `cli`), or a dependency declared in pyproject.toml.
Module names that differ from their distribution name (`yaml` -> PyYAML,
`dotenv` -> python-dotenv, `PIL` -> Pillow) are resolved through a mapping.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".github" / "scripts" / "gate2_deps_check.py"

spec = importlib.util.spec_from_file_location("gate2_deps_check", SCRIPT)
deps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deps)


def test_import_roots_from_source():
    source = "import os\nimport yaml\nfrom dotenv import load_dotenv\nfrom . import x\n"
    assert deps.import_roots(source) == {"os", "yaml", "dotenv"}


def test_stdlib_modules_are_allowed():
    assert deps.classify("os") == "stdlib"
    assert deps.classify("json") == "stdlib"


def test_first_party_modules_are_allowed():
    assert deps.classify("tradingagents") == "first-party"
    assert deps.classify("cli") == "first-party"


def test_mapping_resolves_known_mismatches():
    assert deps.distribution_for("yaml") == "pyyaml"
    assert deps.distribution_for("dotenv") == "python-dotenv"
    assert deps.distribution_for("dateutil") == "python-dateutil"
    assert deps.distribution_for("markdown_it") == "markdown-it-py"
    assert deps.distribution_for("PIL") == "pillow"


def test_distribution_name_normalisation_folds_case_and_separators():
    assert deps.normalize("PyYAML") == deps.normalize("pyyaml")
    assert deps.normalize("python_dotenv") == deps.normalize("python-dotenv")


def test_declared_import_passes():
    declared = {"pyyaml", "python-dotenv"}
    problems = deps.undeclared({"yaml", "dotenv", "os", "tradingagents"}, declared)
    assert problems == []


def test_undeclared_import_is_reported():
    declared = {"pyyaml"}
    problems = deps.undeclared({"unknown_pkg"}, declared)
    assert len(problems) == 1
    assert "unknown_pkg" in problems[0]


def test_mapped_but_undeclared_is_reported():
    declared: set[str] = set()
    problems = deps.undeclared({"yaml"}, declared)
    assert any("yaml" in problem and "pyyaml" in problem for problem in problems)


def test_declared_names_load_from_pyproject():
    declared = deps.declared_distributions(ROOT / "pyproject.toml")
    assert "pyyaml" in declared
    assert "langchain-core" in declared
    assert "langchain-aws" in declared


def test_real_source_tree_has_no_undeclared_imports():
    declared = deps.declared_distributions(ROOT / "pyproject.toml")
    roots: set[str] = set()
    for path in (ROOT / "src").rglob("*.py"):
        roots |= deps.import_roots(path.read_text(encoding="utf-8"))
    assert deps.undeclared(roots, declared) == []
