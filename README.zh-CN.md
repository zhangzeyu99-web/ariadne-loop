# Ariadne Loop

Ariadne Loop 是一个 Loop Engineering 写作工具。它把项目现状、线程上下文、GitHub issue 或粗略任务想法整理成可验证的 loop spec，并生成可以交给 AI agent 执行的任务包。

它不是 prompt 模板库。它解决的是：

- AI 每轮到底 inspect 什么；
- act 的范围怎么收紧；
- verifier 用什么证据证明通过；
- 什么时候继续、停止、回滚或找人确认；
- agent 每轮必须返回什么结构化报告。

## 为什么叫 Ariadne

Ariadne 的意象是一根穿过迷宫的线。一个好 loop 也应该这样：让 AI 在复杂上下文里知道自己该读什么、做什么、怎么验、什么时候停。

## 快速开始

```bash
python -m pip install -e .
ariadne-loop write \
  --input examples/release-readiness-snapshot.json \
  --output examples/generated/release-readiness-loop-report.md \
  --format markdown
```

生成 JSON loop：

```bash
ariadne-loop make \
  --input examples/openclaw-snapshot.json \
  --output examples/generated/openclaw-loop.json \
  --format json
```

校验 loop：

```bash
ariadne-loop check --input examples/generated/openclaw-loop.json
```

校验 agent 返回：

```bash
ariadne-loop report --input examples/agent-report.valid.json
```

## 适合场景

- 把一段很长的 Codex/Claude Code 线程整理成可恢复的执行协议。
- 把 GitHub issue 改写成有验证器和停止条件的 agent 任务。
- 写发布、重构、排障、资料整理这类需要多轮推进的 loop。
- 让 contributor 明确“什么证据算完成”。

## 不适合场景

- 没有 verifier 的纯创意 prompt。
- 不能读回真实结果的任务。
- 需要无限 token、隐藏凭据或不可控外部副作用的任务。

## 开发

```bash
python -m pytest -q
python -m compileall loops_assistant
```

贡献说明见 [CONTRIBUTING.md](CONTRIBUTING.md)。
