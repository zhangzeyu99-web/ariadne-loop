# Reference Patterns

检索时间：2026-06-10。

这些项目不是依赖项，只作为结构参考：

| Project | Stars observed | Useful pattern for Loops Assistant |
| --- | ---: | --- |
| [f/prompts.chat](https://github.com/f/prompts.chat) | 163,511 | Prompt 条目强调 role、task、context、constraints、output format，适合转成 Loop 的说明层。 |
| [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) | 22,080 | 把 prompt/agent/RAG 放进本地 eval、断言和 CI，适合转成 Loop 的 verifier 和 report check。 |
| [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | 34,350 | 低层 agent 编排强调长期、有状态、可恢复，适合转成 Loop 的 state、checkpoint、budget。 |
| [openai/evals](https://github.com/openai/evals) | 18,648 | 把 LLM 系统行为写成 benchmark/eval registry，适合转成 Loop 的测试用例和断言。 |
| [EleutherAI/lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) | 12,906 | 统一评测 harness，适合提醒 Loop 不只看输出，还要看任务集、指标和可重复运行方式。 |

落到本项目里的规则：

- Prompt pattern：role、task、context、constraints、output_contract。
- Harness pattern：state、tools、memory、checkpoints、budget。
- Eval pattern：cycle 存在、verifier 有外部证据、stop/rollback 明确、AI report 可机器校验。

