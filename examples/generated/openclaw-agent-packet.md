# OpenClaw 每日健康监控 Loop Agent Packet

## Goal
每天检查 Gateway、cron、备份和 doctor，只报告可操作异常

## Current State
Gateway 自启动已修复，备份由 OpenClaw 自己执行

## Constraints
- SecretRefs 迁移单独开任务
- 不直接改安全体系
- 只修确定的执行问题

## Cycle
- `inspect`: Read real context, existing artifacts, and previous state. Confirm this turn has one verifiable target. -> Turn scope, known evidence, gaps, and explicit non-goals
- `act`: Take the smallest useful action toward the goal: 每天检查 Gateway、cron、备份和 doctor，只报告可操作异常 -> This turn's artifact or change list
- `verify`: Run or perform these verifiers: Gateway 端口；cron ok；backup verify；doctor 无 error -> Pass, fail, or missing-evidence status for each verifier
- `decide`: Decide whether to continue, stop, rollback, or ask for human confirmation based on verifier results. -> Next action and stop decision

## Verifiers
- `gate-1` (readback): Gateway 端口
- `gate-2` (checklist): cron ok
- `gate-3` (readback): backup verify
- `gate-4` (readback): doctor 无 error

## Stop Rules
- Stop when every verifier has current evidence and passes.
- Stop and narrow the problem after the same verifier fails twice.
- Stop and ask for confirmation when the goal, input, or permissions do not match the current context.

## Rollback
Revert this turn's output or keep the prior state, record the failing evidence, then return to inspect with a narrower scope.

## Human Gates
- Ask for human confirmation before changing external state, publishing, sending, deleting, or paying.

## Budget
- max_iterations: 4
- max_minutes: 90

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
