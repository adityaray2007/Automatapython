"""Turn one construction step into a human sentence (used by the step log in the UI)."""
from __future__ import annotations

from .models import DFA, ConstructionStep
from .subset_construction import set_id


def describe_step(step: ConstructionStep, dfa: DFA) -> str:
    alias = {s.id: s.alias for s in dfa.states}
    if step.moves:
        moves = ", ".join(f"δ({m.state},{step.symbol}) = {set_id(m.targets)}" for m in step.moves)
    else:
        moves = "no NFA states to move from"
    if step.is_new_state:
        verdict = f"NEW state {alias[step.result_id]}"
    else:
        verdict = f"existing state {alias[step.result_id]}"
    return (f"From {alias[step.from_id]} = {step.from_id} on '{step.symbol}': "
            f"{moves} → union = {step.result_id} → {verdict}")

