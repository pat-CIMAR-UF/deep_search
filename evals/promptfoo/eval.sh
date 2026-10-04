#!/usr/bin/env bash
# Grade a golden run with promptfoo.
#   evals/promptfoo/eval.sh <run-name> [extra promptfoo eval args]
# Reads evals/runs/<run-name>/results.jsonl (from evals/run_golden.py) and writes promptfoo.json
# next to it. Set EVAL_MODE=live to run the coordinator per row instead of replaying.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
RUN=${1:?usage: eval.sh <run-name> [promptfoo args]}
shift || true
export EVAL_RUN="$RUN"
export PROMPTFOO_PYTHON="${PROMPTFOO_PYTHON:-$ROOT/.venv/bin/python}"
export PROMPTFOO_DISABLE_TELEMETRY=1
mkdir -p "$ROOT/evals/runs/$RUN"
cd "$ROOT"
exec promptfoo eval -c evals/promptfoo/promptfooconfig.yaml --env-file .env \
  -o "evals/runs/$RUN/promptfoo.json" --no-progress-bar "$@"
