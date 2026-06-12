# Reference Patterns

Ariadne Loop borrows structure from three mature open-source patterns. These projects are references, not dependencies.

## Prompt Libraries

High-quality prompt collections usually separate role, task, context, constraints, and output format. Ariadne keeps those sections but adds state, verification, rollback, and budget.

Useful pattern:

- name the task,
- include enough context,
- state constraints,
- require a structured output.

## Agent Harnesses

Agent runtimes such as graph-based or checkpointed systems show why a loop needs state. A loop should not depend on the agent remembering everything implicitly.

Useful pattern:

- current state,
- memory read/write rules,
- checkpoint or rollback point,
- explicit budget.

## Eval Harnesses

Eval systems are useful because they make success observable. Ariadne treats verifiers as the smallest useful eval layer for agent work.

Useful pattern:

- observable assertions,
- repeatable checks,
- failure messages that narrow the next action,
- reports that can be parsed by another tool.

## Loop Engineering Notes

The current public discussion around Loop Engineering frames the move as designing systems that prompt agents, rather than manually prompting agents one turn at a time. See Addy Osmani's June 2026 essay: <https://addyosmani.com/blog/loop-engineering/>.

Ariadne's practical rule is stricter:

> If a loop has no verifier, stop rule, rollback path, and report contract, it is still just a prompt.
