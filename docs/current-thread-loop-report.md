# Loop Writing Assistant

## Clear Loop
- Name: 当前线程：增强 Loops Assistant Loop
- Goal: 基于高星 prompt、eval 和 harness 项目的结构，把 Loops Assistant 升级成能帮用户写清楚并持续护航 Loop 的助手，并测试、AI smoke、supervise 决策和 GitHub 发布验证
- Current State: 已有 make/check/report/write 命令和 GitHub 发布；本轮新增 supervise 命令、持续护航规则、JSONL 报告读取、BOM 兼容、schema 字段和发布验证
- Tightened Brief: 围绕“基于高星 prompt、eval 和 harness 项目的结构，把 Loops Assistant 升级成能帮用户写清楚并持续护航 Loop 的助手，并测试、AI smoke、supervise 决策和 GitHub 发布验证”运行一个有状态闭环：先读取真实上下文，再执行最小必要动作，用 verifier 逐项验证；验证失败就回滚或收窄，触碰外部状态前请求人工确认。

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
# 当前线程：增强 Loops Assistant Loop Agent Packet

## Goal
基于高星 prompt、eval 和 harness 项目的结构，把 Loops Assistant 升级成能帮用户写清楚并持续护航 Loop 的助手，并测试、AI smoke、supervise 决策和 GitHub 发布验证

## Current State
已有 make/check/report/write 命令和 GitHub 发布；本轮新增 supervise 命令、持续护航规则、JSONL 报告读取、BOM 兼容、schema 字段和发布验证

## Constraints
- 先写失败测试再实现
- 不把建议停在文档，要落到 CLI 和样例
- 不复制第三方项目内容，只借鉴结构
- 发布前必须跑完整测试、AI smoke、supervise 决策和远端读回

## Cycle
- `inspect`: 读取真实上下文、现有产物和上一轮状态，确认本轮只处理一个可验证目标 -> 本轮范围、已知证据、缺口和不做事项
- `act`: 围绕目标执行最小必要动作：基于高星 prompt、eval 和 harness 项目的结构，把 Loops Assistant 升级成能帮用户写清楚并持续护航 Loop 的助手，并测试、AI smoke、supervise 决策和 GitHub 发布验证 -> 本轮产物或改动清单
- `verify`: 运行或执行这些验证：pytest；compileall；output_quality_gate README.md；write 命令生成 current-thread-loop-report.md；Codex AI smoke 返回 valid report；supervise 根据 AI report 输出护航决策；GitHub 远端 main SHA 与本地一致 -> 逐项 verifier 的通过、失败或缺证据状态
- `decide`: 根据验证结果决定继续、停止、回滚或请求人工确认 -> 下一步动作和停止判断

## Verifiers
- `gate-1` (command): pytest
- `gate-2` (checklist): compileall
- `gate-3` (checklist): output_quality_gate README.md
- `gate-4` (checklist): write 命令生成 current-thread-loop-report.md
- `gate-5` (checklist): Codex AI smoke 返回 valid report
- `gate-6` (checklist): supervise 根据 AI report 输出护航决策
- `gate-7` (checklist): GitHub 远端 main SHA 与本地一致

## Stop Rules
- 所有 verifier 都有当前证据且通过时停止
- 同一 verifier 连续失败 2 次时停止并收窄问题
- 发现目标、输入或权限与当前上下文不一致时停止并请求确认
- 执行外部影响动作前停止并确认：commit、push

## Rollback
撤销本轮产物或保持原状态，记录失败证据，回到 inspect 步骤重新收窄范围

## Human Gates
- 需要改变外部状态、发布、发送、删除或付款前必须人工确认
- 风险等级为 medium，失败后不可直接扩大范围
- 外部影响动作完成后必须读回真实载体再报告

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

