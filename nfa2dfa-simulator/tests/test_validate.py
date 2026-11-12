from dataclasses import replace

from algorithm.examples import EXAMPLES
from algorithm.validate import NfaForm, build_nfa, nfa_to_form, split_list


def base():
    return nfa_to_form(EXAMPLES[0].nfa)


def errors_text(result):
    return " | ".join(result.errors)


def test_split_list():
    assert split_list(" a, b ,, c ") == ["a", "b", "c"]


def test_round_trip_every_example():
    for ex in EXAMPLES:
        result = build_nfa(nfa_to_form(ex.nfa))
        assert result.errors == [], ex.id
        assert result.nfa == ex.nfa, ex.id


def test_unknown_start_state():
    result = build_nfa(replace(base(), start="q9"))
    assert result.nfa is None and "start state" in errors_text(result).lower()


def test_duplicate_state_names():
    result = build_nfa(replace(base(), states="q0, q0, q1"))
    assert result.nfa is None and "unique" in errors_text(result).lower()


def test_multi_character_symbol():
    assert "single character" in errors_text(build_nfa(replace(base(), alphabet="a, bb"))).lower()


def test_epsilon_in_a_cell():
    b = base()
    cells = {**b.cells, "q0": {**b.cells["q0"], "a": "ε"}}
    result = build_nfa(replace(b, cells=cells))
    assert result.nfa is None and "ε-transitions" in errors_text(result)


def test_epsilon_words_and_symbols_in_alphabet():
    for token in ("ε", "eps", "epsilon", "λ", "lambda", "EPSILON"):
        assert "ε-transitions" in errors_text(build_nfa(replace(base(), alphabet=f"a, {token}")))


def test_unknown_target_state():
    b = base()
    cells = {**b.cells, "q0": {**b.cells["q0"], "a": "q7"}}
    assert "unknown state" in errors_text(build_nfa(replace(b, cells=cells))).lower()


def test_unknown_accepting_state():
    assert "not a declared state" in errors_text(build_nfa(replace(base(), accepts=["zzz"]))).lower()


def test_more_than_12_states():
    names = [f"s{i}" for i in range(13)]
    form = NfaForm(states=",".join(names), alphabet="a", start="s0", accepts=[], cells={})
    assert "at most 12" in errors_text(build_nfa(form)).lower()


def test_forbidden_characters_in_state_names():
    assert "not allowed" in errors_text(build_nfa(replace(base(), states="q{0}, q1, q2"))).lower()


def test_empty_cells_mean_no_transition():
    assert build_nfa(base()).nfa.transitions["q2"] == {}

