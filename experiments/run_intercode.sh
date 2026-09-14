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
.venv/bin/inspect eval inspect_evals/gdm_intercode_ctf \
  --model "$MODEL" --sample-id "$SAMPLES" --message-limit 30 \
  --log-dir logs/intercode --log-format eval 2>&1 | tee logs/intercode/run.txt
echo "== scout scan (inspect_scout wrapper) over the recorded logs"
SENTINEL_ALLOWLIST=allowlists/intercode_ctf_none.json \
  .venv/bin/scout scan sentinel/scanner.py -T logs/intercode 2>&1 | tee logs/intercode/scout.txt
