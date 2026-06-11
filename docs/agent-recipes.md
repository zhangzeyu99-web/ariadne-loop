# Copy-Paste Agent Recipes

Use these when you want a coding agent to work in a bounded loop instead of
free-form chat. Each recipe has three parts:

- a snapshot source,
- an agent packet,
- a JSON report that Ariadne Loop can supervise.

## Codex Issue Repair

Use this when a GitHub issue describes a bug and you want Codex to repair it
without broad refactors.

```bash
ariadne-loop make \
  --input examples/codex-issue-repair-snapshot.json \
  --output examples/generated/codex-issue-repair-loop.json \
  --format json

ariadne-loop make \
  --input examples/codex-issue-repair-snapshot.json \
  --output examples/generated/codex-issue-repair-agent-packet.md \
  --format markdown
```

Copy this into Codex with the generated agent packet:

```text
Use the attached Ariadne Loop agent packet as the execution contract.

First inspect the issue, current branch, and relevant tests.
Then make the smallest fix that satisfies the verifiers.
Do not push, create a PR, or publish unless a human explicitly confirms.
At the end of the turn, return only the JSON report requested by the packet.
```

Expected report shape:

```json
{
  "action_id": "verify",
  "status": "continue",
  "evidence": [
    "Regression test failed before the fix and passed after the fix",
    "python -m pytest -q passed"
  ],
  "next_step": "decide whether to open a pull request",
  "passed_verifiers": ["gate-1", "gate-2"],
  "failed_verifiers": []
}
```

Then supervise:

```bash
ariadne-loop supervise \
  --loop examples/generated/codex-issue-repair-loop.json \
  --reports .ariadne/reports.jsonl \
  --output .ariadne/decision.json
```

## Release Readiness

Use this before tagging, publishing, or announcing a release.

```bash
ariadne-loop write \
  --input examples/release-readiness-snapshot.json \
  --output examples/generated/release-readiness-loop-report.md \
  --format markdown
```

Copy this instruction into a coding agent:

```text
Use the release readiness loop report as the source of truth.
Collect current evidence for every verifier.
Stop before any tag, GitHub release, package publish, or deploy action.
Return the JSON report only.
```

## Long Thread Handoff

Use this when a Codex or Claude Code session has too much history and the next
agent needs a compact state contract.

```bash
ariadne-loop init --preset agent-handoff --output .ariadne/handoff.json
ariadne-loop make --input .ariadne/handoff.json --output .ariadne/handoff-agent.md --format markdown
```

Copy this instruction into the next agent:

```text
Treat this handoff packet as the only trusted summary.
Read current files and remote state before acting.
If the packet conflicts with current state, report the mismatch and stop.
Return the JSON report only.
```

## PR Review Follow-Up

Use this when a pull request has review comments or failing checks.

Snapshot fields to fill:

```json
{
  "title": "PR review follow-up",
  "goal": "Address actionable PR feedback without changing unrelated behavior",
  "current_state": "PR has review comments and at least one failing check",
  "constraints": [
    "Only address review feedback that is still current",
    "Do not rewrite unrelated code",
    "Do not force-push without confirmation"
  ],
  "verifiers": [
    "Every changed line maps to a review comment or failing check",
    "Focused tests pass",
    "PR diff is read back before reporting completion"
  ],
  "external_effects": ["push"],
  "risk": "medium"
}
```

Agent instruction:

```text
Use this PR follow-up snapshot to generate an Ariadne Loop agent packet.
Inspect review comments and checks first.
Patch only the actionable feedback.
Return a JSON report with evidence and verifier ids.
```
