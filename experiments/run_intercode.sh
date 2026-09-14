#!/usr/bin/env bash
# Real trace: run a public agentic cyber eval we did not write, then point Sentinel at its logs.
# gdm_intercode_ctf declares network_mode: none — the declared scope is empty.
set -euo pipefail
cd "$(dirname "$0")/.."
: "${MODEL:=anthropic/claude-haiku-4-5-20251001}"
: "${N:=8}"
: "${SAMPLES:=2,3,4,5,6,8,10,11}"
mkdir -p logs/intercode
echo "== inspect eval gdm_intercode_ctf  model=$MODEL  samples=$SAMPLES"
# --sandbox points at a prebuilt image (see experiments/intercode_compose.yaml); --max-sandboxes bounds
# concurrent containers so a small VM disk is not asked to hold eight sandboxes at once.
.venv/bin/inspect eval inspect_evals/gdm_intercode_ctf \
  --model "$MODEL" --sample-id "$SAMPLES" --message-limit 30 \
  --sandbox docker:experiments/intercode_compose.yaml --max-sandboxes 4 \
  --log-dir logs/intercode --log-format eval 2>&1 | tee logs/intercode/run.txt
# Inspect exits 0 even when the task errored, so check the log itself before scanning anything.
.venv/bin/python - <<'PYCHK'
import glob, sys
from inspect_ai.log import read_eval_log
f = sorted(glob.glob("logs/intercode/*.eval"))[-1]
log = read_eval_log(f, header_only=True)
done = log.results.completed_samples if log.results else 0
print(f"== eval status: {log.status}  completed samples: {done}")
if log.status != "success" or not done:
    print("== EVAL DID NOT COMPLETE - not scanning. Error:", str(log.error)[:200] if log.error else "-")
    sys.exit(2)
PYCHK
echo "== scout scan (inspect_scout wrapper) over the recorded logs"
SENTINEL_ALLOWLIST=allowlists/intercode_ctf_none.json \
  .venv/bin/scout scan sentinel/scanner.py -T logs/intercode 2>&1 | tee logs/intercode/scout.txt
