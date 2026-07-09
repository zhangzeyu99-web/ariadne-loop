# Coding Agent Workflow

Ariadne Loop is designed to sit just outside a coding agent. It does not run the
agent. It writes the loop contract, then checks the evidence that comes back.

For a zero-install start, use the browser builder:
<https://zhangzeyu99-web.github.io/ariadne-loop/playground.html>

For Claude Code, install the project slash command by copying
`.claude/commands/ariadne-loop.md` into your target repository. It exposes
`/ariadne-loop <task>` as a reusable prompt that generates a snapshot, packet,
verifier plan, and JSON report contract.

## 1. Start From a Preset

For a complete demo directory first:

```bash
ariadne-loop quickstart --output .ariadne/quickstart
```

This creates a Loop Run Kit with a snapshot, loop JSON, agent packet,
`PROGRESS.md`, `RUNBOOK.md`, `CONTROL.md`, `reports.jsonl`, and `decision.json`.
Use it to see the full shape before writing your own snapshot.

To continue the loop in plain language, generate the next agent prompt from the
current decision:

```bash
ariadne-loop prompt --dir .ariadne/quickstart
```

For real work, start from a preset:

```bash
ariadne-loop init --preset bugfix --output .ariadne/bugfix-snapshot.json
```

Edit the snapshot so it names the real issue, current state, constraints, and
verifiers.

Good verifiers are observable:

- the failing test now passes,
- the reproduction steps no longer fail,
- the quick start works from a fresh checkout,
- the generated artifact validates,
- the remote issue, PR, release, or page was read back.

If the work starts from a GitHub issue, keep the issue body in a local Markdown
file and generate the snapshot from it:

```bash
ariadne-loop from-issue \
  --title "Fix stale generated examples" \
  --body-file issue.md \
  --output .ariadne/issue-snapshot.json
```

## 2. Generate an Agent Packet

```bash
ariadne-loop make \
  --input .ariadne/bugfix-snapshot.json \
  --output .ariadne/agent-packet.md \
  --format markdown
```

Give `.ariadne/agent-packet.md` to Codex, Claude Code, or another coding agent.
The important part is the report contract at the end: every turn should come
back as JSON with concrete evidence and verifier ids.

## 3. Save Agent Reports

Append each agent report to a JSONL file:

```jsonl
{"action_id":"inspect","status":"continue","evidence":["read README.md and tests/test_cli.py"],"next_step":"patch failing CLI behavior","passed_verifiers":[],"failed_verifiers":[]}
{"action_id":"verify","status":"continue","evidence":["17 tests passed in 2.16s"],"next_step":"decide whether to push","passed_verifiers":["gate-1"],"failed_verifiers":[]}
```

## 4. Supervise the Loop

```bash
ariadne-loop make \
  --input .ariadne/bugfix-snapshot.json \
  --output .ariadne/bugfix-loop.json \
  --format json

ariadne-loop supervise \
  --loop .ariadne/bugfix-loop.json \
  --reports .ariadne/reports.jsonl \
  --output .ariadne/decision.json
```

If the files live in a complete Run Kit directory with `loop.json`,
`PROGRESS.md`, `reports.jsonl`, and `decision.json`, use:

```bash
ariadne-loop prompt --dir .ariadne/run-kit
```

The decision is explicit:

- `continue`: keep working.
- `stop`: all verifier gates have current evidence and no unresolved failed gate remains.
- `rollback`: the same verifier failed twice.
- `needs_human`: the next step touches an external-impact action or the agent
  requested help. Budget exhaustion before the gates pass also routes here.

## Copyable Agent Prompt

```text
Use this Ariadne Loop packet as your execution contract.

Follow repeated inspect -> act -> verify -> persist -> decide iterations.
Do not skip verifiers.
One verifiable change means one change per iteration, not one change total.
If the refreshed decision is continue, immediately start the next inspect iteration.
Only return stop when stop gates have current evidence. Pause and explain the reason on needs_human, rollback, or budget exhaustion.
Do not take external-impact actions unless the packet allows them and a human has approved.
At the end of this turn, return only the JSON report requested by the packet.
```
