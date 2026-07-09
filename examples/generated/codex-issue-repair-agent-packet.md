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
- `persist`: Write this turn's evidence, verifier results, state change, and next action to durable memory. -> Updated PROGRESS.md, reports.jsonl entry, or equivalent durable state
- `decide`: Decide whether to continue, stop, rollback, or ask for human confirmation based on verifier results. -> Next action and stop decision

## Loop Parts
- automation: Define the trigger, cadence, or wake-up condition that discovers work without a manual prompt.
- isolation: Use worktrees or an equivalent boundary when parallel agents could touch the same files.
- skills: Put repeatable project knowledge in reusable instructions instead of retyping a long prompt each turn.
- connectors: List external systems the loop may read or update; keep filesystem-only loops explicit when there are none.
- evaluator: Keep the maker away from the checker: verifier evidence must be reviewable by a separate pass or human.
- memory: Persist progress on disk or in an external tracker; do not rely on the chat context as memory.

## Verifiers
- `gate-1` (command): Regression test fails before the fix and passes after the fix
- `gate-2` (command): python -m pytest -q
- `gate-3` (checklist): python -m compileall loops_assistant
- `gate-4` (checklist): ariadne-loop check validates the generated loop JSON
- `gate-5` (checklist): git diff shows no unrelated file churn

## Harness
- No extra harness was supplied. Use the repo, current files, and listed verifiers as the source of truth.

## Cost Controls
- verification debt: Do not accept self-graded completion; require concrete verifier evidence before stop.
- comprehension rot: Keep summaries and changed-state notes current so a human can still explain what changed.
- token blowout: Use one bounded target per turn, max iterations, and explicit stop rules to cap runaway work.
- cognitive surrender: Keep human gates for scope changes, external effects, and judgment calls the loop cannot own.

## Operating State
- At the start of every turn, read `PROGRESS.md`, `reports.jsonl`, and the current project state before acting.
- Run repeated loop iterations when the user asks to execute a Run Kit. `One verifiable change` means one change per iteration, not one change total.
- Work on one verifiable change per iteration. Do not batch unrelated fixes into one report.
- Persist verifier evidence, state changes, and next action before deciding whether the loop continues.
- If the refreshed decision is `continue`, immediately start the next inspect iteration unless a human gate, rollback, or budget limit blocks progress.
- Return `stop` only when the stop rules have current evidence; do not stop just because one useful change passed.
- If the same verifier fails in consecutive turns, return `rollback` or `needs_human` instead of retrying blindly.

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
  "action_id": "inspect|act|verify|persist|decide",
  "status": "continue|stop|needs_human|rollback",
  "evidence": ["specific evidence observed in this turn"],
  "next_step": "the next concrete action",
  "passed_verifiers": ["gate ids that passed in this turn"],
  "failed_verifiers": ["gate ids that failed in this turn"]
}
```
