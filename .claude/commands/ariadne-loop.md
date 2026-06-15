---
description: Build or run an Ariadne Loop packet for the current Claude Code task.
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(ariadne-loop:*), Bash(python:*), Bash(git status:*), Bash(git diff:*)
---

Use Ariadne Loop to turn this Claude Code task into a verifiable loop contract.

Task input:

```text
$ARGUMENTS
```

Follow this process:

1. Inspect the current repository state, task description, relevant files, tests,
   and recent diff before acting.
2. Create a focused loop snapshot with:
   - one concrete goal,
   - current state based on inspected evidence,
   - constraints and non-goals,
   - verifiers that can prove completion,
   - external effects,
   - risk level.
3. If `ariadne-loop` is already installed, write the snapshot under `.ariadne/`
   and run:

   ```bash
   ariadne-loop make --input .ariadne/<task>-snapshot.json --output .ariadne/<task>-loop.json --format json
   ariadne-loop make --input .ariadne/<task>-snapshot.json --output .ariadne/<task>-agent-packet.md --format markdown
   ```

4. If `ariadne-loop` is not installed, do not install it automatically. Write
   the snapshot and agent packet manually under `.ariadne/` using the same
   inspect -> act -> verify -> persist -> decide structure.
5. Execute only the smallest safe next action from the packet. Do not publish,
   push, send, delete, pay, or change external state unless the packet allows it
   and a human has explicitly approved.
6. Run or perform the verifiers named in the packet.
7. Persist the verifier evidence and next action in `.ariadne/` state files when
   the task has a run kit.
8. End with JSON only:

```json
{
  "action_id": "inspect|act|verify|persist|decide",
  "status": "continue|stop|needs_human|rollback",
  "evidence": ["specific evidence observed in this turn"],
  "next_step": "the next concrete action",
  "passed_verifiers": ["gate ids that passed in this turn"],
  "failed_verifiers": ["gate ids that failed in this turn"]
}
```
