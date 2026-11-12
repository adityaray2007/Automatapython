"""Generate the Milestone-II Technical Project Report (.docx).

Run from the repo root after scripts/m2_evidence.py, m2_screenshots.py and m2_figures.py:
    python3 scripts/generate_m2_doc.py
"""
import json, re, subprocess
from collections import Counter
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from team import MEMBERS, WORK
import docx
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
M2 = ROOT / "Milestone2"
SHOT, FIG = M2 / "Screenshots", M2 / "Figures"
EV = json.loads((M2 / "TestCases" / "evidence.json").read_text())
PYTEST_TXT = (M2 / "TestCases" / "pytest_output.txt").read_text()
OUT = M2 / "Report" / "Milestone2_Technical_Report.docx"

NAVY = RGBColor(0x0F, 0x17, 0x2A)
BLUE = RGBColor(0x1D, 0x4E, 0xD8)
GREY = RGBColor(0x47, 0x55, 0x69)
HEADFILL, ALTFILL = "E8EEF9", "F8FAFC"
PLACE = "[to be filled by the group]"

doc = docx.Document()
fig_n = [0]
tab_n = [0]

# ----------------------------------------------------------------- page + styles
for s in doc.sections:
    s.page_width, s.page_height = Inches(8.27), Inches(11.69)      # A4
    s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Inches(1)

st = doc.styles["Normal"]
st.font.name, st.font.size = "Calibri", Pt(11)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
st.paragraph_format.line_spacing = 1.15
st.paragraph_format.space_after = Pt(6)
for name, size, before in (("Heading 1", 16, 18), ("Heading 2", 13, 12), ("Heading 3", 11.5, 8)):
    h = doc.styles[name]
    h.font.name, h.font.size, h.font.bold = "Calibri", Pt(size), True
    h.font.color.rgb = NAVY if name != "Heading 1" else BLUE
    h.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    h.element.rPr.rFonts.set(qn("w:ascii"), "Calibri"); h.element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
    h.paragraph_format.space_before, h.paragraph_format.space_after = Pt(before), Pt(4)
    h.paragraph_format.keep_with_next = True


# ----------------------------------------------------------------- helpers
def shade(cell, fill):
    cell._tc.get_or_add_tcPr().append(parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:fill="{fill}"/>'))


def margins(cell, t=50, b=50, l=90, r=90):
    cell._tc.get_or_add_tcPr().append(parse_xml(
        f'<w:tcMar {nsdecls("w")}><w:top w:w="{t}" w:type="dxa"/><w:bottom w:w="{b}" w:type="dxa"/>'
        f'<w:left w:w="{l}" w:type="dxa"/><w:right w:w="{r}" w:type="dxa"/></w:tcMar>'))


def borders(table, color="BFC8D6"):
    tblPr = table._tbl.tblPr
    tblPr.append(parse_xml(
        f'<w:tblBorders {nsdecls("w")}>' + "".join(
            f'<w:{e} w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
            for e in ("top", "left", "bottom", "right", "insideH", "insideV")) + "</w:tblBorders>"))


def H(text, level=1):
    return doc.add_heading(text, level)


def P(text="", bold=False, italic=False, size=None, align=None, after=None, keep=False):
    p = doc.add_paragraph()
    add_runs(p, text, bold, italic, size)
    if align: p.alignment = align
    if after is not None: p.paragraph_format.space_after = Pt(after)
    if keep: p.paragraph_format.keep_with_next = True
    return p


def add_runs(p, text, bold=False, italic=False, size=None):
    """Supports **bold** and `code` inline markup, and [[placeholder]] highlighting."""
    for part in re.split(r"(\*\*.+?\*\*|`.+?`|\[\[.+?\]\])", text):
        if not part: continue
        if part.startswith("**"):
            r = p.add_run(part[2:-2]); r.bold = True
        elif part.startswith("`"):
            r = p.add_run(part[1:-1]); r.font.name = "Consolas"; r.font.size = Pt((size or 11) - 1)
            r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas"); continue
        elif part.startswith("[["):
            r = p.add_run("[" + part[2:-2] + "]"); r.font.highlight_color = 7  # yellow
        else:
            r = p.add_run(part); r.bold = bold
        r.italic = italic
        if size: r.font.size = Pt(size)


def bullets(items, style="List Bullet"):
    for it in items:
        p = doc.add_paragraph(style=style)
        p.paragraph_format.space_after = Pt(2)
        add_runs(p, it)


def numbered(items):
    """Manually numbered list (Word's built-in numbering would continue across lists)."""
    for i, it in enumerate(items, 1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.first_line_indent = Inches(-0.3)
        p.paragraph_format.space_after = Pt(2)
        p.add_run(f"{i}.\t")
        add_runs(p, it)
        p.paragraph_format.tab_stops.add_tab_stop(Inches(0.3))


def caption(kind, text):
    n = fig_n if kind == "Figure" else tab_n
    n[0] += 1
    p = doc.add_paragraph()
    r = p.add_run(f"{kind} {n[0]}: "); r.bold = True; r.font.size = Pt(9.5); r.font.color.rgb = GREY
    r = p.add_run(text); r.italic = True; r.font.size = Pt(9.5); r.font.color.rgb = GREY
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if kind == "Figure" else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(8 if kind == "Figure" else 3)
    if kind == "Table": p.paragraph_format.keep_with_next = True
    return n[0]


def figure(path, text, width=6.0):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True; p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(str(path), width=Inches(width))
    return caption("Figure", text)


def table(headers, rows, widths=None, text_size=9, caption_text=None, mono_cols=()):
    if caption_text: caption("Table", caption_text)
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    borders(t)
    for j, h in enumerate(headers):
        c = t.rows[0].cells[j]; shade(c, HEADFILL); margins(c)
        p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.bold = True; r.font.size = Pt(text_size)
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            c = t.rows[i].cells[j]; margins(c)
            if i % 2 == 0: shade(c, ALTFILL)
            p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
            add_runs(p, str(val), size=text_size)
            if j in mono_cols:
                for r in p.runs: r.font.name = "Consolas"
    # repeat header row on page break, never split a row
    trPr = t.rows[0]._tr.get_or_add_trPr(); trPr.append(OxmlElement("w:tblHeader"))
    for row in t.rows:
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
    if widths:
        for row in t.rows:
            for j, w in enumerate(widths): row.cells[j].width = Inches(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def code(text, size=8.5):
    t = doc.add_table(rows=1, cols=1); borders(t, "CBD5E1")
    c = t.rows[0].cells[0]; shade(c, "F1F5F9"); margins(c, 80, 80, 120, 120)
    lines = text.strip("\n").split("\n")
    p = c.paragraphs[0]
    for i, line in enumerate(lines):
        r = p.add_run(line); r.font.name = "Consolas"; r.font.size = Pt(size)
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
        if i < len(lines) - 1: r.add_break()
    p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def page_break():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def add_field(p, instr):
    for kind, txt in (("begin", None), (None, instr), ("end", None)):
        r = p.add_run()
        if kind:
            fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), kind); r._r.append(fc)
        else:
            it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = txt; r._r.append(it)


# ----------------------------------------------------------------- header / footer
sec = doc.sections[0]
sec.different_first_page_header_footer = True
hp = sec.header.paragraphs[0]
hr = hp.add_run("CSET302 – Automata Theory and Computability  |  Milestone-II Technical Report"); hr.font.size = Pt(8.5); hr.font.color.rgb = GREY
fp = sec.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
fr = fp.add_run("Automata Workbench – NFA to DFA Conversion Simulator   |   Page "); fr.font.size = Pt(8.5); fr.font.color.rgb = GREY
add_field(fp, "PAGE")

# ================================================================= COVER PAGE
for _ in range(2): P("")
P("BENNETT UNIVERSITY", bold=True, size=20, align=WD_ALIGN_PARAGRAPH.CENTER, after=0)
P("School of Computer Science and Engineering Technology (SCSET)", size=12, align=WD_ALIGN_PARAGRAPH.CENTER, after=26)
P("CSET302 – Automata Theory and Computability", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
P("Automata Theory Simulator Development Project", size=12, align=WD_ALIGN_PARAGRAPH.CENTER, after=26)
P("MILESTONE-II", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, after=0)
P("Technical Project Report", bold=True, size=24, align=WD_ALIGN_PARAGRAPH.CENTER, after=14)
P("Automata Workbench", bold=True, size=20, align=WD_ALIGN_PARAGRAPH.CENTER, after=0)
P("An interactive NFA → DFA conversion simulator based on the subset construction", italic=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER, after=30)
meta = doc.add_table(rows=6, cols=2); meta.alignment = WD_TABLE_ALIGNMENT.CENTER; borders(meta)
for i, (k, v) in enumerate([
    ("Project topic", "Topic 1: NFA → DFA Conversion Simulator"),
    ("Group ID", f"[[{PLACE}]]"),
    ("Group members (name – enrolment ID)", "\n".join(f"{n} – {i}" for n, i in MEMBERS)),
    ("Faculty name", f"[[{PLACE}]]"),
    ("Evaluation window", "23–27 November 2026"),
    ("Submission date", f"[[{PLACE}]]")]):
    a, b = meta.rows[i].cells; a.width, b.width = Inches(2.4), Inches(3.9)
    shade(a, HEADFILL); margins(a, 80, 80); margins(b, 80, 80)
    a.paragraphs[0].add_run(k).bold = True
    for n, line in enumerate(v.split("\n")):
        pp = b.paragraphs[0] if n == 0 else b.add_paragraph()
        pp.paragraph_format.space_after = Pt(0)
        add_runs(pp, line)
page_break()

# ================================================================= ABSTRACT + CONTENTS
H("Abstract", 1)
P("Non-deterministic finite automata (NFAs) are convenient to design but cannot be executed directly by a deterministic machine, so converting an NFA to an "
  "equivalent deterministic finite automaton (DFA) is a core topic of Automata Theory. Students usually meet the subset construction only as a pencil-and-paper "
  "procedure, which makes errors easy and the idea hard to see. This report presents **Automata Workbench**, a Python and Streamlit simulator that accepts an NFA, "
  "validates it, converts it to a DFA with the subset construction, and shows every step of the conversion. The simulator provides an NFA editor with thirteen "
  "verified presets, live NFA and DFA diagrams generated as Graphviz DOT, a step player with a natural-language construction log, NFA and DFA transition tables, "
  "single-string and batch testing on both machines, and JSON export of the DFA. All automata logic lives in a pure-Python package with no user-interface imports, "
  "which keeps it testable and explainable. Verification combined a 59-case automated pytest suite, sixteen documented functional test cases, a hand-worked trace, "
  f"and an exhaustive equivalence check of the NFA and DFA on every string of length up to 8 for all thirteen presets ({EV['total_equiv_checks']:,} comparisons, "
  "no disagreement). The worst-case growth of 2ⁿ DFA states was reproduced up to n = 11 (2,048 states, about 23 ms). The main limitations are the absence of ε-transitions "
  "and a 12-state input limit.", after=4)
P("**Keywords:** NFA, DFA, subset construction, powerset construction, automata simulator, Python, Streamlit.", size=10)

H("Contents", 2)
for line in ["1. Introduction", "2. Objectives and Requirements", "3. Background and Theory", "4. System Design", "5. Implementation",
             "6. Testing and Verification", "7. Results and Discussion", "8. Team Contributions", "9. Conclusion and Future Scope",
             "References", "Appendix A – Repository map and README summary", "Appendix B – Automated test log",
             "Appendix C – Additional screenshots", "Appendix D – User manual", "Appendix E – Submission checklist"]:
    P(line, after=1)
page_break()

# ================================================================= 1 INTRODUCTION
H("1. Introduction", 1)
H("1.1 Motivation", 2)
P("An NFA may be in several states at once and may have no move at all on some symbol, whereas a DFA is always in exactly one state and has exactly one move per "
  "symbol. Real hardware and most programs behave like DFAs, so the equivalence of the two models (Rabin and Scott, 1959) is practically important as well as "
  "theoretically elegant. The conversion is mechanical but tedious: for an NFA with n states there can be 2ⁿ candidate subsets, and a single slip in a union "
  "silently produces a wrong machine. A tool that performs the construction, shows each step and checks the result against the original NFA turns the topic from "
  "memorisation into something that can be explored.")
H("1.2 Learning objective", 2)
P("After using the simulator a student should be able to (i) explain why every DFA state in the construction is a set of NFA states, (ii) carry out the construction by "
  "hand on a small NFA, (iii) predict when the DFA will contain a dead state or grow exponentially, and (iv) justify that the NFA and the DFA accept the same language.")
H("1.3 Problem statement", 2)
P("**Given** an NFA M = (Q, Σ, δ, q₀, F) without ε-transitions, entered through a graphical editor, **produce** an equivalent total DFA M′ = (Q′, Σ, δ′, S₀, F′), "
  "display both machines, expose each step of the construction, and let the user verify equivalence by running strings on both machines.")
H("1.4 Scope", 2)
bullets([
    "**In scope:** NFAs without ε-transitions; single-character input symbols; up to 12 NFA states; subset construction restricted to reachable subsets; visualisation, "
    "step-by-step explanation, string testing, and export of the DFA as JSON.",
    "**Out of scope (documented limitations):** ε-NFAs, DFA minimisation, regular expressions, context-free grammars, pushdown automata and Turing machines.",
])

# ================================================================= 2 OBJECTIVES & REQUIREMENTS
H("2. Objectives and Requirements", 1)
H("2.1 Project objectives", 2)
numbered([
    "Convert any valid NFA to an equivalent total DFA using the subset construction.",
    "Make the construction transparent: show the union computed for every (DFA state, symbol) pair and whether it created a new state.",
    "Verify correctness inside the tool by simulating strings on both machines and reporting agreement.",
    "Keep the automata engine free of UI code so that every function can be read, tested and explained on its own.",
    "Provide clear, friendly validation errors instead of crashes for malformed input.",
])
H("2.2 Supported operations", 2)
table(["ID", "Operation", "Where"], [
    ["O1", "Define an NFA (states, alphabet, start, accepting states, δ) or load one of 13 presets / a blank custom NFA", "NFA editor"],
    ["O2", "Draw the NFA live as the user edits it", "NFA diagram"],
    ["O3", "Convert NFA → DFA with the subset construction", "Convert to DFA"],
    ["O4", "Step through the construction (reset, previous, next, auto-play, slider) with a text log", "Construction steps"],
    ["O5", "Show the NFA and DFA transition tables and the subset behind every DFA state", "Transition tables"],
    ["O6", "Highlight, on the NFA diagram, the NFA states that make up a chosen DFA state", "Inspect dropdown"],
    ["O7", "Run one string, or a batch, on both machines and compare verdicts", "String testing"],
    ["O8", "Export the DFA as JSON", "Download JSON"],
    ["O9", "Switch between light and dark themes", "Header toggle"],
], widths=[0.5, 4.4, 1.4], caption_text="Operations supported by the simulator.")
H("2.3 Functional requirements", 2)
table(["ID", "Requirement", "Verified by"], [
    ["FR1", "Reject invalid definitions (duplicate or unknown states, multi-character symbols, ε, more than 12 states) with a readable message.", "T06–T10, test_validate.py"],
    ["FR2", "Treat an empty δ cell as “no transition”.", "T11, test_validate.py"],
    ["FR3", "Produce a DFA that is total: every state has an edge for every symbol.", "test_subset.py"],
    ["FR4", "Create an explicit dead state ∅ when a union is empty, and make it a trap.", "T11, T12"],
    ["FR5", "Mark a DFA state accepting if and only if it contains an NFA accepting state.", "T01–T04, T13"],
    ["FR6", "Give deterministic output (same names and order on every run).", "test_subset.py"],
    ["FR7", "Report symbols outside the alphabet without crashing.", "T05"],
    ["FR8", "Show agreement or disagreement of the NFA and DFA for each tested string.", "T16, test_simulate.py"],
    ["FR9", "Invalidate old results when the NFA is edited after converting.", "test_app.py"],
], widths=[0.5, 4.3, 1.5], caption_text="Functional requirements and where each is verified.")
H("2.4 Non-functional requirements", 2)
table(["ID", "Requirement", "How it is met"], [
    ["NFR1", "Portability", "Python 3.10+ and Streamlit only; Graphviz DOT is rendered in the browser, so no system Graphviz install is required."],
    ["NFR2", "Responsiveness", "Conversion of a 12-state worst case takes about 23 ms (Section 7.3); the page re-renders on each interaction."],
    ["NFR3", "Explainability", "Beginner-level comments in algorithm/, one sentence per construction step."],
    ["NFR4", "Testability", "Pure-logic package; 59 automated tests; one-command verification script."],
    ["NFR5", "Usability", "Presets, live diagrams, light and dark themes, input errors shown next to the editor."],
], widths=[0.6, 1.3, 4.4], caption_text="Non-functional requirements.")
H("2.5 Known limitations", 2)
bullets([
    "No ε-transitions: an ε in the alphabet or a cell is rejected with an explanatory message (Section 5.3).",
    "At most 12 states and 10 symbols are accepted, because the DFA can reach 2¹² = 4,096 states and the diagram would stop being readable.",
    "Symbols are single characters, so multi-character tokens such as “ab” are not supported.",
    "The DFA is not minimised; it contains only reachable subsets and may therefore not be the smallest equivalent DFA.",
])

# ================================================================= 3 BACKGROUND
H("3. Background and Theory", 1)
H("3.1 Finite automata", 2)
P("A **deterministic finite automaton** is a 5-tuple (Q, Σ, δ, q₀, F) where Q is a finite set of states, Σ a finite alphabet, δ : Q × Σ → Q a transition function, q₀ ∈ Q the start state "
  "and F ⊆ Q the accepting states. A **non-deterministic finite automaton** has the same components except that δ : Q × Σ → 𝒫(Q) returns a set of states, possibly empty. "
  "An NFA accepts a string w if at least one sequence of choices ends in an accepting state after reading w. This report treats NFAs without ε-transitions.")
table(["Symbol", "Meaning"], [
    ["Q, Σ, δ, q₀, F", "States, alphabet, transition function, start state, accepting states of the NFA"],
    ["Q′, δ′, S₀, F′", "States, transition function, start state and accepting states of the DFA"],
    ["𝒫(Q)", "Power set of Q (all subsets of Q)"],
    ["∅", "Empty set; as a DFA state it is the dead (trap) state"],
    ["S, T", "A DFA state, i.e. a subset of Q"],
], widths=[1.6, 4.7], caption_text="Notation used in this report.")
H("3.2 Subset (powerset) construction", 2)
P("Rabin and Scott showed that every NFA has an equivalent DFA whose states are subsets of Q. The construction is:")
code("""S0  = { q0 }
δ'(S, a) = ⋃  δ(q, a)     for every q ∈ S
F'  = { S ∈ Q' : S ∩ F ≠ ∅ }""", 10)
P("Only subsets reachable from S₀ are generated, using a breadth-first queue. If δ′(S, a) is empty the DFA moves to the dead state ∅, which loops to itself on every symbol, "
  "so δ′ is total. Because Q has n elements the power set has 2ⁿ members, which is also the worst-case number of DFA states. The family “the n-th symbol from the end is a” "
  "reaches this bound exactly, and is used in Section 7.3 to confirm the implementation.")
H("3.3 Correctness argument", 2)
P("The invariant of the construction is that after reading a prefix u, the DFA is in the state S_u = { q : q is reachable from q₀ on u in the NFA }. It holds for u = ε because "
  "S₀ = {q₀}, and it is preserved by every step because δ′(S_u, a) is by definition the set of states reachable on ua. Hence the DFA is in a set containing an accepting NFA state "
  "exactly when some NFA computation on w accepts, i.e. the two machines accept the same language. The simulator also checks this empirically for every tested string.")

# ================================================================= 4 SYSTEM DESIGN
H("4. System Design", 1)
H("4.1 Architecture", 2)
P("The system has two layers. The **logic layer** (`algorithm/`) contains the data model, validation, the subset construction, string simulation and the sentence generator for the step log; "
  "it imports no Streamlit or other UI code, and an automated test (`test_purity.py`) enforces this. The **presentation layer** (`app.py`, `ui/`) holds session state, widgets, layout, "
  "Graphviz DOT generation and the light/dark theme, and calls the logic layer through plain function calls.")
figure(FIG / "fig_architecture.png", "System architecture: presentation layer and pure-logic layer.", 6.2)
H("4.2 Module responsibilities", 2)
table(["Module", "Responsibility", "Key functions / classes"], [
    ["algorithm/models.py", "Plain dataclasses, no behaviour", "NFA, DFA, DFAState, MoveDetail, ConstructionStep, ConversionResult"],
    ["algorithm/validate.py", "Parse editor text into a valid NFA or a list of errors", "split_list, build_nfa, NfaForm"],
    ["algorithm/subset_construction.py", "The core algorithm", "subset_construction, set_id, alias_for"],
    ["algorithm/simulate.py", "Run strings on the DFA and the NFA", "simulate_dfa, simulate_nfa, parse_batch"],
    ["algorithm/explain.py", "Turn one construction step into an English sentence", "describe_step"],
    ["algorithm/examples.py", "Five textbook presets with expected DFA sizes and test strings", "EXAMPLES"],
    ["algorithm/demo.py", "Terminal demonstration without the UI", "python -m algorithm.demo"],
    ["ui/graphs.py", "Build Graphviz DOT text for NFA and DFA, theme-aware", "nfa_to_dot, dfa_to_dot"],
    ["ui/styles.py", "Light and dark theme stylesheet", "build_css"],
    ["app.py", "Streamlit page: editor, diagrams, step player, tables, tests; eight extra presets", "callbacks on_convert, on_step_*"],
    ["scripts/verify.py", "One-command check: compile, pytest, server smoke test", "-"],
], widths=[1.9, 2.5, 1.9], text_size=8.5, caption_text="Modules and their responsibilities.")
H("4.3 Data structures", 2)
table(["Structure", "Representation", "Why"], [
    ["NFA transitions", "dict[state][symbol] → list of states; a missing key means no transition", "Sparse, and an absent entry maps directly onto δ(q, a) = ∅"],
    ["DFA state", "Dataclass with id (e.g. {q0,q1}), alias (A, B, …), members, flags", "The textual id is a hashable key; the alias keeps diagrams readable"],
    ["Subset", "List sorted by NFA declaration order, duplicates removed", "Same subset always gets the same id, so output is deterministic"],
    ["Work queue", "collections.deque of DFAState", "Breadth-first exploration; each subset is processed once"],
    ["Construction log", "List of ConstructionStep (from, symbol, per-state moves, result, is_new_state)", "Drives the step player, the log and the DFA diagram growth"],
], widths=[1.4, 2.7, 2.2], text_size=8.5, caption_text="Main data structures.")
H("4.4 Workflow", 2)
numbered([
    "The user edits (or loads) an NFA. On every interaction the editor fields are turned into an `NfaForm` and validated; the NFA diagram and NFA table update live.",
    "On **Convert to DFA** the validated NFA is passed to `subset_construction`. The result and a signature of the editor contents are stored in session state.",
    "The DFA diagram, tables and step player are shown only while the stored signature equals the current editor signature; editing the NFA therefore invalidates the result (FR9).",
    "The step player draws the DFA using only the first k construction steps, and the log shows the sentence for each of those steps.",
    "Test strings are run on both machines; the page shows the verdict, the DFA path, the NFA state sets and an agreement badge.",
])
H("4.5 Algorithm design", 2)
P("Pseudocode of the implemented algorithm (breadth-first subset construction):", keep=True)
code("""function SUBSET_CONSTRUCTION(NFA = (Q, Σ, δ, q0, F)):
    order  ← position of each state in the declared list Q
    known  ← empty map  id → DFAState;   queue ← empty FIFO queue;   steps ← []
    S0 ← REGISTER( {q0} );  mark S0 as start;  ENQUEUE(queue, S0)

    while queue is not empty:
        S ← DEQUEUE(queue)
        for each symbol a in Σ (declared order):
            moves ← [ (q, SORT(δ(q, a), order)) for each q in S ]
            T     ← SORT( UNION of all targets in moves, order )
            target, isNew ← REGISTER(T)
            if isNew: ENQUEUE(queue, target)
            DFA.δ'[S][a] ← target
            APPEND(steps, (S, a, moves, T, target, isNew))

    return (DFA, steps)

function REGISTER(T):
    id ← "∅" if T is empty else "{" + join(T, ",") + "}"
    if id in known: return (known[id], false)
    create DFAState(id, alias = next letter, members = T,
                    is_accepting = (T ∩ F ≠ ∅),  is_dead = (T = ∅))
    return (new state, true)""", 8.3)
P("**Complexity.** Each reachable DFA state is dequeued once, and for each of the |Σ| symbols the union costs at most O(n) lookups, giving O(|Q′| · |Σ| · n) time. "
  "In the worst case |Q′| = 2ⁿ, which is why the input is limited to 12 states.")
figure(FIG / "fig_flowchart.png", "Flowchart of the subset construction as implemented.", 4.3)
H("4.6 User-interface design", 2)
P("The interface is a flat, neutral layout of five horizontal rows: the NFA editor (full width), the NFA and DFA diagrams side by side, the Construction Steps card (player on the "
  "left, scrolling log on the right), the NFA and DFA transition tables side by side, and the single-string and batch testers side by side. A toggle in the header switches between "
  "light and dark themes. Buttons that cannot be used yet (step player, string tests) are disabled until the NFA has been converted. Figure 3 shows the finished interface.")
figure(SHOT / "fig02_full_interface_light.png", "The complete interface after converting the preset “Ends with ab” (light theme).", 5.4)

# ================================================================= 5 IMPLEMENTATION
H("5. Implementation", 1)
H("5.1 Technology stack", 2)
table(["Item", "Choice", "Version / note"], [
    ["Language", "Python", "3.10 or newer (developed on 3.13)"],
    ["UI framework", "Streamlit", ">= 1.40 (tested on 1.67.0)"],
    ["Diagrams", "Graphviz DOT via st.graphviz_chart", "Rendered in the browser; no system Graphviz needed"],
    ["Testing", "pytest and Streamlit AppTest", "pytest >= 8 (tested on 9.2.0)"],
    ["Third-party code", "None beyond the above", "All algorithms written by the group"],
], widths=[1.4, 2.4, 2.5], caption_text="Technology stack.")
H("5.2 Core logic", 2)
P("The heart of the program is the loop below (from `algorithm/subset_construction.py`, comments shortened). For every symbol it collects, for each NFA state in the current subset, "
  "where that state can go, takes the union, and either reuses or registers the resulting subset:", keep=True)
code("""while queue:
    current = queue.popleft()
    for symbol in nfa.alphabet:
        moves = [MoveDetail(state=q,
                            targets=normalize(nfa.transitions.get(q, {}).get(symbol, [])))
                 for q in current.members]
        result_members = normalize(t for move in moves for t in move.targets)   # the union
        seen_before = len(known)
        target = register(result_members)
        is_new = len(known) > seen_before
        if is_new:
            queue.append(target)
        dfa_transitions[current.id][symbol] = target.id
        steps.append(ConstructionStep(index=len(steps), from_id=current.id, symbol=symbol,
                     moves=moves, result_members=result_members,
                     result_id=target.id, is_new_state=is_new))""", 8.3)
P("`normalize` removes duplicates and sorts by declaration order, which makes ids such as `{q0,q1}` canonical. String simulation tracks one state for the DFA and a **set** of states "
  "for the NFA (`simulate_nfa`), and the NFA frontier after each symbol is shown next to the DFA state in the trace table.")
H("5.3 Input validation and invalid cases", 2)
table(["Condition", "Handling"], [
    ["Duplicate state names / duplicate symbols", "Error “State names must be unique.” / “Input symbols must be unique.”"],
    ["More than 12 states", "Error “At most 12 states are supported.”"],
    ["Characters that would break the DOT output ({ } \" \\ `)", "Error naming the offending state"],
    ["Multi-character symbol", "Error “Input symbol … must be a single character.”"],
    ["ε, eps, epsilon, λ, lambda in alphabet or cells", "Error “ε-transitions are not supported here — this simulator handles plain NFAs only.”"],
    ["Start or accepting state not declared; δ points to an unknown state", "Error naming the state"],
    ["Empty δ cell", "Valid: means no transition (the NFA branch dies); contributes nothing to a union"],
    ["Test string contains a symbol outside Σ", "Rejected with a warning; no crash"],
    ["Empty test string", "Allowed; accepted only if the start state is accepting (use `<empty>` in batch mode)"],
], widths=[2.7, 3.6], text_size=8.5, caption_text="Validation rules and handling of invalid input.")
P("**Incomplete machines and ε.** The input is an NFA, so missing transitions are legal. In the DFA they are made explicit: whenever a union is empty the construction creates the dead "
  "state ∅ (drawn dashed in red) and sends the transition there; the DFA is therefore always total, and the dead state is created only when it is actually reached. ε input is "
  "never silently ignored; it produces the error above.")
H("5.4 State handling in the user interface", 2)
P("Streamlit re-runs the script on every interaction, so the application keeps the editor contents, the conversion result, the step counter and test results in `st.session_state`. "
  "A signature string built from all editor fields decides whether a stored result is still fresh. Callbacks (`on_convert`, `on_step_next`, …) change state before the next run, "
  "which keeps the step player consistent. The theme toggle regenerates both the CSS and the Graphviz colours, so diagrams stay readable in dark mode.")
H("5.5 Code documentation conventions", 2)
bullets([
    "Every module starts with a docstring explaining its purpose in plain English; every public function has a docstring stating inputs and results.",
    "Data containers are dataclasses with a comment per field; names follow the mathematics (`transitions`, `accepts`, `members`).",
    "The repository contains a README with setup, run, test and viva-demo commands, a repository map and a test sheet (Appendix A).",
])

# ================================================================= 6 TESTING
H("6. Testing and Verification", 1)
H("6.1 Test plan", 2)
P("Testing has four layers: (1) unit tests of the logic layer, (2) headless end-to-end tests of the interface using Streamlit AppTest, (3) sixteen documented functional test cases "
  "(Table 10) that were executed by script against the real code, and (4) an exhaustive equivalence check and a hand-worked example that check mathematical correctness.")
counts = Counter(re.findall(r"^tests/(test_\w+)\.py::", PYTEST_TXT, flags=re.M))
descr = {"test_app": "End-to-end UI behaviour: presets, string tests, validation messages, step player, invalidation",
         "test_examples": "Preset consistency and expected DFA sizes", "test_explain": "Wording of the construction-step sentences",
         "test_graphs": "DOT output: double circles, start arrow, dead state, edge merging, highlighting",
         "test_purity": "algorithm/ has no UI imports", "test_simulate": "Verdicts, NFA/DFA agreement up to length 8, traces, batch parsing",
         "test_subset": "Exact DFAs, dead state, totality, determinism", "test_validate": "Every validation rule in Table 8"}
rows = [[f"tests/{k}.py", descr[k], counts[k]] for k in sorted(counts)]
rows.append(["**Total**", "", f"**{sum(counts.values())}**"])
table(["File", "What it checks", "Tests"], rows, widths=[1.6, 4.0, 0.7], text_size=8.5, caption_text="Automated test suite (all tests passed).")
H("6.2 Functional test cases", 2)
P("Each case below was executed against the real implementation by `scripts/m2_evidence.py`; the “Actual result” column is the program's own output, not typed in by hand. "
  "The machine under test is the preset “Ends with ab” (Σ = {a,b}) unless stated otherwise.")
table(["ID", "Feature / input", "Expected", "Actual result", "Status"],
      [[c["id"], f"{c['feature']}; {c['input']}", c["expected"], c["actual"], c["status"]] for c in EV["cases"]],
      widths=[0.4, 2.0, 1.3, 2.1, 0.5], text_size=8, caption_text="Functional test cases with expected and actual results.")
n_pass = sum(c["status"] == "Pass" for c in EV["cases"])
P(f"**Result:** {n_pass} of {len(EV['cases'])} functional cases passed. Evidence for the user-interface cases is shown in Figures 5 to 7 and 12.")
H("6.3 Hand-worked validation example", 2)
P("NFA: Q = {q0, q1, q2}, Σ = {a, b}, start q0, F = {q2}; δ(q0,a) = {q0,q1}, δ(q0,b) = {q0}, δ(q1,b) = {q2}, all other cells empty (strings ending in “ab”). "
  "The construction below was done by hand first and then compared with the simulator.")
table(["Step", "From", "Symbol", "δ for each member", "Union", "Result"], [
    ["1", "A = {q0}", "a", "δ(q0,a) = {q0,q1}", "{q0,q1}", "NEW state B"],
    ["2", "A = {q0}", "b", "δ(q0,b) = {q0}", "{q0}", "existing A"],
    ["3", "B = {q0,q1}", "a", "δ(q0,a) = {q0,q1}; δ(q1,a) = ∅", "{q0,q1}", "existing B"],
    ["4", "B = {q0,q1}", "b", "δ(q0,b) = {q0}; δ(q1,b) = {q2}", "{q0,q2}", "NEW state C"],
    ["5", "C = {q0,q2}", "a", "δ(q0,a) = {q0,q1}; δ(q2,a) = ∅", "{q0,q1}", "existing B"],
    ["6", "C = {q0,q2}", "b", "δ(q0,b) = {q0}; δ(q2,b) = ∅", "{q0}", "existing A"],
], widths=[0.4, 0.95, 0.6, 2.2, 0.85, 1.0], text_size=8.5, caption_text="Hand-worked subset construction for “Ends with ab”.")
table(["DFA state", "Subset", "on a", "on b", "Accepting"], [
    ["→ A", "{q0}", "B", "A", "No"], ["B", "{q0,q1}", "B", "C", "No"], ["C", "{q0,q2}", "B", "A", "Yes (contains q2)"]],
    widths=[0.9, 1.1, 0.8, 0.8, 1.8], caption_text="Resulting DFA (identical to the simulator's output in Figure 4).")
P("**String checks.** “ab”: A –a→ B –b→ C (accepting) and the NFA frontier {q0} → {q0,q1} → {q0,q2} contains q2: accepted by both. “aab”: A → B → B → C: accepted. “abb”: A → B → C → A: "
  "rejected (frontier {q0} contains no q2). ε: stays in A, which is not accepting: rejected. These are exactly cases T01–T04 in Table 10, and the simulator's answers agree with the hand trace.")
H("6.4 Equivalence and preset verification", 2)
P(f"For every one of the 13 presets, the NFA and the generated DFA were run on **every** string over the alphabet of length 0 to 8 ({EV['total_equiv_checks']:,} comparisons in total). "
  "No disagreement was found. Table 13 lists the presets, the NFA and DFA sizes and the number of strings compared.")
table(["Preset", "NFA states", "Σ", "DFA states", "Dead state", "Strings compared", "Mismatches"],
      [[p["title"], p["nfa_states"], ",".join(p["alphabet"]), p["dfa_states"], "yes" if p["has_dead"] else "no", f"{p['strings']:,}", p["mismatches"]] for p in EV["presets"]],
      widths=[2.3, 0.6, 0.5, 0.6, 0.6, 0.9, 0.7], text_size=8, caption_text="Conversion and equivalence results for all presets.")
H("6.5 How to run the tests", 2)
code("""cd nfa2dfa-simulator
python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest              # expected: 59 passed
.venv/bin/python scripts/verify.py      # compile + tests + server smoke test (3 x PASS)
.venv/bin/python -m algorithm.demo      # terminal demonstration of the construction""", 9)
P("Reference checking: results were compared with the hand-worked trace in Section 6.3 and with the expected DFA sizes recorded with each textbook preset. "
  "A comparison with JFLAP was not performed for this report.")

# ================================================================= 7 RESULTS
H("7. Results and Discussion", 1)
H("7.1 Simulator output", 2)
P("Figures 4 to 7 show the simulator in use. The construction log in Figure 5 is the log produced up to step 3 of the hand-worked example, and the string tester in Figure 6 confirms that “aab” is accepted "
  "with the DFA path A → B → B → C and the NFA frontiers shown side by side.")
figure(SHOT / "el_dfa_diagram.png", "DFA diagram for “Ends with ab”: start arrow, double circle for the accepting state C.", 4.6)
figure(SHOT / "el_construction_step3.png", "Step player paused at step 3 of 6; the active log entry is highlighted and the DFA shows only what has been discovered so far.", 5.9)
figure(SHOT / "el_string_test.png", "Single-string test of “aab” with the DFA/NFA trace and agreement badge.", 4.4)
figure(SHOT / "el_batch_test.png", "Batch test of five strings, including <empty> for ε.", 4.2)
H("7.2 Larger examples and the dead state", 2)
P("The preset “3rd symbol from the end is a” has 4 NFA states and produces an 8-state DFA (Figure 8), illustrating the exponential growth. The preset “Starts with 0” shows the dead state "
  "∅ (Figure 9): the NFA has no move on 1 from the start state, so the DFA sends that transition to a dashed red trap state that loops on both symbols.")
figure(SHOT / "el_dfa_third_from_last.png", "DFA for “3rd symbol from the end is a”: 8 states (2³).", 5.4)
figure(SHOT / "el_dfa_dead_state.png", "DFA for “Starts with 0”: the dead state ∅ (state C) is dashed and loops on 0,1.", 3.6)
H("7.3 Behaviour at scale", 2)
P("To test the worst case, the family “the n-th symbol from the end is a” (n + 1 NFA states) was converted for n = 1 … 11. The DFA size matched 2ⁿ exactly in every case, and the conversion time "
  "(measured with `time.perf_counter` on the development laptop) grew from well under a millisecond to about 23 ms for 2,048 states.")
table(["n", "NFA states", "DFA states", "2ⁿ", "Time (ms)"], [[r["n"], r["nfa_states"], f"{r['dfa_states']:,}", f"{r['expected']:,}", r["ms"]] for r in EV["scaling"]],
      widths=[0.6, 1.0, 1.1, 1.0, 1.0], caption_text="Worst-case growth and conversion time.")
figure(FIG / "fig_scaling.png", "DFA size (log scale) and conversion time against n.", 5.0)
H("7.4 Discussion", 2)
bullets([
    "**Correctness.** Three independent kinds of evidence agree: the hand-worked trace, the 59 automated tests, and zero mismatches in 100% of the exhaustively compared strings (length ≤ 8) for all presets.",
    "**Exponential blow-up is real but bounded here.** The tool reproduces the 2ⁿ bound; the 12-state cap keeps the largest DFA at 4,096 states. The conversion itself is fast; for large DFAs the "
    "limiting factor is the readability of the diagram, not the computation.",
    "**Explainability.** Because each DFA edge is backed by a log step containing the individual δ values, a student can check any single union by hand, which was the main pedagogical goal.",
    "**Limitations.** No ε-transitions, no minimisation, single-character symbols only, 12-state limit, and equivalence is checked on strings up to length 8 rather than proven by the simulator (the proof is the invariant in Section 3.3).",
])

# ================================================================= 8 TEAM
H("8. Team Contributions", 1)
P("The project was divided so that the five members carry the same load. **The core logic (`algorithm/`) is split equally**: each member owns one module group, "
  "so every member can explain a complete part of the mathematics. **The frontend is split equally by interface component**: each member owns one visible part of the page, "
  "so no single person is responsible for the whole interface. Each member also owns one group of tests and a share of this report.")
table(["Member", "Core logic (algorithm/)", "Frontend (app.py, ui/)"],
      [[f"**{w['name']}**\n{MEMBERS[i][1]}", w["core"], w["frontend"]] for i, w in enumerate(WORK)],
      widths=[1.3, 2.7, 2.3], text_size=8.5, caption_text="Equal division of core logic and frontend.")
table(["Member", "Tests written / run", "Report sections written"],
      [[f"**{w['name']}**", w["tests"], w["report"]] for w in WORK],
      widths=[1.3, 2.5, 2.5], text_size=8.5, caption_text="Testing and documentation responsibilities.")
table(["Area", "Share per member", "Basis"], [
    ["Core logic", "20 % each", "One module group each: validate / subset_construction / simulate / models+explain+demo / examples"],
    ["Frontend", "20 % each", "One interface component each: editor / DFA diagram / string testing / step player and tables / theme and page shell"],
    ["Testing and report", "20 % each", "Each member tests their own module and writes the sections listed above"],
], widths=[1.2, 1.2, 3.9], text_size=8.5, caption_text="Summary of the equal division of work.")
P("Every member is expected to demonstrate their own module and explain its code and the related automata concept during the evaluation.")

# ================================================================= 9 CONCLUSION
H("9. Conclusion and Future Scope", 1)
P("Automata Workbench achieves its goals: it converts valid NFAs to total DFAs with the subset construction, exposes every step of the construction, verifies equivalence on demand, and handles invalid "
  "input with clear messages. The pure-logic design made the code easy to test (59 passing tests) and to explain, and the results were confirmed by a hand-worked example, an exhaustive equivalence check and a worst-case "
  "scaling experiment.")
P("**Unresolved issues:** ε-transitions are rejected rather than supported, and the produced DFA is not minimised. **Realistic enhancements:**")
bullets([
    "ε-closure so that ε-NFAs can be converted (the construction then starts from ε-closure({q₀}) and takes ε-closures after each move).",
    "DFA minimisation (table-filling or Hopcroft's algorithm) and a side-by-side comparison with the unminimised DFA.",
    "Import and export of machines in a common file format so results can be cross-checked in JFLAP.",
    "Regular expression → NFA (Thompson construction) as an input route.",
])

# ================================================================= REFERENCES
H("References", 1)
for ref in [
    "[1] M. Sipser, *Introduction to the Theory of Computation*, 3rd ed. Boston, MA: Cengage Learning, 2013.",
    "[2] J. E. Hopcroft, R. Motwani and J. D. Ullman, *Introduction to Automata Theory, Languages, and Computation*, 3rd ed. Boston, MA: Pearson, 2006.",
    "[3] M. O. Rabin and D. Scott, “Finite automata and their decision problems,” *IBM Journal of Research and Development*, vol. 3, no. 2, pp. 114–125, 1959.",
    "[4] S. H. Rodger and T. W. Finley, *JFLAP: An Interactive Formal Languages and Automata Package*. Sudbury, MA: Jones and Bartlett, 2006.",
    "[5] Streamlit Inc., “Streamlit documentation.” https://docs.streamlit.io (accessed November 2026).",
    "[6] Graphviz, “The DOT language.” https://graphviz.org/doc/info/lang.html (accessed November 2026).",
    "[7] pytest-dev, “pytest documentation.” https://docs.pytest.org (accessed November 2026).",
]:
    p = doc.add_paragraph(); p.paragraph_format.left_indent = Inches(0.3); p.paragraph_format.first_line_indent = Inches(-0.3); p.paragraph_format.space_after = Pt(3)
    for part in re.split(r"(\*.+?\*)", ref):
        if part.startswith("*"):
            r = p.add_run(part[1:-1]); r.italic = True
        else:
            p.add_run(part)
P("Third-party software used: Python standard library, Streamlit, pytest, Graphviz DOT (rendered by Streamlit in the browser). No source code was copied from other projects.", size=10)

# ================================================================= APPENDICES
page_break()
H("Appendix A – Repository map and README summary", 1)
code("""nfa2dfa-simulator/
├─ app.py                     Streamlit entry point  (run: python -m streamlit run app.py)
├─ requirements.txt           streamlit>=1.40, pytest>=8
├─ pytest.ini                 test configuration
├─ README.md                  setup, run, test, viva guide
├─ .streamlit/config.toml     theme and privacy settings
├─ algorithm/                 PURE LOGIC (no UI imports)
│  ├─ models.py  validate.py  subset_construction.py  simulate.py  explain.py  examples.py  demo.py
├─ ui/
│  ├─ graphs.py               Graphviz DOT generation (light/dark)
│  └─ styles.py               theme CSS
├─ scripts/verify.py          compile + tests + server smoke test
└─ tests/                     59 tests (8 files)""", 8.5)
P("The README follows the recommended template: overview, supported features, technology stack, installation, how to run, worked example, project structure, testing, known limitations "
  "and troubleshooting. Recommended submission package: `GroupID_Topic_Milestone2/` with `Report/` (this report as PDF and DOCX), `SourceCode/` (the repository above), `TestCases/` "
  "(`evidence.json`, `pytest_output.txt`) and `Screenshots/`.")

H("Appendix B – Automated test log", 1)
P("Output of `python -m pytest -v` (59 tests), reproduced from `TestCases/pytest_output.txt`:", size=10)
lines = [l for l in PYTEST_TXT.splitlines() if l.startswith("tests/") or l.startswith("=")]
lines = [re.sub(r"\s+\[\s*\d+%\]$", "", l) for l in lines]
code("\n".join(lines), 6.8)

H("Appendix C – Additional screenshots", 1)
figure(SHOT / "el_editor.png", "NFA editor with the preset “Ends with ab”.", 5.6)
figure(SHOT / "el_validation_error.png", "Validation: duplicate state names produce readable errors (test T06).", 5.6)
figure(SHOT / "fig05_dark_mode.png", "Dark theme, full page.", 5.2)
figure(SHOT / "el_dfa_table_third.png", "DFA transition table for “3rd symbol from the end is a”.", 5.6)

H("Appendix D – User manual", 1)
numbered([
    "Install and start: `python3 -m venv .venv`, `.venv/bin/python -m pip install -r requirements.txt`, then `.venv/bin/python -m streamlit run app.py`; open http://localhost:8501.",
    "Choose a preset (Custom / Blank is first) or type states, alphabet, start and accepting states; fill the transition table by picking target states or by typing names.",
    "Press **Convert to DFA**. Errors, if any, appear under the editor and nothing is converted.",
    "Use **Next / Prev / Play / Reset** or the slider in *Construction Steps* to watch the DFA being built, and read the log on the right.",
    "Pick a DFA state in *Inspect a DFA state* to highlight its NFA members on the NFA diagram.",
    "Enter a string in *Single String Testing* (or several in the batch box, `<empty>` for ε) and press Run; check the verdict and the agreement badge.",
    "Use **Download JSON** to export the DFA, and the toggle at the top right to switch between light and dark themes.",
])
H("Appendix E – Submission checklist", 1)
table(["Item", "Status"], [
    ["Report has cover page, abstract, numbered sections, captions and references", "Done (group ID, faculty name and submission date on the cover page still to be filled in)"],
    ["Source code runs on a clean setup using the README", "Done (verified with scripts/verify.py)"],
    ["Every feature has at least one documented test; edge cases included", "Done (Tables 9 and 10)"],
    ["Screenshots and results match the actual simulator", "Done (screenshots captured from the running application)"],
    ["Each member can explain their contribution and the core logic", "Group to confirm"],
    ["No unattributed material; no secrets committed", "Done"],
    ["Evaluation slot confirmed (23–27 November 2026)", "Group to confirm"],
], widths=[4.2, 2.1], text_size=9)

OUT.parent.mkdir(parents=True, exist_ok=True)
doc.save(OUT)
print("saved", OUT)
