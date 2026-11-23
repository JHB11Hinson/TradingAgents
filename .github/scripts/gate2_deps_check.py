#!/usr/bin/env python3
"""gate-2 dependency-declaration checker (ADR-018).

Every top-level import in ``src/**/*.py`` must resolve to the standard library,
first-party code (``tradingagents``, ``cli``) or a dependency declared in
``pyproject.toml``. The checker uses only the standard library: the tool that detects
undeclared dependencies must not itself be an undeclared dependency.

Module names and distribution (pip package) names differ (``yaml`` -> PyYAML,
``dotenv`` -> python-dotenv, ``PIL`` -> Pillow); ``MODULE_TO_DIST`` resolves them.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
import tomllib
from pathlib import Path

FIRST_PARTY = {"tradingagents", "cli"}

# module root -> distribution name; compared after normalize().
MODULE_TO_DIST = {
    "yaml": "pyyaml",
    "dotenv": "python-dotenv",
    "dateutil": "python-dateutil",
    "markdown_it": "markdown-it-py",
    "PIL": "pillow",
    "langchain_core": "langchain-core",
    "langchain_anthropic": "langchain-anthropic",
    "langchain_google_genai": "langchain-google-genai",
    "langchain_openai": "langchain-openai",
    "langchain_aws": "langchain-aws",
    "langgraph": "langgraph",
    "typing_extensions": "typing-extensions",
    "stockstats": "stockstats",
    "questionary": "questionary",
}

_REQ_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


def normalize(name: str) -> str:
    return name.strip().lower().replace("_", "-")


def import_roots(source: str) -> set[str]:
    roots: set[str] = set()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def distribution_for(module: str) -> str:
    return MODULE_TO_DIST.get(module, module)


def classify(module: str) -> str:
    if module in sys.stdlib_module_names or module in {"__future__"}:
        return "stdlib"
    if module in FIRST_PARTY:
        return "first-party"
    return "third-party"


def declared_distributions(pyproject: Path) -> set[str]:
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    project = data.get("project", {})
    requirements: list[str] = list(project.get("dependencies", []))
    for extra in project.get("optional-dependencies", {}).values():
        requirements.extend(extra)
    names: set[str] = set()
    for requirement in requirements:
        match = _REQ_NAME.match(requirement)
        if match:
            names.add(normalize(match.group(0)))
    return names


def undeclared(roots: set[str], declared: set[str]) -> list[str]:
    problems = []
    for module in sorted(roots):
        kind = classify(module)
        if kind != "third-party":
            continue
        dist = distribution_for(module)
        if normalize(dist) not in declared:
            problems.append(f"import {module!r} needs distribution {dist!r}, which is not declared")
    return problems


def check(src_dir: Path, pyproject: Path) -> tuple[bool, str]:
    declared = declared_distributions(pyproject)
    roots: set[str] = set()
    for path in src_dir.rglob("*.py"):
        roots |= import_roots(path.read_text(encoding="utf-8"))
    problems = undeclared(roots, declared)
    if problems:
        return False, "; ".join(problems)
    return True, f"every third-party import is declared ({len(roots)} roots scanned)"


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--src", default=str(root / "src"))
    parser.add_argument("--pyproject", default=str(root / "pyproject.toml"))
    args = parser.parse_args(argv)

    ok, reason = check(Path(args.src), Path(args.pyproject))
    if ok:
        print(f"gate-2 deps: pass ({reason})")
        return 0

    print(f"::error file=pyproject.toml::gate-2 deps: {reason}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
