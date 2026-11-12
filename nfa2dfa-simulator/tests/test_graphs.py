from algorithm.examples import EXAMPLES, EXAMPLES_BY_ID
from algorithm.subset_construction import subset_construction
from ui.graphs import dfa_to_dot, nfa_to_dot


def conv(example_id):
    return subset_construction(EXAMPLES_BY_ID[example_id].nfa)


def test_dot_is_wellformed_for_all_examples():
    for ex in EXAMPLES:
        for dot in (dfa_to_dot(subset_construction(ex.nfa)), nfa_to_dot(ex.nfa)):
            assert dot.startswith("digraph") and dot.rstrip().endswith("}")


def test_accepting_states_are_double_circles():
    assert dfa_to_dot(conv("ends-with-ab")).count("shape=doublecircle") == 1
    assert nfa_to_dot(EXAMPLES_BY_ID["ends-with-ab"].nfa).count("shape=doublecircle") == 1


def test_start_arrow():
    assert '__start__ -> "{q0}"' in dfa_to_dot(conv("ends-with-ab"))


def test_dead_state_is_dashed():
    dot = dfa_to_dot(conv("starts-with-0-dead-state"))
    lines = [l.strip() for l in dot.splitlines() if l.strip().startswith('"∅" [')]
    assert len(lines) == 1 and "dashed" in lines[0]


def test_parallel_edges_are_merged():
    assert 'label="a,b"' in dfa_to_dot(conv("a-star-accepts-empty"))


def test_upto_zero_shows_only_start_state():
    dot = dfa_to_dot(conv("ends-with-ab"), upto=0)
    assert '"{q0}"' in dot and '"{q0,q1}"' not in dot


def test_path_highlight():
    result = conv("ends-with-ab")
    assert "penwidth=3" not in dfa_to_dot(result)
    assert "penwidth=3" in dfa_to_dot(result, path=[("{q0}", "{q0,q1}")])


def test_nfa_glow_marks_only_selected_states():
    nfa = EXAMPLES_BY_ID["ends-with-ab"].nfa
    lines = nfa_to_dot(nfa, glow={"q1"}).splitlines()
    q1 = next(l for l in lines if l.strip().startswith('"q1" ['))
    q0 = next(l for l in lines if l.strip().startswith('"q0" ['))
    assert "penwidth=3" in q1 and "penwidth=3" not in q0

