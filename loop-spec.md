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
| `cycle` | The `inspect -> act -> verify -> decide` loop. |
| `verifiers` | Observable checks that prove whether the turn worked. |
| `stop_rules` | Conditions for stopping, narrowing, or asking a human. |
| `rollback` | What to do when a verifier fails or scope is crossed. |
| `memory` | What to read and write each turn. |
| `budget` | Iteration and time limits. |
| `human_gates` | Actions that require explicit human confirmation. |
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
  "risk": "medium"
}
```

## Agent Report Contract

Every agent turn should return parseable JSON:

```json
{
  "action_id": "inspect",
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

- all four cycle steps,
- at least one verifier,
- stop rules,
- rollback,
- a positive budget,
- required report fields.
