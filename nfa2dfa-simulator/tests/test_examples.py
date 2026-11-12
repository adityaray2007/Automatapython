from algorithm.examples import EXAMPLES
from algorithm.validate import build_nfa, nfa_to_form


def test_ids_unique_and_cases_present():
    assert len({e.id for e in EXAMPLES}) == len(EXAMPLES) == 5
    for e in EXAMPLES:
        assert len(e.cases) > 3


def test_every_example_is_a_valid_nfa():
    for e in EXAMPLES:
        assert build_nfa(nfa_to_form(e.nfa)).errors == [], e.id


def test_expected_sizes():
    assert [e.expected_dfa_states for e in EXAMPLES] == [3, 8, 6, 3, 2]

