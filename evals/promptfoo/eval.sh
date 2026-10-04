#!/usr/bin/env bash
# Grade a golden run with promptfoo.
#   evals/promptfoo/eval.sh <run-name> [extra promptfoo eval args]
# Reads evals/runs/<run-name>/results.jsonl (from evals/run_golden.py), writes promptfoo.json next to it
# and records the judge deployment in run.json (read by evals/score.py). Set EVAL_MODE=live to run the
# coordinator per row instead of replaying. Exits with promptfoo's status (100 when any assertion failed).
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
RUN=${1:?usage: eval.sh <run-name> [promptfoo args]}
shift || true
export EVAL_RUN="$RUN"
export PROMPTFOO_PYTHON="${PROMPTFOO_PYTHON:-$ROOT/.venv/bin/python}"
export PROMPTFOO_DISABLE_TELEMETRY=1
RUN_DIR="$ROOT/evals/runs/$RUN"
mkdir -p "$RUN_DIR"
cd "$ROOT"
set +e
promptfoo eval -c evals/promptfoo/promptfooconfig.yaml --env-file .env \
  -o "$RUN_DIR/promptfoo.json" --no-progress-bar "$@"
status=$?
set -e
if [ -f "$RUN_DIR/promptfoo.json" ]; then
  "$PROMPTFOO_PYTHON" -c "import sys; from pathlib import Path; from evals.graders.judge import record_judge; print('judge:', record_judge(Path(sys.argv[1])))" "$RUN_DIR"
fi
exit "$status"
