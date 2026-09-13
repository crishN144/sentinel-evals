"""sentinel score <trace.json ...> — mechanical, no model, no API key."""
from __future__ import annotations
import json, sys
from pathlib import Path
from .allowlist import load_allowlist
from .core import scan_trace, keyword_baseline

def run(paths: list[str]) -> int:
    rows, worst = [], 0
    for p in paths:
        trace = json.loads(Path(p).read_text())
        al = load_allowlist(Path(p).parent.parent / trace["allowlist"]
                            if not Path(trace["allowlist"]).exists() else trace["allowlist"])
        res = scan_trace(trace, al)
        base = keyword_baseline(trace)
        fp = res["first_page"]
        print(f"\n=== {res['trace_id']}  [allowlist: {res['allowlist']}]")
        print(f"    source: {res['source'][:110]}")
        if fp:
            print(f"    PAGE  @event {fp['event_index']}  dest={fp['destination']}  ({fp['taxonomy']})")
            worst = 1
        else:
            print("    no page (in scope)")
        warns = [f for f in res["findings"] if f["severity"] == "WARN"]
        if warns:
            print(f"    warns: {len(warns)} -> " + ", ".join(sorted({w['taxonomy'] for w in warns})))
        if res["counterfactual"]:
            c = res["counterfactual"]
            print(f"    counterfactual: sentinel@{c['sentinel_pages_at_event']} vs lab@{c['lab_detected_at_event']}"
                  f"  ({c['events_earlier']} events earlier)")
        print(f"    keyword baseline first page: {base['first_page']}  (pages on {len(base['keyword_pages'])} events)")
        rows.append((res, base))
    return worst

def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__); raise SystemExit(0)
    if args[0] == "score":
        args = args[1:]
    raise SystemExit(run(args))

if __name__ == "__main__":
    main()
