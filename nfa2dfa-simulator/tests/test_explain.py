from algorithm.examples import EXAMPLES_BY_ID
from algorithm.explain import describe_step
from algorithm.subset_construction import subset_construction


def test_first_steps_of_ends_with_ab():
    result = subset_construction(EXAMPLES_BY_ID["ends-with-ab"].nfa)
    assert describe_step(result.steps[0], result.dfa) == (
        "From A = {q0} on 'a': δ(q0,a) = {q0,q1} → union = {q0,q1} → NEW state B")
    assert describe_step(result.steps[1], result.dfa) == (
        "From A = {q0} on 'b': δ(q0,b) = {q0} → union = {q0} → existing state A")


def test_dead_state_sentence():
    result = subset_construction(EXAMPLES_BY_ID["starts-with-0-dead-state"].nfa)
    last = result.steps[-1]
    assert describe_step(last, result.dfa) == (
        "From C = ∅ on '1': no NFA states to move from → union = ∅ → existing state C")


def test_new_state_count_matches():
    for ex_id in EXAMPLES_BY_ID:
        result = subset_construction(EXAMPLES_BY_ID[ex_id].nfa)
        texts = [describe_step(s, result.dfa) for s in result.steps]
        assert sum("NEW state" in t for t in texts) == len(result.dfa.states) - 1

