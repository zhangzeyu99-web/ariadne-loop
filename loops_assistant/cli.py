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
            parse_agent_report(Path(args.input).read_text(encoding="utf-8"))
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

        print(f"created Ariadne Loop quickstart in {output_dir}")
        print(f"agent packet: {files['agent_packet']}")
        print(f"decision: {files['decision']}")
        return 0

    return 2


def _quickstart_files(output_dir: Path) -> dict[str, Path]:
    return {
        "snapshot": output_dir / "snapshot.json",
        "loop": output_dir / "loop.json",
        "agent_packet": output_dir / "agent-packet.md",
        "loop_report": output_dir / "loop-report.md",
        "reports": output_dir / "reports.jsonl",
        "decision": output_dir / "decision.json",
    }


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
