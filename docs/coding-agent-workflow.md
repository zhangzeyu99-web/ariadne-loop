# Coding Agent Workflow

Ariadne Loop is designed to sit just outside a coding agent. It does not run the
agent. It writes the loop contract, then checks the evidence that comes back.

## 1. Start From a Preset

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

The decision is explicit:

- `continue`: keep working.
- `stop`: all verifiers passed or the budget is exhausted.
- `rollback`: the same verifier failed twice.
- `needs_human`: the next step touches an external-impact action or the agent
  requested help.

## Copyable Agent Prompt

```text
Use this Ariadne Loop packet as your execution contract.

Follow the inspect -> act -> verify -> decide cycle.
Do not skip verifiers.
Do not take external-impact actions unless the packet allows them and a human has approved.
At the end of this turn, return only the JSON report requested by the packet.
```
