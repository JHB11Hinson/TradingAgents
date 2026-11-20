"""Verifies D1-REQ-GOV-003: the six blocking gates exist and agree with protection.

The gate name in `ci.yml` and in the branch-protection `contexts` must match
character for character; a drift leaves a pull request pending forever. The
gate-4 job must run the local evaluator (`EVAL-001`) on the shipped fixed set,
and the evaluator's YAML dependency must be declared rather than imported from a
transitive dependency (debt category 4: hidden dependencies).
"""

from __future__ import annotations

import json
import pathlib
import tomllib

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parents[2]
GATES = (
    "gate-1-test-approval",
    "gate-2-static-analysis",
    "gate-3-schema",
    "gate-4-semantic-eval",
    "gate-5-regression",
    "gate-6-ai-use-log",
)


def _workflow() -> dict:
    return yaml.safe_load((REPO / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8"))


def _protection() -> dict:
    path = REPO / "docs" / "code-governance" / "protection.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.unit
def test_the_workflow_defines_exactly_the_six_gate_jobs():
    jobs = _workflow()["jobs"]

    assert sorted(jobs) == sorted(GATES)
    for job_id, job in jobs.items():
        assert job["name"] == job_id


@pytest.mark.unit
def test_the_protection_baseline_requires_exactly_the_six_contexts():
    assert _protection()["required_status_checks"]["contexts"] == list(GATES)


@pytest.mark.unit
def test_gate_4_runs_the_local_evaluator_on_the_shipped_fixed_set():
    job = _workflow()["jobs"]["gate-4-semantic-eval"]
    run = "\n".join(step.get("run", "") for step in job["steps"])

    assert "pip install -e ." in run
    assert "python -m eval.run" in run
    assert "--set eval/fixed-set.json" in run
    assert "--thresholds eval/thresholds.yaml" in run


@pytest.mark.unit
def test_the_evaluator_yaml_dependency_is_declared():
    pyproject = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = pyproject["project"]["dependencies"]

    assert any(dependency.lower().startswith("pyyaml") for dependency in dependencies)


@pytest.mark.unit
def test_the_protection_baseline_still_enforces_the_admin_rules():
    protection = _protection()

    assert protection["enforce_admins"] is True
    assert protection["allow_force_pushes"] is False
    assert protection["allow_deletions"] is False
    assert protection["required_pull_request_reviews"]["required_approving_review_count"] >= 1
    assert protection["required_pull_request_reviews"]["dismiss_stale_reviews"] is True
