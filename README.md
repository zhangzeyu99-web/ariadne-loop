# Loops Assistant

把线程、项目或任务的现状整理成可验证的 Loop Engineering 规范，并生成一份可以直接交给 AI 执行的任务包。

它解决的问题不是“写更长 prompt”，而是把 AI 每轮要做什么、用什么证据验证、什么时候停止、失败怎么回滚、什么时候必须找人确认写清楚。

## 能做什么

- 从 JSON 或 Markdown 现状记录生成 Loop 规范。
- 把粗糙想法改写成更清楚的 Loop Writing Report，包含清晰度评分、缺口问题和 AI 执行包。
- 校验一份 Loop 是否真的包含 cycle、verifier、stop rule、rollback、budget 和 AI report contract。
- 生成 AI 可读的 Markdown packet，要求 AI 每轮只返回结构化 JSON。
- 校验 AI 返回的执行报告，避免 AI 用自然语言绕过闭环。
- 护航持续运行的 Loop：读取每轮 AI report，判断继续、停止、回滚或请求人工确认。

## 快速开始

```powershell
python -m pytest -q
python -m loops_assistant make --input examples/openclaw-snapshot.json --output examples/generated/openclaw-loop.json --format json
python -m loops_assistant make --input examples/openclaw-snapshot.json --output examples/generated/openclaw-agent-packet.md --format markdown
python -m loops_assistant check --input examples/generated/openclaw-loop.json
python -m loops_assistant write --input examples/current-thread-snapshot.json --output examples/generated/current-thread-loop-report.md --format markdown
python -m loops_assistant supervise --loop examples/generated/openclaw-loop.json --reports examples/openclaw-reports.jsonl --output examples/generated/openclaw-decision.json
```

把 `examples/generated/openclaw-agent-packet.md` 的内容交给 AI，它需要按下面结构返回：

```json
{
  "action_id": "inspect|act|verify|decide",
  "status": "continue|stop|needs_human|rollback",
  "evidence": ["specific evidence observed in this turn"],
  "next_step": "the next concrete action"
}
```

校验 AI 返回：

```powershell
python -m loops_assistant report --input tmp/ai-report.json
```

## 输入格式

推荐输入 JSON：

```json
{
  "title": "OpenClaw 每日健康监控",
  "goal": "每天检查 Gateway、cron、备份和 doctor，只报告可操作异常",
  "current_state": "Gateway 自启动已修复，备份由 OpenClaw 自己执行",
  "recent_progress": ["日备份试跑 OK", "doctor 无 error"],
  "constraints": ["SecretRefs 迁移单独开任务"],
  "verifiers": ["Gateway 端口", "cron ok", "backup verify", "doctor 无 error"],
  "external_effects": [],
  "risk": "low"
}
```

也可以输入 Markdown，工具会做轻量提取；严肃交付建议用 JSON，因为 verifier 和约束更明确。

## 什么算有效 Loop

一份有效 Loop 至少要有：

- 明确目标和当前状态。
- `inspect -> act -> verify -> decide` 四步 cycle。
- 至少一个 verifier，而且 verifier 必须能产生外部证据。
- stop rules，说明什么时候结束、什么时候停下来找人。
- rollback，说明验证失败后怎么退回。
- budget，限制轮次和时间。
- agent contract，约束 AI 返回结构化报告。

缺少 verifier 或 stop rule 的内容只算 prompt，不算 Loop。

## 写清楚 Loop

`write` 命令会输出一份面向人的报告：

- Clear Loop：目标、当前状态和收紧后的 brief。
- Clarity Score：目标、状态、验证器、约束、停止规则、AI contract 的评分。
- Missing Inputs：还缺哪些信息，尤其是 verifier、当前状态和权限边界。
- Borrowed Structures：把 prompt 项目的结构、harness 项目的状态管理、eval 项目的断言合成一张写 Loop 的清单。
- Agent Packet：可以直接贴给 AI 执行的任务包。

本项目参考的开源结构记录在 `docs/reference-patterns.md`。

## 用 Codex 做 AI smoke test

本机已登录 Codex CLI 时，可以用生成的任务包做一次真实 AI 读取测试：

```powershell
python scripts/codex_smoke.py --packet examples/generated/openclaw-agent-packet.md --output tmp/ai-report.json
python -m loops_assistant report --input tmp/ai-report.json
```

这一步不要求 AI 完成真实运维任务，只验证任务包能被 AI 读懂，并能按 contract 返回可校验报告。

## 持续护航

持续跑 Loop 时，不应该让 AI 自己决定无限继续。`supervise` 命令读取 Loop JSON 和每轮 AI report 的 JSONL 日志，输出护航决策：

- `continue`：继续下一步。
- `stop`：预算耗尽或所有 verifier 已通过。
- `rollback`：同一 verifier 连续失败，需要回滚或收窄。
- `needs_human`：AI 自报需要人、下一步触碰 `commit/push/send/delete/payment` 等外部影响动作，或 Loop 本身无效。

用于护航的 AI report 必须带 `passed_verifiers` 和 `failed_verifiers`，没有通过或失败项时填空数组：

```json
{
  "action_id": "verify",
  "status": "continue",
  "evidence": ["pytest passed"],
  "next_step": "push to GitHub",
  "passed_verifiers": ["gate-1"],
  "failed_verifiers": []
}
```

这个项目不自动执行外部动作；它只给出护航决策，让外层 harness 或人类接管下一步。
