from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ._version import __version__
from .core import (
    build_loop,
    load_snapshot,
    parse_agent_report,
    render_loop_writing_report,
    render_agent_packet,
    snapshot_from_issue,
    starter_preset_names,
    starter_snapshot,
    supervise_loop,
    validate_loop,
    write_loop,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ariadne-loop",
        description=(
            "Ariadne Loop turns rough project context into verifiable "
            "Loop Engineering specs and AI execution packets."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"Ariadne Loop {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    make_parser = subparsers.add_parser("make", help="Generate a loop spec or AI packet.")
    make_parser.add_argument("--input", required=True, help="Thread or project snapshot file.")
    make_parser.add_argument("--output", required=True, help="Output file path.")
    make_parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="markdown",
        help="Output format.",
    )

    write_parser = subparsers.add_parser(
        "write", help="Generate a clear loop plus clarity review and AI packet."
    )
    write_parser.add_argument("--input", required=True, help="Rough loop snapshot file.")
    write_parser.add_argument("--output", required=True, help="Output file path.")
    write_parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="markdown",
        help="Output format.",
    )

    check_parser = subparsers.add_parser("check", help="Validate a loop spec JSON file.")
    check_parser.add_argument("--input", required=True, help="Loop spec JSON file.")

    report_parser = subparsers.add_parser(
        "report", help="Validate an AI agent JSON report."
    )
    report_parser.add_argument("--input", required=True, help="Agent report file.")

    init_parser = subparsers.add_parser(
        "init", help="Create an editable starter snapshot JSON file."
    )
    init_parser.add_argument(
        "--preset",
        choices=starter_preset_names(),
        default="bugfix",
        help="Starter snapshot preset.",
    )
    init_parser.add_argument("--output", required=True, help="Snapshot JSON output file.")
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the output file if it already exists.",
    )

    issue_parser = subparsers.add_parser(
        "from-issue", help="Create a snapshot from a GitHub issue title and body file."
    )
    issue_parser.add_argument("--title", required=True, help="Issue title.")
    issue_parser.add_argument("--body-file", required=True, help="Markdown issue body.")
    issue_parser.add_argument("--output", required=True, help="Snapshot JSON output file.")
    issue_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the output file if it already exists.",
    )

    supervise_parser = subparsers.add_parser(
        "supervise", help="Guard an ongoing loop using JSONL agent reports."
    )
    supervise_parser.add_argument("--loop", required=True, help="Loop spec JSON file.")
    supervise_parser.add_argument(
        "--reports", required=True, help="Agent report JSONL file."
    )
    supervise_parser.add_argument("--output", required=True, help="Decision JSON file.")

    quickstart_parser = subparsers.add_parser(
        "quickstart", help="Create a complete runnable demo loop in one directory."
    )
    quickstart_parser.add_argument(
        "--output",
        default=".ariadne/quickstart",
        help="Directory where quickstart files will be created.",
    )
    quickstart_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite quickstart files if they already exist.",
    )

    audit_parser = subparsers.add_parser(
        "audit", help="Read-only audit for a Loop Run Kit directory."
    )
    audit_parser.add_argument("--dir", required=True, help="Loop Run Kit directory.")
    audit_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Audit output format.",
    )

    args = parser.parse_args(argv)

    if args.command == "make":
        snapshot = load_snapshot(args.input)
        loop = build_loop(snapshot)
        errors = validate_loop(loop)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if args.format == "json":
            output_path.write_text(
                json.dumps(loop, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        else:
            output_path.write_text(render_agent_packet(loop), encoding="utf-8")
        print(str(output_path))
        return 0

    if args.command == "write":
        package = write_loop(load_snapshot(args.input))
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if args.format == "json":
            output_path.write_text(
                json.dumps(package, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        else:
            output_path.write_text(
                render_loop_writing_report(package),
                encoding="utf-8",
            )
        print(str(output_path))
        return 0

    if args.command == "check":
        loop = json.loads(Path(args.input).read_text(encoding="utf-8"))
        errors = validate_loop(loop)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        print("valid")
        return 0

    if args.command == "report":
        try:
            parse_agent_report(Path(args.input).read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print("valid")
        return 0

    if args.command == "init":
        output_path = Path(args.output)
        if output_path.exists() and not args.force:
            print(f"{output_path} already exists; pass --force to overwrite", file=sys.stderr)
            return 1
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(starter_snapshot(args.preset), ensure_ascii=False, indent=2)
            + "\n",
            encoding="utf-8",
        )
        print(str(output_path))
        return 0

    if args.command == "from-issue":
        output_path = Path(args.output)
        if output_path.exists() and not args.force:
            print(f"{output_path} already exists; pass --force to overwrite", file=sys.stderr)
            return 1
        body = Path(args.body_file).read_text(encoding="utf-8")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(
                snapshot_from_issue(args.title, body),
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(str(output_path))
        return 0

    if args.command == "supervise":
        loop = json.loads(Path(args.loop).read_text(encoding="utf-8"))
        reports = _load_jsonl(Path(args.reports))
        decision = supervise_loop(loop, reports)
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(str(output_path))
        return 0

    if args.command == "quickstart":
        output_dir = Path(args.output)
        files = _quickstart_files(output_dir)
        existing = [path for path in files.values() if path.exists()]
        if existing and not args.force:
            joined = ", ".join(str(path) for path in existing)
            print(f"quickstart files already exist: {joined}; pass --force to overwrite", file=sys.stderr)
            return 1

        output_dir.mkdir(parents=True, exist_ok=True)
        snapshot = {
            "title": "Quickstart bug repair",
            "goal": "Show how Ariadne Loop turns a bug report into a verifiable coding-agent packet",
            "current_state": "A bug report exists, but the next agent needs bounded instructions and proof gates",
            "recent_progress": ["Bug report captured", "Likely CLI files identified"],
            "constraints": [
                "Start by inspecting current files and tests",
                "Keep the repair scoped to the failing behavior",
                "Do not push or open a pull request without human confirmation",
            ],
            "verifiers": [
                "Regression test covers the reported bug",
                "python -m pytest -q passes",
            ],
            "external_effects": ["commit", "push", "pull request"],
            "risk": "medium",
            "harness": {
                "tools": ["python", "pytest", "git"],
                "official_sources": ["project README", "current repository files"],
                "browser_verification": [
                    "Use browser checks when the loop changes public pages"
                ],
                "forbidden_areas": [
                    "Do not tag, release, publish, or push without human confirmation"
                ],
                "local_secrets": "Do not read local secrets or private config unless the user explicitly asks.",
                "source_priority": [
                    "official docs/API",
                    "repo/tests/current files",
                    "search",
                    "model inference",
                ],
                "cost_strategy": [
                    "Use stronger models for hard design or repair turns",
                    "Use cheaper models for formatting, sync, and final checks",
                ],
            },
        }
        loop = build_loop(snapshot)
        package = write_loop(snapshot)
        reports = [
            {
                "action_id": "inspect",
                "status": "continue",
                "evidence": ["Read the bug report and identified likely CLI files"],
                "next_step": "write a focused regression test",
                "passed_verifiers": [],
                "failed_verifiers": [],
            },
            {
                "action_id": "verify",
                "status": "continue",
                "evidence": [
                    "Regression test covers the reported bug",
                    "python -m pytest -q passes",
                ],
                "next_step": "decide whether the loop can stop",
                "passed_verifiers": ["gate-1", "gate-2"],
                "failed_verifiers": [],
            },
        ]
        decision = supervise_loop(loop, reports)

        files["snapshot"].write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        files["loop"].write_text(
            json.dumps(loop, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        files["agent_packet"].write_text(render_agent_packet(loop), encoding="utf-8")
        files["loop_report"].write_text(
            render_loop_writing_report(package), encoding="utf-8"
        )
        files["reports"].write_text(
            "\n".join(json.dumps(report, ensure_ascii=False) for report in reports)
            + "\n",
            encoding="utf-8",
        )
        files["decision"].write_text(
            json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        files["progress"].write_text(
            _render_quickstart_progress(loop, reports, decision),
            encoding="utf-8",
        )
        files["runbook"].write_text(
            _render_quickstart_runbook(output_dir, loop),
            encoding="utf-8",
        )

        print(f"created Ariadne Loop quickstart Loop Run Kit in {output_dir}")
        print(f"agent packet: {files['agent_packet']}")
        print(f"runbook: {files['runbook']}")
        print(
            "next command: "
            f"ariadne-loop supervise --loop {files['loop']} "
            f"--reports {files['reports']} --output {files['decision']}"
        )
        print(f"decision: {files['decision']}")
        return 0

    if args.command == "audit":
        result = _audit_run_kit(Path(args.dir))
        text = (
            json.dumps(result, ensure_ascii=False, indent=2) + "\n"
            if args.format == "json"
            else _render_audit_text(result)
        )
        if result["ok"]:
            print(text, end="")
            return 0
        if args.format == "json":
            print(text, end="")
        else:
            print(text, end="", file=sys.stderr)
        return 1

    return 2


def _quickstart_files(output_dir: Path) -> dict[str, Path]:
    return {
        "snapshot": output_dir / "snapshot.json",
        "loop": output_dir / "loop.json",
        "agent_packet": output_dir / "agent-packet.md",
        "loop_report": output_dir / "loop-report.md",
        "reports": output_dir / "reports.jsonl",
        "decision": output_dir / "decision.json",
        "progress": output_dir / "PROGRESS.md",
        "runbook": output_dir / "RUNBOOK.md",
    }


def _render_quickstart_progress(
    loop: dict[str, object], reports: list[dict], decision: dict[str, object]
) -> str:
    passed = sorted(
        {
            gate
            for report in reports
            for gate in report.get("passed_verifiers", [])
        }
    )
    failed = sorted(
        {
            gate
            for report in reports
            for gate in report.get("failed_verifiers", [])
        }
    )
    latest = reports[-1] if reports else {}
    passed_lines = _markdown_lines(passed)
    failed_lines = _markdown_lines(failed)
    evidence_lines = _markdown_lines(latest.get("evidence", []))
    reasons = decision.get("reasons", [])

    return f"""# Loop Run Kit Progress

## Current Goal
{loop["goal"]}

## Completed
- Created `snapshot.json`, `loop.json`, `agent-packet.md`, `reports.jsonl`, and `decision.json`.
- Recorded {len(reports)} example agent reports.

## Next Step
{decision.get("next_action_id", latest.get("next_step", "inspect current state"))}

## Verifier Record
Passed:
{passed_lines}

Failed:
{failed_lines}

## Latest Evidence
{evidence_lines}

## Current Decision
- decision: {decision.get("decision", "continue")}
- reasons: {"; ".join(str(reason) for reason in reasons) if reasons else "None"}

## Blockers
- None in the generated quickstart. Add real blockers here before returning `needs_human`.
"""


def _render_quickstart_runbook(output_dir: Path, loop: dict[str, object]) -> str:
    return f"""# Loop Run Kit Runbook

Use this directory as a complete handoff package for one coding-agent loop.

## Files
- `snapshot.json`: editable task snapshot.
- `loop.json`: machine-checkable loop contract.
- `agent-packet.md`: instructions to hand to the coding agent.
- `PROGRESS.md`: current goal, latest evidence, next step, and blockers.
- `reports.jsonl`: one JSON report per agent turn.
- `decision.json`: latest supervise decision.

## Every Turn
1. Inspect: read `PROGRESS.md`, `reports.jsonl`, `loop.json`, and the real project state.
2. Act: make one verifiable change only.
3. Verify: run the listed verifier gates and collect concrete evidence.
4. Persist: update `PROGRESS.md` and append exactly one JSON object to `reports.jsonl`.
5. Decide: run:

```bash
ariadne-loop supervise --loop {output_dir / "loop.json"} --reports {output_dir / "reports.jsonl"} --output {output_dir / "decision.json"}
```

## Stop Rules
- Return `stop` when all verifiers pass with current evidence.
- Return `needs_human` when approval, missing access, or unclear product intent blocks the next turn.
- Return `rollback` when a verifier fails repeatedly or a change crosses a constraint.
- Do not push, publish, release, or open a pull request without human confirmation.

## Current Loop
- name: {loop["name"]}
- max_iterations: {loop["budget"]["max_iterations"]}
- max_minutes: {loop["budget"]["max_minutes"]}
"""


def _markdown_lines(values: object) -> str:
    if not isinstance(values, list) or not values:
        return "- None"
    return "\n".join(f"- {value}" for value in values)


def _load_jsonl(path: Path) -> list[dict]:
    reports: list[dict] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), 1
    ):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"line {line_number} is not a JSON object")
        reports.append(value)
    return reports


def _audit_run_kit(directory: Path) -> dict[str, object]:
    files = _quickstart_files(directory)
    required_files = {
        "snapshot": "snapshot.json",
        "loop": "loop.json",
        "agent_packet": "agent-packet.md",
        "loop_report": "loop-report.md",
        "reports": "reports.jsonl",
        "decision": "decision.json",
        "progress": "PROGRESS.md",
        "runbook": "RUNBOOK.md",
    }
    issues: list[str] = []
    for key, filename in required_files.items():
        if not files[key].exists():
            issues.append(f"missing {filename}")

    loop: dict[str, object] | None = None
    reports: list[dict] = []
    expected_decision: dict[str, object] | None = None
    actual_decision: dict[str, object] | None = None

    if files["loop"].exists():
        try:
            loaded_loop = json.loads(files["loop"].read_text(encoding="utf-8"))
            if not isinstance(loaded_loop, dict):
                issues.append("loop.json must contain a JSON object")
            else:
                loop = loaded_loop
                loop_errors = validate_loop(loop)
                issues.extend(f"loop.json: {error}" for error in loop_errors)
        except (json.JSONDecodeError, OSError) as exc:
            issues.append(f"loop.json: {exc}")

    if files["reports"].exists():
        try:
            for line_number, line in enumerate(
                files["reports"].read_text(encoding="utf-8-sig").splitlines(), 1
            ):
                if not line.strip():
                    continue
                try:
                    reports.append(parse_agent_report(line))
                except (json.JSONDecodeError, ValueError) as exc:
                    issues.append(f"reports.jsonl line {line_number}: {exc}")
        except OSError as exc:
            issues.append(f"reports.jsonl: {exc}")

    if files["decision"].exists():
        try:
            loaded_decision = json.loads(files["decision"].read_text(encoding="utf-8"))
            if not isinstance(loaded_decision, dict):
                issues.append("decision.json must contain a JSON object")
            else:
                actual_decision = loaded_decision
        except (json.JSONDecodeError, OSError) as exc:
            issues.append(f"decision.json: {exc}")

    if loop is not None:
        expected_decision = supervise_loop(loop, reports)
        if actual_decision is not None and actual_decision != expected_decision:
            issues.append("decision.json does not match current reports")

    text_checks = {
        "agent_packet": [
            "PROGRESS.md",
            "reports.jsonl",
            "one verifiable change",
            "Report Contract",
        ],
        "progress": ["Current Goal", "Next Step", "Verifier Record"],
        "runbook": [
            "reports.jsonl",
            "ariadne-loop supervise",
            "needs_human",
            "rollback",
        ],
    }
    for key, required_terms in text_checks.items():
        if not files[key].exists():
            continue
        text = files[key].read_text(encoding="utf-8")
        for term in required_terms:
            if term not in text:
                issues.append(f"{required_files[key]} missing {term}")

    return {
        "ok": not issues,
        "issues": issues,
        "directory": str(directory),
        "reports": len(reports),
        "expected_decision": expected_decision,
    }


def _render_audit_text(result: dict[str, object]) -> str:
    if result["ok"]:
        return (
            "run kit audit passed\n"
            f"reports: {result['reports']}\n"
            f"decision: {result.get('expected_decision', {}).get('decision', 'unknown')}\n"
        )
    issues = result.get("issues", [])
    lines = ["run kit audit failed", *[f"- {issue}" for issue in issues]]
    return "\n".join(lines) + "\n"
