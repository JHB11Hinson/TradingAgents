"""``python -m eval.run`` — replay the fixed evaluation set and judge it.

Usage::

    python -m eval.run --set eval/fixed-set.json --thresholds eval/thresholds.yaml

Exit codes: ``0`` every threshold passed, ``1`` a threshold failed, ``2`` the
set, the thresholds or the baseline could not be read. Fit criteria:
``D1-REQ-EVAL-001`` (fixed set + thresholds + pass/fail exit code) and
``D1-REQ-COST-001`` (tokens and cost against the recorded baseline).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tradingagents.evaluation import (
    BaselineError,
    FixedSetError,
    ThresholdError,
    evaluate_cases,
    load_baseline,
    load_fixed_set,
    load_thresholds,
)

DEFAULT_SET = "eval/fixed-set.json"
DEFAULT_THRESHOLDS = "eval/thresholds.yaml"
DEFAULT_BASELINE = "eval/baseline.json"
DEFAULT_RESULTS = "eval/results"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m eval.run",
        description="Replay the fixed evaluation set and judge its thresholds.",
    )
    parser.add_argument("--set", default=DEFAULT_SET, help="fixed set JSON (default: %(default)s)")
    parser.add_argument(
        "--thresholds", default=DEFAULT_THRESHOLDS, help="thresholds YAML (default: %(default)s)"
    )
    parser.add_argument(
        "--baseline", default=DEFAULT_BASELINE, help="recorded baseline JSON (default: %(default)s)"
    )
    parser.add_argument(
        "--results-dir",
        default=DEFAULT_RESULTS,
        help="where the replay writes its run artifacts (default: %(default)s)",
    )
    parser.add_argument(
        "--out", default=None, help="write the JSON report here (default: <results-dir>/report.json)"
    )
    parser.add_argument(
        "--budget",
        type=int,
        default=None,
        help="override context_budget_tokens for the replay (default: the shipped value)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        cases = load_fixed_set(args.set)
        thresholds = load_thresholds(args.thresholds)
        baseline = load_baseline(args.baseline)
    except (FixedSetError, ThresholdError, BaselineError, OSError) as exc:
        print(f"eval.run: {exc}", file=sys.stderr)
        return 2

    from eval.replay import build_replay_analyzer

    overrides = {"context_budget_tokens": args.budget} if args.budget is not None else None
    analyzer = build_replay_analyzer(args.results_dir, overrides)
    report = evaluate_cases(
        cases,
        analyzer,
        baseline,
        thresholds,
        set_path=str(args.set),
        thresholds_path=str(args.thresholds),
    )
    print(report.summary())

    out = Path(args.out) if args.out else Path(args.results_dir) / "report.json"
    print(f"eval.run: report written to {report.write(out)}")
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
