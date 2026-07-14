# Loop Governance Design

## Goal

Absorb three proven ideas from `cobusgreyling/loop-engineering` into Ariadne Loop: phased execution authority, mechanical stall detection, and an L0-L3 readiness assessment. The result must remain compatible with existing snapshots, loop JSON, report JSONL, and CLI commands.

## P0: Execution Policy

Snapshots may optionally declare:

```json
{
  "execution_policy": {
    "mode": "report_only|assisted|unattended",
    "allowed_effects": ["commit", "push"],
    "human_required_effects": ["release", "package publish"]
  }
}
```

`build_loop()` normalizes this into `loop.execution_policy`. When the field is absent, the generated loop uses `assisted` with no allowed effects, preserving the current behavior that external effects require a human.

- `report_only`: every detected external effect requires a human.
- `assisted`: only `allowed_effects` may proceed; all others require a human.
- `unattended`: declared `context.external_effects` may proceed except items in `human_required_effects`.
- `human_required_effects` always wins.
- An undeclared risky action always requires a human, including in unattended mode.

The supervisor reports which effects were requested, allowed, and blocked. The agent packet and natural-language control prompt state the active policy.

## P1: Circuit Breaker

The supervisor gains two checks using the existing report contract:

- Repeated failed verifier: keep the existing two-report rollback behavior.
- Stagnation: normalize volatile numbers, timestamps, paths, and whitespace in the latest evidence and next step. If the same report signature repeats three times, return `needs_human`.
- No progress: if three consecutive reports add no newly passed verifier and repeat the same next step, return `needs_human`.

No new report field is required. Existing JSONL remains valid.

## P2: Readiness Audit

`ariadne-loop audit --dir` remains a strict integrity check: malformed or stale Run Kits still exit `1`. Successful audits additionally return a 0-100 readiness score and level:

- `L0`: incomplete or invalid Run Kit.
- `L1`: valid Run Kit, report-only operation.
- `L2`: valid Run Kit with verifier evidence and supervised/allowlisted execution.
- `L3`: valid unattended policy, concrete allowlist, run evidence, and no unresolved supervision issue.

The score is evidence-based, not decorative. Required-file integrity, valid loop and reports, current decision, verifier evidence, execution policy, and actual run history contribute signals. L3 is capped unless unattended operation has both an allowlist and real reports.

## Public Surfaces

- `loops_assistant.core.build_loop()` accepts optional `execution_policy`.
- `loops_assistant.core.supervise_loop()` adds external-effect and circuit-breaker evidence to its decision output.
- `ariadne-loop audit --dir ... --format text|json` adds `score`, `level`, `assessment`, and `signals`.
- Builder adds a compact execution-policy section and includes it in Run Kit ZIP output.
- Existing commands and required report fields do not change.

## Verification

- Focused red/green tests for each behavior.
- Full `python -m pytest -q`.
- `python -m compileall loops_assistant`.
- Generate and audit a fresh quickstart Run Kit.
- Validate generated example loop.
- Run UTF-8/CJK output gates for Chinese public files.

