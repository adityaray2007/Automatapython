from algorithm.examples import EXAMPLES, EXAMPLES_BY_ID
from algorithm.models import NFA
from algorithm.subset_construction import alias_for, set_id, subset_construction


def get(example_id):
    return EXAMPLES_BY_ID[example_id]


def test_set_id_and_alias():
    assert set_id([]) == "∅"
    assert set_id(["q0", "q1"]) == "{q0,q1}"
    assert [alias_for(i) for i in (0, 1, 25, 26, 27)] == ["A", "B", "Z", "A1", "B1"]


def test_exact_dfa_for_ends_with_ab():
    dfa = subset_construction(get("ends-with-ab").nfa).dfa
    assert [s.id for s in dfa.states] == ["{q0}", "{q0,q1}", "{q0,q2}"]
    assert [s.alias for s in dfa.states] == ["A", "B", "C"]
    assert dfa.start == "{q0}"
    assert dfa.accepts == ["{q0,q2}"]
    assert dfa.transitions["{q0}"] == {"a": "{q0,q1}", "b": "{q0}"}
    assert dfa.transitions["{q0,q1}"] == {"a": "{q0,q1}", "b": "{q0,q2}"}
    assert dfa.transitions["{q0,q2}"] == {"a": "{q0,q1}", "b": "{q0}"}


def test_exact_dfa_for_contains_101():
    dfa = subset_construction(get("contains-101").nfa).dfa
    assert [s.id for s in dfa.states] == [
        "{q0}", "{q0,q1}", "{q0,q2}", "{q0,q1,q3}", "{q0,q2,q3}", "{q0,q3}",
    ]
    assert dfa.accepts == ["{q0,q1,q3}", "{q0,q2,q3}", "{q0,q3}"]
    assert dfa.transitions["{q0,q2}"] == {"0": "{q0}", "1": "{q0,q1,q3}"}
    assert dfa.transitions["{q0,q1,q3}"] == {"0": "{q0,q2,q3}", "1": "{q0,q1,q3}"}


def test_dead_state_is_created_for_missing_transitions():
    dfa = subset_construction(get("starts-with-0-dead-state").nfa).dfa
    assert [s.id for s in dfa.states] == ["{q0}", "{q1}", "∅"]
    dead = next(s for s in dfa.states if s.id == "∅")
    assert dead.is_dead is True
    assert dead.is_accepting is False
    assert dfa.transitions["∅"] == {"0": "∅", "1": "∅"}


def test_start_state_accepting_when_nfa_start_accepting():
    dfa = subset_construction(get("a-star-accepts-empty").nfa).dfa
    assert next(s for s in dfa.states if s.is_start).is_accepting is True
    assert [s.id for s in dfa.states] == ["{q0}", "∅"]


def test_expected_dfa_size_for_every_example():
    for ex in EXAMPLES:
        assert len(subset_construction(ex.nfa).dfa.states) == ex.expected_dfa_states, ex.id


def test_dfa_is_total_and_steps_are_consistent():
    for ex in EXAMPLES:
        result = subset_construction(ex.nfa)
        dfa, steps = result.dfa, result.steps
        ids = {s.id for s in dfa.states}
        assert len({s.alias for s in dfa.states}) == len(dfa.states)
        for state in dfa.states:
            for symbol in dfa.alphabet:
                assert dfa.transitions[state.id][symbol] in ids, ex.id
        assert len(steps) == len(dfa.states) * len(dfa.alphabet)
        assert sum(1 for s in steps if s.is_new_state) == len(dfa.states) - 1
        assert [s.index for s in steps] == list(range(len(steps)))


def test_deterministic_and_independent_of_target_order():
    base = get("ends-with-ab").nfa
    reordered = NFA(
        states=base.states, alphabet=base.alphabet,
        transitions={**base.transitions, "q0": {"a": ["q1", "q0"], "b": ["q0"]}},
        start=base.start, accepts=base.accepts,
    )
    assert subset_construction(reordered).dfa == subset_construction(base).dfa
    assert subset_construction(base) == subset_construction(base)

