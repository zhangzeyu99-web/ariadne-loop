from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_homepage_links_to_browser_builder():
    index = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")

    assert "./playground.html" in index
    assert "Open Builder" in index


def test_playground_contains_required_static_controls():
    playground = (ROOT / "docs" / "playground.html").read_text(encoding="utf-8")

    for element_id in [
        'id="preset"',
        'id="title"',
        'id="goal"',
        'id="currentState"',
        'id="verifiers"',
        'id="output"',
        'id="copyButton"',
        'id="downloadButton"',
    ]:
        assert element_id in playground

    assert "navigator.clipboard.writeText" in playground
    assert "loop-snapshot.json" in playground
    assert "ariadne-loop check" in playground
