# Loops Assistant

把线程、项目或任务的现状整理成可验证的 Loop Engineering 规范，并生成一份可以直接交给 AI 执行的任务包。

它解决的问题不是“写更长 prompt”，而是把 AI 每轮要做什么、用什么证据验证、什么时候停止、失败怎么回滚、什么时候必须找人确认写清楚。

## 能做什么

- 从 JSON 或 Markdown 现状记录生成 Loop 规范。
- 校验一份 Loop 是否真的包含 cycle、verifier、stop rule、rollback、budget 和 AI report contract。
- 生成 AI 可读的 Markdown packet，要求 AI 每轮只返回结构化 JSON。
- 校验 AI 返回的执行报告，避免 AI 用自然语言绕过闭环。

## 快速开始

```powershell
python -m pytest -q
python -m loops_assistant make --input examples/openclaw-snapshot.json --output examples/generated/openclaw-loop.json --format json
python -m loops_assistant make --input examples/openclaw-snapshot.json --output examples/generated/openclaw-agent-packet.md --format markdown
python -m loops_assistant check --input examples/generated/openclaw-loop.json
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

## 用 Codex 做 AI smoke test

本机已登录 Codex CLI 时，可以用生成的任务包做一次真实 AI 读取测试：

```powershell
python scripts/codex_smoke.py --packet examples/generated/openclaw-agent-packet.md --output tmp/ai-report.json
python -m loops_assistant report --input tmp/ai-report.json
```

这一步不要求 AI 完成真实运维任务，只验证任务包能被 AI 读懂，并能按 contract 返回可校验报告。
