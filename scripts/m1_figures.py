"""Figures for the Milestone-1 report: processing workflow and UI wireframe (matplotlib)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).resolve().parent.parent / "Milestone1" / "Figures"
OUT.mkdir(parents=True, exist_ok=True)
INK, LINE, BLUE, TINT, GREEN, GTINT, RED, RTINT = "#0f172a", "#475569", "#1d4ed8", "#eff6ff", "#047857", "#ecfdf5", "#b91c1c", "#fef2f2"


def box(ax, x, y, w, h, text, fc="white", ec=LINE, fs=8.5, bold=False, ha="center"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=1.2))
    tx = x + w / 2 if ha == "center" else x + 0.15
    ax.text(tx, y + h / 2, text, ha=ha, va="center", fontsize=fs, color=INK, weight="bold" if bold else "normal")


def arrow(ax, p, q, text=None, dx=0.0, dy=0.1, fs=7.5):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=12, lw=1.2, color=LINE))
    if text:
        ax.text((p[0] + q[0]) / 2 + dx, (p[1] + q[1]) / 2 + dy, text, fontsize=fs, color=INK, ha="center")


# ---------------- processing workflow ----------------
fig, ax = plt.subplots(figsize=(8.6, 7.4)); ax.set_xlim(0, 12); ax.set_ylim(0, 10.4); ax.axis("off")
box(ax, 3.6, 9.5, 4.8, 0.7, "User input / preset chooser", fc=TINT, ec=BLUE, bold=True)
box(ax, 3.0, 7.9, 6.0, 1.0, "Input validation (algorithm/validate.py)\nsplit, de-duplicate, reject ε, check Σ and Q")
arrow(ax, (6, 9.5), (6, 8.9))
box(ax, 9.6, 7.9, 2.2, 1.0, "Friendly error\nbadges", fc=RTINT, ec=RED, fs=8)
arrow(ax, (9.0, 8.4), (9.6, 8.4), "invalid", dy=0.15)
box(ax, 3.0, 6.3, 6.0, 1.0, "Live NFA diagram (ui/graphs.py)\nGraphviz DOT, rendered in the browser")
arrow(ax, (6, 7.9), (6, 7.3), "valid NFA", dx=0.8, dy=0)
box(ax, 2.6, 4.2, 6.8, 1.5, "Subset construction (subset_construction.py)\nS₀ = {q₀}; BFS queue; for each a ∈ Σ:\nT = ⋃ δ(q, a); register T if new; log step", fc=GTINT, ec=GREEN, fs=8.5)
arrow(ax, (6, 6.3), (6, 5.7), "user clicks Convert to DFA", dx=1.6, dy=0)
for x, t in ((0.4, "DFA graph generator\nnode / edge focus\nhighlights"), (4.4, "Step player controller\nslider 0…N and\nEnglish step log"), (8.4, "Dual simulation engine\nstrings on NFA and DFA,\nagreement badge")):
    box(ax, x, 1.4, 3.2, 1.5, t, fs=8)
    arrow(ax, (6, 4.2), (x + 1.6, 2.9))
ax.text(6, 0.7, "Outputs: DFA diagram · construction log · transition tables · verdicts", ha="center", fontsize=8.5, color=LINE, style="italic")
fig.savefig(OUT / "fig_m1_workflow.png", dpi=200, bbox_inches="tight"); plt.close(fig)

# ---------------- UI wireframe ----------------
fig, ax = plt.subplots(figsize=(8.6, 9.2)); ax.set_xlim(0, 12); ax.set_ylim(0, 13); ax.axis("off")
ax.add_patch(FancyBboxPatch((0.1, 0.1), 11.8, 12.8, boxstyle="round,pad=0.02,rounding_size=0.1", fc="#f8fafc", ec=LINE, lw=1.4))
box(ax, 0.4, 12.0, 11.2, 0.7, "HEADER   Automata Workbench   ·   NFA to DFA conversion by subset construction          [ Dark mode toggle ]", fc="white", fs=8, ha="left")


def card(y, h, title, left=None, right=None, ratio=0.5):
    ax.add_patch(FancyBboxPatch((0.4, y), 11.2, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc="white", ec=LINE, lw=1.2))
    ax.text(0.65, y + h - 0.3, title, fontsize=8.5, weight="bold", color=BLUE, va="center")
    if left is None: return
    w = 11.2 - 0.5
    lw = w * ratio - 0.1 if right else w
    box(ax, 0.65, y + 0.2, lw, h - 0.8, left, fc="#f1f5f9", ec="#cbd5e1", fs=7.5)
    if right:
        box(ax, 0.65 + lw + 0.2, y + 0.2, w - lw - 0.2, h - 0.8, right, fc="#f1f5f9", ec="#cbd5e1", fs=7.5)


card(9.6, 2.1, "ROW 1 · NFA EDITOR & CONFIGURATION        [ Convert to DFA ]  [ Reset editor ]",
     "Preset dropdown (Custom first, 13 presets)\nStates input  |  Alphabet input\nStart select  |  Accepting multiselect",
     "Transition table δ(state, symbol)\nEntry mode: (•) Choose states  ( ) Type names\nGrid  State | a | b — one row per NFA state")
card(7.1, 2.3, "ROW 2 · DIAGRAMS (50 % / 50 %)",
     "NFA State Diagram\nInspect-DFA-state dropdown (highlight)\nLive NFA chart: start arrow, double-circle accepts",
     "DFA Diagram                [ Download JSON ]\nLive DFA chart grows with the step player\nDead state drawn dashed red")
card(4.9, 2.0, "ROW 3 · CONSTRUCTION STEPS",
     "Step player: [Reset] [Prev] [Play] [Next]\nSlider 0…N      counter 3 / 6",
     "Construction log (scrollable)\nStep 1: From A on 'a' → NEW state B\nStep 2: …   (active step highlighted)", ratio=0.42)
card(2.7, 2.0, "ROW 4 · TRANSITION TABLES (50 % / 50 %)",
     "NFA Transition Table   (→ start, * accept)\nState | a | b   (— = no transition)",
     "DFA Transition Table   (alias = subset)\nA = {q0} | B {q0,q1} | A {q0} | Accepting")
card(0.4, 2.1, "ROW 5 · VERIFICATION (50 % / 50 %)",
     "Single String Testing: input + Run\nVerdict badge + “NFA and DFA agree”\nDFA path / NFA frontier trace table",
     "Batch Test Suite (<empty> = ε)\nRun batch button\nTable: String | Verdict | Final DFA state")
fig.savefig(OUT / "fig_m1_wireframe.png", dpi=200, bbox_inches="tight"); plt.close(fig)
print("ok")
