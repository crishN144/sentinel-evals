"""Fill a containment disclosure record for one evaluation class: the pair (trace, allowlist) plus the
verdict and everything a third party needs to recompute it. Hashes are computed here, not typed."""
import hashlib, json, sys
from datetime import date
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sentinel.allowlist import load_allowlist
from sentinel.core import scan_trace

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def make(trace_path, allowlist_path, eval_class, provenance):
    trace = json.loads((ROOT / trace_path).read_text())
    al = load_allowlist(ROOT / allowlist_path)
    r = scan_trace(trace, al); fp = r["first_page"]
    return {
        "record_version": "0.1",
        "evaluation_class": eval_class,
        "filled": date.today().isoformat(),
        "declared_scope": {"path": allowlist_path, "sha256": sha(ROOT / allowlist_path),
                           "allowed_hosts": sorted(al.allowed_hosts), "allowed_cidrs": al.allowed_cidrs,
                           "internet_expected": al.internet_expected},
        "trace": {"path": trace_path, "sha256": sha(ROOT / trace_path), "events": len(trace["events"]),
                  "provenance": provenance},
        "verdict": {"severity": "PAGE" if fp else "OK",
                    "first_out_of_scope_event": fp["event_index"] if fp else None,
                    "destination": fp["destination"] if fp else None,
                    "warn_only_findings": sum(1 for f in r["findings"] if f["severity"] == "WARN")},
        "recompute": {"command": f"sentinel score {trace_path}",
                      "requires": "the two files above and this repository; no network, no model, no API key",
                      "code_sha256_core": sha(ROOT / "sentinel/core.py"),
                      "code_sha256_extract": sha(ROOT / "sentinel/extract.py")},
        "not_established": ["that the escape was prevented (page != prevent)",
                            "anything about traffic through allowlisted hosts (SSRF via a permitted proxy is invisible)",
                            "anything about destinations the agent reached but did not state (declared, not observed, action)"],
    }

if __name__ == "__main__":
    rec = make("traces/hf_openai.json", "allowlists/exploitgym.json", "exploitgym-cyber-eval",
               "RECONSTRUCTION from the public record (huggingface.co/blog/agent-intrusion-technical-timeline; "
               "openai.com/index/hugging-face-model-evaluation-security-incident). A lab would attach its own log.")
    out = ROOT / "records/exploitgym-cyber-eval.json"
    out.write_text(json.dumps(rec, indent=1)); print(json.dumps(rec, indent=1))
