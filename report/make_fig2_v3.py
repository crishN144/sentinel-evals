"""Fig 2 v3 — v1 layout, retinted to Fig 1's ink. Standalone; writes fig2_layers_v3.png only."""
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]

# --- palette: one ink with Fig 1 ---
INK        = "#2b2724"   # title, body text in boxes
GREY       = "#6b635a"   # subtitles, taglines, layer 3
SLATE      = "#2e5c8a"   # layers 1-2 stroke + chips  (Fig 1's "correct/real" line)
SLATE_FILL = "#e8eef4"   # slate at ~10%
SANDY      = "#8a7d6b"   # layer 4 stroke + chip
SAND_FILL  = "#f3eee4"
CRIMSON    = "#B42318"   # appears exactly once
RULE       = "#D6C7B0"
PREV_FILL  = "#f7f2ea"
STRIP_EC   = "#e3ddd3"
MONO       = "Menlo"
plt.rcParams.update({"font.family": "Helvetica", "text.color": INK})

fig, ax = plt.subplots(figsize=(10.2, 4.6), dpi=300)
fig.patch.set_facecolor("white"); ax.set_facecolor("white"); ax.axis("off")
ax.set_xlim(0, 10.2); ax.set_ylim(0, 4.6)

ax.text(0.15, 4.42, "Four layers of containment evidence", fontsize=13, fontweight="bold", color=INK, va="center")
ax.text(0.15, 4.16, "Sentinel checks what the agent said it would reach (2) against what the evaluation declared (1). "
        "Nothing on this row prevents anything.", fontsize=9, color=GREY, va="center")

cards = [
    (0.15, "1", "Declared scope", "what the evaluation permits",
     'allowed_hosts:\n  api.openai.com\n  artifactory.internal', SLATE, SLATE_FILL, "solid"),
    (2.70, "2", "Declared action", "what the agent said it would reach",
     'event 3  curl https://\n  cybergym-…modal.run\n  → OUT of scope', SLATE, SLATE_FILL, "solid"),
    (5.25, "3", "Observed action", "what the network actually saw",
     'flow log  10.0.3.4 →\n  34.x.x.x:443\n  vs the same allowlist', GREY, "white", "dashed"),
    (7.80, "4", "Attestation", "what a third party can recompute",
     'PAGE @3\nfrom (trace, allowlist)\nno lab network needed', SANDY, SAND_FILL, "solid"),
]
y0, h, w = 1.55, 2.25, 2.05
for x, n, head, sub, ex, col, fill, ls in cards:
    ax.add_patch(FancyBboxPatch((x, y0), w, h, boxstyle="round,pad=0.02,rounding_size=0.10",
                                fc=fill, ec=col, lw=1.5, ls=ls))
    ax.add_patch(plt.Circle((x + 0.28, y0 + h - 0.30), 0.16, fc=col, ec="none"))
    ax.text(x + 0.28, y0 + h - 0.30, n, ha="center", va="center", fontsize=9.5, fontweight="bold", color="white")
    ax.text(x + 0.55, y0 + h - 0.30, head, fontsize=11, fontweight="bold", color=col, va="center")
    ax.text(x + 0.12, y0 + h - 0.66, sub, fontsize=8.3, color=GREY, va="center", style="italic")
    ax.add_patch(Rectangle((x + 0.12, y0 + 0.14), w - 0.24, 1.05, fc="white", ec=STRIP_EC, lw=0.8))
    ax.text(x + 0.20, y0 + 0.66, ex, fontsize=7.6, color=INK, va="center", family=MONO, linespacing=1.45)

for x, verb in ((2.22, "checked\nagainst"), (4.77, "diffed vs\nscope"), (7.32, "replayed\nfrom files")):
    ax.add_patch(FancyArrowPatch((x + 0.04, y0 + 0.66), (x + 0.44, y0 + 0.66),
                                 arrowstyle="-|>", mutation_scale=11, color=GREY, lw=1.1))
    ax.text(x + 0.24, y0 + 0.80, verb, ha="center", va="bottom", fontsize=6.6, color=GREY, linespacing=1.2)

def bracket(x1, x2, y, label, col):
    ax.plot([x1, x1, x2, x2], [y + 0.08, y, y, y + 0.08], color=col, lw=1.1)
    ax.text((x1 + x2)/2, y - 0.16, label, ha="center", va="top", fontsize=8.6, color=col, fontweight="bold")
bracket(0.15, 4.75, 1.38, "built here: Sentinel (Apache-2.0, 18 tests)", SLATE)
bracket(5.25, 7.30, 1.38, "not built: one month of follow-up", GREY)
bracket(7.80, 9.85, 1.38, "the Track 1 criterion", SANDY)

ax.plot([0.15, 9.85], [0.80, 0.80], color=RULE, lw=0.8, ls=(0, (2, 3)))
ax.add_patch(FancyBboxPatch((0.15, 0.10), 9.7, 0.58, boxstyle="round,pad=0.02,rounding_size=0.08",
                            fc=PREV_FILL, ec=RULE, lw=1.0))
ax.text(0.32, 0.38, "PREVENTION", fontsize=8.5, fontweight="bold", color=CRIMSON, va="center")
ax.text(1.45, 0.39, "default-deny egress · a hardened permitted proxy · production classifiers left on.\n"
        "These stop escapes. They live inside the lab and produce no third-party evidence; this paper adds none of them.",
        fontsize=8.0, color=INK, va="center", linespacing=1.35)

fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
out = ROOT / "report/figures/fig2_layers_v3.png"
fig.savefig(out, dpi=300, facecolor="white"); print("wrote", out)
