"""Generate the Milestone-1 Design Report (.docx) in the same visual style as the Milestone-2 report.

The wording of the report is stored in scripts/m1_content.json (unchanged from the original report);
this script only controls the presentation. Run from the repo root:
    python3 scripts/m1_figures.py && python3 scripts/generate_m1_doc.py
"""
import json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from docstyle import Doc, WD_ALIGN_PARAGRAPH, Inches, Pt, WD_TABLE_ALIGNMENT, NAVY, BLUE, GREY
from team import MEMBERS, WORK

ROOT = Path(__file__).resolve().parent.parent
M1 = ROOT / "Milestone1"
FIG = M1 / "Figures"
DATA = json.loads((Path(__file__).parent / "m1_content.json").read_text())
OUT = M1 / "Milestone_1_Design_Report.docx"
PLACE = "[[to be filled by the group]]"

D = Doc("CSET302 – Automata Theory and Computability  |  Milestone-I Design Report",
        "Automata Workbench – NFA to DFA Conversion Simulator")

# ============================================================== cover
for _ in range(2): D.p("")
D.p("BENNETT UNIVERSITY", bold=True, size=20, align=WD_ALIGN_PARAGRAPH.CENTER, after=0)
D.p("School of Computer Science and Engineering Technology (SCSET)", size=12, align=WD_ALIGN_PARAGRAPH.CENTER, after=26)
D.p("CSET302 – Automata Theory and Computability", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
D.p("Automata Theory Simulator Development Project", size=12, align=WD_ALIGN_PARAGRAPH.CENTER, after=26)
D.p("MILESTONE-I", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, after=0)
D.p("Project Design Report", bold=True, size=24, align=WD_ALIGN_PARAGRAPH.CENTER, after=14)
D.p("Automata Workbench", bold=True, size=20, align=WD_ALIGN_PARAGRAPH.CENTER, after=0)
D.p("Topic 1: NFA → DFA Conversion Simulator", italic=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER, after=6)
D.p("Focus: Problem Analysis & Project Design (5 Marks)", size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, after=26)

members = "\n".join(f"{n} – {i}" + (" (Lead)" if n == "Aditya Ray" else "") for n, i in MEMBERS)
meta = D.doc.add_table(rows=5, cols=2); meta.alignment = WD_TABLE_ALIGNMENT.CENTER; D.borders(meta)
for i, (k, v) in enumerate([
        ("Project topic", "Topic 1: NFA → DFA Conversion Simulator"),
        ("Group ID", PLACE),
        ("Group members", members),
        ("Faculty name", PLACE),
        ("Evaluation window", "2–6 November 2026")]):
    a, b = meta.rows[i].cells; a.width, b.width = Inches(2.0), Inches(4.3)
    D.shade(a, "E8EEF9"); D.margins(a, 80, 80); D.margins(b, 80, 80)
    a.paragraphs[0].add_run(k).bold = True
    lines = v.split("\n")
    for n, line in enumerate(lines):
        p = b.paragraphs[0] if n == 0 else b.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        D.runs(p, line)
D.page_break()

# ============================================================== front matter
D.h("Milestone 1 Evaluation Rubric and Deliverables Alignment", 1)
rub = DATA["rubric"]
D.table(rub[0], rub[1:], widths=[2.0, 0.7, 3.6], size=9, caption="Rubric criteria and where each is addressed in this report.", bold_first_col=True)
D.h("Contents", 2)
for line in ["1. Problem Definition & Automata Specification", "2. Existing Tools & Feasibility Analysis",
             "3. Simulator Design & Methodology", "4. Algorithm Selection & Correctness",
             "5. Plain-Language Walkthrough (How to Explain This Project)", "Conclusion & Next Steps for Milestone 2",
             "Team responsibilities"]:
    D.p(line, after=1)

# ============================================================== body renderers
TABLE_INFO = {
    "Feature / Requirement": ("Feature comparison of existing tools and the proposed simulator.", [1.5, 1.2, 1.1, 1.2, 1.3]),
    "Module Path": ("Modules of the simulator and their responsibilities.", [1.9, 0.9, 3.5]),
    "Step #": ("Manual subset-construction trace for “Ends with ab”.", [0.5, 1.0, 0.6, 1.9, 0.85, 1.45]),
    "DFA State": ("Resulting DFA transition matrix.", [1.4, 1.3, 1.3, 1.3]),
    "Maths": ("Mapping the mathematics to the code and to the screen.", [2.0, 2.3, 2.0]),
}


def lab(text):
    """Bold a short 'Label: rest' prefix."""
    m = re.match(r"^([^:]{2,45}):\s+(.+)$", text)
    return f"**{m.group(1)}:** {m.group(2)}" if m else text


def render_body(title, body):
    if title.startswith("4.2"):
        D.code(body.strip("\n"), 7.8)
        return
    para = []
    after_number = [False]   # a '- ' line directly under a numbered line is nested

    def flush():
        if para:
            D.p(" ".join(para)); para.clear()

    for raw in body.split("\n"):
        if raw.strip() == "":
            flush(); continue
        if raw.strip().startswith("─"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        s = raw.strip()
        if indent >= 6:
            flush()
            if s.startswith(("DFA", "NFA", "If ")) or "Path" in s[:12]:
                D.p(s, size=10, indent=0.7, after=1)
            else:
                D.p(s, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
            continue
        m = re.match(r"^•\s+(.*)$", s)
        if m:
            flush(); t = m.group(1); after_number[0] = False
            if t.endswith(":"):
                D.p(t[:-1], bold=True, after=2, keep=True)
            else:
                D.bullet(lab(t))
            continue
        m = re.match(r"^-\s+(.*)$", s)
        if m:
            flush(); t = m.group(1)
            D.bullet(f"**{t[:-1]}**" if t.endswith(":") else lab(t), level=1 if after_number[0] else 0)
            continue
        m = re.match(r"^(\d+)\.\s+(.*)$", s)
        if m:
            flush(); t = m.group(2); after_number[0] = True
            D.numbered_item(m.group(1) + ".", f"**{t[:-1]}**" if t.endswith(":") else lab(t), indent=0.3 if indent >= 3 else 0)
            continue
        m = re.match(r"^Q:\s+(.*?)\s+A:\s+(.*)$", s)
        if m:
            flush(); D.p(f"**Q:** {m.group(1)}", after=1, keep=True); D.p(f"**A:** {m.group(2)}", indent=0.3, after=5)
            continue
        para.append(s)
    flush()


blocks = DATA["blocks"]
for b in blocks:
    if b["type"] == "h":
        title = re.sub(r"\s*\(Criterion[^)]*\)\s*$", "", b["title"])   # no marks beside titles
        D.h(title, 1 if b["level"] == 1 else 2)                          # sections flow on, no forced new page
        if b["title"].startswith("3.3"):
            D.p(b["body"].strip(), keep=True); D.figure(FIG / "fig_m1_workflow.png", "System architecture and processing workflow.", 5.6)
        elif b["title"].startswith("3.4"):
            D.p("The interface is a flat, neutral, professional layout (white cards, thin borders, one blue accent) with a light/dark theme toggle. "
                "It is organised as five horizontal rows so that input is at the top and every result is visible below it without hunting:", keep=True)
            D.figure(FIG / "fig_m1_wireframe.png", "UI wireframe of the simulator (five rows).", 5.3)
        else:
            render_body(b["title"], b["body"])
    elif b["type"] == "table":
        rows = b["rows"]; cap, widths = TABLE_INFO.get(rows[0][0], (None, None))
        D.table(rows[0], rows[1:], widths=widths, size=8.5, caption=cap)
    elif b["type"] == "body":
        render_body("", b["text"])
    # 'mono' blocks (old ASCII diagrams) are replaced by the figures above

# ============================================================== team responsibilities
D.h("Team responsibilities", 1)
D.p("The work is divided equally: every member owns one part of the core logic in `algorithm/`, one part of the frontend, one group of tests and a share of this report.")
D.table(["Member", "Core logic (algorithm/)", "Frontend (app.py / ui/)"],
        [[f"{w['name']}\n{MEMBERS[i][1]}", w["core"], w["frontend"]] for i, w in enumerate(WORK)],
        widths=[1.3, 2.7, 2.3], size=8.5, caption="Equal division of core logic and frontend among the five members.", bold_first_col=True)

M1.mkdir(parents=True, exist_ok=True)
D.save(OUT)
print("saved", OUT)
