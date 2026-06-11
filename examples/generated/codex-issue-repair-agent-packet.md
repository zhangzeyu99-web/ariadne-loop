# Codex issue repair Loop Agent Packet

## Goal
Turn a GitHub bug report into a bounded Codex repair loop that ends only after the failing case and related checks pass

## Current State
A public issue describes a reproducible CLI failure. The repository builds locally, but no focused regression test exists yet.

## Constraints
- Start by reproducing or writing a regression test
- Keep the fix scoped to the failing CLI behavior
- Do not push, tag, or publish without human confirmation

## Cycle
- `inspect`: Read real context, existing artifacts, and previous state. Confirm this turn has one verifiable target. -> Turn scope, known evidence, gaps, and explicit non-goals
- `act`: Take the smallest useful action toward the goal: Turn a GitHub bug report into a bounded Codex repair loop that ends only after the failing case and related checks pass -> This turn's artifact or change list
- `verify`: Run or perform these verifiers: Regression test fails before the fix and passes after the fix; python -m pytest -q; python -m compileall loops_assistant; ariadne-loop check validates the generated loop JSON; git diff shows no unrelated file churn -> Pass, fail, or missing-evidence status for each verifier
- `decide`: Decide whether to continue, stop, rollback, or ask for human confirmation based on verifier results. -> Next action and stop decision

## Verifiers
- `gate-1` (command): Regression test fails before the fix and passes after the fix
- `gate-2` (command): python -m pytest -q
- `gate-3` (checklist): python -m compileall loops_assistant
- `gate-4` (checklist): ariadne-loop check validates the generated loop JSON
- `gate-5` (checklist): git diff shows no unrelated file churn

## Stop Rules
- Stop when every verifier has current evidence and passes.
- Stop and narrow the problem after the same verifier fails twice.
- Stop and ask for confirmation when the goal, input, or permissions do not match the current context.
- Ask for confirmation before external-impact actions: commit, push, pull request

## Rollback
Revert this turn's output or keep the prior state, record the failing evidence, then return to inspect with a narrower scope.

## Human Gates
- Ask for human confirmation before changing external state, publishing, sending, deleting, or paying.
- Risk is medium; do not expand scope after failure.
- After an external-impact action, read back the real target before reporting success.

## Budget
- max_iterations: 3
- max_minutes: 60

## Report Contract
Return JSON only. Do not add prose outside the JSON.

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
