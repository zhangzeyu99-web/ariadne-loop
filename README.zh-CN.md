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

可以先打开网页生成 snapshot：[Ariadne Loop Builder](https://zhangzeyu99-web.github.io/ariadne-loop/playground.html)。
如果要直接复制给 Codex 或 Claude Code，用这页开始：[Agent Recipes](docs/agent-recipes.md)。

一条命令生成完整 demo loop：

```bash
ariadne-loop quickstart --output .ariadne/quickstart
```

Codex skill 安装：

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo zhangzeyu99-web/ariadne-loop \
  --path skills/ariadne-loop \
  --name ariadne-loop
```

Claude Code slash command:

```bash
mkdir -p .claude/commands
curl -L https://raw.githubusercontent.com/zhangzeyu99-web/ariadne-loop/main/.claude/commands/ariadne-loop.md \
  -o .claude/commands/ariadne-loop.md
```

Then run:

```text
/ariadne-loop fix this failing issue without broad refactors
```

```bash
python -m pip install -e .
ariadne-loop init --preset release --output loop-snapshot.json
ariadne-loop write \
  --input loop-snapshot.json \
  --output loop-report.md \
  --format markdown
```

可用预设：

```bash
ariadne-loop init --preset bugfix --output bugfix-loop.json
ariadne-loop init --preset release --output release-loop.json
ariadne-loop init --preset refactor --output refactor-loop.json
ariadne-loop init --preset agent-handoff --output handoff-loop.json
```

也可以把 GitHub issue 正文转换成 snapshot：

```bash
ariadne-loop from-issue \
  --title "Fix stale generated examples" \
  --body-file issue.md \
  --output issue-loop.json
```

生成 JSON loop：

```bash
ariadne-loop make \
  --input examples/openclaw-snapshot.json \
  --output examples/generated/openclaw-loop.json \
  --format json
```

Codex issue repair 示例：

```bash
ariadne-loop make \
  --input examples/codex-issue-repair-snapshot.json \
  --output examples/generated/codex-issue-repair-agent-packet.md \
  --format markdown
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

接入 Codex/Claude Code 的完整流程见 [Coding Agent Workflow](docs/coding-agent-workflow.md)。
可复制的 agent recipes 见 [Agent Recipes](docs/agent-recipes.md)。
常见验证器模板见 [Verifier Recipes](docs/verifier-recipes.md)。
