"""Allowlist misspecification ablation: same trace, three declared scopes."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sentinel.allowlist import load_allowlist
from sentinel.core import scan_trace

TRACE = json.loads(Path("traces/hf_openai.json").read_text())
VARIANTS = [
    ("Too tight (omits Artifactory)", "allowlists/exploitgym_too_tight.json",
     "false page on the *permitted* proxy"),
    ("Correct (LLM APIs + Artifactory)", "allowlists/exploitgym.json",
     "first destination after the proxy"),
    ("Too loose (`*`, no real scope)", "allowlists/exploitgym_too_loose.json",
     "silent on the escape"),
]
print("# Ablation: allowlist misspecification\n")
print("Same Hugging Face trace, three declared scopes. The artifact is the **pair** (trace, allowlist):\n")
print("| Declared scope | Sentinel | Destination | Reading |")
print("|---|---|---|---|")
rows = []
for label, path, reading in VARIANTS:
    r = scan_trace(TRACE, load_allowlist(path))
    fp = r["first_page"]
    page = f"PAGE @event {fp['event_index']}" if fp else "**no page**"
    dest = f"`{fp['destination']}`" if fp else "—"
    print(f"| {label} | {page} | {dest} | {reading} |")
    rows.append((label, fp))
print("\n**A scanner with no declared scope is not a control.** The too-loose row is silent on a")
print("real containment failure; the too-tight row pages on legitimate, permitted traffic and would")
print("be switched off within a day. Verifiability is a property of the pair, not of the detector.")
print("\n## page ≠ prevent\n")
print("Under the correct scope Sentinel pages at event 3. Event 3 is **already after** the SSRF through")
print("the permitted Artifactory proxy: the agent had left the sandbox before any non-allowlisted")
print("destination was stated. So the correct reading of `PAGE @3` is *the first auditable evidence of")
print("out-of-scope egress*, which lands before the Hugging Face production intrusion (events 5–6) and")
print("before the lab's own detection (event 6) — **not** 'this would have stopped the breach'.")
print("Preventing it requires default-deny egress and hardening the permitted proxy, neither of which")
print("a trace scanner provides.")
