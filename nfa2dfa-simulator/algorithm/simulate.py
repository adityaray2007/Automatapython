"""Run an input string on the DFA and on the NFA (to prove both accept the same language)."""
from __future__ import annotations

from dataclasses import dataclass, field

from .models import DFA, NFA


@dataclass
class DfaTraceStep:
    source: str
    symbol: str
    target: str


@dataclass
class DfaRun:
    accepted: bool
    path: list[DfaTraceStep]
    final_state: str
    error: str | None = None


def simulate_dfa(dfa: DFA, text: str) -> DfaRun:
    """A DFA is simple: exactly one current state, move along one edge per symbol."""
    current = dfa.start
    path: list[DfaTraceStep] = []
    for symbol in text:
        nxt = dfa.transitions.get(current, {}).get(symbol)
        if nxt is None:  # the symbol has no edge => it is not in the alphabet
            return DfaRun(False, path, current, f'Symbol "{symbol}" is not in the alphabet.')
        path.append(DfaTraceStep(current, symbol, nxt))
        current = nxt
    return DfaRun(current in dfa.accepts, path, current)


@dataclass
class NfaRun:
    accepted: bool
    # frontier[0] = [start]; frontier[i] = all NFA states we could be in after i symbols
    frontier: list[list[str]] = field(default_factory=list)
    error: str | None = None


def simulate_nfa(nfa: NFA, text: str) -> NfaRun:
    """Track the SET of states the NFA could be in. Accept if any of them is accepting."""
    order = {s: i for i, s in enumerate(nfa.states)}
    current = [nfa.start]
    frontier = [current]
    for symbol in text:
        if symbol not in nfa.alphabet:
            return NfaRun(False, frontier, f'Symbol "{symbol}" is not in the alphabet.')
        reached = set()
        for state in current:
            for target in nfa.transitions.get(state, {}).get(symbol, []):
                reached.add(target)
        current = sorted(reached, key=lambda s: order.get(s, 0))
        frontier.append(current)
    return NfaRun(any(s in nfa.accepts for s in current), frontier)


def parse_batch(raw: str) -> list[str]:
    """Turn the batch text box into a list of test strings.

    One string per line. A line that is exactly '<empty>' means the empty string.
    Completely blank lines are ignored.
    """
    words = []
    for line in raw.splitlines():
        line = line.rstrip("\r")
        if line == "<empty>":
            words.append("")
        elif line.strip() != "":
            words.append(line)
    return words

