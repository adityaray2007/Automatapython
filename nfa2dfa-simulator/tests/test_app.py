from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from algorithm.examples import EXAMPLES

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def fresh_app():
    at = AppTest.from_file(APP, default_timeout=30)
    at.run()
    assert not at.exception
    return at


def convert(at, example_id="ends-with-ab"):
    at.selectbox(key="example_select").select(example_id).run()
    at.button(key="convert_btn").click().run()
    assert not at.exception
    return at


def markdown_values(at):
    return [m.value for m in at.markdown if not m.value.strip().startswith("<style>")]


def dfa_tables(at):
    """Tables whose columns include 'Accepting' (that is the DFA table)."""
    return [t.value for t in at.table if "Accepting" in list(t.value.columns)]


def test_app_starts_without_error_and_tests_are_disabled_before_convert():
    at = fresh_app()
    assert at.button(key="run_test_btn").disabled is True
    assert at.button(key="batch_run_btn").disabled is True


@pytest.mark.parametrize("example", EXAMPLES, ids=[e.id for e in EXAMPLES])
def test_every_preset_converts_to_the_expected_size(example):
    at = convert(fresh_app(), example.id)
    tables = dfa_tables(at)
    assert len(tables) == 1
    assert len(tables[0]) == example.expected_dfa_states


@pytest.mark.parametrize("example", EXAMPLES, ids=[e.id for e in EXAMPLES])
def test_every_preset_case_gives_the_documented_verdict(example):
    at = convert(fresh_app(), example.id)
    for case in example.cases[:4]:
        at.text_input(key="test_input").set_value(case.input).run()
        at.button(key="run_test_btn").click().run()
        results = [v for v in markdown_values(at) if "test-result" in v]
        assert len(results) == 1, (example.id, case.input)
        expected = "Accepted" if case.accept else "Rejected"
        assert expected in results[0], (example.id, case.input)


def test_string_testing_accepts_then_rejects():
    at = convert(fresh_app())
    at.text_input(key="test_input").set_value("aab").run()
    at.button(key="run_test_btn").click().run()
    assert any("test-result" in v and "Accepted" in v for v in markdown_values(at))
    at.text_input(key="test_input").set_value("abb").run()
    at.button(key="run_test_btn").click().run()
    assert any("test-result" in v and "Rejected" in v for v in markdown_values(at))
    assert any("agree" in v for v in markdown_values(at))


def test_symbol_outside_alphabet_is_rejected_with_a_warning():
    at = convert(fresh_app())
    at.text_input(key="test_input").set_value("abc").run()
    at.button(key="run_test_btn").click().run()
    assert any("test-result" in v and "Rejected" in v for v in markdown_values(at))
    assert any("not in the alphabet" in w.value for w in at.warning)


def test_duplicate_state_names_show_a_validation_error():
    at = fresh_app()
    at.text_input(key="states_input").set_value("q0, q0").run()
    at.button(key="convert_btn").click().run()
    assert not at.exception
    assert any("unique" in e.value.lower() for e in at.error)
    assert dfa_tables(at) == []


def test_epsilon_in_alphabet_shows_friendly_error():
    at = fresh_app()
    at.text_input(key="alphabet_input").set_value("a, ε").run()
    at.button(key="convert_btn").click().run()
    assert not at.exception
    assert any("ε-transitions" in e.value for e in at.error)


def test_editing_after_convert_invalidates_the_result():
    at = convert(fresh_app())
    assert at.button(key="run_test_btn").disabled is False
    at.text_input(key="alphabet_input").set_value("a, b, c").run()
    assert at.button(key="run_test_btn").disabled is True
    assert dfa_tables(at) == []


def test_batch_tester():
    at = convert(fresh_app())
    at.text_area(key="batch_input").set_value("ab\nabb\n<empty>").run()
    at.button(key="batch_run_btn").click().run()
    tables = [t.value for t in at.table if "Verdict" in list(t.value.columns)]
    assert len(tables) == 1
    assert list(tables[0]["Verdict"]) == ["Accepted", "Rejected", "Rejected"]
    assert list(tables[0]["String"]) == ["ab", "abb", "<empty>"]


def test_step_player():
    at = convert(fresh_app())
    assert any("6 / 6" in v for v in markdown_values(at))          # starts at the end
    at.button(key="step_reset").click().run()
    assert any("0 / 6" in v and "step-counter" in v for v in markdown_values(at))
    at.button(key="step_next").click().run()
    assert any("1 / 6" in v and "step-counter" in v for v in markdown_values(at))
    at.button(key="step_prev").click().run()
    assert any("0 / 6" in v and "step-counter" in v for v in markdown_values(at))
