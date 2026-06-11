---
name: ariadne-loop
description: Use when a user wants to turn a GitHub issue, rough task, release plan, refactor, bugfix, or long coding-agent thread into a verifiable Loop Engineering contract with inspect/act/verify/decide steps, human gates, rollback rules, and JSON agent reports.
metadata:
  short-description: Write verifiable loop specs for coding agents
---

# Ariadne Loop

Use this skill to turn vague agent work into a bounded loop contract. The goal
is not to make a longer prompt. The goal is to make the next agent turn
verifiable.

## When to Use

Use this skill when the user asks for any of these:

- a loop, agent loop, or Loop Engineering spec,
- a resumable handoff for Codex, Claude Code, or another coding agent,
- a GitHub issue converted into an executable agent task,
- release, refactor, bugfix, or documentation work that needs explicit gates,
- supervision rules for repeated agent reports.

## Preferred Workflow

1. Identify the source shape:
   - rough notes,
   - GitHub issue title and body,
   - release/refactor/bugfix request,
   - long thread handoff.
2. Create a snapshot JSON with:
   - `title`,
   - `goal`,
   - `current_state`,
   - `recent_progress`,
   - `constraints`,
   - `verifiers`,
   - `external_effects`,
   - `risk`.
3. Generate or write an agent packet that includes:
   - inspect -> act -> verify -> decide cycle,
   - concrete verifiers,
   - stop rules,
   - rollback behavior,
   - human gates for external effects,
   - JSON-only report contract.
4. If the Ariadne Loop CLI is installed, prefer using it:

   ```bash
   ariadne-loop init --preset bugfix --output loop-snapshot.json
   ariadne-loop write --input loop-snapshot.json --output loop-report.md --format markdown
   ariadne-loop make --input loop-snapshot.json --output loop.json --format json
   ariadne-loop check --input loop.json
   ```

5. If the work starts from a GitHub issue body:

   ```bash
   ariadne-loop from-issue \
     --title "Issue title" \
     --body-file issue.md \
     --output issue-loop.json
   ```

6. For running loops, ask the agent to append JSON reports to JSONL and use:

   ```bash
   ariadne-loop supervise \
     --loop loop.json \
     --reports reports.jsonl \
     --output decision.json
   ```

## If the CLI Is Not Installed

Do not block. Produce the snapshot JSON and the agent packet directly in the
response or in files. Tell the user they can use the browser builder:

```text
https://zhangzeyu99-web.github.io/ariadne-loop/playground.html
```

Use this report contract:

```json
{
  "action_id": "inspect|act|verify|decide",
  "status": "continue|stop|needs_human|rollback",
  "evidence": ["specific evidence observed in this turn"],
  "next_step": "the next concrete action",
  "passed_verifiers": ["gate ids that passed in this turn"],
  "failed_verifiers": ["gate ids that failed in this turn"]
}
```

## Verifier Rules

Prefer observable gates:

- command output,
- rendered page or screenshot readback,
- generated artifact exists and validates,
- remote GitHub issue, PR, release, or Pages output is read back,
- diff contains no unrelated churn,
- failing reproduction now passes.

Avoid weak gates:

- "looks good",
- "done",
- "agent says it completed",
- unverified screenshots,
- claims about remote state without readback.

## Human Gates

Require human confirmation before:

- `commit`,
- `push`,
- tag or release creation,
- package publish,
- deploy,
- deletion,
- sending external messages,
- payment or billing actions.

After any approved external effect, read back the real target before reporting
success.
