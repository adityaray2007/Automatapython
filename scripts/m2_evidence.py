"""Compute real evidence (preset sizes, equivalence checks, scaling, test cases) for the M2 report.

Run from the repo root:  nfa2dfa-simulator/.venv/bin/python scripts/m2_evidence.py
"""
import ast, itertools, json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIM = ROOT / "nfa2dfa-simulator"
sys.path.insert(0, str(SIM))

from algorithm.examples import EXAMPLES
from algorithm.models import NFA
from algorithm.simulate import parse_batch, simulate_dfa, simulate_nfa
from algorithm.subset_construction import subset_construction
from algorithm.validate import NfaForm, build_nfa, split_list

# Extra presets live in app.py; read the literal without importing Streamlit.
tree = ast.parse((SIM / "app.py").read_text())
extra = next(n for n in tree.body if isinstance(n, ast.AnnAssign) and getattr(n.target, "id", "") == "EXTRA_PRESETS")
EXTRA = ast.literal_eval(extra.value)


def nfa_from_preset(p):
    states, alpha = split_list(p["states"]), split_list(p["alphabet"])
    cells = {s: {a: p["cells"].get(s, {}).get(a, "") for a in alpha} for s in states}
    res = build_nfa(NfaForm(p["states"], p["alphabet"], p["start"], p["accepts"], cells))
    assert not res.errors, (p["id"], res.errors)
    return res.nfa


presets = [(e.id, e.title, e.nfa) for e in EXAMPLES]
presets += [(k, v["title"], nfa_from_preset(v)) for k, v in EXTRA.items() if k != "custom"]


def strings_upto(alpha, n):
    for L in range(n + 1):
        for t in itertools.product(alpha, repeat=L):
            yield "".join(t)


out = {"presets": [], "scaling": [], "cases": []}
for pid, title, nfa in presets:
    r = subset_construction(nfa)
    n_checked, mism = 0, 0
    for w in strings_upto(nfa.alphabet, 8):
        n_checked += 1
        if simulate_dfa(r.dfa, w).accepted != simulate_nfa(nfa, w).accepted:
            mism += 1
    out["presets"].append(dict(
        id=pid, title=title, nfa_states=len(nfa.states), alphabet=nfa.alphabet,
        dfa_states=len(r.dfa.states), accepting=len(r.dfa.accepts), steps=len(r.steps),
        has_dead=any(s.is_dead for s in r.dfa.states), strings=n_checked, mismatches=mism))

# Worst-case family: "n-th symbol from the end is 'a'" has n+1 NFA states and 2^n DFA states.
for n in range(1, 12):
    states = [f"q{i}" for i in range(n + 1)]
    trans = {"q0": {"a": ["q0", "q1"], "b": ["q0"]}}
    for i in range(1, n):
        trans[f"q{i}"] = {"a": [f"q{i+1}"], "b": [f"q{i+1}"]}
    nfa = NFA(states, ["a", "b"], trans, "q0", [f"q{n}"])
    t0 = time.perf_counter(); r = subset_construction(nfa); dt = (time.perf_counter() - t0) * 1000
    out["scaling"].append(dict(n=n, nfa_states=n + 1, dfa_states=len(r.dfa.states), expected=2 ** n, ms=round(dt, 2)))


def form(states, alpha, start, accepts, cells):
    return NfaForm(states, alpha, start, accepts, cells)


ends_ab = next(n for i, t, n in presets if i == "ends-with-ab")
dfa_ab = subset_construction(ends_ab).dfa


def run_string(w):
    d, n = simulate_dfa(dfa_ab, w), simulate_nfa(ends_ab, w)
    return d, n


def verdict(w, expect):
    d, n = run_string(w)
    got = "Accept" if d.accepted else "Reject"
    extra = " (NFA agrees)" if d.accepted == n.accepted else " (NFA DISAGREES)"
    return got + extra, got == expect and d.accepted == n.accepted


cases = []
def add(tid, feat, setup, expect, actual, ok):
    cases.append(dict(id=tid, feature=feat, input=setup, expected=expect, actual=actual, status="Pass" if ok else "FAIL"))

for tid, w, ex in [("T01", "aab", "Accept"), ("T02", "abb", "Reject"), ("T03", "ab", "Accept"), ("T04", "", "Reject")]:
    a, ok = verdict(w, ex)
    label = {"T01": "Accepted string", "T02": "Rejected string", "T03": "Shortest accepted string", "T04": "Empty string ε"}[tid]
    add(tid, f"Preset 'Ends with ab' - {label}", f"input = '{w}'" if w else "input = (empty string)", ex, a, ok)

d = simulate_dfa(dfa_ab, "abc")
add("T05", "Symbol outside the alphabet", "input = 'abc' (c not in {a,b})", "Warning, string rejected",
    f"Rejected; message: {d.error}", (not d.accepted) and d.error is not None)

def build(states, alpha, start, accepts, cells):
    return build_nfa(NfaForm(states, alpha, start, accepts, cells))

cell = {"q0": {"a": "", "b": ""}, "q1": {"a": "", "b": ""}}
r = build("q0, q0", "a, b", "q0", [], {"q0": {"a": "", "b": ""}})
add("T06", "Duplicate state names", "states = 'q0, q0'", "Validation error", "; ".join(r.errors), bool(r.errors))
r = build("q0, q1", "a, eps", "q0", [], {"q0": {"a": "", "eps": ""}, "q1": {"a": "", "eps": ""}})
add("T07", "ε in the alphabet", "alphabet = 'a, eps'", "Friendly error", "; ".join(r.errors), bool(r.errors))
r = build("q0, q1", "a, ab", "q0", [], {"q0": {"a": "", "ab": ""}, "q1": {"a": "", "ab": ""}})
add("T08", "Multi-character symbol", "alphabet = 'a, ab'", "Validation error", "; ".join(r.errors), bool(r.errors))
r = build("q0, q1", "a", "q0", [], {"q0": {"a": "q9"}, "q1": {"a": ""}})
add("T09", "Transition to unknown state", "delta(q0,a) = q9", "Validation error", "; ".join(r.errors), bool(r.errors))
r = build(", ".join(f"q{i}" for i in range(13)), "a", "q0", [], {f"q{i}": {"a": ""} for i in range(13)})
add("T10", "More than 12 states", "13 states", "Validation error", "; ".join(r.errors), bool(r.errors))
r = build("q0, q1", "a, b", "q0", ["q1"], {"q0": {"a": "q1", "b": ""}, "q1": {"a": "", "b": ""}})
res = subset_construction(r.nfa)
dead = [s for s in res.dfa.states if s.is_dead]
add("T11", "Missing transition -> dead state", "delta(q0,b) = (empty)", "DFA gets explicit dead state ∅",
    f"DFA states: {[s.id for s in res.dfa.states]}; dead state present = {bool(dead)}", bool(dead))
n = next(n for i, t, n in presets if i == "starts-with-0-dead-state")
r2 = subset_construction(n); loops = all(r2.dfa.transitions["∅"][a] == "∅" for a in n.alphabet)
add("T12", "Dead state is a trap", "preset 'Starts with 0'", "∅ loops to ∅ on every symbol", f"loops = {loops}", loops)
n = next(n for i, t, n in presets if i == "a-star-accepts-empty")
r3 = subset_construction(n); a3 = simulate_dfa(r3.dfa, "").accepted
add("T13", "Start state is accepting", "preset 'a*', input = ε", "Accept", "Accept" if a3 else "Reject", a3)
n = next(n for i, t, n in presets if i == "third-from-last-a")
r4 = subset_construction(n)
add("T14", "Exponential blow-up", "preset '3rd symbol from end is a'", "8 DFA states (2^3)", f"{len(r4.dfa.states)} DFA states", len(r4.dfa.states) == 8)
words = parse_batch("ab\n<empty>\n\nbab\n")
add("T15", "Batch parser", "'ab', '<empty>', blank line, 'bab'", "3 strings: ab, ε, bab", f"{len(words)} strings: {words}", words == ["ab", "", "bab"])
all_ok = all(p["mismatches"] == 0 for p in out["presets"])
total = sum(p["strings"] for p in out["presets"])
add("T16", "NFA vs DFA equivalence", f"every string up to length 8, all {len(presets)} presets ({total} checks)", "0 disagreements",
    f"{sum(p['mismatches'] for p in out['presets'])} disagreements", all_ok)
out["cases"] = cases
out["total_equiv_checks"] = total
(ROOT / "Milestone2/TestCases/evidence.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
print(json.dumps({"presets": [(p["id"], p["nfa_states"], p["dfa_states"], p["mismatches"]) for p in out["presets"]],
                  "scaling": out["scaling"], "cases": [(c["id"], c["status"]) for c in cases]}, ensure_ascii=False, indent=1))
