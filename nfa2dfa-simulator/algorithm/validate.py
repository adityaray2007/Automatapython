"""Turn the raw text typed into the editor into a clean, validated NFA (or a list of errors)."""
from __future__ import annotations

from dataclasses import dataclass

from .models import NFA

MAX_STATES = 12
EPSILON_TOKENS = ("ε", "eps", "epsilon", "λ", "lambda")
EPSILON_MESSAGE = "ε-transitions are not supported here — this simulator handles plain NFAs only."
FORBIDDEN_IN_NAMES = set('{}"\\`')


@dataclass
class NfaForm:
    """Everything the user typed, kept as plain strings so typing never breaks anything."""
    states: str                              # "q0, q1, q2"
    alphabet: str                            # "a, b"
    start: str                               # "q0"
    accepts: list[str]                       # ["q2"]
    cells: dict[str, dict[str, str]]         # cells[state][symbol] = "q0, q1"


@dataclass
class BuildResult:
    nfa: NFA | None
    errors: list[str]


def split_list(raw: str) -> list[str]:
    """'a, b ,c' -> ['a','b','c'] (trims spaces, drops empty pieces)."""
    return [part.strip() for part in raw.split(",") if part.strip() != ""]


def is_epsilon(token: str) -> bool:
    return token.lower() in EPSILON_TOKENS


def build_nfa(form: NfaForm) -> BuildResult:
    errors: list[str] = []
    states = split_list(form.states)
    alphabet = split_list(form.alphabet)

    # --- states ---
    if len(states) == 0:
        errors.append("Add at least one state.")
    if len(states) > MAX_STATES:
        errors.append(f"At most {MAX_STATES} states are supported.")
    if len(set(states)) != len(states):
        errors.append("State names must be unique.")
    for s in states:
        if s == "∅" or any(ch in FORBIDDEN_IN_NAMES for ch in s):
            errors.append(f'State name "{s}" is not allowed (avoid {{ }} ∅ quotes backslash backtick).')

    # --- alphabet ---
    if len(alphabet) == 0:
        errors.append("Add at least one input symbol.")
    if len(set(alphabet)) != len(alphabet):
        errors.append("Input symbols must be unique.")
    for sym in alphabet:
        if is_epsilon(sym):
            errors.append(EPSILON_MESSAGE)
        elif len(sym) != 1:
            errors.append(f'Input symbol "{sym}" must be a single character.')

    # --- start / accepting ---
    if form.start not in states:
        errors.append("Choose a start state from the declared states.")
    accepts = list(dict.fromkeys(form.accepts))  # remove duplicates, keep order
    for a in accepts:
        if a not in states:
            errors.append(f'Accepting state "{a}" is not a declared state.')

    # --- transitions ---
    transitions: dict[str, dict[str, list[str]]] = {}
    for state in states:
        transitions[state] = {}
        for sym in alphabet:
            text = form.cells.get(state, {}).get(sym, "")
            targets = list(dict.fromkeys(split_list(text)))
            for t in targets:
                if is_epsilon(t):
                    errors.append(EPSILON_MESSAGE)
                elif t not in states:
                    errors.append(f'δ({state}, {sym}) points to unknown state "{t}".')
            if targets:
                transitions[state][sym] = targets

    unique_errors = list(dict.fromkeys(errors))
    if unique_errors:
        return BuildResult(None, unique_errors)
    return BuildResult(NFA(states, alphabet, transitions, form.start, accepts), [])


def nfa_to_form(nfa: NFA) -> NfaForm:
    """The reverse direction: used to load a preset into the editor."""
    cells = {s: {a: ", ".join(nfa.transitions.get(s, {}).get(a, [])) for a in nfa.alphabet}
             for s in nfa.states}
    return NfaForm(
        states=", ".join(nfa.states),
        alphabet=", ".join(nfa.alphabet),
        start=nfa.start,
        accepts=list(nfa.accepts),
        cells=cells,
    )

