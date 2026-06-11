import json
import subprocess
import sys
import tomllib
from pathlib import Path

from loops_assistant import __version__


ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str):
    return subprocess.run(
        [sys.executable, "-m", "loops_assistant", *args],
        text=True,
        capture_output=True,
        check=False,
    )


def test_cli_version_uses_public_project_name():
    result = run_cli("--version")

    assert result.returncode == 0
    assert "Ariadne Loop" in result.stdout


def test_project_version_metadata_stays_in_sync():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    result = run_cli("--version")

    assert pyproject["project"]["version"] == __version__
    assert result.stdout.strip() == f"Ariadne Loop {__version__}"


def test_cli_generates_json_and_markdown_packets(tmp_path):
    input_path = tmp_path / "thread.json"
    json_output = tmp_path / "loop.json"
    markdown_output = tmp_path / "agent.md"
    input_path.write_text(
        json.dumps(
            {
                "title": "Terminology extraction",
                "goal": "Extract evidence-backed terms from a language pack and announcement copy",
                "current_state": "A local script extracted candidates; Codex still needs to verify them",
                "recent_progress": ["Candidate packet generated"],
                "constraints": ["Do not add terms without source evidence"],
                "verifiers": ["Each new term traces back to a source row"],
            }
        ),
        encoding="utf-8",
    )

    json_result = run_cli(
        "make",
        "--input",
        str(input_path),
        "--output",
        str(json_output),
        "--format",
        "json",
    )
    markdown_result = run_cli(
        "make",
        "--input",
        str(input_path),
        "--output",
        str(markdown_output),
        "--format",
        "markdown",
    )

    assert json_result.returncode == 0, json_result.stderr
    assert markdown_result.returncode == 0, markdown_result.stderr

    loop = json.loads(json_output.read_text(encoding="utf-8"))
    packet = markdown_output.read_text(encoding="utf-8")

    assert loop["name"] == "Terminology extraction Loop"
    assert loop["verifiers"]
    assert "Return JSON only" in packet
    assert "Do not add terms without source evidence" in packet


def test_generated_examples_match_current_cli(tmp_path):
    generated_cases = [
        (
            "make",
            ROOT / "examples" / "release-readiness-snapshot.json",
            "release-readiness-loop.json",
            "json",
        ),
        (
            "write",
            ROOT / "examples" / "release-readiness-snapshot.json",
            "release-readiness-loop-report.md",
            "markdown",
        ),
        (
            "make",
            ROOT / "examples" / "release-readiness-snapshot.json",
            "release-readiness-agent-packet.md",
            "markdown",
        ),
        (
            "make",
            ROOT / "examples" / "openclaw-snapshot.json",
            "openclaw-loop.json",
            "json",
        ),
        (
            "make",
            ROOT / "examples" / "openclaw-snapshot.json",
            "openclaw-agent-packet.md",
            "markdown",
        ),
        (
            "make",
            ROOT / "examples" / "codex-issue-repair-snapshot.json",
            "codex-issue-repair-loop.json",
            "json",
        ),
        (
            "make",
            ROOT / "examples" / "codex-issue-repair-snapshot.json",
            "codex-issue-repair-agent-packet.md",
            "markdown",
        ),
    ]

    for command, source, generated_name, output_format in generated_cases:
        output_path = tmp_path / generated_name
        result = run_cli(
            command,
            "--input",
            str(source),
            "--output",
            str(output_path),
            "--format",
            output_format,
        )

        assert result.returncode == 0, result.stderr
        assert output_path.read_text(encoding="utf-8") == (
            ROOT / "examples" / "generated" / generated_name
        ).read_text(encoding="utf-8")

    decision_output = tmp_path / "openclaw-decision.json"
    decision_result = run_cli(
        "supervise",
        "--loop",
        str(ROOT / "examples" / "generated" / "openclaw-loop.json"),
        "--reports",
        str(ROOT / "examples" / "openclaw-reports.jsonl"),
        "--output",
        str(decision_output),
    )

    assert decision_result.returncode == 0, decision_result.stderr
    assert decision_output.read_text(encoding="utf-8") == (
        ROOT / "examples" / "generated" / "openclaw-decision.json"
    ).read_text(encoding="utf-8")


def test_cli_init_creates_snapshot_that_write_can_use(tmp_path):
    snapshot_path = tmp_path / "snapshot.json"
    report_path = tmp_path / "report.md"

    init_result = run_cli(
        "init",
        "--preset",
        "agent-handoff",
        "--output",
        str(snapshot_path),
    )
    write_result = run_cli(
        "write",
        "--input",
        str(snapshot_path),
        "--output",
        str(report_path),
        "--format",
        "markdown",
    )

    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    report = report_path.read_text(encoding="utf-8")

    assert init_result.returncode == 0, init_result.stderr
    assert write_result.returncode == 0, write_result.stderr
    assert snapshot["title"] == "Agent handoff loop"
    assert snapshot["verifiers"]
    assert "Agent handoff loop Loop" in report
    assert "Return JSON only" in report


def test_cli_init_does_not_overwrite_without_force(tmp_path):
    snapshot_path = tmp_path / "snapshot.json"
    snapshot_path.write_text('{"title": "keep me"}\n', encoding="utf-8")

    result = run_cli(
        "init",
        "--preset",
        "bugfix",
        "--output",
        str(snapshot_path),
    )

    assert result.returncode == 1
    assert "already exists" in result.stderr
    assert json.loads(snapshot_path.read_text(encoding="utf-8"))["title"] == "keep me"


def test_cli_from_issue_creates_checkable_snapshot(tmp_path):
    issue_body = tmp_path / "issue.md"
    snapshot_path = tmp_path / "snapshot.json"
    loop_path = tmp_path / "loop.json"
    issue_body.write_text(
        """
## Current State
The quick start still requires users to write JSON by hand.

## Constraints
- Keep the CLI dependency-free.
- Do not require a GitHub token.

## Acceptance Criteria
- A generated snapshot can be edited by a user.
- The generated loop passes ariadne-loop check.
""",
        encoding="utf-8",
    )

    from_issue_result = run_cli(
        "from-issue",
        "--title",
        "Add starter snapshots",
        "--body-file",
        str(issue_body),
        "--output",
        str(snapshot_path),
    )
    make_result = run_cli(
        "make",
        "--input",
        str(snapshot_path),
        "--output",
        str(loop_path),
        "--format",
        "json",
    )
    check_result = run_cli("check", "--input", str(loop_path))

    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))

    assert from_issue_result.returncode == 0, from_issue_result.stderr
    assert make_result.returncode == 0, make_result.stderr
    assert check_result.returncode == 0, check_result.stderr
    assert snapshot["title"] == "Add starter snapshots"
    assert "dependency-free" in snapshot["constraints"][0]
    assert "generated loop passes" in " ".join(snapshot["verifiers"])


def test_cli_check_rejects_invalid_loop(tmp_path):
    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text(
        json.dumps({"version": "1.0", "goal": "Missing loop gates"}),
        encoding="utf-8",
    )

    result = run_cli("check", "--input", str(invalid_path))

    assert result.returncode == 1
    assert "verifier" in result.stderr


def test_cli_report_validates_agent_json_report(tmp_path):
    report_path = tmp_path / "agent-report.md"
    report_path.write_text(
        """```json
{
  "action_id": "verify",
  "status": "continue",
  "evidence": ["gate-1 passed"],
  "next_step": "run decide"
}
```""",
        encoding="utf-8",
    )

    result = run_cli("report", "--input", str(report_path))

    assert result.returncode == 0
    assert "valid" in result.stdout


def test_agent_report_example_matches_public_schema_contract():
    schema = json.loads(
        (ROOT / "schemas" / "agent-report.schema.json").read_text(encoding="utf-8")
    )
    report = json.loads(
        (ROOT / "examples" / "agent-report.valid.json").read_text(encoding="utf-8")
    )

    assert set(schema["required"]).issubset(report)
    assert report["action_id"] in schema["properties"]["action_id"]["enum"]
    assert report["status"] in schema["properties"]["status"]["enum"]
    assert isinstance(report["evidence"], list) and report["evidence"]
    assert isinstance(report["passed_verifiers"], list)
    assert isinstance(report["failed_verifiers"], list)

    result = run_cli(
        "report",
        "--input",
        str(ROOT / "examples" / "agent-report.valid.json"),
    )

    assert result.returncode == 0, result.stderr


def test_cli_write_outputs_human_readable_loop_report(tmp_path):
    input_path = tmp_path / "rough.json"
    output_path = tmp_path / "loop-report.md"
    input_path.write_text(
        json.dumps(
            {
                "title": "Current thread",
                "goal": "Keep improving Ariadne Loop using public project evidence",
                "current_state": "make, check, report, and supervise commands already exist",
                "constraints": ["Write tests first", "Do not stop at advice"],
                "verifiers": ["pytest", "AI smoke", "GitHub remote readback"],
                "external_effects": ["commit", "push"],
            }
        ),
        encoding="utf-8",
    )

    result = run_cli(
        "write",
        "--input",
        str(input_path),
        "--output",
        str(output_path),
        "--format",
        "markdown",
    )

    assert result.returncode == 0, result.stderr
    report = output_path.read_text(encoding="utf-8")
    assert "# Ariadne Loop Report" in report
    assert "Current thread Loop" in report
    assert "Clarity Score" in report
    assert "Agent Packet" in report


def test_cli_supervise_outputs_guardrail_decision(tmp_path):
    loop_path = tmp_path / "loop.json"
    reports_path = tmp_path / "reports.jsonl"
    output_path = tmp_path / "decision.json"
    snapshot_path = tmp_path / "snapshot.json"
    snapshot_path.write_text(
        json.dumps(
            {
                "title": "Release guardrail",
                "goal": "Keep running and publish only after verification",
                "current_state": "Waiting for verification",
                "verifiers": ["pytest", "GitHub remote readback"],
                "external_effects": ["push"],
            }
        ),
        encoding="utf-8",
    )
    subprocess.run(
        [
            sys.executable,
            "-m",
            "loops_assistant",
            "make",
            "--input",
            str(snapshot_path),
            "--output",
            str(loop_path),
            "--format",
            "json",
        ],
        check=True,
    )
    reports_path.write_text(
        json.dumps(
            {
                "action_id": "decide",
                "status": "continue",
                "evidence": ["pytest passed"],
                "next_step": "push to GitHub",
                "passed_verifiers": ["gate-1"],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_cli(
        "supervise",
        "--loop",
        str(loop_path),
        "--reports",
        str(reports_path),
        "--output",
        str(output_path),
    )

    assert result.returncode == 0, result.stderr
    decision = json.loads(output_path.read_text(encoding="utf-8"))
    assert decision["decision"] == "needs_human"
    assert decision["next_action_id"] == "decide"


def test_cli_supervise_accepts_utf8_bom_jsonl(tmp_path):
    loop_path = tmp_path / "loop.json"
    reports_path = tmp_path / "reports.jsonl"
    output_path = tmp_path / "decision.json"
    loop_path.write_text(
        json.dumps(
            {
                "version": "1.0",
                "name": "BOM Loop",
                "goal": "Handle Windows logs",
                "context": {"external_effects": []},
                "cycle": [
                    {"id": "inspect", "instruction": "inspect"},
                    {"id": "act", "instruction": "act"},
                    {"id": "verify", "instruction": "verify"},
                    {"id": "decide", "instruction": "decide"},
                ],
                "verifiers": [{"id": "gate-1", "instruction": "pytest"}],
                "stop_rules": ["stop when done"],
                "rollback": {"action": "rollback"},
                "budget": {"max_iterations": 3},
                "agent_contract": {
                    "required_fields": [
                        "action_id",
                        "status",
                        "evidence",
                        "next_step",
                    ]
                },
            }
        ),
        encoding="utf-8",
    )
    reports_path.write_bytes(
        b"\xef\xbb\xbf"
        + json.dumps(
            {
                "action_id": "verify",
                "status": "continue",
                "evidence": ["pytest passed"],
                "next_step": "decide",
                "passed_verifiers": ["gate-1"],
                "failed_verifiers": [],
            }
        ).encode("utf-8")
        + b"\n"
    )

    result = run_cli(
        "supervise",
        "--loop",
        str(loop_path),
        "--reports",
        str(reports_path),
        "--output",
        str(output_path),
    )

    assert result.returncode == 0, result.stderr
    decision = json.loads(output_path.read_text(encoding="utf-8"))
    assert decision["decision"] == "stop"


def test_cli_quickstart_creates_complete_demo(tmp_path):
    output_dir = tmp_path / "quickstart"

    result = run_cli("quickstart", "--output", str(output_dir))

    assert result.returncode == 0, result.stderr
    expected_files = [
        "snapshot.json",
        "loop.json",
        "agent-packet.md",
        "loop-report.md",
        "reports.jsonl",
        "decision.json",
    ]
    for name in expected_files:
        assert (output_dir / name).exists(), name

    loop = json.loads((output_dir / "loop.json").read_text(encoding="utf-8"))
    decision = json.loads((output_dir / "decision.json").read_text(encoding="utf-8"))
    packet = (output_dir / "agent-packet.md").read_text(encoding="utf-8")

    assert loop["name"] == "Quickstart bug repair Loop"
    assert decision["decision"] == "stop"
    assert "Return JSON only" in packet
    assert "created Ariadne Loop quickstart" in result.stdout


def test_cli_quickstart_does_not_overwrite_without_force(tmp_path):
    output_dir = tmp_path / "quickstart"
    output_dir.mkdir()
    (output_dir / "snapshot.json").write_text('{"title": "keep"}\n', encoding="utf-8")

    result = run_cli("quickstart", "--output", str(output_dir))

    assert result.returncode == 1
    assert "already exist" in result.stderr
    assert json.loads((output_dir / "snapshot.json").read_text(encoding="utf-8"))[
        "title"
    ] == "keep"
