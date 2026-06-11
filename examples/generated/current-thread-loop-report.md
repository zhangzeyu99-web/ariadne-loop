# Ariadne Loop Report

## Clear Loop
- Name: Ariadne Loop public launch Loop
- Goal: Turn the first working loop CLI into a public open-source project that a developer can understand, run, supervise, and contribute to in under ten minutes
- Current State: The core generator, writer, report validator, and supervise command exist; the repository needs stronger naming, public documentation, generated examples, metadata, and distribution hooks
- Tightened Brief: Run a stateful loop around "Turn the first working loop CLI into a public open-source project that a developer can understand, run, supervise, and contribute to in under ten minutes": inspect real context, take the smallest useful action, verify each gate, then stop, continue, rollback, or ask for human confirmation before changing external state.

## Clarity Score
- Score: 100/100
- goal_specificity: strong
- state_grounding: strong
- verifier_strength: strong
- constraint_quality: strong
- stop_safety: strong
- ai_contract: strong

## Missing Inputs
- None

## Borrowed Structures
- Prompt pattern: role, task, context, constraints, output_contract
- Harness pattern: state, tools, memory, checkpoints, budget
- Eval pattern:
- loop has inspect/act/verify/decide cycle
- each verifier has observable evidence
- stop and rollback are explicit
- agent report is machine-checkable JSON

## Agent Packet
# Ariadne Loop public launch Loop Agent Packet

## Goal
Turn the first working loop CLI into a public open-source project that a developer can understand, run, supervise, and contribute to in under ten minutes

## Current State
The core generator, writer, report validator, and supervise command exist; the repository needs stronger naming, public documentation, generated examples, metadata, and distribution hooks

## Constraints
- Keep the compatibility command for existing users
- Do not add heavy runtime dependencies
- Do not publish before generated examples and metadata updates are committed
- Do not hide external-impact actions behind automation

## Cycle
- `inspect`: Read real context, existing artifacts, and previous state. Confirm this turn has one verifiable target. -> Turn scope, known evidence, gaps, and explicit non-goals
- `act`: Take the smallest useful action toward the goal: Turn the first working loop CLI into a public open-source project that a developer can understand, run, supervise, and contribute to in under ten minutes -> This turn's artifact or change list
- `verify`: Run or perform these verifiers: pytest；python -m compileall loops_assistant；README quick start works；generated examples validate；supervise produces a decision from JSONL reports；GitHub repo metadata is updated -> Pass, fail, or missing-evidence status for each verifier
- `decide`: Decide whether to continue, stop, rollback, or ask for human confirmation based on verifier results. -> Next action and stop decision

## Verifiers
- `gate-1` (command): pytest
- `gate-2` (checklist): python -m compileall loops_assistant
- `gate-3` (checklist): README quick start works
- `gate-4` (checklist): generated examples validate
- `gate-5` (checklist): supervise produces a decision from JSONL reports
- `gate-6` (checklist): GitHub repo metadata is updated

## Stop Rules
- Stop when every verifier has current evidence and passes.
- Stop and narrow the problem after the same verifier fails twice.
- Stop and ask for confirmation when the goal, input, or permissions do not match the current context.
- Ask for confirmation before external-impact actions: commit、push、GitHub repository rename、GitHub release

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

