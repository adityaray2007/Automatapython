"""Subset Lab — NFA to DFA Conversion Simulator.

Thin Streamlit UI layer. All automata logic lives in algorithm/.
"""
from __future__ import annotations

import dataclasses
import html
import json
import time

import streamlit as st

from algorithm.examples import EXAMPLES, EXAMPLES_BY_ID
from algorithm.explain import describe_step
from algorithm.models import DFA, NFA, ConversionResult
from algorithm.simulate import parse_batch, simulate_dfa, simulate_nfa
from algorithm.subset_construction import set_id, subset_construction
from algorithm.validate import NfaForm, build_nfa, split_list
from ui.graphs import dfa_to_dot, nfa_to_dot
from ui.styles import GLASS_CSS

st.set_page_config(layout="wide", page_title="Subset Lab")
st.markdown(GLASS_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Extra Preset Configurations (Custom / Exercises)
# ---------------------------------------------------------------------------

EXTRA_PRESETS: dict[str, dict] = {
    "custom": {
        "id": "custom",
        "title": "✨ Custom / Blank (Type Your Own NFA)",
        "description": "Start with a clean slate to define your own custom NFA.",
        "states": "",
        "alphabet": "",
        "start": "",
        "accepts": [],
        "cells": {},
    },
    "contains-aa": {
        "id": "contains-aa",
        "title": "Exercise 6: Contains substring “aa”",
        "description": "NFA from Exercise 6 over {a,b}. Produces a 4-state DFA.",
        "states": "q0, q1, q2",
        "alphabet": "a, b",
        "start": "q0",
        "accepts": ["q2"],
        "cells": {
            "q0": {"a": "q0, q1", "b": "q0"},
            "q1": {"a": "q2", "b": ""},
            "q2": {"a": "q2", "b": "q2"},
        },
    },
    "even-zeros": {
        "id": "even-zeros",
        "title": "Even number of 0s",
        "description": "Binary strings with an even number of 0s. Produces a 2-state DFA.",
        "states": "q0, q1",
        "alphabet": "0, 1",
        "start": "q0",
        "accepts": ["q0"],
        "cells": {
            "q0": {"0": "q1", "1": "q0"},
            "q1": {"0": "q0", "1": "q1"},
        },
    },
}

ALL_PRESET_IDS = [e.id for e in EXAMPLES] + list(EXTRA_PRESETS.keys())
PRESET_TITLES = {e.id: e.title for e in EXAMPLES}
for pid, pdata in EXTRA_PRESETS.items():
    PRESET_TITLES[pid] = pdata["title"]


# ---------------------------------------------------------------------------
# State Management & Helpers
# ---------------------------------------------------------------------------

def load_example(example_id: str) -> None:
    """Load a preset NFA (standard or custom) into the editor session state."""
    # Clean previous cell keys
    for k in list(st.session_state.keys()):
        if k.startswith("cell_") or k.startswith("ms_"):
            del st.session_state[k]

    if example_id in EXAMPLES_BY_ID:
        ex = EXAMPLES_BY_ID[example_id]
        st.session_state["states_input"] = ", ".join(ex.nfa.states)
        st.session_state["alphabet_input"] = ", ".join(ex.nfa.alphabet)
        st.session_state["start_select"] = ex.nfa.start
        st.session_state["accepts_select"] = list(ex.nfa.accepts)
        for s in ex.nfa.states:
            for a in ex.nfa.alphabet:
                targets = ex.nfa.transitions.get(s, {}).get(a, [])
                st.session_state[f"cell_{s}_{a}"] = ", ".join(targets)
                st.session_state[f"ms_{s}_{a}"] = list(targets)
    elif example_id in EXTRA_PRESETS:
        pdata = EXTRA_PRESETS[example_id]
        st.session_state["states_input"] = pdata["states"]
        st.session_state["alphabet_input"] = pdata["alphabet"]
        st.session_state["start_select"] = pdata["start"]
        st.session_state["accepts_select"] = list(pdata["accepts"])
        states = split_list(pdata["states"])
        alphabet = split_list(pdata["alphabet"])
        for s in states:
            for a in alphabet:
                cell_text = pdata["cells"].get(s, {}).get(a, "")
                targets = split_list(cell_text)
                st.session_state[f"cell_{s}_{a}"] = cell_text
                st.session_state[f"ms_{s}_{a}"] = list(targets)

    st.session_state["validation_errors"] = []
    st.session_state["error_sig"] = None
    st.session_state["conversion_result"] = None
    st.session_state["conversion_nfa"] = None
    st.session_state["conversion_sig"] = None
    st.session_state["test_result"] = None
    st.session_state["batch_result"] = None
    st.session_state["step"] = 0
    st.session_state["playing"] = False
    st.session_state["inspect_state"] = "—"


if "initialized" not in st.session_state:
    st.session_state["initialized"] = True
    load_example(EXAMPLES[0].id)
    st.session_state["example_select"] = EXAMPLES[0].id


def compute_signature() -> str:
    """Compute signature from editor fields to detect freshness."""
    states_raw = st.session_state.get("states_input", "")
    alpha_raw = st.session_state.get("alphabet_input", "")
    start_val = str(st.session_state.get("start_select", ""))
    accepts_val = ",".join(sorted(st.session_state.get("accepts_select", [])))

    parts = [states_raw, alpha_raw, start_val, accepts_val]
    states = list(dict.fromkeys(split_list(states_raw)))
    alphabet = list(dict.fromkeys(split_list(alpha_raw)))
    for s in states:
        for a in alphabet:
            parts.append(f"{s}:{a}:{st.session_state.get(f'cell_{s}_{a}', '')}")
    return "|".join(parts)


def get_current_form() -> NfaForm:
    """Construct NfaForm from editor widgets."""
    states_raw = st.session_state.get("states_input", "")
    alpha_raw = st.session_state.get("alphabet_input", "")
    start_val = str(st.session_state.get("start_select", ""))
    accepts_val = list(st.session_state.get("accepts_select", []))

    states = list(dict.fromkeys(split_list(states_raw)))
    alphabet = list(dict.fromkeys(split_list(alpha_raw)))

    cells: dict[str, dict[str, str]] = {}
    for s in states:
        cells[s] = {}
        for a in alphabet:
            cells[s][a] = st.session_state.get(f"cell_{s}_{a}", "")

    return NfaForm(
        states=states_raw,
        alphabet=alpha_raw,
        start=start_val,
        accepts=accepts_val,
        cells=cells,
    )


# Callbacks
def on_preset_change() -> None:
    eid = st.session_state.get("example_select")
    if eid in ALL_PRESET_IDS:
        load_example(eid)


def on_reset() -> None:
    eid = st.session_state.get("example_select", EXAMPLES[0].id)
    if eid in ALL_PRESET_IDS:
        load_example(eid)


def on_convert() -> None:
    sig = compute_signature()
    form = get_current_form()
    build_res = build_nfa(form)
    if build_res.errors:
        st.session_state["validation_errors"] = build_res.errors
        st.session_state["error_sig"] = sig
        st.session_state["conversion_result"] = None
        st.session_state["conversion_nfa"] = None
        st.session_state["conversion_sig"] = None
    else:
        st.session_state["validation_errors"] = []
        st.session_state["error_sig"] = None
        nfa = build_res.nfa
        conv_res = subset_construction(nfa)
        st.session_state["conversion_nfa"] = nfa
        st.session_state["conversion_result"] = conv_res
        st.session_state["conversion_sig"] = sig
        st.session_state["step"] = len(conv_res.steps)
        st.session_state["playing"] = False
        st.session_state["inspect_state"] = "—"

    st.session_state["test_result"] = None
    st.session_state["batch_result"] = None


def on_step_reset() -> None:
    st.session_state["step"] = 0
    st.session_state["playing"] = False


def on_step_prev() -> None:
    st.session_state["step"] = max(0, st.session_state.get("step", 0) - 1)
    st.session_state["playing"] = False


def on_step_next(total: int) -> None:
    st.session_state["step"] = min(total, st.session_state.get("step", 0) + 1)
    st.session_state["playing"] = False


def on_step_play(total: int) -> None:
    if st.session_state.get("step", 0) >= total:
        st.session_state["step"] = 0
    st.session_state["playing"] = True


def on_slider_change() -> None:
    st.session_state["step"] = st.session_state.get("step_slider", 0)
    st.session_state["playing"] = False


def on_run_test() -> None:
    st.session_state["test_result"] = (compute_signature(), st.session_state.get("test_input", ""))


def on_batch_run() -> None:
    st.session_state["batch_result"] = (compute_signature(), st.session_state.get("batch_input", ""))


def make_sync_callback(state_name: str, sym_name: str):
    def _sync():
        selected = st.session_state.get(f"ms_{state_name}_{sym_name}", [])
        st.session_state[f"cell_{state_name}_{sym_name}"] = ", ".join(selected)
    return _sync


# Freshness evaluation
current_signature = compute_signature()
is_fresh = (
    st.session_state.get("conversion_result") is not None
    and st.session_state.get("conversion_sig") == current_signature
)

conv_res: ConversionResult | None = st.session_state.get("conversion_result") if is_fresh else None
conv_nfa: NFA | None = st.session_state.get("conversion_nfa") if is_fresh else None

# Sanitize start and accepts based on declared states
declared_states = list(dict.fromkeys(split_list(st.session_state.get("states_input", ""))))
declared_alphabet = list(dict.fromkeys(split_list(st.session_state.get("alphabet_input", ""))))

if declared_states:
    if st.session_state.get("start_select") not in declared_states:
        st.session_state["start_select"] = declared_states[0]
    st.session_state["accepts_select"] = [
        s for s in st.session_state.get("accepts_select", []) if s in declared_states
    ]
    start_options = declared_states
    accepts_options = declared_states
else:
    start_options = [""]
    accepts_options = []
    st.session_state["start_select"] = ""
    st.session_state["accepts_select"] = []


# ---------------------------------------------------------------------------
# UI Layout
# ---------------------------------------------------------------------------

# Brand Header
st.markdown(
    '<div class="brand"><h1>Subset Lab</h1><p>Watch an NFA collapse into a DFA.</p></div>',
    unsafe_allow_html=True,
)

# SECTION 1: Master NFA Editor & Configuration Deck
with st.container(border=True):
    col_hdr, col_actions = st.columns([3, 2])
    with col_hdr:
        st.markdown("### 🛠 NFA Editor & Configuration")
    with col_actions:
        btn_col1, btn_col2 = st.columns(2)
        btn_col1.button("⚡ Convert to DFA", key="convert_btn", type="primary", on_click=on_convert, use_container_width=True)
        btn_col2.button("↺ Reset editor", key="reset_btn", on_click=on_reset, use_container_width=True)

    # 2-column layout inside Editor: Left = Definition inputs; Right = Transition Table
    col_def, col_trans = st.columns([1, 1], gap="medium")

    with col_def:
        st.selectbox(
            "Choose a preset NFA",
            options=ALL_PRESET_IDS,
            format_func=lambda eid: PRESET_TITLES.get(eid, eid),
            key="example_select",
            on_change=on_preset_change,
        )

        col_st_in, col_al_in = st.columns(2)
        col_st_in.text_input("States (comma-separated)", key="states_input")
        col_al_in.text_input("Alphabet (comma-separated)", key="alphabet_input")

        col_st_sel, col_acc_sel = st.columns(2)
        with col_st_sel:
            st.selectbox("Start state", options=start_options, key="start_select")
        with col_acc_sel:
            st.multiselect("Accepting states", options=accepts_options, key="accepts_select")

        # Show validation errors if present and form is unchanged
        if st.session_state.get("validation_errors") and st.session_state.get("error_sig") == current_signature:
            for err in st.session_state["validation_errors"]:
                st.error(err)

    with col_trans:
        col_t_title, col_t_mode = st.columns([2, 3])
        with col_t_title:
            st.markdown("##### Transition Table $\\delta(state, symbol)$")
        with col_t_mode:
            grid_mode = st.radio(
                "Entry mode:",
                options=["Choose states (Multi-select)", "Type names (Text input)"],
                horizontal=True,
                key="grid_input_mode",
            )

        if len(declared_states) > 30 or len(declared_alphabet) > 10:
            st.info("Grid capped at 30 states × 10 symbols.")
        elif declared_states and declared_alphabet:
            # Header row
            header_cols = st.columns([1] + [2] * len(declared_alphabet))
            header_cols[0].markdown("**State**")
            for i, a in enumerate(declared_alphabet):
                header_cols[i + 1].markdown(f"**{a}**")

            # Data rows
            for s in declared_states:
                r_cols = st.columns([1] + [2] * len(declared_alphabet))
                r_cols[0].markdown(f"**{s}**")
                for i, a in enumerate(declared_alphabet):
                    cell_val = st.session_state.get(f"cell_{s}_{a}", "")
                    if grid_mode.startswith("Choose"):
                        # Multiselect mode: select from declared states
                        parsed = [t for t in split_list(cell_val) if t in declared_states]
                        r_cols[i + 1].multiselect(
                            label=f"δ({s},{a})",
                            options=declared_states,
                            default=parsed,
                            key=f"ms_{s}_{a}",
                            label_visibility="collapsed",
                            on_change=make_sync_callback(s, a),
                        )
                    else:
                        # Text box mode: standard text inputs
                        r_cols[i + 1].text_input(
                            label=f"δ({s},{a})",
                            label_visibility="collapsed",
                            key=f"cell_{s}_{a}",
                        )


# SECTION 2: The Automata Showcase (NFA on Left, DFA + Step Player on Right)
col_show_nfa, col_show_dfa = st.columns([1, 1], gap="medium")

with col_show_nfa:
    with st.container(border=True):
        st.markdown("### 📡 NFA State Diagram")
        live_form = get_current_form()
        live_res = build_nfa(live_form)
        live_nfa = live_res.nfa

        # State inspector
        if is_fresh and conv_res is not None:
            dfa_opts = ["—"] + [s.id for s in conv_res.dfa.states]
            alias_map_inv = {s.id: s.alias for s in conv_res.dfa.states}
            if st.session_state.get("inspect_state") not in dfa_opts:
                st.session_state["inspect_state"] = "—"
            st.selectbox(
                "Inspect a DFA state (highlights subset members in NFA):",
                options=dfa_opts,
                format_func=lambda x: "— None —" if x == "—" else f"{alias_map_inv.get(x, '')} — {x}",
                key="inspect_state",
            )
        else:
            st.selectbox(
                "Inspect a DFA state (highlights subset members in NFA):",
                options=["—"],
                key="inspect_state",
                disabled=True,
            )

        glow_states = set()
        if is_fresh and conv_res is not None and st.session_state.get("inspect_state", "—") != "—":
            inspected = next(
                (s for s in conv_res.dfa.states if s.id == st.session_state["inspect_state"]),
                None,
            )
            if inspected:
                glow_states = set(inspected.members)

        if live_nfa is not None:
            st.graphviz_chart(nfa_to_dot(live_nfa, glow=glow_states), use_container_width=True)
        else:
            st.info("Enter a valid NFA in the editor to see its diagram.")

with col_show_dfa:
    with st.container(border=True):
        col_dfa_title, col_dfa_dl = st.columns([3, 2])
        with col_dfa_title:
            st.markdown("### 🕸 DFA State Diagram & Construction")
        with col_dfa_dl:
            if is_fresh and conv_res is not None:
                dfa_json_str = json.dumps(dataclasses.asdict(conv_res.dfa), ensure_ascii=False, indent=2)
                st.download_button(
                    "Download DFA (JSON)",
                    data=dfa_json_str,
                    file_name="dfa.json",
                    mime="application/json",
                    key="dfa_json_btn",
                    use_container_width=True,
                )
            else:
                st.download_button(
                    "Download DFA (JSON)",
                    data="",
                    file_name="dfa.json",
                    mime="application/json",
                    key="dfa_json_btn",
                    disabled=True,
                    use_container_width=True,
                )

        if is_fresh and conv_res is not None:
            total_steps = len(conv_res.steps)
            step_val = st.session_state.get("step", total_steps)
            focus_step = (step_val - 1) if (0 < step_val < total_steps) else None

            path_trace = None
            if step_val == total_steps and st.session_state.get("test_result"):
                t_sig, t_text = st.session_state["test_result"]
                if t_sig == current_signature:
                    run_trace = simulate_dfa(conv_res.dfa, t_text)
                    path_trace = [(p.source, p.target) for p in run_trace.path]

            dfa_dot = dfa_to_dot(conv_res, upto=step_val, path=path_trace, focus_step=focus_step)
            st.graphviz_chart(dfa_dot, use_container_width=True)

            # Step Player Controls directly under the DFA graph
            st.markdown("##### ⏯ Step Player")
            cur_step = max(0, min(step_val, total_steps))
            st.session_state["step"] = cur_step
            st.session_state["step_slider"] = cur_step

            col_r, col_p, col_play, col_n, col_cnt = st.columns([1, 1, 1, 1, 2])
            col_r.button("⏮ Reset", key="step_reset", on_click=on_step_reset, use_container_width=True)
            col_p.button("◀ Prev", key="step_prev", on_click=on_step_prev, use_container_width=True)
            col_play.button("▶ Play", key="step_play", on_click=on_step_play, args=(total_steps,), use_container_width=True)
            col_n.button("Next ▶", key="step_next", on_click=on_step_next, args=(total_steps,), use_container_width=True)
            with col_cnt:
                st.markdown(
                    f'<span class="step-counter">{cur_step} / {total_steps}</span>',
                    unsafe_allow_html=True,
                )

            st.slider(
                "Construction Step",
                min_value=0,
                max_value=max(1, total_steps),
                key="step_slider",
                on_change=on_slider_change,
            )

            st.markdown("##### Step-by-Step Construction Log")
            if cur_step == 0:
                st.markdown(
                    '<div class="step-item active"><strong>Step 0:</strong> Initial DFA start state <code>'
                    + conv_res.dfa.start
                    + "</code> registered. Press <b>Next ▶</b> or <b>Play ▶</b> to process transitions.</div>",
                    unsafe_allow_html=True,
                )
            else:
                for idx in range(cur_step):
                    st_item = conv_res.steps[idx]
                    sentence = describe_step(st_item, conv_res.dfa)
                    if idx == cur_step - 1:
                        st.markdown(
                            f'<div class="step-item active"><strong>▶ Step {idx + 1}:</strong> {sentence}</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f'<div class="step-item"><strong>Step {idx + 1}:</strong> {sentence}</div>',
                            unsafe_allow_html=True,
                        )
        else:
            col_r, col_p, col_play, col_n, col_cnt = st.columns([1, 1, 1, 1, 2])
            col_r.button("⏮ Reset", key="step_reset", disabled=True, use_container_width=True)
            col_p.button("◀ Prev", key="step_prev", disabled=True, use_container_width=True)
            col_play.button("▶ Play", key="step_play", disabled=True, use_container_width=True)
            col_n.button("Next ▶", key="step_next", disabled=True, use_container_width=True)
            with col_cnt:
                st.markdown('<span class="step-counter">0 / 0</span>', unsafe_allow_html=True)
            st.slider("Construction Step", min_value=0, max_value=1, key="step_slider", disabled=True)
            st.info("Press Convert to generate the DFA diagram and step through the construction.")


# SECTION 3: Transition Tables (NFA Table on Left, DFA Table on Right)
col_tbl_nfa, col_tbl_dfa = st.columns([1, 1], gap="medium")

with col_tbl_nfa:
    with st.container(border=True):
        st.markdown("### 📋 NFA Transition Table")
        if live_nfa is not None:
            nfa_rows = []
            for s in live_nfa.states:
                prefix = ""
                if s == live_nfa.start:
                    prefix += "→ "
                if s in live_nfa.accepts:
                    prefix += "* "
                row = {"State": f"{prefix}{s}"}
                for a in live_nfa.alphabet:
                    targets = live_nfa.transitions.get(s, {}).get(a, [])
                    row[a] = ", ".join(targets) if targets else "—"
                nfa_rows.append(row)
            st.table(nfa_rows)
        else:
            st.info("Enter a valid NFA in the editor to view its transition table.")

with col_tbl_dfa:
    with st.container(border=True):
        st.markdown("### 📊 DFA Transition Table")
        if is_fresh and conv_res is not None:
            alias_map = {s.id: s.alias for s in conv_res.dfa.states}
            dfa_rows = []
            for s in conv_res.dfa.states:
                prefix = "→ " if s.is_start else ""
                row = {"State": f"{prefix}{s.alias} = {s.id}"}
                for a in conv_res.dfa.alphabet:
                    target_id = conv_res.dfa.transitions[s.id][a]
                    target_alias = alias_map.get(target_id, "")
                    row[a] = f"{target_alias} {target_id}"
                row["Accepting"] = "✓" if s.is_accepting else ""
                dfa_rows.append(row)
            st.table(dfa_rows)
        else:
            st.info("Press Convert to view the DFA transition table.")


# SECTION 4: String Testing & Equivalence Verification
col_test_single, col_test_batch = st.columns([1, 1], gap="medium")

with col_test_single:
    with st.container(border=True):
        st.markdown("### 🧪 Single String Testing")
        st.text_input("Input string", key="test_input")
        st.button(
            "Run string test",
            key="run_test_btn",
            disabled=not is_fresh,
            on_click=on_run_test,
        )

        if is_fresh and conv_res is not None and conv_nfa is not None:
            t_res = st.session_state.get("test_result")
            if t_res is not None and t_res[0] == current_signature:
                test_str = t_res[1]
                d_run = simulate_dfa(conv_res.dfa, test_str)
                n_run = simulate_nfa(conv_nfa, test_str)

                # Exactly one verdict element matching test contract
                if d_run.accepted:
                    st.markdown('<div class="test-result ok">Accepted</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="test-result bad">Rejected</div>', unsafe_allow_html=True)

                if d_run.error:
                    st.warning(d_run.error)

                # Trace table
                alias_m = {s.id: s.alias for s in conv_res.dfa.states}
                trace_rows = []
                init_alias = alias_m.get(conv_res.dfa.start, "")
                init_nfa = set_id(n_run.frontier[0]) if n_run.frontier else "—"
                trace_rows.append({
                    "Step": 0,
                    "Symbol": "—",
                    "DFA state": f"{init_alias} {conv_res.dfa.start}",
                    "NFA states": init_nfa,
                })
                for i, p in enumerate(d_run.path, start=1):
                    step_frontier = set_id(n_run.frontier[i]) if i < len(n_run.frontier) else "—"
                    t_alias = alias_m.get(p.target, "")
                    trace_rows.append({
                        "Step": i,
                        "Symbol": p.symbol,
                        "DFA state": f"{t_alias} {p.target}",
                        "NFA states": step_frontier,
                    })
                st.table(trace_rows)

                if d_run.accepted == n_run.accepted and d_run.error is None and n_run.error is None:
                    st.markdown(
                        '<span class="agree-badge">NFA and DFA agree ✓</span>',
                        unsafe_allow_html=True,
                    )

with col_test_batch:
    with st.container(border=True):
        st.markdown("### 📑 Batch Test Suite")
        st.text_area(
            "Batch strings (one per line, <empty> for empty string)",
            key="batch_input",
            height=120,
        )
        st.button(
            "Run batch test",
            key="batch_run_btn",
            disabled=not is_fresh,
            on_click=on_batch_run,
        )

        if is_fresh and conv_res is not None:
            b_res = st.session_state.get("batch_result")
            if b_res is not None and b_res[0] == current_signature:
                b_raw = b_res[1]
                words = parse_batch(b_raw)
                alias_m = {s.id: s.alias for s in conv_res.dfa.states}
                batch_rows = []
                for w in words:
                    r = simulate_dfa(conv_res.dfa, w)
                    final_alias = alias_m.get(r.final_state, "")
                    batch_rows.append({
                        "String": "<empty>" if w == "" else w,
                        "Verdict": "Accepted" if r.accepted else "Rejected",
                        "Final DFA state": f"{final_alias} {r.final_state}",
                        "Note": r.error if r.error else "",
                    })
                st.table(batch_rows)


# ---------------------------------------------------------------------------
# Auto-play loop for step player
# ---------------------------------------------------------------------------
if is_fresh and conv_res is not None and st.session_state.get("playing", False):
    total_steps = len(conv_res.steps)
    cur_step = st.session_state.get("step", 0)
    if cur_step < total_steps:
        time.sleep(0.9)
        st.session_state["step"] = cur_step + 1
        st.rerun()
    else:
        st.session_state["playing"] = False
