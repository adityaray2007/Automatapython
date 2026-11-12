"""THE CORE ALGORITHM — subset construction (NFA -> DFA).

Idea in one paragraph
---------------------
An NFA can be in several states at once. So we let each DFA state *be a set of NFA states*.
Start with the set {start}. For every DFA state S and every input symbol a:
    1. For every NFA state q in S, look up delta(q, a)   (where q can go on 'a').
    2. Take the UNION of all those targets. That union is a new set T.
    3. Add the edge  S --a--> T  to the DFA.  If T has never been seen, it is a NEW DFA state
       and we must process it later too.
Repeat until no new sets appear. A DFA state is accepting if it CONTAINS an NFA accepting state.
If T is empty we get the dead state ∅ (a trap that loops to itself on every symbol).
"""
from __future__ import annotations

from collections import deque

from .models import (
    DFA, ConstructionStep, ConversionResult, DFAState, MoveDetail, NFA,
)


def set_id(members: list[str]) -> str:
    """Write a subset as text: ['q0','q1'] -> '{q0,q1}', [] -> '∅'."""
    if len(members) == 0:
        return "∅"
    return "{" + ",".join(members) + "}"


def alias_for(index: int) -> str:
    """0->A, 1->B, ... 25->Z, 26->A1, 27->B1, ... (short names for DFA states)."""
    letter = chr(65 + index % 26)
    round_number = index // 26
    return letter if round_number == 0 else f"{letter}{round_number}"


def subset_construction(nfa: NFA) -> ConversionResult:
    # Remember the declared order of NFA states so every subset is written the same way
    # ({q0,q1}, never {q1,q0}). This makes the output deterministic.
    order = {state: i for i, state in enumerate(nfa.states)}

    def normalize(items) -> list[str]:
        """Remove duplicates and sort by NFA declaration order."""
        return sorted(set(items), key=lambda s: order.get(s, 0))

    accept_set = set(nfa.accepts)

    dfa_states: list[DFAState] = []              # all DFA states, in discovery order
    dfa_transitions: dict[str, dict[str, str]] = {}
    steps: list[ConstructionStep] = []           # a log of every (state, symbol) we processed
    known: dict[str, DFAState] = {}              # id -> state, to detect "have we seen this set?"

    def register(members: list[str]) -> DFAState:
        """Return the DFA state for this subset, creating it if it is new."""
        sid = set_id(members)
        if sid in known:
            return known[sid]
        created = DFAState(
            id=sid,
            alias=alias_for(len(dfa_states)),
            members=members,
            is_start=False,
            is_accepting=any(m in accept_set for m in members),
            is_dead=(len(members) == 0),
        )
        known[sid] = created
        dfa_states.append(created)
        dfa_transitions[sid] = {}
        return created

    # Step 1: the DFA start state is the set containing only the NFA start state.
    start_state = register(normalize([nfa.start]))
    start_state.is_start = True

    # Step 2: process DFA states one by one (breadth-first) until the queue is empty.
    queue: deque[DFAState] = deque([start_state])
    while queue:
        current = queue.popleft()
        for symbol in nfa.alphabet:
            # 2a. Where can each NFA state inside 'current' go on this symbol?
            moves = [
                MoveDetail(
                    state=q,
                    targets=normalize(nfa.transitions.get(q, {}).get(symbol, [])),
                )
                for q in current.members
            ]
            # 2b. Union of all those targets = the next DFA state.
            result_members = normalize(t for move in moves for t in move.targets)

            seen_before = len(known)
            target = register(result_members)
            is_new = len(known) > seen_before
            if is_new:
                queue.append(target)  # new sets must be processed too

            # 2c. Record the DFA edge and a log entry for the step player.
            dfa_transitions[current.id][symbol] = target.id
            steps.append(ConstructionStep(
                index=len(steps),
                from_id=current.id,
                symbol=symbol,
                moves=moves,
                result_members=result_members,
                result_id=target.id,
                is_new_state=is_new,
            ))

    dfa = DFA(
        alphabet=list(nfa.alphabet),
        states=dfa_states,
        transitions=dfa_transitions,
        start=start_state.id,
        accepts=[s.id for s in dfa_states if s.is_accepting],
    )
    return ConversionResult(dfa=dfa, steps=steps)

