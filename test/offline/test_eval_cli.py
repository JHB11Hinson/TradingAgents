"""Verifies D1-REQ-EVAL-001: ``python -m eval.run`` exits on the verdict.

The fit criterion is an exit code, so the test runs the real command in a
subprocess: zero when every threshold passes, non-zero when one fails, and a
distinct configuration error when the set or thresholds cannot be read.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

# The evidence budget gate-4 replays at. Since CHG-043 the compact debate turns put a full run at
# about 43,500 tokens, below the shipped 50,000 cap, so the shipped default would leave the
# capped/uncapped comparison at 1.0 (see `docs/architecture/evaluation-logbook.md` E-008).
EVIDENCE_BUDGET = ("--budget", "40000")


def _run(*args: str, timeout: int = 240) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "eval.run", *args],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


@pytest.mark.unit
def test_the_runner_exits_zero_when_every_threshold_passes(tmp_path):
    out = tmp_path / "report.json"

    proc = _run(
        *EVIDENCE_BUDGET, "--results-dir", str(tmp_path / "runs"), "--out", str(out)
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["ok"] is True
    assert report["metrics"]["cases_failed"] == 0
    assert report["metrics"]["total_tokens_ratio"] <= 0.5
    assert report["metrics"]["est_cost_ratio"] <= 0.5
    assert report["metrics"]["budget_respected_rate"] == 1.0
    assert report["metrics"]["review_rate"] == 0.0
    assert report["metrics"]["structured_output_pass_rate"] == 1.0
    assert report["metrics"]["uncapped_tokens"] > report["metrics"]["total_tokens"]
    assert report["metrics"]["capped_tokens_ratio"] <= 0.98
    assert "verdict: pass" in proc.stdout
    assert (tmp_path / "runs" / "capped").is_dir()
    assert (tmp_path / "runs" / "uncapped").is_dir()


@pytest.mark.unit
def test_the_runner_writes_the_default_report_under_results_dir(tmp_path):
    results = tmp_path / "runs"

    proc = _run(*EVIDENCE_BUDGET, "--results-dir", str(results))

    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert (results / "report.json").is_file()


@pytest.mark.unit
def test_the_runner_exits_non_zero_when_a_threshold_fails(tmp_path):
    thresholds = tmp_path / "thresholds.yaml"
    thresholds.write_text(
        "metrics:\n  total_tokens_ratio: {max: 0.0}\n", encoding="utf-8"
    )

    proc = _run(
        "--thresholds", str(thresholds),
        "--results-dir", str(tmp_path / "runs"),
        "--out", str(tmp_path / "report.json"),
    )

    assert proc.returncode == 1, proc.stdout + proc.stderr
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert report["ok"] is False
    assert report["thresholds"][0]["metric"] == "total_tokens_ratio"
    assert report["thresholds"][0]["ok"] is False


@pytest.mark.unit
def test_a_malformed_fixed_set_exits_with_a_configuration_error(tmp_path):
    bad = tmp_path / "set.json"
    bad.write_text(json.dumps({"version": 1, "cases": []}), encoding="utf-8")

    proc = _run("--set", str(bad), "--results-dir", str(tmp_path / "runs"))

    assert proc.returncode == 2
    assert "non-empty" in proc.stderr
