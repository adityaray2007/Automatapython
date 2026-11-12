"""Build Graphviz DOT text for the NFA and the DFA. Streamlit renders it with st.graphviz_chart."""
from __future__ import annotations

from algorithm.models import NFA, ConversionResult



LIGHT = dict(INK="#0f172a", MUTED="#64748b", ACCENT="#1d4ed8", VIOLET="#1e40af", TEAL="#047857",
             ROSE="#b91c1c", LAVENDER="#eff6ff", MINT="#ecfdf5", PEACH="#fef3c7", DEAD="#fef2f2")
DARK = dict(INK="#e2e8f0", MUTED="#94a3b8", ACCENT="#60a5fa", VIOLET="#93c5fd", TEAL="#34d399",
            ROSE="#f87171", LAVENDER="#1e293b", MINT="#064e3b", PEACH="#78350f", DEAD="#450a0a")


def _q(text: str) -> str:
    """Quote text for DOT."""
    return '"' + text.replace('"', '\\"') + '"'


def _header(c: dict) -> list[str]:
    return [
        "digraph G {",
        "  rankdir=LR;",
        '  bgcolor="transparent";',
        "  pad=0.5; nodesep=0.6; ranksep=0.8;",
        '  margin="0.3,0.3";',
        f'  node [shape=circle fontname="Helvetica,Arial,sans-serif" fontsize=12 fontcolor="{c["INK"]}" color="{c["ACCENT"]}" penwidth=1.5];',
        f'  edge [fontname="Helvetica,Arial,sans-serif" fontsize=12 fontcolor="{c["INK"]}" color="{c["MUTED"]}" arrowsize=0.8 penwidth=1.4];',
    ]


def _merge(edges: list[tuple[str, str, str]]) -> dict[tuple[str, str], list[str]]:
    """Several symbols between the same two nodes become ONE edge labelled 'a,b'."""
    merged: dict[tuple[str, str], list[str]] = {}
    for source, target, symbol in edges:
        merged.setdefault((source, target), []).append(symbol)
    return merged


def nfa_to_dot(nfa: NFA, glow: set[str] | None = None, dark: bool = False) -> str:
    """Draw the NFA. States in `glow` are highlighted (used to show a DFA state's subset)."""
    c = DARK if dark else LIGHT
    glow = glow or set()
    lines = _header(c)
    lines.append(f'  __start__ [shape=point width=0.12 color="{c["INK"]}"];')
    for state in nfa.states:
        accepting = state in nfa.accepts
        shape = "doublecircle" if accepting else "circle"
        if state in glow:
            fill, extra = c["PEACH"], " penwidth=3"
        else:
            fill, extra = (c["MINT"] if accepting else c["LAVENDER"]), ""
        color = c["TEAL"] if accepting else c["ACCENT"]
        lines.append(
            f'  {_q(state)} [shape={shape} style="filled" fillcolor="{fill}" '
            f'color="{color}"{extra} label={_q(state)}];'
        )
    lines.append(f"  __start__ -> {_q(nfa.start)};")
    edges = [(s, t, a) for s in nfa.states for a in nfa.alphabet
             for t in nfa.transitions.get(s, {}).get(a, [])]
    for (source, target), symbols in _merge(edges).items():
        lines.append(f'  {_q(source)} -> {_q(target)} [label={_q(",".join(symbols))}];')
    lines.append("}")
    return "\n".join(lines)


def dfa_to_dot(
    result: ConversionResult,
    upto: int | None = None,
    path: list[tuple[str, str]] | None = None,
    focus_step: int | None = None,
    dark: bool = False,
) -> str:
    """Draw the DFA.

    upto       -> only draw what has been discovered after this many construction steps
                  (None = everything; 0 = only the start state).
    path       -> list of (source_id, target_id) edges to light up (string-test trace).
    focus_step -> index of the step being shown: its source node gets a thick border and its
                  edge is emphasised.
    """
    c = DARK if dark else LIGHT
    dfa, steps = result.dfa, result.steps
    n = len(steps) if upto is None else max(0, min(upto, len(steps)))
    shown = steps[:n]
    visible = {dfa.start} | {s.result_id for s in shown if s.is_new_state}
    path_edges = set(path or [])
    focus = steps[focus_step] if focus_step is not None and 0 <= focus_step < len(steps) else None

    lines = _header(c)
    lines.append(f'  __start__ [shape=point width=0.12 color="{c["INK"]}"];')
    for state in dfa.states:
        if state.id not in visible:
            continue
        pulse = " penwidth=3" if (focus is not None and state.id == focus.from_id) else ""
        label = state.alias + "\\n" + state.id          # alias on top, subset underneath
        if state.is_dead:
            attrs = f'shape=circle style="dashed,filled" fillcolor="{c["DEAD"]}" color="{c["ROSE"]}"{pulse}'
        elif state.is_accepting:
            attrs = (f'shape=doublecircle style="filled" fillcolor="{c["MINT"]}" '
                     f'color="{c["TEAL"]}"{pulse}')
        else:
            attrs = f'shape=circle style="filled" fillcolor="{c["LAVENDER"]}" color="{c["ACCENT"]}"{pulse}'
        lines.append(f"  {_q(state.id)} [{attrs} label={_q(label)}];")
    lines.append(f"  __start__ -> {_q(dfa.start)};")

    edges = [(s.from_id, s.result_id, s.symbol) for s in shown]
    for (source, target), symbols in _merge(edges).items():
        if (source, target) in path_edges:
            style = f' color="{c["ACCENT"]}" fontcolor="{c["ACCENT"]}" penwidth=3'
        elif focus is not None and (source, target) == (focus.from_id, focus.result_id) \
                and focus.symbol in symbols:
            style = f' color="{c["VIOLET"]}" fontcolor="{c["VIOLET"]}" penwidth=2.5'
        else:
            style = ""
        lines.append(f'  {_q(source)} -> {_q(target)} [label={_q(",".join(symbols))}{style}];')
    lines.append("}")
    return "\n".join(lines)
