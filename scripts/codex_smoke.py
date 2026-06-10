from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Send a generated agent packet to Codex with UTF-8 input."
    )
    parser.add_argument(
        "--packet",
        default="examples/generated/openclaw-agent-packet.md",
        help="Generated agent packet markdown.",
    )
    parser.add_argument(
        "--schema",
        default="schemas/agent-report.schema.json",
        help="JSON schema for the Codex final answer.",
    )
    parser.add_argument(
        "--output",
        default="tmp/ai-report.json",
        help="Where Codex should write the final report.",
    )
    args = parser.parse_args()

    packet_path = Path(args.packet)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    packet = packet_path.read_text(encoding="utf-8")
    command = [
        "codex",
        "exec",
        "--ephemeral",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "-c",
        'approval_policy="never"',
        "--output-schema",
        args.schema,
        "--output-last-message",
        str(output_path),
        "Read the agent packet below and return one valid JSON report for the next action. Do not run commands.",
    ]
    result = subprocess.run(
        command,
        input=packet,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

