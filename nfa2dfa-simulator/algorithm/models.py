"""Plain data containers used everywhere. They hold data only — no logic."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NFA:
    states: list[str]                                # e.g. ["q0", "q1", "q2"]
    alphabet: list[str]                              # e.g. ["a", "b"]
    # transitions[state][symbol] = list of target states.
    # A missing entry means "no transition" (the NFA simply dies on that branch).
    transitions: dict[str, dict[str, list[str]]]
    start: str
    accepts: list[str]


@dataclass
class DFAState:
    id: str            # "{q0,q1}" or "∅" — the NFA subset written as text
    alias: str         # "A", "B", "C", ... in the order the states are discovered
    members: list[str] # NFA states inside this subset, in NFA declaration order
    is_start: bool
    is_accepting: bool # True if ANY member is an NFA accepting state
    is_dead: bool      # True for the empty set ∅ (a trap state)


@dataclass
class DFA:
    alphabet: list[str]
    states: list[DFAState]
    # transitions[dfa_state_id][symbol] = dfa_state_id. Always complete (total).
    transitions: dict[str, dict[str, str]]
    start: str
    accepts: list[str]


@dataclass
class MoveDetail:
    state: str          # one NFA state inside the current subset
    targets: list[str]  # delta(state, symbol) in the NFA


@dataclass
class ConstructionStep:
    """One row of the construction: 'from this DFA state, on this symbol, we land here'."""
    index: int
    from_id: str
    symbol: str
    moves: list[MoveDetail]
    result_members: list[str]
    result_id: str
    is_new_state: bool   # True if this step discovered a brand-new DFA state


@dataclass
class ConversionResult:
    dfa: DFA
    steps: list[ConstructionStep]

