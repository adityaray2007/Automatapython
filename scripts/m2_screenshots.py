"""Capture the report screenshots from the running app (http://localhost:8501)."""
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / "Milestone2" / "Screenshots"
URL = "http://localhost:8501"


def settle(page, ms=1500):
    page.wait_for_timeout(ms)


def convert(page):
    page.get_by_role("button", name="Convert to DFA").click(); settle(page, 2000)


def choose_preset(page, title):
    page.get_by_label("Choose a preset NFA").click(); settle(page, 500)
    page.keyboard.type(title[:12]); settle(page, 500)
    page.keyboard.press("Enter"); settle(page, 1500)


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=str(Path.home() / "Library/Caches/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-mac-arm64/chrome-headless-shell"))
    page = b.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=1.5)

    def fresh():
        page.goto(URL); page.wait_for_selector("text=Automata Workbench"); settle(page, 2500)

    fresh()
    page.screenshot(path=OUT / "fig01_initial_state.png", full_page=True)
    convert(page)
    page.screenshot(path=OUT / "fig02_full_interface_light.png", full_page=True)

    def card(name, fn):
        page.locator(f".st-key-card-{name}").screenshot(path=OUT / fn)

    card("editor", "el_editor.png"); card("nfa-diagram", "el_nfa_diagram.png"); card("dfa-diagram", "el_dfa_diagram.png")
    card("construction", "el_construction_full.png"); card("nfa-table", "el_nfa_table.png"); card("dfa-table", "el_dfa_table.png")

    # Step player at step 3
    page.get_by_role("button", name="Reset", exact=True).click(); settle(page)
    for _ in range(3):
        page.get_by_role("button", name="Next", exact=True).click(); settle(page, 1000)
    page.screenshot(path=OUT / "fig03_step_player_step3.png", full_page=True)
    card("dfa-diagram", "el_dfa_diagram_step3.png"); card("construction", "el_construction_step3.png")
    for _ in range(3):
        page.get_by_role("button", name="Next", exact=True).click(); settle(page, 600)

    # String test
    page.get_by_label("Input string").fill("aab"); page.keyboard.press("Enter"); settle(page, 800)
    page.get_by_role("button", name="Run string test").click(); settle(page, 1800)
    page.screenshot(path=OUT / "fig04_string_test_aab.png", full_page=True)
    card("single-test", "el_string_test.png")
    page.get_by_label("Batch strings (one per line, <empty> for empty string)").fill("ab\n<empty>\naab\nabb\nbab")
    page.keyboard.press("Control+Enter"); settle(page, 800)
    page.get_by_role("button", name="Run batch test").click(); settle(page, 1800)
    card("batch-test", "el_batch_test.png")

    # Dark mode
    page.get_by_text("Dark mode").click(); settle(page, 2000)
    page.screenshot(path=OUT / "fig05_dark_mode.png", full_page=True)
    page.get_by_text("Dark mode").click(); settle(page, 1500)

    # Larger example: 3rd symbol from the end is "a"
    choose_preset(page, "3rd symbol from the end is “a”")
    convert(page)
    page.screenshot(path=OUT / "fig06_third_from_last_a.png", full_page=True)
    card("dfa-diagram", "el_dfa_third_from_last.png"); card("dfa-table", "el_dfa_table_third.png")

    # Dead-state example
    choose_preset(page, "Starts with 0 (dead state ∅)")
    convert(page)
    page.screenshot(path=OUT / "fig07_dead_state.png", full_page=True)
    card("dfa-diagram", "el_dfa_dead_state.png")

    # Validation error: duplicate state names
    fresh()
    f = page.get_by_label("States (comma-separated)")
    f.fill("q0, q0"); page.keyboard.press("Enter"); settle(page, 1500)
    page.get_by_role("button", name="Convert to DFA").click(); settle(page, 2000)
    page.screenshot(path=OUT / "fig08_validation_error.png", full_page=False)
    card("editor", "el_validation_error.png")
    b.close()
print(sorted(x.name for x in OUT.iterdir()))
