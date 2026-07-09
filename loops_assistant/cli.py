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

    prompt_parser = subparsers.add_parser(
        "prompt", help="Print the next natural-language control prompt for a Run Kit."
    )
    prompt_parser.add_argument("--dir", required=True, help="Loop Run Kit directory.")
    prompt_parser.add_argument(
        "--lang",
        choices=["en", "zh"],
        default="en",
        help="Prompt language.",
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
        files["control"].write_text(
            _render_control_file(output_dir, loop, decision),
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
        print(f"next prompt: ariadne-loop prompt --dir {output_dir}")
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

    if args.command == "prompt":
        try:
            print(_render_next_control_prompt(Path(args.dir), args.lang))
        except (json.JSONDecodeError, OSError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
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
        "progress": output_dir / "PROGRESS.md",
        "runbook": output_dir / "RUNBOOK.md",
        "control": output_dir / "CONTROL.md",
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

Use this directory as a complete handoff package for a continuous coding-agent loop.

## Files
- `snapshot.json`: editable task snapshot.
- `loop.json`: machine-checkable loop contract.
- `agent-packet.md`: instructions to hand to the coding agent.
- `PROGRESS.md`: current goal, latest evidence, next step, and blockers.
- `reports.jsonl`: one JSON report per agent turn.
- `decision.json`: latest supervise decision.
- `CONTROL.md`: copyable natural-language control prompts.

## Every Turn
1. Inspect: read `PROGRESS.md`, `reports.jsonl`, `loop.json`, and the real project state.
2. Act: make one verifiable change only.
3. Verify: run the listed verifier gates and collect concrete evidence.
4. Persist: update `PROGRESS.md` and append exactly one JSON object to `reports.jsonl`.
5. Decide: run:

```bash
ariadne-loop supervise --loop {output_dir / "loop.json"} --reports {output_dir / "reports.jsonl"} --output {output_dir / "decision.json"}
```

## Loop Mode
- `one verifiable change` means one change per iteration, not one change total.
- If `decision.json` says `continue`, immediately start the next inspect -> act -> verify -> persist -> decide iteration.
- Do not summarize and stop after a single successful iteration unless the stop rules have current evidence.
- Stop only for `stop`, `needs_human`, `rollback`, or the loop budget.

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


def _render_control_file(
    output_dir: Path, loop: dict[str, object], decision: dict[str, object]
) -> str:
    next_prompt = _render_control_prompt(
        directory=output_dir,
        loop=loop,
        decision=decision,
        lang="en",
    )
    zh_prompt = _render_control_prompt(
        directory=output_dir,
        loop=loop,
        decision=decision,
        lang="zh",
    )
    return f"""# Natural Language Control

Use this file when you want to steer a coding agent in plain language instead of rebuilding the prompt by hand.

## Copy The Current Prompt

```bash
ariadne-loop prompt --dir {output_dir}
ariadne-loop prompt --dir {output_dir} --lang zh
```

## English

{next_prompt}

## 中文

{zh_prompt}

## Control Rules

- Point the agent at this Run Kit directory, not at scattered chat history.
- Ask for continuous execution until `stop`, `needs_human`, `rollback`, or budget exhaustion. Budget exhaustion is a pause, not proof that the goal is complete.
- Ask for one verifiable change per iteration.
- Require updates to `PROGRESS.md`, one appended JSON line in `reports.jsonl`, and a refreshed `decision.json`.
- If `decision.json` says `continue`, require the agent to begin the next iteration instead of summarizing as done.
- Use `needs_human` for missing access, unclear product intent, or external effects.
- Use `rollback` when the same verifier fails repeatedly or the change crosses a constraint.
"""


def _render_next_control_prompt(directory: Path, lang: str) -> str:
    files = _quickstart_files(directory)
    required = [files["loop"], files["decision"], files["progress"], files["reports"]]
    missing = [path.name for path in required if not path.exists()]
    if missing:
        raise ValueError(f"run kit missing files: {', '.join(missing)}")
    loop = json.loads(files["loop"].read_text(encoding="utf-8"))
    decision = json.loads(files["decision"].read_text(encoding="utf-8"))
    return _render_control_prompt(directory=directory, loop=loop, decision=decision, lang=lang)


def _render_control_prompt(
    directory: Path,
    loop: dict[str, object],
    decision: dict[str, object],
    lang: str,
) -> str:
    next_action = str(decision.get("next_action_id", "inspect"))
    decision_name = str(decision.get("decision", "continue"))
    reasons = decision.get("reasons", [])
    reason_text = "; ".join(str(reason) for reason in reasons) if isinstance(reasons, list) else str(reasons)
    goal = str(loop.get("goal", "complete the loop with current evidence"))
    directory_text = str(directory)

    if lang == "zh":
        if decision_name == "stop":
            return (
                f"这个 Loop Run Kit 可以停止。请读取 `{directory_text}` 中的 `PROGRESS.md`、"
                "`reports.jsonl` 和 `decision.json`，总结已通过的证据、剩余风险和是否需要人工收尾。"
                "不要继续改代码，除非发现证据缺口。"
            )
        if decision_name == "needs_human":
            return (
                f"暂停这个 Loop Run Kit，并向人类确认下一步。目录：`{directory_text}`。"
                f"原因：{reason_text or 'decision.json 要求人类确认'}。"
                "不要继续执行外部影响动作。"
            )
        if decision_name == "rollback":
            return (
                f"回滚或收窄这个 Loop Run Kit 的上一轮改动。目录：`{directory_text}`。"
                f"原因：{reason_text or 'decision.json 要求 rollback'}。"
                "先记录失败证据，再回到 inspect。"
            )
        return (
            f"继续执行这个 Loop Run Kit：`{directory_text}`。\n"
            f"目标：{goal}\n"
            f"下一步动作：{next_action}\n"
            "连续运行 inspect -> act -> verify -> persist -> decide；每轮只做一个可验证改动，不是总共只做一个。"
            "先读 `PROGRESS.md`、`reports.jsonl`、`decision.json`、`loop.json` 和真实项目状态。"
            "完成一轮后运行验证器，更新 `PROGRESS.md`，"
            "向 `reports.jsonl` 追加一行 JSON，再运行 `ariadne-loop supervise` 刷新 `decision.json`。"
            "如果刷新后仍是 `continue`，不要总结收工，立刻开始下一轮 inspect。"
            "只有 stop gate 有当前证据时才返回 `stop`；遇到 `needs_human`、`rollback` 或预算耗尽时暂停并说明原因。"
            "如果需要 push、release、deploy、delete、send 或权限不清，返回 `needs_human`。"
        )

    if decision_name == "stop":
        return (
            f"The loop can stop. Read `{directory_text}/PROGRESS.md`, `reports.jsonl`, "
            "and `decision.json`, then summarize the evidence, remaining risk, and any human handoff. "
            "Do not keep changing files unless you find missing evidence."
        )
    if decision_name == "needs_human":
        return (
            f"Pause this Loop Run Kit and ask a human for the next decision. Directory: `{directory_text}`. "
            f"Reason: {reason_text or 'decision.json requires human input'}. "
            "Do not continue external-impact actions."
        )
    if decision_name == "rollback":
        return (
            f"Rollback or narrow the previous turn for this Loop Run Kit. Directory: `{directory_text}`. "
            f"Reason: {reason_text or 'decision.json requests rollback'}. "
            "Record failing evidence, then return to inspect."
        )
    return (
        f"Continue this Loop Run Kit: `{directory_text}`.\n"
        f"Goal: {goal}\n"
        f"Next action: {next_action}\n"
        "Run repeated inspect -> act -> verify -> persist -> decide iterations. One verifiable change means one "
        "change per iteration, not one change total. Read `PROGRESS.md`, `reports.jsonl`, `decision.json`, "
        "`loop.json`, and the real project state first. After each iteration, run the verifiers, update "
        "`PROGRESS.md`, append exactly one JSON line to `reports.jsonl`, and run `ariadne-loop supervise` to "
        "refresh `decision.json`. If the refreshed decision is `continue`, immediately begin the next inspect "
        "iteration instead of summarizing as done. Return `stop` only when stop gates have current evidence; "
        "pause and explain the reason on `needs_human`, `rollback`, or budget exhaustion. "
        "Return `needs_human` before push, release, deploy, delete, send, or unclear permissions."
    )


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
        "control": "CONTROL.md",
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
        "control": [
            "Natural Language Control",
            "ariadne-loop prompt",
            "one verifiable change",
            "needs_human",
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
