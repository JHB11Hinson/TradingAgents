#!/usr/bin/env bash
# CS5351 demo runner.
# Shows each command before running it, then prints the exit code.
# B1 is expected to exit 1: gate 4 must fail without compaction.
# The live run is separate: docs/demo/demo.sh live, or docs/demo/demo.sh full.

set -u

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${DEMO_REPO:-$(cd -- "$SCRIPT_DIR/../.." 2>/dev/null && pwd)}"
cd "$REPO_DIR" || { echo "Repository not found: $REPO_DIR"; exit 2; }

if [ -x .venv/bin/python ]; then
  # shellcheck disable=SC1091
  . .venv/bin/activate
else
  echo "Warning: .venv not found; using python on PATH."
fi

FAILURES=0

pause() {
  if [ "${DEMO_PAUSE:-1}" = "1" ]; then
    printf '\n[Enter] next step'
    read -r _
    printf '\033[1A\r\033[2K'
  fi
}

show() {
  printf '\n$ %s\n' "$1"
}

run_step() {
  local title="$1" expected="$2" fn="$3"
  printf '\n# %s\n' "$title"
  "$fn"
  local status=$?
  printf 'exit=%s\n' "$status"
  if [ "$status" -ne "$expected" ]; then
    printf 'WARNING: expected exit %s, got %s\n' "$expected" "$status"
    FAILURES=$((FAILURES + 1))
  fi
  pause
}

step_live() {
  show 'python docs/demo/demo_live.py'
  python "$SCRIPT_DIR/demo_live.py"
}

step_b1() {
  rm -rf -- /tmp/opencode/demo-nocap
  show 'python -m eval.run \
  --set eval/fixed-set.json \
  --thresholds eval/thresholds.yaml \
  --results-dir /tmp/opencode/demo-nocap'
  python -m eval.run \
    --set eval/fixed-set.json \
    --thresholds eval/thresholds.yaml \
    --results-dir /tmp/opencode/demo-nocap
}

step_b2() {
  rm -rf -- /tmp/opencode/demo-cap
  show 'python -m eval.run \
  --set eval/fixed-set.json \
  --thresholds eval/thresholds.yaml \
  --budget 40000 \
  --results-dir /tmp/opencode/demo-cap'
  python -m eval.run \
    --set eval/fixed-set.json \
    --thresholds eval/thresholds.yaml \
    --budget 40000 \
    --results-dir /tmp/opencode/demo-cap
}

step_b3() {
  local status=0
  show 'python docs/demo/demo_debate.py'
  python "$SCRIPT_DIR/demo_debate.py" || status=$?
  show 'python -m pytest -q test/offline/test_debate_turns.py'
  python -m pytest -q test/offline/test_debate_turns.py || status=$?
  return "$status"
}

step_b4() {
  local status=0
  show 'python docs/demo/demo_guardrails.py'
  python "$SCRIPT_DIR/demo_guardrails.py" || status=$?
  show 'python -m pytest -q test/offline/test_guardrails.py'
  python -m pytest -q test/offline/test_guardrails.py || status=$?
  return "$status"
}

step_b5() {
  show 'grep -n "D1-REQ-COST-003" docs/architecture/trace-matrix.md'
  grep -n "D1-REQ-COST-003" docs/architecture/trace-matrix.md
}

step_b6() {
  local status=0
  show 'ruff check src'
  ruff check src || status=$?
  show 'check-jsonschema --schemafile docs/req/req-schema.json docs/req/requirements.yaml'
  check-jsonschema --schemafile docs/req/req-schema.json docs/req/requirements.yaml || status=$?
  show 'python -m pytest -q'
  python -m pytest -q || status=$?
  return "$status"
}

run_all() {
  printf '\n[skip] B0 live run: use docs/demo/demo.sh live (or docs/demo/demo.sh full)\n'
  run_step 'B1: no compaction. Gate 4 should FAIL.' 1 step_b1
  run_step 'B2: 40k budget. Gate 4 should PASS.' 0 step_b2
  run_step 'B3: debate contract: prose vs structured.' 0 step_b3
  run_step 'B4: safety guardrails: 50% -> 10%; bad decision -> REVIEW.' 0 step_b4
  run_step 'B5: one requirement -> component, tests, monitor, gate.' 0 step_b5
  run_step 'B6: static checks + full regression.' 0 step_b6
}

printf 'CS5351 demo runner\n'
printf 'Repo: %s\n' "$PWD"
printf 'B0 is the real live run. B1 exits 1 on purpose. B2-B6 should exit 0.\n'

case "${1:-all}" in
  all) run_all ;;
  live) run_step 'B0: real live run. Calls the model and vendors; several minutes.' 0 step_live ;;
  full)
    run_step 'B0: real live run. Calls the model and vendors; several minutes.' 0 step_live
    run_all
    ;;
  b1) run_step 'B1: no compaction. Gate 4 should FAIL.' 1 step_b1 ;;
  b2) run_step 'B2: 40k budget. Gate 4 should PASS.' 0 step_b2 ;;
  b3) run_step 'B3: debate contract: prose vs structured.' 0 step_b3 ;;
  b4) run_step 'B4: safety guardrails: 50% -> 10%; bad decision -> REVIEW.' 0 step_b4 ;;
  b5) run_step 'B5: one requirement -> component, tests, monitor, gate.' 0 step_b5 ;;
  b6) run_step 'B6: static checks + full regression.' 0 step_b6 ;;
  *)
    echo "Usage: $0 [all|full|live|b1|b2|b3|b4|b5|b6]"
    exit 2
    ;;
esac

if [ "$FAILURES" -ne 0 ]; then
  printf '\nFinished with %s unexpected exit code(s).\n' "$FAILURES"
  exit 1
fi

printf '\nFinished. B1 should be the only non-zero exit.\n'
