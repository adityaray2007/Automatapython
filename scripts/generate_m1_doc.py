"""Generate the official Milestone 1 (M1) Design Report Word document (.docx)."""
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    """Set background color for a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set internal cell padding."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def create_m1_document(filename="Milestone_1_Design_Report.docx"):
    doc = docx.Document()

    # Page Margins: 1 inch all around
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Styles & Colors
    PRIMARY_COLOR = RGBColor(91, 91, 214)     # #5b5bd6 Indigo Accent
    DARK_COLOR = RGBColor(31, 35, 64)         # #1f2340 Ink
    MUTED_COLOR = RGBColor(93, 98, 133)       # #5d6285 Muted Slate
    ACCENT_TEAL = RGBColor(13, 148, 136)      # #0d9488 Teal
    BG_LIGHT = "F6F3FF"                       # Light Indigo tint for table headers
    BORDER_LIGHT = "D9CCFF"

    # Default font styling
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)
    font.color.rgb = DARK_COLOR

    # Header Title
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(2)
    run_sub = title_p.add_run("COURSE PROJECT DESIGN REPORT — MILESTONE 1\n")
    run_sub.font.size = Pt(10)
    run_sub.font.bold = True
    run_sub.font.color.rgb = PRIMARY_COLOR

    run_title = title_p.add_run("Topic 1: NFA → DFA Conversion Simulator (“Subset Lab”)")
    run_title.font.size = Pt(20)
    run_title.font.bold = True
    run_title.font.color.rgb = DARK_COLOR

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(14)
    run_eval = p_sub.add_run("Evaluation Phase: Milestone 1 (M1) — Focus: Problem Analysis & Project Design (Total: 5 Marks)\nEvaluation Window: 2–6 November 2026 | Academic Course: Automata Theory & Formal Languages")
    run_eval.font.size = Pt(9.5)
    run_eval.font.italic = True
    run_eval.font.color.rgb = MUTED_COLOR

    # Team & Project Metadata Box (Table)
    meta_table = doc.add_table(rows=6, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False

    meta_fields = [
        ("Project Topic & Title:", "Topic 1: NFA to DFA Conversion Simulator (Subset Lab)"),
        ("Project / Team ID:", "________________________________________________"),
        ("Team Member 1 (Lead):", "Aditya Ray               | Enrollment No: _________________________"),
        ("Team Member 2:", "________________________ | Enrollment No: _________________________"),
        ("Team Member 3:", "________________________ | Enrollment No: _________________________"),
        ("Team Member 4:", "________________________ | Enrollment No: _________________________"),
    ]

    for i, (label, val) in enumerate(meta_fields):
        row = meta_table.rows[i]
        c0 = row.cells[0]
        c1 = row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.3)
        set_cell_background(c0, "F0EDFA")
        set_cell_background(c1, "FAF8FF")
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)

        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(label)
        r0.font.bold = True
        r0.font.size = Pt(9.5)
        r0.font.color.rgb = DARK_COLOR

        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(val)
        r1.font.size = Pt(9.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Evaluation Rubric Alignment Box
    rubric_p = doc.add_paragraph()
    rubric_p.paragraph_format.space_before = Pt(8)
    rubric_p.paragraph_format.space_after = Pt(4)
    r_hdr = rubric_p.add_run("Milestone 1 Evaluation Rubric & Deliverables Alignment")
    r_hdr.font.bold = True
    r_hdr.font.size = Pt(11)
    r_hdr.font.color.rgb = PRIMARY_COLOR

    rubric_table = doc.add_table(rows=5, cols=3)
    rubric_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    rubric_headers = ["Criterion", "Marks", "Expected Evidence & Section Reference"]
    for j, h in enumerate(rubric_headers):
        c = rubric_table.rows[0].cells[j]
        set_cell_background(c, "EBE6FA")
        set_cell_margins(c, 80, 80, 100, 100)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(h)
        run.font.bold = True
        run.font.size = Pt(9.5)

    rubric_data = [
        ("Problem Definition & Automata Specification", "1 Mark", "Problem, objective, inputs/outputs, and formal mathematical 5-tuple specification (Section 1)."),
        ("Existing Tools & Feasibility Analysis", "1 Mark", "Review of relevant tools (JFLAP, FAdo), limitations, and feasibility analysis across technical, pedagogical, and economic domains (Section 2)."),
        ("Simulator Design & Methodology", "2 Marks", "Pure-logic vs Presentation architecture, module specifications, system flowchart, UI wireframe mock-up, and IPO workflow (Section 3)."),
        ("Algorithm Selection & Correctness", "1 Mark", "Rabin-Scott subset construction algorithm, step-by-step pseudocode, correctness proof, and manually validated 'ends-with-ab' example (Section 4)."),
    ]

    for i, (crit, marks, ev) in enumerate(rubric_data):
        row = rubric_table.rows[i + 1]
        c0, c1, c2 = row.cells[0], row.cells[1], row.cells[2]
        c0.width = Inches(2.2)
        c1.width = Inches(0.8)
        c2.width = Inches(3.5)
        for cell in (c0, c1, c2):
            set_cell_margins(cell, 60, 60, 100, 100)
            if (i % 2) == 1:
                set_cell_background(cell, "FBF9FF")
        p0 = c0.paragraphs[0]; p0.paragraph_format.space_after = Pt(0)
        r = p0.add_run(crit); r.font.bold = True; r.font.size = Pt(9.0)
        p1 = c1.paragraphs[0]; p1.paragraph_format.space_after = Pt(0)
        r = p1.add_run(marks); r.font.bold = True; r.font.size = Pt(9.0); r.font.color.rgb = PRIMARY_COLOR
        p2 = c2.paragraphs[0]; p2.paragraph_format.space_after = Pt(0)
        r = p2.add_run(ev); r.font.size = Pt(9.0)

    doc.add_page_break()

    # ---------------------------------------------------------------------------
    # SECTION 1: Problem Definition & Automata Specification
    # ---------------------------------------------------------------------------
    s1_hdr = doc.add_paragraph()
    s1_hdr.paragraph_format.space_before = Pt(12)
    s1_hdr.paragraph_format.space_after = Pt(4)
    r = s1_hdr.add_run("1. Problem Definition & Automata Specification (Criterion 1 — 1 Mark)")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = PRIMARY_COLOR

    # 1.1 Problem Statement
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("1.1 Problem Statement\n")
    r.font.bold = True
    p.add_run(
        "Non-Deterministic Finite Automata (NFAs) offer an intuitive and expressive mathematical framework for modeling regular languages, "
        "enabling state transitions to branch simultaneously across multiple paths or terminate on dead ends. However, physical computer hardware "
        "and production lexers/compilers are deterministic systems that cannot pursue multiple execution paths concurrently. "
        "Consequently, NFAs must be systematically converted into equivalent Deterministic Finite Automata (DFAs).\n\n"
        "In university Automata Theory curricula, the Subset Construction (Rabin-Scott powerset construction) is the fundamental bridge connecting "
        "non-determinism to deterministic realization. However, students frequently encounter significant pedagogical hurdles: (1) visualizing how multiple "
        "concurrent NFA states coalesce into a single composite DFA state, (2) tracking non-trivial state-space blowup (up to 2ⁿ states), (3) comprehending "
        "why dead states (∅) are necessary for total transition functions, and (4) verifying whether the generated DFA rigorously accepts the exact "
        "same language as the original NFA. Existing software often presents conversion as a single 'black-box' step, depriving learners of the incremental, "
        "step-by-step mathematical union derivation required for viva examinations."
    )

    # 1.2 Objectives
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("1.2 Project Objectives\n")
    r.font.bold = True
    p.add_run(
        "The primary goal of this project is to design and develop “Subset Lab” — a transparent, educational, interactive Python simulator "
        "specifically tailored for Topic 1: NFA → DFA Conversion. The project targets the following measurable objectives:\n"
        "1. Step-by-Step Pedagogical Visualization: Provide an interactive construction player (Reset, Step Prev, Step Next, Auto-Play) that displays the exact mathematical union δ(q, a) computed at each transition step.\n"
        "2. Dual-Machine Simultaneous Verification: Simulate user-entered strings simultaneously on both the NFA and DFA, displaying step-by-step active state frontiers and proving language equivalence through automated agreement verification.\n"
        "3. Strict Architectural Purity for Viva Defense: Completely isolate all automata mathematics in a pure-Python package (`algorithm/`) containing zero UI or framework dependencies, heavily commented in beginner-friendly English so that student teams can explain every line during academic vivas.\n"
        "4. Client-Side Rendering with Zero System Footprint: Dynamically synthesize Graphviz DOT code rendered natively in the browser without requiring external C-libraries, binaries, or cloud dependencies."
    )

    # 1.3 Inputs & Outputs
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("1.3 System Inputs & Outputs\n")
    r.font.bold = True
    p.add_run(
        "• System Inputs:\n"
        "   - States Q: Comma-separated list of alphanumeric state identifiers (e.g., q0, q1, q2; capped at 12 states).\n"
        "   - Alphabet Σ: Comma-separated single-character input tokens (e.g., a, b or 0, 1).\n"
        "   - Start State q₀: Exactly one state selected from Q.\n"
        "   - Accepting States F: Subset of states F ⊆ Q.\n"
        "   - Transition Table δ_NFA: Matrix specifying target states for each (state, symbol) pair via multi-select choice or text input.\n"
        "   - Verification Strings w: Individual strings or batch newline-delimited test suites for language verification.\n\n"
        "• System Outputs:\n"
        "   - Complete DFA Specification: States Q_DFA, Alphabet Σ, Transition function δ_DFA, Start state q₀_DFA, Accepts F_DFA.\n"
        "   - Canonical Subset Mapping: Transparent correspondence between alphabetical aliases (A, B, C...) and exact subsets ({q0}, {q0,q1}).\n"
        "   - Visual State Diagrams: Interactive Graphviz diagrams for both machines with double-circle accept states and subset highlighting.\n"
        "   - Step Construction Log: Chronological natural language log explaining the origin, symbol, move union, and result state for each step.\n"
        "   - Trace & Agreement Report: Step-by-step state execution path and automated verification confirmation showing NFA and DFA equivalence."
    )

    # 1.4 Formal Theoretical Model
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("1.4 Formal Mathematical Specification\n")
    r.font.bold = True
    p.add_run(
        "• Formal Definition of the Input NFA:\n"
        "The input machine is formally specified as a 5-tuple:\n"
        "      M_NFA = (Q, Σ, δ, q₀, F)\n"
        "Where:\n"
        "   1. Q is a finite non-empty set of states: Q = {q₀, q₁, ..., qₙ₋₁}, with |Q| ≤ 12.\n"
        "   2. Σ is a finite non-empty input alphabet such that ∀a ∈ Σ, |a| = 1 and a ∉ {ε, eps, epsilon, λ, lambda}.\n"
        "   3. δ: Q × Σ → 𝒫(Q) is the transition function mapping each state and symbol to a subset of Q. Note that δ(q, a) = ∅ indicates no valid transition.\n"
        "   4. q₀ ∈ Q is the designated initial state.\n"
        "   5. F ⊆ Q is the set of final/accepting states.\n\n"
        "• Formal Definition of the Target DFA:\n"
        "The resulting converted deterministic machine is specified as:\n"
        "      M_DFA = (Q', Σ, δ', q₀', F')\n"
        "Where:\n"
        "   1. Q' ⊆ 𝒫(Q) is the set of reachable subsets of Q discovered during powerset exploration (|Q'| ≤ 2^|Q|).\n"
        "   2. Σ is identical to the input NFA alphabet.\n"
        "   3. q₀' = {q₀} is the DFA start state, consisting of the singleton set containing the NFA start state.\n"
        "   4. δ': Q' × Σ → Q' is the deterministic total transition function defined mathematically by:\n"
        "            δ'(S, a) = ⋃_{q ∈ S} δ(q, a)   for all S ∈ Q' and a ∈ Σ\n"
        "      If ⋃_{q ∈ S} δ(q, a) = ∅, the transition lands in the explicit dead/trap state ∅, where δ'(∅, a) = ∅ for all a ∈ Σ.\n"
        "   5. F' = {S ∈ Q' | S ∩ F ≠ ∅} is the set of DFA accepting states (a subset state is accepting iff it contains at least one NFA accepting state).\n\n"
        "• Language Equivalence Theorem:\n"
        "The subset construction guarantees that L(M_NFA) = L(M_DFA). An input string w = a₁a₂...aₘ is accepted by M_NFA iff there exists a path "
        "q₀ → q₁ → ... → qₘ such that qₘ ∈ F. By induction on |w|, the state S reached by M_DFA on input w is precisely the set of all NFA states reachable "
        "from q₀ on input w. Therefore, S ∈ F' if and only if S ∩ F ≠ ∅, proving rigorous language equivalence.\n\n"
        "• Scope Boundaries:\n"
        "- Plain NFAs only: ε-transitions are intentionally excluded (ε-NFA is a separate curricular topic). Friendly validation errors reject any attempt to input ε.\n"
        "- Upper State Bound: Maximum 12 NFA states to prevent uncontrolled exponential explosion in educational environments (2¹² = 4096 states)."
    )

    doc.add_page_break()

    # ---------------------------------------------------------------------------
    # SECTION 2: Existing Tools & Feasibility Analysis
    # ---------------------------------------------------------------------------
    s2_hdr = doc.add_paragraph()
    s2_hdr.paragraph_format.space_before = Pt(12)
    s2_hdr.paragraph_format.space_after = Pt(4)
    r = s2_hdr.add_run("2. Existing Tools & Feasibility Analysis (Criterion 2 — 1 Mark)")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = PRIMARY_COLOR

    # 2.1 Review of Existing Tools
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("2.1 Review of Existing Tools\n")
    r.font.bold = True
    p.add_run(
        "To establish a solid rationale for designing a new simulator, existing academic and open-source automata tools were reviewed:\n\n"
        "1. JFLAP (Java Formal Languages and Automata Package):\n"
        "   - Background: Developed at Duke University, JFLAP is the historical gold standard for teaching automata theory.\n"
        "   - Limitations: Built on legacy Java Swing architecture; requires a local Java Runtime Environment (JRE) install which frequently causes modern OS security and DPI scaling issues. Graph layout often requires manual node dragging. Critically, JFLAP's conversion utility generates dense, cluttered transition tables without clear natural language step explanations or synchronized dual-machine frontier tracing.\n\n"
        "2. Python Computational Libraries (Automata-lib, FAdo):\n"
        "   - Background: Pure Python and C++ libraries designed for programmatic automata minimization, regex parsing, and union operations.\n"
        "   - Limitations: Strictly developer-oriented CLI tools without a visual user interface. They perform conversions as instantaneous batch operations, providing zero visual intermediate steps for students learning how the algorithm functions.\n\n"
        "3. Generic Web-Based State Machine Editors (e.g., FSM Simulator, Cyberzhg):\n"
        "   - Background: JavaScript/Canvas-based web apps allowing users to draw graphs in the browser.\n"
        "   - Limitations: Most online tools combine ε-transitions, DFA minimization, and regex conversion into a single monolithic interface. They lack structured validation, do not support interactive step-by-step subset construction playback, and do not provide side-by-side verification proving that the generated DFA agrees with the NFA."
    )

    # 2.2 Critical Tool Comparison Table
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("2.2 Feature Comparison Matrix & Identified Gaps\n")
    r.font.bold = True

    comp_table = doc.add_table(rows=5, cols=5)
    comp_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    comp_headers = ["Feature / Requirement", "JFLAP", "Automata-lib", "Online FSM Tools", "Proposed Subset Lab"]
    for j, h in enumerate(comp_headers):
        c = comp_table.rows[0].cells[j]
        set_cell_background(c, "EBE6FA")
        set_cell_margins(c, 70, 70, 80, 80)
        p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.font.bold = True; r.font.size = Pt(8.5)

    comp_rows = [
        ("Platform & Setup", "Java desktop app (requires JRE)", "Python CLI library only", "JavaScript web app", "Zero-install Python + Browser"),
        ("Step-by-Step Construction Playback", "Partial / Clunky", "None (instantaneous)", "None", "Full (Reset, Prev, Play, Next)"),
        ("Synchronized NFA/DFA Diagrams", "No (separate windows)", "No", "No", "Yes (side-by-side real-time)"),
        ("Dual String Frontier Agreement", "No", "No", "No", "Yes (frontier logging & badge)"),
    ]

    for i, row_data in enumerate(comp_rows):
        row = comp_table.rows[i + 1]
        for j, val in enumerate(row_data):
            cell = row.cells[j]
            set_cell_margins(cell, 50, 50, 80, 80)
            if j == 4:
                set_cell_background(cell, "F0EDFA")
            elif (i % 2) == 1:
                set_cell_background(cell, "FAF9FF")
            p = cell.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val); r.font.size = Pt(8.5)
            if j == 4: r.font.bold = True; r.font.color.rgb = PRIMARY_COLOR

    # 2.3 Feasibility Analysis
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("2.3 Feasibility Analysis\n")
    r.font.bold = True
    p.add_run(
        "• Technical Feasibility: Highly Feasible. The technology stack relies solely on Python ≥ 3.10 and Streamlit ≥ 1.40. "
        "Crucially, Graphviz DOT text is rendered client-side directly by the browser using Streamlit's built-in `st.graphviz_chart()`. "
        "This completely eliminates the need for OS-level Graphviz binary installations (`dot` executable) or C-extensions, ensuring 100% platform portability across Windows, macOS, and Linux.\n\n"
        "• Pedagogical & Operational Feasibility: Highly Feasible. The user experience is optimized for classroom demos and viva presentations. "
        "Preloaded with five verified textbook presets (including famous edge cases such as 'Ends with ab', '3rd symbol from end is a' state blow-up, and 'Dead state ∅'), "
        "students can immediately explore the algorithm without tedious manual setup. The strict separation of pure-Python automata logic in `algorithm/` ensures "
        "students can confidently read, explain, and defend every mathematical function.\n\n"
        "• Economic & Resource Feasibility: Highly Feasible. All components are free, open-source software (MIT/Apache licenses). "
        "The simulator executes entirely locally on commodity consumer laptops with zero cloud infrastructure, hosting, or database expenses."
    )

    doc.add_page_break()

    # ---------------------------------------------------------------------------
    # SECTION 3: Simulator Design & Methodology
    # ---------------------------------------------------------------------------
    s3_hdr = doc.add_paragraph()
    s3_hdr.paragraph_format.space_before = Pt(12)
    s3_hdr.paragraph_format.space_after = Pt(4)
    r = s3_hdr.add_run("3. Simulator Design & Methodology (Criterion 3 — 2 Marks)")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = PRIMARY_COLOR

    # 3.1 Architecture
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("3.1 High-Level Architecture & Separation of Concerns\n")
    r.font.bold = True
    p.add_run(
        "The simulator adopts a strict decoupled architecture comprising two independent layers:\n"
        "1. Pure Computational Logic Layer (`algorithm/`): Contains zero UI code, zero Streamlit imports, and zero third-party dependencies. "
        "All data structures are implemented using standard library dataclasses. This guarantees that the core automata engine can be tested, "
        "verified, and explained completely independently in terminal environments via `algorithm.demo`.\n"
        "2. Presentation & Interaction Layer (`app.py`, `ui/`): A thin reactive controller that handles session state, form validation reporting, "
        "Graphviz DOT synthesis (`ui/graphs.py`), and glassmorphism styling (`ui/styles.py`)."
    )

    # 3.2 Module Breakdown Table
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("3.2 Modular Component Breakdown\n")
    r.font.bold = True

    mod_table = doc.add_table(rows=9, cols=3)
    mod_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(["Module Path", "Layer", "Functional Responsibility & Key Functions"]):
        c = mod_table.rows[0].cells[j]
        set_cell_background(c, "EBE6FA")
        set_cell_margins(c, 70, 70, 80, 80)
        p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.font.bold = True; r.font.size = Pt(8.5)

    modules = [
        ("algorithm/models.py", "Pure Logic", "Defines plain dataclasses: NFA, DFA, DFAState, MoveDetail, ConstructionStep, ConversionResult."),
        ("algorithm/validate.py", "Pure Logic", "Parses editor text into validated NFA objects; enforces single-character symbols, state uniqueness, and ε rejection."),
        ("algorithm/subset_construction.py", "Pure Logic", "The core algorithm; implements BFS queue exploration, subset alias mapping (A, B...), and deterministic normalization."),
        ("algorithm/simulate.py", "Pure Logic", "Executes string traces on DFA and tracks active state frontiers on NFA to prove language equivalence."),
        ("algorithm/explain.py", "Pure Logic", "Translates individual ConstructionStep transitions into human-readable English mathematical explanations."),
        ("algorithm/examples.py", "Pure Logic", "Holds 5 textbook preset NFAs with verified test cases and expected DFA state counts."),
        ("algorithm/demo.py", "Pure Logic", "Standalone terminal runner (`python -m algorithm.demo`) that prints full conversion logs without launching UI."),
        ("ui/graphs.py & styles.py", "UI Layer", "Synthesizes Graphviz DOT code with radial gradients, double circles, and responsive glassmorphism CSS."),
    ]

    for i, (mpath, layer, resp) in enumerate(modules):
        row = mod_table.rows[i + 1]
        c0, c1, c2 = row.cells[0], row.cells[1], row.cells[2]
        c0.width = Inches(2.2); c1.width = Inches(1.0); c2.width = Inches(3.3)
        for c in (c0, c1, c2): set_cell_margins(c, 50, 50, 80, 80)
        if (i % 2) == 1:
            for c in (c0, c1, c2): set_cell_background(c, "FAF9FF")
        p = c0.paragraphs[0]; p.paragraph_format.space_after = Pt(0); r = p.add_run(mpath); r.font.size = Pt(8.0); r.font.bold = True
        p = c1.paragraphs[0]; p.paragraph_format.space_after = Pt(0); r = p.add_run(layer); r.font.size = Pt(8.0)
        p = c2.paragraphs[0]; p.paragraph_format.space_after = Pt(0); r = p.add_run(resp); r.font.size = Pt(8.0)

    # 3.3 System Workflow Flowchart
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("3.3 System Architecture & Processing Workflow\n")
    r.font.bold = True
    p.add_run(
        "The overall system processing lifecycle is structured as follows:\n\n"
        "   [User Input / Presets] \n"
        "             │\n"
        "             ▼\n"
        "   ┌──────────────────────────────────────────────┐\n"
        "   │  Input Validation (algorithm/validate.py)    │ ───► Invalid ──► [Display Friendly Error Badges]\n"
        "   └──────────────────────────────────────────────┘\n"
        "             │ Valid NFA\n"
        "             ▼\n"
        "   ┌──────────────────────────────────────────────┐\n"
        "   │  Live NFA Graphviz Synthesis (ui/graphs.py)  │ ───► [Render Interactive Live NFA Diagram]\n"
        "   └──────────────────────────────────────────────┘\n"
        "             │ User clicks 'Convert to DFA'\n"
        "             ▼\n"
        "   ┌────────────────────────────────────────────────────────┐\n"
        "   │  Subset Construction Engine (subset_construction.py)   │\n"
        "   │  • Initialize start subset S₀ = {q₀}                   │\n"
        "   │  • Enqueue S₀ in BFS Queue                             │\n"
        "   │  • While Queue not empty:                              │\n"
        "   │      For each a ∈ Σ:                                   │\n"
        "   │          T = ⋃ δ(q, a) for q ∈ Current                 │\n"
        "   │          Register T; if new, enqueue T                 │\n"
        "   │          Log ConstructionStep & record edge            │\n"
        "   └────────────────────────────────────────────────────────┘\n"
        "             │\n"
        "             ├────────────────────────────────────────┬────────────────────────────────────────┐\n"
        "             ▼                                        ▼                                        ▼\n"
        "   [DFA Graph Generator]                   [Step Player Controller]                 [Dual Simulation Engine]\n"
        "   Renders DFA with edge                   Controls step slider (0..N)              Runs user test strings on both\n"
        "   and node focus highlights               and natural language step log            NFA and DFA; emits agreement badge\n"
    )

    # 3.4 UI Wireframe
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("3.4 UI Wireframe & Spatial Orientation Design\n")
    r.font.bold = True
    p.add_run(
        "The user interface follows a modern glassmorphism design with a four-section layout that balances input and output:\n\n"
        "┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐\n"
        "│  HEADER: Brand Title 'Subset Lab' | Tagline 'Watch an NFA collapse into a DFA.'                      │\n"
        "├──────────────────────────────────────────────────────────────────────────────────────────────────────┤\n"
        "│  SECTION 1: NFA MASTER CONFIGURATION DECK (Wide Balanced Card)                                       │\n"
        "│  ┌─────────────────────────────────────────┐  ┌──────────────────────────────────────────────────┐  │\n"
        "│  │ Preset Dropdown | Convert & Reset Btns  │  │ Transition Table Matrix δ(state, symbol)        │  │\n"
        "│  │ States Input    | Alphabet Input        │  │ Mode: [🔘 Multi-Select Picker | ⚪ Text Inputs]  │  │\n"
        "│  │ Start Select    | Accepting Multiselect │  │ Cells: q0 [q0,q1], q1 [q2], q2 [—]               │  │\n"
        "│  └─────────────────────────────────────────┘  └──────────────────────────────────────────────────┘  │\n"
        "├──────────────────────────────────────────────────────────────────────────────────────────────────────┤\n"
        "│  SECTION 2: AUTOMATA SHOWCASE (Side-by-Side Horizontal Parity 50% / 50%)                             │\n"
        "│  ┌─────────────────────────────────────────┐  ┌──────────────────────────────────────────────────┐  │\n"
        "│  │ 📡 NFA State Diagram                    │  │ 🕸 DFA State Diagram & Construction              │  │\n"
        "│  │ • Inspect DFA State Dropdown (Glow)     │  │ • Live DFA Graphviz Chart (Edge/Node Focus)      │  │\n"
        "│  │ • Live Graphviz Chart (Generous Padding)│  │ • Step Player Controls: [⏮][◀][▶ Play][Next ▶]   │  │\n"
        "│  │ • Start Arrow, Double-Circle Accepts    │  │ • Step Counter: '3 / 6' | Step Slider            │  │\n"
        "│  │                                         │  │ • Scrollable Construction Step Log Cards         │  │\n"
        "│  └─────────────────────────────────────────┘  └──────────────────────────────────────────────────┘  │\n"
        "├──────────────────────────────────────────────────────────────────────────────────────────────────────┤\n"
        "│  SECTION 3: TRANSITION TABLES (50% / 50%)                                                            │\n"
        "│  ┌─────────────────────────────────────────┐  ┌──────────────────────────────────────────────────┐  │\n"
        "│  │ 📋 NFA Transition Table                 │  │ 📊 DFA Transition Table (Alias = Subset Matrix)  │  │\n"
        "│  │ Columns: State, a, b                    │  │ Columns: State, a, b, Accepting (✓) | JSON Export│  │\n"
        "│  └─────────────────────────────────────────┘  └──────────────────────────────────────────────────┘  │\n"
        "├──────────────────────────────────────────────────────────────────────────────────────────────────────┤\n"
        "│  SECTION 4: VERIFICATION & TESTING SUITE (50% / 50%)                                                 │\n"
        "│  ┌─────────────────────────────────────────┐  ┌──────────────────────────────────────────────────┐  │\n"
        "│  │ 🧪 Single String Verification           │  │ 📑 Batch Test Suite                              │  │\n"
        "│  │ • Input String Field & Run Button       │  │ • Multi-line String Textarea (<empty> support)   │  │\n"
        "│  │ • Verdict Badge: [Accepted / Rejected]  │  │ • Run Batch Button                               │  │\n"
        "│  │ • Agreement Badge: [NFA and DFA agree ✓]│  │ • Batch Table: String | Verdict | Final State    │  │\n"
        "│  │ • Step-by-Step DFA/NFA Frontier Trace   │  │                                                  │  │\n"
        "│  └─────────────────────────────────────────┘  └──────────────────────────────────────────────────┘  │\n"
        "└──────────────────────────────────────────────────────────────────────────────────────────────────────┘"
    )

    doc.add_page_break()

    # ---------------------------------------------------------------------------
    # SECTION 4: Algorithm Selection & Correctness
    # ---------------------------------------------------------------------------
    s4_hdr = doc.add_paragraph()
    s4_hdr.paragraph_format.space_before = Pt(12)
    s4_hdr.paragraph_format.space_after = Pt(4)
    r = s4_hdr.add_run("4. Algorithm Selection & Correctness (Criterion 4 — 1 Mark)")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = PRIMARY_COLOR

    # 4.1 Selection & Justification
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("4.1 Algorithm Selection & Justification\n")
    r.font.bold = True
    p.add_run(
        "The project implements the Rabin-Scott Powerset / Subset Construction using Breadth-First Search (BFS) queue exploration. "
        "This algorithm is selected over naive brute-force powerset generation for several vital reasons:\n"
        "1. Minimal Reachable Subgraph: An NFA with n states has 2ⁿ potential subsets. Brute-force generation constructs all 2ⁿ states indiscriminately. "
        "In contrast, the BFS queue approach explores only reachable subsets starting from {q₀}, eliminating disconnected unreachable states and keeping the DFA as compact as possible.\n"
        "2. Deterministic Canonical Ordering: By sorting and de-duplicating subset members based on their initial NFA declaration order, "
        "the subset string ID (e.g. {q0,q1}) and assigned alias (A, B, C...) are 100% deterministic and reproducible across repeated runs.\n"
        "3. Total DFA Transition Guarantee: When transitions for certain symbols do not exist in the NFA, the algorithm maps them to the explicit dead/trap state ∅, "
        "ensuring the output strictly satisfies the formal definition of a total DFA."
    )

    # 4.2 Pseudocode
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("4.2 Structured Algorithmic Pseudocode\n")
    r.font.bold = True
    p.add_run(
        "Algorithm: SubsetConstruction(NFA)\n"
        "Input:  NFA M = (Q, Σ, δ, q₀, F)\n"
        "Output: DFA M' = (Q', Σ, δ', q₀', F') and ConstructionLog Steps\n"
        "─────────────────────────────────────────────────────────────────────────────\n"
        "1.  Let Order = map assigning declaration index to each q ∈ Q\n"
        "2.  Define Normalize(S): return sorted unique elements of S ordered by Order\n"
        "3.  Define SetID(S): if S is empty return '∅', else return '{' + join(S, ',') + '}'\n"
        "4.  Let KnownStates = empty dictionary {SetID -> DFAState}\n"
        "5.  Let DFAStatesList = empty list\n"
        "6.  Let DFATransitions = empty nested dictionary {SetID -> {symbol -> SetID}}\n"
        "7.  Let StepsLog = empty list\n"
        "8.  \n"
        "9.  Function RegisterState(members):\n"
        "10.     sid = SetID(members)\n"
        "11.     if sid in KnownStates: return KnownStates[sid]\n"
        "12.     alias = AliasFor(length of DFAStatesList)   // 0->A, 1->B...\n"
        "13.     is_acc = (members ∩ F ≠ ∅)\n"
        "14.     is_dead = (length of members == 0)\n"
        "15.     state = CreateDFAState(id=sid, alias=alias, members=members, is_acc, is_dead)\n"
        "16.     KnownStates[sid] = state\n"
        "17.     Append state to DFAStatesList\n"
        "18.     DFATransitions[sid] = empty dictionary\n"
        "19.     return state\n"
        "20. \n"
        "21. // Step 1: Initialize start state\n"
        "22. start_state = RegisterState(Normalize([q₀]))\n"
        "23. start_state.is_start = True\n"
        "24. \n"
        "25. // Step 2: Breadth-first queue processing\n"
        "26. Queue = FIFOQueue([start_state])\n"
        "27. while Queue is not empty:\n"
        "28.     Current = Queue.pop_left()\n"
        "29.     for each symbol a ∈ Σ:\n"
        "30.         moves = []\n"
        "31.         for each q ∈ Current.members:\n"
        "32.             targets = Normalize(δ(q, a))\n"
        "33.             moves.append(MoveDetail(state=q, targets=targets))\n"
        "34.         \n"
        "35.         // Compute Union: T = ⋃ δ(q, a)\n"
        "36.         result_members = Normalize(⋃ move.targets)\n"
        "37.         prev_count = length of KnownStates\n"
        "38.         target_state = RegisterState(result_members)\n"
        "39.         is_new = (length of KnownStates > prev_count)\n"
        "40.         if is_new:\n"
        "41.             Queue.push(target_state)  // Enqueue newly discovered subset\n"
        "42.         \n"
        "43.         DFATransitions[Current.id][a] = target_state.id\n"
        "44.         StepsLog.append(ConstructionStep(Current, a, moves, result_members, target_state, is_new))\n"
        "45. \n"
        "46. Return DFA(states=DFAStatesList, alphabet=Σ, transitions=DFATransitions, start=start_state.id, accepts), StepsLog\n"
    )

    # 4.3 Manually Solved Validation Example
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("4.3 Manually Solved Validation Example (Walkthrough)\n")
    r.font.bold = True
    p.add_run(
        "To rigorously verify mathematical correctness, the textbook example 'Ends with ab' is manually solved step-by-step.\n\n"
        "• Problem Statement:\n"
        "Construct an equivalent DFA for the NFA accepting all strings over Σ = {a, b} that end in the substring 'ab'.\n\n"
        "• NFA Specification:\n"
        "Q = {q0, q1, q2},  Σ = {a, b},  Start = q0,  Accepting F = {q2}\n"
        "Transition Function δ:\n"
        "   - δ(q0, a) = {q0, q1}\n"
        "   - δ(q0, b) = {q0}\n"
        "   - δ(q1, b) = {q2}\n"
        "   - δ(q1, a) = ∅,  δ(q2, a) = ∅,  δ(q2, b) = ∅\n\n"
        "• Step-by-Step Manual Construction Trace:\n"
    )

    trace_table = doc.add_table(rows=7, cols=6)
    trace_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_headers = ["Step #", "DFA State S", "Symbol", "NFA Moves: δ(q, a)", "Union Set T", "Status / Target"]
    for j, h in enumerate(t_headers):
        c = trace_table.rows[0].cells[j]
        set_cell_background(c, "EBE6FA")
        set_cell_margins(c, 60, 60, 60, 60)
        p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.font.bold = True; r.font.size = Pt(8.5)

    trace_data = [
        ("1", "A = {q0}", "a", "δ(q0,a) = {q0,q1}", "{q0,q1}", "NEW State B"),
        ("2", "A = {q0}", "b", "δ(q0,b) = {q0}", "{q0}", "Existing State A"),
        ("3", "B = {q0,q1}", "a", "δ(q0,a) = {q0,q1}, δ(q1,a) = ∅", "{q0,q1}", "Existing State B"),
        ("4", "B = {q0,q1}", "b", "δ(q0,b) = {q0}, δ(q1,b) = {q2}", "{q0,q2}", "NEW State C (Accepting*)"),
        ("5", "C = {q0,q2}", "a", "δ(q0,a) = {q0,q1}, δ(q2,a) = ∅", "{q0,q1}", "Existing State B"),
        ("6", "C = {q0,q2}", "b", "δ(q0,b) = {q0}, δ(q2,b) = ∅", "{q0}", "Existing State A"),
    ]

    for i, row_data in enumerate(trace_data):
        row = trace_table.rows[i + 1]
        for j, val in enumerate(row_data):
            cell = row.cells[j]
            set_cell_margins(cell, 45, 45, 60, 60)
            if (i % 2) == 1:
                set_cell_background(cell, "FAF9FF")
            p = cell.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val); r.font.size = Pt(8.5)
            if "NEW" in val: r.font.bold = True; r.font.color.rgb = ACCENT_TEAL

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    p.add_run(
        "• Resulting DFA Transition Matrix:\n"
    )

    dfa_mat_table = doc.add_table(rows=4, cols=4)
    dfa_mat_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(["DFA State", "Subset Members", "Input 'a'", "Input 'b'"]):
        c = dfa_mat_table.rows[0].cells[j]
        set_cell_background(c, "EBE6FA")
        set_cell_margins(c, 60, 60, 80, 80)
        p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.font.bold = True; r.font.size = Pt(8.5)

    dfa_mat_data = [
        ("→ A (Start)", "{q0}", "B {q0,q1}", "A {q0}"),
        ("   B", "{q0,q1}", "B {q0,q1}", "C {q0,q2}"),
        ("* C (Accepting)", "{q0,q2}", "B {q0,q1}", "A {q0}"),
    ]

    for i, row_data in enumerate(dfa_mat_data):
        row = dfa_mat_table.rows[i + 1]
        for j, val in enumerate(row_data):
            cell = row.cells[j]
            set_cell_margins(cell, 45, 45, 80, 80)
            if (i % 2) == 1:
                set_cell_background(cell, "FAF9FF")
            p = cell.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val); r.font.size = Pt(8.5)
            if "*" in val or "→" in val: r.font.bold = True

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    p.add_run(
        "• Manual String Verification & Language Equivalence:\n"
        "   - String 'ab':\n"
        "       DFA Path: A ──a──► B ──b──► C (Accepting) ──► ACCEPTED\n"
        "       NFA Active Frontier: [q0] ──a──► [q0, q1] ──b──► [q0, q2] (contains q2) ──► ACCEPTED (Agreement ✓)\n"
        "   - String 'aab':\n"
        "       DFA Path: A ──a──► B ──a──► B ──b──► C (Accepting) ──► ACCEPTED\n"
        "       NFA Active Frontier: [q0] ──a──► [q0, q1] ──a──► [q0, q1] ──b──► [q0, q2] ──► ACCEPTED (Agreement ✓)\n"
        "   - String 'abb':\n"
        "       DFA Path: A ──a──► B ──b──► C ──b──► A (Non-accepting) ──► REJECTED\n"
        "       NFA Active Frontier: [q0] ──a──► [q0, q1] ──b──► [q0, q2] ──b──► [q0] (no q2) ──► REJECTED (Agreement ✓)\n"
        "   - String ε (empty):\n"
        "       DFA State: A (Non-accepting) ──► REJECTED\n"
        "       NFA State: q0 ∉ F ──► REJECTED (Agreement ✓)\n"
    )

    p_concl = doc.add_paragraph()
    p_concl.paragraph_format.space_before = Pt(12)
    p_concl.paragraph_format.space_after = Pt(4)
    r = p_concl.add_run("Conclusion & Next Steps for Milestone 2\n")
    r.font.bold = True
    r.font.color.rgb = PRIMARY_COLOR
    p_concl.add_run(
        "The theoretical design, mathematical specification, architecture, and manual verification for Milestone 1 are complete. "
        "As established in the feasibility study, the project methodology provides a deterministic, reliable foundation for implementation. "
        "In Milestone 2, the complete interactive Streamlit application, dual Graphviz rendering engine, and automated 59-test suite "
        "will be finalized and delivered."
    )

    doc.save(filename)
    print(f"Successfully generated: {filename}")

if __name__ == "__main__":
    create_m1_document()
