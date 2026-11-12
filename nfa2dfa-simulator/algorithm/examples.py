"""Five preset NFAs. Each lists the expected DFA size and test strings with the right verdicts."""
from __future__ import annotations

from dataclasses import dataclass

from .models import NFA


@dataclass
class ExampleCase:
    input: str
    accept: bool


@dataclass
class Example:
    id: str
    title: str
    description: str
    nfa: NFA
    expected_dfa_states: int
    cases: list[ExampleCase]


def _cases(pairs) -> list[ExampleCase]:
    return [ExampleCase(text, verdict) for text, verdict in pairs]


EXAMPLES: list[Example] = [
    Example(
        id="ends-with-ab",
        title="Ends with “ab”",
        description="Classic textbook NFA over {a,b}. Produces a 3-state DFA.",
        nfa=NFA(
            states=["q0", "q1", "q2"],
            alphabet=["a", "b"],
            transitions={"q0": {"a": ["q0", "q1"], "b": ["q0"]}, "q1": {"b": ["q2"]}, "q2": {}},
            start="q0",
            accepts=["q2"],
        ),
        expected_dfa_states=3,
        cases=_cases([("ab", True), ("aab", True), ("bab", True), ("abab", True),
                      ("abb", False), ("a", False), ("ba", False), ("", False)]),
    ),
    Example(
        id="third-from-last-a",
        title="3rd symbol from the end is “a”",
        description="The famous blow-up case: 4 NFA states → 2³ = 8 DFA states.",
        nfa=NFA(
            states=["q0", "q1", "q2", "q3"],
            alphabet=["a", "b"],
            transitions={
                "q0": {"a": ["q0", "q1"], "b": ["q0"]},
                "q1": {"a": ["q2"], "b": ["q2"]},
                "q2": {"a": ["q3"], "b": ["q3"]},
                "q3": {},
            },
            start="q0",
            accepts=["q3"],
        ),
        expected_dfa_states=8,
        cases=_cases([("abb", True), ("aab", True), ("aaa", True), ("babb", True), ("bbabb", True),
                      ("baa", False), ("bab", False), ("bbb", False), ("ab", False), ("", False)]),
    ),
    Example(
        id="contains-101",
        title="Contains substring “101”",
        description="Binary strings containing 101. Produces a 6-state DFA.",
        nfa=NFA(
            states=["q0", "q1", "q2", "q3"],
            alphabet=["0", "1"],
            transitions={
                "q0": {"0": ["q0"], "1": ["q0", "q1"]},
                "q1": {"0": ["q2"]},
                "q2": {"1": ["q3"]},
                "q3": {"0": ["q3"], "1": ["q3"]},
            },
            start="q0",
            accepts=["q3"],
        ),
        expected_dfa_states=6,
        cases=_cases([("101", True), ("0101", True), ("11011", True), ("1010", True),
                      ("1001", False), ("100", False), ("0110", False), ("11", False), ("", False)]),
    ),
    Example(
        id="starts-with-0-dead-state",
        title="Starts with 0 (dead state ∅)",
        description="Missing transitions create the empty-set trap state ∅ in the DFA.",
        nfa=NFA(
            states=["q0", "q1"],
            alphabet=["0", "1"],
            transitions={"q0": {"0": ["q1"]}, "q1": {"0": ["q1"], "1": ["q1"]}},
            start="q0",
            accepts=["q1"],
        ),
        expected_dfa_states=3,
        cases=_cases([("0", True), ("01", True), ("0110", True),
                      ("1", False), ("10", False), ("", False)]),
    ),
    Example(
        id="a-star-accepts-empty",
        title="a* (accepts the empty string)",
        description="Start state is accepting; symbol b leads to the dead state ∅.",
        nfa=NFA(
            states=["q0"],
            alphabet=["a", "b"],
            transitions={"q0": {"a": ["q0"]}},
            start="q0",
            accepts=["q0"],
        ),
        expected_dfa_states=2,
        cases=_cases([("", True), ("a", True), ("aaa", True),
                      ("b", False), ("ab", False), ("ba", False)]),
    ),
]

EXAMPLES_BY_ID: dict[str, Example] = {e.id: e for e in EXAMPLES}

