# Orange Book Alignment

This note records how Ariadne Loop maps the Loop Engineering Orange Book and current first-hand research into product behavior.

## Sources Reviewed

- Loop Engineering Orange Book v260615, Chinese and English PDFs: <https://github.com/alchaincyf/loop-engineering-orange-book>
- Addy Osmani, "Loop Engineering", June 7 2026: <https://addyosmani.com/blog/loop-engineering/>
- Addy Osmani, "Agent Harness Engineering": <https://addyosmani.com/blog/agent-harness-engineering/>
- Anthropic, "Effective harnesses for long-running agents": <https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents>
- Anthropic, "Building effective agents": <https://www.anthropic.com/engineering/building-effective-agents>
- OpenAI Codex app Automations, Worktrees, and Best Practices docs: <https://developers.openai.com/codex/app/automations>
- Lenny's Newsletter / How I AI summary of Stripe Minions with Steve Kaliski: <https://www.lennysnewsletter.com/p/this-week-on-how-i-ai-how-stripe>

## Product Mapping

| Orange Book idea | Ariadne behavior |
| --- | --- |
| Prompt -> context -> harness -> loop stack | Ariadne writes the loop layer while preserving harness details as optional structured input. |
| Five moves: discover, handoff, verify, persist, schedule | Ariadne uses `inspect -> act -> verify -> persist -> decide`. |
| Six parts: automation, worktrees, skills, connectors, evaluator, memory | Generated loop JSON includes `loop_parts` and the agent packet prints them. |
| Independent evaluator | Verifiers, report JSON, repeated-failure rollback, and human gates prevent self-graded completion. |
| Memory must live outside context | Run Kit includes `PROGRESS.md`, `reports.jsonl`, and `decision.json`; `persist` is now a first-class cycle step. |
| Verification debt | `cost_controls.verification_debt` requires concrete verifier evidence before stop. |
| Comprehension rot | `cost_controls.comprehension_rot` requires changed-state notes a human can read back. |
| Token blowout | Budget plus one bounded target per turn caps runaway work. |
| Cognitive surrender | Human gates remain for scope changes, external effects, and judgment calls. |

## Design Decisions

- `persist` is required for new valid loop specs. Old snapshots remain compatible because `make`, `write`, Builder, and quickstart generate the new five-step cycle.
- Builder Run Kit ZIP now emits a complete loop contract with `state`, `memory`, `loop_parts`, `cost_controls`, `agent_contract`, and harness metadata.
- Reports viewer follows the same five-step action order as the CLI, so a partial `verify` turn routes to `persist` before `decide`.
- Ariadne stays dependency-light: no frontend build chain, no scheduler implementation, and no hidden automation runner. It writes run kits and supervision decisions; the outer harness or human chooses where the loop runs.

## Remaining Product Gap

Ariadne still does not create Codex/Claude automations directly. That is intentional for now: scheduler setup has environment-specific permissions and external effects. The correct next feature would be a read-only "scheduler plan" generator that tells the user how to install the loop in Codex Automations, Claude Code, GitHub Actions, or a local cron without doing it silently.
