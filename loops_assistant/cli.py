from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import (
    build_loop,
    load_snapshot,
    parse_agent_report,
    render_loop_writing_report,
    render_agent_packet,
    supervise_loop,
    validate_loop,
    write_loop,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="loops-assistant",
        description="Generate and validate Loop Engineering specs.",
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

    supervise_parser = subparsers.add_parser(
        "supervise", help="Guard an ongoing loop using JSONL agent reports."
    )
    supervise_parser.add_argument("--loop", required=True, help="Loop spec JSON file.")
    supervise_parser.add_argument(
        "--reports", required=True, help="Agent report JSONL file."
    )
    supervise_parser.add_argument("--output", required=True, help="Decision JSON file.")

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

    return 2


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
