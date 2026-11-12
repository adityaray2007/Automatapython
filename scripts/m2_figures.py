"""Draw the architecture and algorithm-flowchart figures for the M2 report (matplotlib only)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon

OUT = Path(__file__).resolve().parent.parent / "Milestone2" / "Figures"
INK, LINE, BLUE, TINT, GREEN, GTINT = "#0f172a", "#475569", "#1d4ed8", "#eff6ff", "#047857", "#ecfdf5"


def box(ax, x, y, w, h, text, fc="white", ec=LINE, fs=8.5, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=INK, weight="bold" if bold else "normal")


def arrow(ax, p, q, text=None, fs=7.5, dx=0.0, dy=0.1):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=12, lw=1.2, color=LINE))
    if text:
        ax.text((p[0] + q[0]) / 2 + dx, (p[1] + q[1]) / 2 + dy, text, fontsize=fs, color=INK, ha="center")


# ---------------- Figure: architecture ----------------
fig, ax = plt.subplots(figsize=(9, 5.2)); ax.set_xlim(0, 12); ax.set_ylim(0, 7); ax.axis("off")
ax.add_patch(FancyBboxPatch((0.2, 0.3), 5.0, 6.4, boxstyle="round,pad=0.02,rounding_size=0.1", fc=TINT, ec=BLUE, lw=1.2))
ax.text(2.7, 6.4, "Presentation layer (Streamlit)", ha="center", fontsize=9.5, weight="bold", color=BLUE)
box(ax, 0.6, 4.9, 4.2, 0.9, "app.py\nsession state, widgets, layout, callbacks", fc="white", bold=False)
box(ax, 0.6, 3.3, 4.2, 0.9, "ui/graphs.py\nNFA / DFA → Graphviz DOT text")
box(ax, 0.6, 1.9, 4.2, 0.9, "st.graphviz_chart\n(rendered in the browser)", fc="#f8fafc")
box(ax, 0.6, 0.6, 4.2, 0.9, "ui/styles.py\nlight / dark theme CSS")
ax.add_patch(FancyBboxPatch((6.6, 0.3), 5.2, 6.4, boxstyle="round,pad=0.02,rounding_size=0.1", fc=GTINT, ec=GREEN, lw=1.2))
ax.text(9.2, 6.4, "Logic layer (algorithm/, no UI imports)", ha="center", fontsize=9.5, weight="bold", color=GREEN)
mods = [("validate.py", "text form → validated NFA / errors"), ("subset_construction.py", "NFA → DFA + construction log"),
        ("simulate.py", "run strings on DFA and NFA"), ("explain.py", "step → English sentence"),
        ("examples.py / models.py", "13 presets, dataclasses")]
for i, (m, d) in enumerate(mods):
    box(ax, 7.0, 5.2 - i * 1.0, 4.4, 0.8, f"{m}\n{d}", fs=8)
arrow(ax, (4.8, 5.35), (7.0, 5.6), "calls", dx=0, dy=0.12)
arrow(ax, (7.0, 4.4), (4.8, 5.15), "NFA, DFA, steps", dy=-0.6, dx=0.5)
arrow(ax, (2.7, 4.9), (2.7, 4.2)); arrow(ax, (2.7, 3.3), (2.7, 2.8))
ax.text(0.2, 0.0, "tests/ (59 pytest cases) exercise both layers; test_purity.py enforces that algorithm/ never imports UI code.", fontsize=7.5, color=LINE)
fig.savefig(OUT / "fig_architecture.png", dpi=200, bbox_inches="tight"); plt.close(fig)

# ---------------- Figure: algorithm flowchart ----------------
fig, ax = plt.subplots(figsize=(7.2, 8.6)); ax.set_xlim(0, 10); ax.set_ylim(0, 15); ax.axis("off")


def diamond(x, y, w, h, text, fs=8):
    ax.add_patch(Polygon([(x, y + h / 2), (x + w / 2, y + h), (x + w, y + h / 2), (x + w / 2, y)], fc="#fff7ed", ec="#c2410c", lw=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=INK)


box(ax, 2.4, 14.0, 5.2, 0.7, "START: validated NFA (Q, Σ, δ, q0, F)", fc=TINT, ec=BLUE, bold=True, fs=8)
box(ax, 2.5, 12.6, 5, 0.9, "Register start subset {q0}\nenqueue it in the BFS queue")
arrow(ax, (5, 14.0), (5, 13.5))
diamond(2.5, 10.9, 5, 1.2, "Queue empty?")
arrow(ax, (5, 12.6), (5, 12.1))
box(ax, 2.5, 9.4, 5, 0.9, "Dequeue current subset S")
arrow(ax, (5, 10.9), (5, 10.3), "no", dx=0.3, dy=0)
diamond(2.5, 7.9, 5, 1.2, "Another symbol a in Σ?")
arrow(ax, (5, 9.4), (5, 9.1))
box(ax, 2.2, 6.2, 5.6, 1.1, "T = union of δ(q, a) for every q in S\n(empty union → ∅, the dead state)")
arrow(ax, (5, 7.9), (5, 7.3), "yes", dx=0.3, dy=0)
diamond(2.5, 4.6, 5, 1.2, "Is T new?")
arrow(ax, (5, 6.2), (5, 5.8))
box(ax, 0.2, 2.9, 4.2, 1.1, "Register T, enqueue it\nis_accepting = T ∩ F ≠ ∅")
box(ax, 5.6, 2.9, 4.2, 1.1, "Reuse existing DFA state T")
arrow(ax, (3.2, 4.6), (2.3, 4.0), "yes", dx=-0.3, dy=0.05)
arrow(ax, (6.8, 4.6), (7.7, 4.0), "no", dx=0.3, dy=0.05)
box(ax, 2.2, 1.3, 5.6, 1.0, "Record edge S --a--> T and a log step", fc=GTINT, ec=GREEN)
arrow(ax, (2.3, 2.9), (4.0, 2.3)); arrow(ax, (7.7, 2.9), (6.0, 2.3))
# loop back to next symbol
ax.add_patch(FancyArrowPatch((7.8, 1.8), (9.4, 1.8), arrowstyle="-", lw=1.2, color=LINE))
ax.add_patch(FancyArrowPatch((9.4, 1.8), (9.4, 8.5), arrowstyle="-", lw=1.2, color=LINE))
arrow(ax, (9.4, 8.5), (7.5, 8.5), "next symbol", dy=0.15, dx=0.2)
# no more symbols -> back to queue test
ax.add_patch(FancyArrowPatch((2.5, 8.5), (0.8, 8.5), arrowstyle="-", lw=1.2, color=LINE))
ax.add_patch(FancyArrowPatch((0.8, 8.5), (0.8, 11.5), arrowstyle="-", lw=1.2, color=LINE))
arrow(ax, (0.8, 11.5), (2.5, 11.5), "")
ax.text(1.0, 8.65, "no more\nsymbols", fontsize=7.5, color=INK)
# queue empty -> end
ax.add_patch(FancyArrowPatch((7.5, 11.5), (9.0, 11.5), arrowstyle="-|>", mutation_scale=12, lw=1.2, color=LINE))
ax.text(8.25, 11.62, "yes", fontsize=7.5, ha="center", color=INK)
box(ax, 7.8, 12.5, 2.0, 0.9, "END: return\nDFA + steps", fc=TINT, ec=BLUE, fs=8, bold=True)
ax.add_patch(FancyArrowPatch((9.0, 11.5), (9.0, 12.5), arrowstyle="-|>", mutation_scale=12, lw=1.2, color=LINE))
fig.savefig(OUT / "fig_flowchart.png", dpi=200, bbox_inches="tight"); plt.close(fig)
print("ok")

# ---------------- Figure: scaling chart ----------------
import json
ev = json.loads((OUT.parent / "TestCases" / "evidence.json").read_text())
sc = ev["scaling"]
fig, ax1 = plt.subplots(figsize=(6.4, 3.4))
ns = [r["n"] for r in sc]
ax1.plot(ns, [r["dfa_states"] for r in sc], "o-", color=BLUE, label="DFA states produced")
ax1.plot(ns, [r["expected"] for r in sc], "--", color="#94a3b8", label="2ⁿ (theoretical)")
ax1.set_yscale("log"); ax1.set_xlabel("n  (NFA has n+1 states)"); ax1.set_ylabel("DFA states (log scale)")
ax2 = ax1.twinx(); ax2.bar(ns, [r["ms"] for r in sc], alpha=0.25, color=GREEN, label="conversion time (ms)")
ax2.set_ylabel("conversion time (ms)")
h1, l1 = ax1.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=8); ax1.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(OUT / "fig_scaling.png", dpi=200); plt.close(fig)
