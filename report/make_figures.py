"""Figures for the Sentinel sprint report. Palette + typography follow the evalaware write-up
(sampled from its PNGs): ink #2b2724, slate #2e5c8a, crimson #b04a3f, sand #a89680, grey #6b635a."""
import json, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sentinel.allowlist import load_allowlist
from sentinel.core import scan_trace

INK, SLATE, CRIMSON, SAND, GREY, BAND = "#2b2724", "#2e5c8a", "#b04a3f", "#a89680", "#6b635a", "#ebe4da"
plt.rcParams.update({"font.family": "Helvetica", "font.size": 11, "axes.edgecolor": GREY,
                     "text.color": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK})

# ---------- Fig 1: same trace, three declared scopes ----------
trace = json.loads((ROOT / "traces/hf_openai.json").read_text())
events = trace["events"]
labels = ["id; env", "mountinfo,\ncgroup", "artifactory\n(permitted proxy)", "modal.run", "paste.ee", "k8s svc\n(HF internal)", "huggingface.co\n/api (HF prod)"]
scopes = [("too tight\n(omits proxy)", "allowlists/exploitgym_too_tight.json"),
          ("correct\n(LLM APIs + proxy)", "allowlists/exploitgym.json"),
          ("wildcard *\n(no real scope)", "allowlists/exploitgym_too_loose.json")]
rows = []
for name, path in scopes:
    r = scan_trace(trace, load_allowlist(ROOT / path))
    rows.append((name, r["first_page"]))

fig, ax = plt.subplots(figsize=(10.2, 4.1), dpi=300)
fig.patch.set_facecolor("white"); ax.set_facecolor("white")
n = len(events)
ax.axvspan(4.5, 6.5, color=BAND, alpha=0.6, lw=0)
ax.text(5.5, 2.78, "post-escape: inside Hugging Face", ha="center", va="center", fontsize=9, color=GREY)
ax.axvline(2, ls=":", color=GREY, lw=1)
ax.text(2.06, 2.78, "SSRF through the permitted proxy\n(the escape; not visible to any allowlist)", fontsize=8.5, color=GREY, va="center")
ax.axvline(trace["lab_detected_at_event"], ls=":", color=GREY, lw=1)
for y, (name, fp) in enumerate(rows):
    ax.plot(range(n), [y]*n, color="#c9c0b4", lw=1.2, zorder=1)
    ax.scatter(range(n), [y]*n, s=28, color="white", edgecolor=GREY, zorder=2, lw=0.9)
    if fp is None:
        ax.text(n - 0.35, y, "no page", color=CRIMSON, fontsize=10.5, va="center", ha="left", fontweight="bold")
    else:
        i = fp["event_index"]
        col = CRIMSON if "tight" in name else SLATE
        ax.scatter([i], [y], s=170, color=col, zorder=3, edgecolor="white", lw=1.2)
        txt = "PAGE @%d  (false page on permitted egress)" % i if col == CRIMSON else "PAGE @%d  first auditable out-of-scope destination" % i
        ax.text(i + 0.18, y + 0.30, txt, color=col, fontsize=9.5, fontweight="bold", va="center")
ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=10)
ax.set_xticks(range(n)); ax.set_xticklabels([f"{i}\n{l}" for i, l in enumerate(labels)], fontsize=8.5)
ax.set_xlim(-0.5, n + 0.9); ax.set_ylim(-0.6, 3.05)
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.tick_params(axis="y", length=0)
ax.set_xlabel("event index in the Hugging Face reconstruction (tool calls, in order)", fontsize=9.5, color=GREY)
ax.text(-0.5, 3.35, "Same trace, three declared scopes. Only the allowlist changes.", fontsize=13, fontweight="bold", color=INK, va="bottom", clip_on=False)
ax.text(-0.5, 3.12, "slate = the page a correct scope produces; crimson = a misspecified scope. Dotted: the escape (event 2) and the lab's own detection (event 6).", fontsize=9, color=GREY, va="bottom", clip_on=False)
ax.text(trace["lab_detected_at_event"] + 0.06, -0.45, "lab noticed\n(reconstruction)", fontsize=8.5, color=GREY, va="center")
fig.subplots_adjust(left=0.13, right=0.99, top=0.80, bottom=0.2)
fig.savefig(ROOT / "report/figures/fig1_ablation.png", dpi=300, facecolor="white")
print("fig1 written; rows:", [(r[0].split("\n")[0], r[1]["event_index"] if r[1] else None) for r in rows])

# ---------- Fig 2: what each layer can and cannot establish ----------
fig, ax = plt.subplots(figsize=(10.2, 3.25), dpi=300)
fig.patch.set_facecolor("white"); ax.set_facecolor("white"); ax.axis("off")
ax.set_xlim(0, 10.2); ax.set_ylim(-0.25, 3.0)
boxes = [
    (0.15, "1  Declared scope", "allowlist.json:\nhosts, suffixes, CIDRs,\ninternet_expected", SLATE, "this paper"),
    (2.75, "2  Declared action", "tool-call arguments,\nstated destination,\nclassified against scope", SLATE, "this paper (Sentinel)"),
    (5.35, "3  Observed action", "egress flow logs\n(Hubble / Squid) diffed\nagainst the same scope", GREY, "not implemented"),
    (7.95, "4  Attestation", "third party replays\n(trace, allowlist, verdict)\nfrom files alone", SLATE, "Track 1 test"),
]
for x, head, body, col, tag in boxes:
    ax.add_patch(FancyBboxPatch((x, 0.85), 2.1, 1.6, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc="white", ec=col, lw=1.6))
    ax.text(x + 0.12, 2.22, head, fontsize=10.5, fontweight="bold", color=col, va="center")
    ax.text(x + 0.12, 1.55, body, fontsize=8.8, color=INK, va="center", linespacing=1.35)
    ax.text(x + 0.12, 0.6, tag, fontsize=8.5, color=col, style="italic", va="center")
for x in (2.25, 4.85, 7.45):
    ax.add_patch(FancyArrowPatch((x + 0.02, 1.62), (x + 0.48, 1.62), arrowstyle="-|>", mutation_scale=12, color=GREY, lw=1.2))
ax.text(0.27, 2.85, "Four layers of containment evidence. A scanner checks layer 2 against layer 1; it prevents nothing.",
        fontsize=12.5, fontweight="bold", color=INK, va="center")
ax.text(0.27, 0.1, "Prevention lives elsewhere: default-deny egress and a hardened permitted proxy. Layer 3 is the complement that turns 'isolation assumed' into 'isolation attested'.",
        fontsize=8.8, color=GREY, va="center")
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
fig.savefig(ROOT / "report/figures/fig2_layers.png", dpi=300, facecolor="white")
print("fig2 written")
