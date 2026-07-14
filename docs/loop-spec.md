# Loop Spec Anatomy

Ariadne Loop generates a small, explicit contract for coding agents and other AI assistants.

## Required Fields

| Field | Purpose |
| --- | --- |
| `version` | Spec version for future migrations. |
| `name` | Human-readable loop name. |
| `goal` | The outcome the loop is trying to reach. |
| `context` | Current state, evidence, constraints, risk, and external effects. |
| `state` | Progress and open questions carried between turns. |
| `cycle` | The `inspect -> act -> verify -> persist -> decide` loop. |
| `verifiers` | Observable checks that prove whether the turn worked. |
| `stop_rules` | Conditions for stopping, narrowing, or asking a human. |
| `rollback` | What to do when a verifier fails or scope is crossed. |
| `memory` | What to read and write each turn. |
| `loop_parts` | Orange Book primitives: automation, isolation, skills, connectors, evaluator, and memory. |
| `cost_controls` | Guardrails for verification debt, comprehension rot, token blowout, and cognitive surrender. |
| `budget` | Iteration and time limits. |
| `human_gates` | Actions that require explicit human confirmation. |
| `execution_policy` | Execution mode plus allowed and human-required external effects. |
| `agent_contract` | Required JSON report shape for the agent. |

## Minimal Snapshot

```json
{
  "title": "Fix flaky checkout flow",
  "goal": "Find and fix the checkout E2E flake without changing payment behavior",
  "current_state": "CI fails in checkout.spec.ts after shipping address entry",
  "constraints": ["Do not touch payment provider code"],
  "verifiers": ["checkout.spec.ts passes", "unit tests pass", "no payment API changes"],
  "external_effects": ["pull request"],
  "execution_policy": {
    "mode": "assisted",
    "allowed_effects": ["commit", "push"],
    "human_required_effects": ["pull request", "release"]
  },
  "risk": "medium"
}
```

## Execution Policy

- `report_only`: every external effect requires confirmation.
- `assisted`: only `allowed_effects` may run without asking.
- `unattended`: declared external effects may run except `human_required_effects`.
- `human_required_effects` always wins, and undeclared external effects always require a human.

Existing snapshots without `execution_policy` behave like assisted mode with an empty allowlist.

## Circuit Breaker

Supervision returns `needs_human` when the same normalized attempt repeats three times (`stagnation`) or three reports repeat the same next step without new verifier evidence (`no_progress`). Repeated failed verifier IDs still return `rollback` after two reports.

## Audit Levels

- `L0`: incomplete, invalid, or stale Run Kit.
- `L1`: valid for report-only operation.
- `L2`: verifier evidence supports supervised execution.
- `L3`: an unattended allowlist, completed verifier evidence, and a current decision support bounded unattended execution.

## Agent Report Contract

Every agent turn should return parseable JSON:

```json
{
  "action_id": "persist",
  "status": "continue",
  "evidence": ["checkout.spec.ts fails at shipping address wait"],
  "next_step": "inspect the address form readiness condition"
}
```

Allowed statuses:

- `continue`
- `stop`
- `needs_human`
- `rollback`

## Validation Rules

`ariadne-loop check` rejects prompt-only plans. A valid loop must include:

- all five cycle steps,
- at least one verifier,
- stop rules,
- rollback,
- a positive budget,
- required report fields.
