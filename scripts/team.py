"""Team data shared by the Milestone-1 and Milestone-2 report generators."""

MEMBERS = [
    ("Ayushman Mathmati", "S24CSEU1033"),
    ("Aditya Ray", "S24CSEU1020"),
    ("Shantanu Kumar", "S24CSEU1041"),
    ("Prashan Mishra", "S24CSEU1011"),
    ("Himanshu Shekhar", "S24CSEU1016"),
]

# One core-logic module group, one frontend component, one test group and a share of the report per member.
# Each member therefore owns 20 % of the core logic and 20 % of the frontend.
WORK = [
    dict(name="Ayushman Mathmati",
         core="algorithm/validate.py: parsing of the editor text, the 12-state limit, duplicate and unknown-state checks, ε rejection, friendly error messages",
         frontend="NFA editor card in app.py: state, alphabet, start and accepting inputs, transition grid (multi-select and typed modes), validation errors",
         tests="tests/test_validate.py; functional cases T06–T10",
         report="Introduction, Objectives and Requirements (M2 §1–2); Problem Definition (M1 §1)"),
    dict(name="Aditya Ray",
         core="algorithm/subset_construction.py: breadth-first subset construction, canonical subset ids, aliases A, B, C…, dead state ∅, construction log",
         frontend="DFA diagram card and ui/graphs.py: Graphviz DOT for the NFA and DFA, accepting/dead-state styling, subset highlighting, DFA JSON export",
         tests="tests/test_subset.py, tests/test_graphs.py; functional cases T11–T14",
         report="Background and Theory, algorithm design and pseudocode (M2 §3, §4.5); Algorithm Selection (M1 §4)"),
    dict(name="Shantanu Kumar",
         core="algorithm/simulate.py: DFA trace, NFA state-set simulation, batch-string parser, NFA/DFA language-equivalence check",
         frontend="Single String Testing and Batch Test Suite cards: verdict badge, agreement badge, DFA/NFA trace table, batch result table",
         tests="tests/test_simulate.py, tests/test_app.py (end-to-end UI); functional cases T01–T05, T15–T16",
         report="Testing and Verification (M2 §6); Simulator Design workflow (M1 §3.3)"),
    dict(name="Prashan Mishra",
         core="algorithm/models.py, algorithm/explain.py, algorithm/demo.py: data model dataclasses, one-sentence step explanations, terminal demo",
         frontend="Construction Steps card and the NFA/DFA transition-table cards: step player (reset, prev, play, next, slider) and scrolling construction log",
         tests="tests/test_explain.py, tests/test_purity.py",
         report="System Design and Implementation (M2 §4, §5); Simulator Design and UI wireframe (M1 §3)"),
    dict(name="Himanshu Shekhar",
         core="algorithm/examples.py: the five textbook presets with expected DFA sizes and test strings, plus the eight extra presets and their verification",
         frontend="ui/styles.py and page shell: light/dark theme and toggle, header, preset dropdown, layout rows, README and scripts/verify.py",
         tests="tests/test_examples.py; preset equivalence experiment (M2 §6.4)",
         report="Results and Discussion, Conclusion, appendices (M2 §7, §9); Existing Tools and Feasibility (M1 §2)"),
]
