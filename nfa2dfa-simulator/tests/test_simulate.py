from algorithm.examples import EXAMPLES
from algorithm.simulate import parse_batch, simulate_dfa, simulate_nfa
from algorithm.subset_construction import subset_construction


def all_strings(alphabet, max_len):
    out, layer = [""], [""]
    for _ in range(max_len):
        layer = [prefix + a for prefix in layer for a in alphabet]
        out.extend(layer)
    return out


def test_documented_verdicts_for_every_example_case():
    for ex in EXAMPLES:
        dfa = subset_construction(ex.nfa).dfa
        for case in ex.cases:
            assert simulate_nfa(ex.nfa, case.input).accepted is case.accept, (ex.id, case.input)
            assert simulate_dfa(dfa, case.input).accepted is case.accept, (ex.id, case.input)


def test_nfa_and_dfa_agree_on_every_string_up_to_length_8():
    for ex in EXAMPLES:
        dfa = subset_construction(ex.nfa).dfa
        for word in all_strings(ex.nfa.alphabet, 8):
            assert simulate_dfa(dfa, word).accepted == simulate_nfa(ex.nfa, word).accepted, (ex.id, word)


def test_path_has_one_step_per_symbol_and_ends_at_final_state():
    ex = EXAMPLES[0]
    dfa = subset_construction(ex.nfa).dfa
    run = simulate_dfa(dfa, "aab")
    assert len(run.path) == 3
    assert run.path[0].source == dfa.start
    assert run.path[2].target == run.final_state
    assert run.accepted is True


def test_symbols_outside_alphabet_are_reported_not_crashing():
    ex = EXAMPLES[0]
    dfa = subset_construction(ex.nfa).dfa
    d = simulate_dfa(dfa, "abc")
    assert d.accepted is False and "not in the alphabet" in d.error.lower()
    n = simulate_nfa(ex.nfa, "abc")
    assert n.accepted is False and "not in the alphabet" in n.error.lower()


def test_nfa_frontier_shape():
    run = simulate_nfa(EXAMPLES[0].nfa, "aab")
    assert run.frontier[0] == ["q0"]
    assert len(run.frontier) == 4


def test_parse_batch():
    assert parse_batch("ab\n<empty>\n\nabb\r\n") == ["ab", "", "abb"]
    assert parse_batch("") == []

