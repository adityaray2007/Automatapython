"""The algorithm folder must stay free of UI code so the team can explain it on its own."""
import pathlib

FORBIDDEN = ("streamlit", "graphviz", "import ui", "from ui", "import app")


def test_algorithm_package_has_no_ui_imports():
    folder = pathlib.Path(__file__).resolve().parents[1] / "algorithm"
    files = list(folder.glob("*.py"))
    assert len(files) >= 7
    for file in files:
        text = file.read_text(encoding="utf-8").lower()
        for word in FORBIDDEN:
            assert word not in text, f"{file.name} mentions '{word}'"

