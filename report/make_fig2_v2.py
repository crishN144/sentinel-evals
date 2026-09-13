"""Fig 2, editorial redesign (v2). Same information architecture; flatter, thinner, quieter.
Not wired into the report build — writes report/figures/fig2_layers_v2.png only."""
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon

ROOT = Path(__file__).resolve().parents[1]
INK, SLATE, CRIMSON, SAND, GREY = "#2b2724", "#2e5c8a", "#b04a3f", "#8c7a5c", "#6b635a"
RULE, TINT_SLATE, TINT_SAND, MONO = "#cfc9bf", "#eef2f7", "#f4f0e8", "Menlo"
plt.rcParams.update({"font.family": "Helvetica", "text.color": INK})

fig, ax = plt.subplots(figsize=(10.2, 4.35), dpi=300)
fig.patch.set_facecolor("white"); ax.set_facecolor("white"); ax.axis("off")
ax.set_xlim(0, 10.2); ax.set_ylim(0, 4.35)

# ---- title block: figure title + one-line annotation, hairline under it
ax.text(0.15, 4.12, "Four layers of containment evidence", fontsize=12.5, fontweight="bold", va="center")
ax.text(0.15, 3.86, "Sentinel compares the agent's stated destination (2) with the evaluation's declared scope (1). "
        "Neither layer prevents anything.", fontsize=8.8, color=GREY, va="center")
ax.plot([0.15, 10.05], [3.66, 3.66], color=RULE, lw=0.7)

# ---- four columns
X = [0.15, 2.70, 5.25, 7.80]; W = 2.05; Y0, H = 1.42, 2.0
cols = [
    ("LAYER 1", "Declared scope", "what the evaluation permits", "allowed_hosts:\n  api.openai.com\n  artifactory.internal", SLATE, TINT_SLATE, "-", "built"),
    ("LAYER 2", "Declared action", "what the agent said it would reach", "event 3  curl https://\n  cybergym-…modal.run\n  → OUT of scope", SLATE, TINT_SLATE, "-", "built"),
    ("LAYER 3", "Observed action", "what the network actually saw", "flow log  10.0.3.4 →\n  34.x.x.x:443\n  vs the same allowlist", GREY, "white", (0, (3, 2.5)), "not built"),
    ("LAYER 4", "Attestation", "what a third party can recompute", "PAGE @3\nfrom (trace, allowlist)\nno lab network needed", SAND, TINT_SAND, "-", "criterion"),
]
for x, (over, head, sub, ex, col, tint, ls, kind) in zip(X, cols):
    ax.add_patch(FancyBboxPatch((x, Y0), W, H, boxstyle="round,pad=0,rounding_size=0.04", fc=tint, ec=col, lw=0.9, ls=ls))
    if kind != "not built":  # a heavier top rule marks the layers that exist
        ax.plot([x, x + W], [Y0 + H, Y0 + H], color=col, lw=2.2, solid_capstyle="butt")
    ax.text(x + 0.16, Y0 + H - 0.24, over, fontsize=7, color=col, va="center", fontweight="bold")
    ax.text(x + 0.16, Y0 + H - 0.50, head, fontsize=11.2, fontweight="bold", color=INK, va="center")
    ax.text(x + 0.16, Y0 + H - 0.74, sub, fontsize=8, color=GREY, va="center", style="italic")
    ax.add_patch(Rectangle((x + 0.14, Y0 + 0.14), W - 0.28, 0.92, fc="white", ec=RULE, lw=0.6))
    ax.text(x + 0.22, Y0 + 0.60, ex, fontsize=7.0, color=INK, va="center", family=MONO, linespacing=1.45)

# ---- connectors: hairline + small open head, verb in small caps above
def arrow(x1, x2, y, verb):
    ax.plot([x1, x2 - 0.09], [y, y], color=GREY, lw=0.8)
    ax.add_patch(Polygon([[x2 - 0.09, y - 0.05], [x2, y], [x2 - 0.09, y + 0.05]], closed=True, fc="white", ec=GREY, lw=0.8))
    ax.text((x1 + x2) / 2, y + 0.09, verb, ha="center", va="bottom", fontsize=5.9, color=GREY, linespacing=1.15)
yA = Y0 + 0.62
arrow(X[0] + W + 0.02, X[1] - 0.02, yA, "CHECKED\nAGAINST")
arrow(X[1] + W + 0.02, X[2] - 0.02, yA, "DIFFED VS\nSAME SCOPE")
arrow(X[2] + W + 0.02, X[3] - 0.02, yA, "REPLAYED\nFROM FILES")

# ---- status line under the columns: a rule per group, label beneath
def group(x1, x2, label, col, ls="-"):
    ax.plot([x1, x2], [Y0 - 0.18, Y0 - 0.18], color=col, lw=1.0, ls=ls)
    ax.text(x1, Y0 - 0.30, label, fontsize=8.2, color=col, va="top", fontweight="bold")
group(X[0], X[1] + W, "Built: Sentinel  ·  Apache-2.0, 15 tests", SLATE)
group(X[2], X[2] + W, "Not built: one month of follow-up", GREY, (0, (3, 2.5)))
group(X[3], X[3] + W, "Track 1 criterion", SAND)

# ---- prevention: a footnote row, not a card
ax.plot([0.15, 10.05], [0.62, 0.62], color=RULE, lw=0.7)
ax.add_patch(Rectangle((0.15, 0.24), 0.08, 0.26, fc=CRIMSON, ec="none"))
ax.text(0.34, 0.44, "Prevention is a different layer.", fontsize=8.4, fontweight="bold", color=CRIMSON, va="center")
ax.text(0.34, 0.24, "Default-deny egress, a hardened permitted proxy and production classifiers stop escapes; they live inside the lab "
        "and yield no third-party evidence. This paper adds none of them.", fontsize=8.0, color=INK, va="center")
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
out = ROOT / "report/figures/fig2_layers_v2.png"; fig.savefig(out, dpi=300, facecolor="white"); print("wrote", out)
