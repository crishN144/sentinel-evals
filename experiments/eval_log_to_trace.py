"""Convert real Inspect .eval logs into Sentinel's JSON trace schema, then score them.
This is the 'pointed at something we did not make' path: the tool calls come from a model
running a public benchmark, not from a fixture we wrote."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from inspect_ai.log import list_eval_logs, read_eval_log
from sentinel.allowlist import load_allowlist
from sentinel.core import scan_trace, keyword_baseline

log_dir, allow = sys.argv[1], sys.argv[2]
al = load_allowlist(allow)
out_dir = Path(log_dir) / "traces"; out_dir.mkdir(exist_ok=True)
rows = []
for info in list_eval_logs(log_dir):
    log = read_eval_log(info.name)
    for s in log.samples or []:
        events = []
        for m in s.messages:
            for tc in (getattr(m, "tool_calls", None) or []):
                events.append({"i": len(events), "role": "assistant", "tool": tc.function, "arguments": tc.arguments})
        trace = {"trace_id": f"{log.eval.task}:{s.id}:{s.epoch}", "source": f"REAL: inspect log {Path(info.name).name}, model {log.eval.model}",
                 "allowlist": allow, "events": events}
        (out_dir / f"{s.id}.json").write_text(json.dumps(trace, indent=1))
        r = scan_trace(trace, al); b = keyword_baseline(trace)
        warns = sorted({f["taxonomy"] for f in r["findings"] if f["severity"] == "WARN"})
        rows.append((trace["trace_id"], len(events), r["first_page"], warns, b["first_page"], len(b["keyword_pages"]), s.scores))
print(f"| sample | tool calls | Sentinel | warns | keyword baseline first hit | baseline hits | score |")
print("|---|---|---|---|---|---|---|")
for tid, n, fp, warns, bf, bn, sc in rows:
    page = f"PAGE @{fp['event_index']} {fp['destination']}" if fp else "no page"
    score = ",".join(f"{k}={v.value}" for k, v in (sc or {}).items())
    print(f"| {tid} | {n} | {page} | {' '.join(warns) or '—'} | {bf if bf is not None else '—'} | {bn} | {score} |")
