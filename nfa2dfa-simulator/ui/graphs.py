"""Build Graphviz DOT text for the NFA and the DFA. Streamlit renders it with st.graphviz_chart."""
from __future__ import annotations

from algorithm.models import NFA, ConversionResult

INK = "#1f2340"
MUTED = "#5d6285"
ACCENT = "#5b5bd6"
VIOLET = "#8b5cf6"
TEAL = "#0d9488"
ROSE = "#e11d48"
LAVENDER = "#d9ccff"
MINT = "#c9f2e4"
PEACH = "#ffd9c7"


def _q(text: str) -> str:
    """Quote text for DOT."""
    return '"' + text.replace('"', '\\"') + '"'


def _header() -> list[str]:
    return [
        "digraph G {",
        "  rankdir=LR;",
        '  bgcolor="transparent";',
        "  pad=0.5; nodesep=0.6; ranksep=0.8;",
        '  margin="0.3,0.3";',
        f'  node [shape=circle fontname="Helvetica" fontsize=12 fontcolor="{INK}" color="{ACCENT}" penwidth=1.5];',
        f'  edge [fontname="Helvetica" fontsize=12 fontcolor="{INK}" color="{MUTED}" arrowsize=0.8 penwidth=1.4];',
    ]


def _merge(edges: list[tuple[str, str, str]]) -> dict[tuple[str, str], list[str]]:
    """Several symbols between the same two nodes become ONE edge labelled 'a,b'."""
    merged: dict[tuple[str, str], list[str]] = {}
    for source, target, symbol in edges:
        merged.setdefault((source, target), []).append(symbol)
    return merged


def nfa_to_dot(nfa: NFA, glow: set[str] | None = None) -> str:
    """Draw the NFA. States in `glow` are highlighted (used to show a DFA state's subset)."""
    glow = glow or set()
    lines = _header()
    lines.append(f'  __start__ [shape=point width=0.12 color="{INK}"];')
    for state in nfa.states:
        accepting = state in nfa.accepts
        shape = "doublecircle" if accepting else "circle"
        if state in glow:
            fill, extra = f"{PEACH}:#ffb38a", " penwidth=3"
        else:
            fill, extra = (f"#ffffff:{MINT}" if accepting else f"#ffffff:{LAVENDER}"), ""
        color = TEAL if accepting else ACCENT
        lines.append(
            f'  {_q(state)} [shape={shape} style="filled,radial" fillcolor="{fill}" '
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
) -> str:
    """Draw the DFA.

    upto       -> only draw what has been discovered after this many construction steps
                  (None = everything; 0 = only the start state).
    path       -> list of (source_id, target_id) edges to light up (string-test trace).
    focus_step -> index of the step being shown: its source node gets a thick border and its
                  edge is emphasised.
    """
    dfa, steps = result.dfa, result.steps
    n = len(steps) if upto is None else max(0, min(upto, len(steps)))
    shown = steps[:n]
    visible = {dfa.start} | {s.result_id for s in shown if s.is_new_state}
    path_edges = set(path or [])
    focus = steps[focus_step] if focus_step is not None and 0 <= focus_step < len(steps) else None

    lines = _header()
    lines.append(f'  __start__ [shape=point width=0.12 color="{INK}"];')
    for state in dfa.states:
        if state.id not in visible:
            continue
        pulse = " penwidth=3" if (focus is not None and state.id == focus.from_id) else ""
        label = state.alias + "\\n" + state.id          # alias on top, subset underneath
        if state.is_dead:
            attrs = f'shape=circle style="dashed,filled" fillcolor="#ffe4ea" color="{ROSE}"{pulse}'
        elif state.is_accepting:
            attrs = (f'shape=doublecircle style="filled,radial" fillcolor="#ffffff:{MINT}" '
                     f'color="{TEAL}"{pulse}')
        else:
            attrs = f'shape=circle style="filled,radial" fillcolor="#ffffff:{LAVENDER}" color="{ACCENT}"{pulse}'
        lines.append(f"  {_q(state.id)} [{attrs} label={_q(label)}];")
    lines.append(f"  __start__ -> {_q(dfa.start)};")

    edges = [(s.from_id, s.result_id, s.symbol) for s in shown]
    for (source, target), symbols in _merge(edges).items():
        if (source, target) in path_edges:
            style = f' color="{ACCENT}" fontcolor="{ACCENT}" penwidth=3'
        elif focus is not None and (source, target) == (focus.from_id, focus.result_id) \
                and focus.symbol in symbols:
            style = f' color="{VIOLET}" fontcolor="{VIOLET}" penwidth=2.5'
        else:
            style = ""
        lines.append(f'  {_q(source)} -> {_q(target)} [label={_q(",".join(symbols))}{style}];')
    lines.append("}")
    return "\n".join(lines)
