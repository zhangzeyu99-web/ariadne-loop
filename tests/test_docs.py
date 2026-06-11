from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_homepage_links_to_browser_builder():
    index = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")

    assert "./playground.html" in index
    assert "Open Builder" in index
    assert "verifier-recipes.md" in index


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


def test_verifier_recipes_are_linked_and_concrete():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    use_cases = (ROOT / "docs" / "use-cases.md").read_text(encoding="utf-8")
    recipes = (ROOT / "docs" / "verifier-recipes.md").read_text(encoding="utf-8")

    assert "docs/verifier-recipes.md" in readme
    assert "verifier-recipes.md" in use_cases
    for heading in [
        "Python Package Release Loop",
        "Frontend Bugfix Loop",
        "Documentation Refresh Loop",
        "GitHub Issue Triage Loop",
    ]:
        assert heading in recipes

    assert '"action_id": "verify"' in recipes
    assert "python -m pytest -q" in recipes
