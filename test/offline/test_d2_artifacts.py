"""Verifies D1-REQ-GOV-009: the D2 architecture set exists and matches the code.

Every artifact the registry names must be present and non-empty, and every module
the blueprint names as a component must exist on disk. A missing file or a
blueprint that points at a module which was moved or renamed is a review blocker,
so the check fails rather than warns.
"""

from __future__ import annotations

import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]

D2_ARTIFACTS = (
    "architecture-blueprint.md",
    "docs/architecture/adr/001-adopt-inherited-architecture.md",
    "docs/architecture/invariants.md",
    "docs/architecture/trace-matrix.md",
    "docs/architecture/memory-design.md",
    "docs/architecture/permission-model.md",
    "docs/architecture/runtime-policy-catalog.md",
    "docs/architecture/evaluation-table.md",
    "docs/architecture/evaluation-logbook.md",
    "docs/architecture/risk-list.md",
    "docs/architecture/option-ledger.md",
)

# The blueprint names components as `src/...` code spans; each one must exist.
MODULE = re.compile(r"`(src/[A-Za-z0-9_./-]+)`")


@pytest.mark.unit
@pytest.mark.parametrize("artifact", D2_ARTIFACTS)
def test_each_d2_artifact_exists_and_is_not_empty(artifact):
    path = REPO / artifact

    assert path.is_file(), f"{artifact} is missing"
    text = path.read_text(encoding="utf-8")
    assert text.lstrip().startswith("#"), f"{artifact} has no title"
    assert len(text) > 400, f"{artifact} is too short to be an artifact"


@pytest.mark.unit
def test_every_module_the_blueprint_names_exists():
    blueprint = (REPO / "architecture-blueprint.md").read_text(encoding="utf-8")
    named = sorted(set(MODULE.findall(blueprint)))

    assert named, "the blueprint names no modules"
    missing = [name for name in named if not (REPO / name).exists()]
    assert missing == [], f"the blueprint names missing module(s): {missing}"


@pytest.mark.unit
def test_the_optional_artifacts_say_why_they_are_optional():
    for artifact in (
        "docs/architecture/evaluation-logbook.md",
        "docs/architecture/risk-list.md",
        "docs/architecture/option-ledger.md",
    ):
        text = (REPO / artifact).read_text(encoding="utf-8").lower()
        assert "optional" in text, f"{artifact} must say it is optional (course D2.9–D2.11)"
