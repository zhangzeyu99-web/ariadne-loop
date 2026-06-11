# Changelog

## 0.6.0 - 2026-06-11

- Added a static browser Loop Builder at `docs/playground.html`.
- Linked the builder from the GitHub Pages home page, README, Chinese README, and coding-agent workflow guide.
- Added docs checks for the hosted builder entry point.

## 0.5.0 - 2026-06-11

- Added `ariadne-loop from-issue` to convert a GitHub issue title and Markdown body into a loop snapshot.
- Added Markdown issue-section parsing for current state, constraints, acceptance criteria, evidence, and open questions.
- Added tests proving issue-derived snapshots can generate valid loop specs.
- Documented the issue-to-loop workflow.

## 0.4.0 - 2026-06-11

- Added `ariadne-loop init` to create editable starter snapshots.
- Added starter presets for bugfix, release, refactor, and agent handoff loops.
- Added overwrite protection for generated snapshot files.
- Added a coding-agent workflow guide for Codex, Claude Code, and similar tools.
- Updated the README and homepage quick start to begin from a generated snapshot.

## 0.3.0 - 2026-06-11

- Rebranded the project as Ariadne Loop.
- Added `ariadne-loop` as the primary CLI command while keeping `loops-assistant` as a compatibility alias.
- Added English-first public documentation, use cases, loop anatomy docs, and contributor guidance.
- Added local verification guidance for Python 3.11 and 3.12 users.
- Added release readiness and valid agent-report examples.
- Switched generated default loop text to English while preserving non-English user input.

## 0.2.0 - 2026-06-10

- Added the `write` command for loop-writing reports.
- Added clarity scoring and missing-input feedback.
- Added agent packet generation and agent-report validation.

## 0.1.0 - 2026-06-10

- Initial loop generation, validation, and CLI.
