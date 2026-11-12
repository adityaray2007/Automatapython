"""Terminal demo for the viva:  python -m algorithm.demo [example-id]

Prints the NFA, every construction step, and the final DFA table — no UI needed.
"""
from __future__ import annotations

import sys

from .examples import EXAMPLES, EXAMPLES_BY_ID
from .explain import describe_step
from .subset_construction import subset_construction


def main(example_id: str | None = None) -> None:
    example = EXAMPLES_BY_ID[example_id] if example_id else EXAMPLES[0]
    result = subset_construction(example.nfa)
    print(f"Example: {example.title}")
    print(f"NFA states: {example.nfa.states}  start: {example.nfa.start}  accepts: {example.nfa.accepts}")
    print("\nConstruction steps:")
    for step in result.steps:
        print(f"  {step.index + 1:>2}. {describe_step(step, result.dfa)}")
    print("\nDFA table:")
    for state in result.dfa.states:
        marks = ("→" if state.is_start else " ") + ("*" if state.is_accepting else " ")
        row = "  ".join(f"{a}:{result.dfa.transitions[state.id][a]}" for a in result.dfa.alphabet)
        print(f"  {marks} {state.alias} = {state.id:<14} {row}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)

