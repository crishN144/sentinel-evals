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
ax.text(-0.5, 3.12, "slate = the page a correct scope produces; crimson = a misspecified scope. Dotted at event 2: the SSRF through the permitted proxy.", fontsize=9, color=GREY, va="bottom", clip_on=False)
ax.text(trace["lab_detected_at_event"] + 0.06, -0.45, "lab noticed\n(reconstruction)", fontsize=8.5, color=GREY, va="center")
fig.subplots_adjust(left=0.13, right=0.99, top=0.80, bottom=0.2)
fig.savefig(ROOT / "report/figures/fig1_ablation.png", dpi=300, facecolor="white")
print("fig1 written; rows:", [(r[0].split("\n")[0], r[1]["event_index"] if r[1] else None) for r in rows])

# ---------- Fig 2: what each layer can and cannot establish ----------
from matplotlib.patches import Rectangle
MONO = "Menlo"
fig, ax = plt.subplots(figsize=(10.2, 4.6), dpi=300)
fig.patch.set_facecolor("white"); ax.set_facecolor("white"); ax.axis("off")
ax.set_xlim(0, 10.2); ax.set_ylim(0, 4.6)
LIGHT_SLATE, LIGHT_SAND = "#e8eef5", "#f3eee5"

# title + subtitle (same voice as Fig 1)
ax.text(0.15, 4.42, "Four layers of containment evidence", fontsize=13, fontweight="bold", color=INK, va="center")
ax.text(0.15, 4.16, "Sentinel checks what the agent said it would reach (2) against what the evaluation declared (1). "
        "Nothing on this row prevents anything.", fontsize=9, color=GREY, va="center")

# the evidence row: four cards
cards = [
    (0.15, "1", "Declared scope", "what the evaluation permits", 'allowed_hosts:\n  api.openai.com\n  artifactory.internal', SLATE, LIGHT_SLATE, "solid"),
    (2.70, "2", "Declared action", "what the agent said it would reach", 'event 3  curl https://\n  cybergym-…modal.run\n  → OUT of scope', SLATE, LIGHT_SLATE, "solid"),
    (5.25, "3", "Observed action", "what the network actually saw", 'flow log  10.0.3.4 →\n  34.x.x.x:443\n  vs the same allowlist', GREY, "white", "dashed"),
    (7.80, "4", "Attestation", "what a third party can recompute", 'PAGE @3\nfrom (trace, allowlist)\nno lab network needed', SAND, LIGHT_SAND, "solid"),
]
y0, h, w = 1.55, 2.25, 2.05
for x, n, head, sub, ex, col, fill, ls in cards:
    ax.add_patch(FancyBboxPatch((x, y0), w, h, boxstyle="round,pad=0.02,rounding_size=0.10",
                                fc=fill, ec=col, lw=1.5, ls=ls))
    # number badge
    ax.add_patch(plt.Circle((x + 0.28, y0 + h - 0.30), 0.16, fc=col, ec="none"))
    ax.text(x + 0.28, y0 + h - 0.30, n, ha="center", va="center", fontsize=9.5, fontweight="bold", color="white")
    ax.text(x + 0.55, y0 + h - 0.30, head, fontsize=11, fontweight="bold", color=col if col != SAND else "#7d6a4d", va="center")
    ax.text(x + 0.12, y0 + h - 0.66, sub, fontsize=8.3, color=GREY, va="center", style="italic")
    # example strip
    ax.add_patch(Rectangle((x + 0.12, y0 + 0.14), w - 0.24, 1.05, fc="white", ec="#e3ddd3", lw=0.8))
    ax.text(x + 0.20, y0 + 0.66, ex, fontsize=7.6, color=INK, va="center", family=MONO, linespacing=1.45)
# arrows with verbs
for x, verb in ((2.22, "checked\nagainst"), (4.77, "diffed vs\nscope"), (7.32, "replayed\nfrom files")):
    ax.add_patch(FancyArrowPatch((x + 0.04, y0 + 0.66), (x + 0.44, y0 + 0.66), arrowstyle="-|>", mutation_scale=11, color=GREY, lw=1.1))
    ax.text(x + 0.24, y0 + 0.80, verb, ha="center", va="bottom", fontsize=6.6, color=GREY, linespacing=1.2)
# brackets under the row: what is built vs not vs the test
def bracket(x1, x2, y, label, col):
    ax.plot([x1, x1, x2, x2], [y + 0.08, y, y, y + 0.08], color=col, lw=1.1)
    ax.text((x1 + x2)/2, y - 0.16, label, ha="center", va="top", fontsize=8.6, color=col, fontweight="bold")
bracket(0.15, 4.75, 1.38, "built here: Sentinel (Apache-2.0, 15 tests)", SLATE)
bracket(5.25, 7.30, 1.38, "not built: one month of follow-up", GREY)
bracket(7.80, 9.85, 1.38, "the Track 1 criterion", "#7d6a4d")

# the prevention row: visibly a different thing
ax.plot([0.15, 9.85], [0.80, 0.80], color="#d8d2c8", lw=0.8, ls=(0, (2, 3)))
ax.add_patch(FancyBboxPatch((0.15, 0.10), 9.7, 0.58, boxstyle="round,pad=0.02,rounding_size=0.08", fc="#faf6f0", ec="#d8d2c8", lw=1.0))
ax.text(0.32, 0.38, "PREVENTION", fontsize=8.5, fontweight="bold", color=CRIMSON, va="center")
ax.text(1.45, 0.39, "default-deny egress · a hardened permitted proxy · production classifiers left on.\n"
        "These stop escapes. They live inside the lab and produce no third-party evidence; this paper adds none of them.",
        fontsize=8.0, color=INK, va="center", linespacing=1.35)
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
fig.savefig(ROOT / "report/figures/fig2_layers.png", dpi=300, facecolor="white")
print("fig2 written")
