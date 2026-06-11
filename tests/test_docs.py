from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_homepage_links_to_browser_builder():
    index = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "./playground.html" in index
    assert "Open Builder" in index
    assert "./openclaw.html" in index
    assert "OpenClaw guide" in index
    assert "造梦师" in index
    assert "Give AI agents a loop they can finish." in index
    assert "让 AI Agent 顺着循环跑完。" in index
    assert 'data-i18n="openTemplate"' not in index
    assert 'data-i18n="openClawGuide"' not in index
    assert "agent-recipes.md" in index
    assert "Agent recipes" in index
    assert "Claude Code command" in index
    assert "/ariadne-loop" in index
    assert "ariadne-loop quickstart" in index
    assert "llms.txt" in readme


def test_homepage_has_share_and_search_metadata():
    index = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    robots = (ROOT / "docs" / "robots.txt").read_text(encoding="utf-8")
    sitemap = (ROOT / "docs" / "sitemap.xml").read_text(encoding="utf-8")
    llms = (ROOT / "docs" / "llms.txt").read_text(encoding="utf-8")
    og_image = ROOT / "docs" / "assets" / "ariadne-loop-og.png"
    hero_image = ROOT / "docs" / "assets" / "ariadne-hero-v2.webp"

    assert 'rel="canonical"' in index
    assert 'hreflang="zh-CN"' in index
    assert 'name="keywords"' in index
    assert 'property="og:site_name"' in index
    assert 'property="og:title"' in index
    assert 'name="twitter:card"' in index
    assert "application/ld+json" in index
    assert '"applicationCategory": "DeveloperApplication"' in index
    assert "ariadne-loop-og.png" in index
    assert "ariadne-hero-v2.webp" in index
    assert "Sitemap:" in robots
    assert "https://zhangzeyu99-web.github.io/ariadne-loop/" in sitemap
    assert "https://zhangzeyu99-web.github.io/ariadne-loop/playground.html" in sitemap
    assert "https://zhangzeyu99-web.github.io/ariadne-loop/openclaw.html" in sitemap
    assert "https://zhangzeyu99-web.github.io/ariadne-loop/llms.txt" in sitemap
    assert "LLMs:" in robots
    assert "Ariadne Loop" in llms
    assert "Claude Code Command" in llms
    assert "ariadne-loop quickstart" in llms
    assert "https://github.com/zhangzeyu99-web/ariadne-loop" in llms
    assert og_image.read_bytes().startswith(b"\x89PNG")
    assert hero_image.read_bytes().startswith(b"RIFF")


def test_openclaw_page_has_search_metadata_and_setup():
    page = (ROOT / "docs" / "openclaw.html").read_text(encoding="utf-8")

    assert 'rel="canonical"' in page
    assert "OpenClaw" in page
    assert "Ariadne Loop for OpenClaw" in page
    assert 'property="og:title"' in page
    assert 'name="twitter:card"' in page
    assert "application/ld+json" in page
    assert '"@type": "TechArticle"' in page
    assert "ariadne-loop quickstart" in page
    assert "inspect -> act -> verify -> decide" in page


def test_playground_has_share_and_search_metadata():
    playground = (ROOT / "docs" / "playground.html").read_text(encoding="utf-8")

    assert 'rel="canonical"' in playground
    assert 'name="keywords"' in playground
    assert 'property="og:site_name"' in playground
    assert 'property="og:title"' in playground
    assert 'name="twitter:card"' in playground
    assert "application/ld+json" in playground
    assert '"@type": "WebApplication"' in playground
    assert "Local AI Agent Packet Generator" in playground
    assert "ariadne-loop-og.png" in playground
    assert 'hreflang="zh-CN"' in playground


def test_playground_contains_required_static_controls():
    playground = (ROOT / "docs" / "playground.html").read_text(encoding="utf-8")

    for element_id in [
        'id="preset"',
        'id="outputMode"',
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
    assert "agent-packet.md" in playground
    assert "Agent packet" in playground
    assert "Return JSON only" in playground
    assert "ariadne-loop check" in playground
    assert "造梦构建器" in playground
    assert "造梦师构建器" not in playground
    assert "先写清循环" in playground
    assert "presetRelease" in playground


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


def test_agent_recipes_are_linked_and_copyable():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_zh = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
    workflow = (ROOT / "docs" / "coding-agent-workflow.md").read_text(
        encoding="utf-8"
    )
    recipes = (ROOT / "docs" / "agent-recipes.md").read_text(encoding="utf-8")
    snapshot = (
        ROOT / "examples" / "codex-issue-repair-snapshot.json"
    ).read_text(encoding="utf-8")

    for doc in [readme, readme_zh]:
        assert "docs/agent-recipes.md" in doc
        assert "examples/codex-issue-repair-snapshot.json" in doc
        assert "ariadne-loop quickstart" in doc

    assert "ariadne-loop quickstart" in workflow
    assert "Codex Issue Repair" in recipes
    assert "PR Review Follow-Up" in recipes
    assert "Return the JSON report only" in recipes
    assert "Regression test fails before the fix" in snapshot


def test_generated_examples_do_not_contain_known_mojibake():
    generated_files = list((ROOT / "examples" / "generated").glob("*"))
    assert generated_files

    bad_tokens = ["\ufffd", "\u951b", "\u9286"]
    for path in generated_files:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for token in bad_tokens:
            assert token not in text, f"{path.name} contains mojibake token {token!r}"


def test_codex_skill_is_installable_from_readme():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_zh = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
    skill = (ROOT / "skills" / "ariadne-loop" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    for doc in [readme, readme_zh]:
        assert "install-skill-from-github.py" in doc
        assert "--repo zhangzeyu99-web/ariadne-loop" in doc
        assert "--path skills/ariadne-loop" in doc
        assert "--name ariadne-loop" in doc

    assert skill.startswith("---\n")
    assert "name: ariadne-loop" in skill
    assert "description:" in skill
    assert "short-description:" in skill
    assert "inspect -> act -> verify -> decide" in skill
    assert "ariadne-loop quickstart" in skill
    assert "ariadne-loop init" in skill
    assert "ariadne-loop from-issue" in skill
    assert "ariadne-loop supervise" in skill
    assert "https://zhangzeyu99-web.github.io/ariadne-loop/playground.html" in skill


def test_claude_code_command_is_documented_and_bounded():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_zh = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
    workflow = (ROOT / "docs" / "coding-agent-workflow.md").read_text(
        encoding="utf-8"
    )
    command = (ROOT / ".claude" / "commands" / "ariadne-loop.md").read_text(
        encoding="utf-8"
    )

    assert ".claude/commands/ariadne-loop.md" in readme
    assert "Claude Code slash command" in readme
    assert "Claude Code slash command" in readme_zh
    assert "/ariadne-loop" in workflow
    assert command.startswith("---\n")
    assert "allowed-tools:" in command
    assert "$ARGUMENTS" in command
    assert "inspect -> act -> verify -> decide" in command
    assert "do not install it automatically" in command
    assert "dangerously-skip-permissions" not in command
    assert '"status": "continue|stop|needs_human|rollback"' in command
