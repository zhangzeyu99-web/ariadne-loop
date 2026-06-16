# Project Optimization Roadmap

This roadmap keeps the next Ariadne Loop improvements visible without expanding the P0 change beyond the current release-quality surface.

## P0: Loop Run Kit

Status: implemented in the current P0 pass.

- Extend `ariadne-loop quickstart` into a Loop Run Kit generator.
- Keep the existing files and add `PROGRESS.md` plus `RUNBOOK.md`.
- Strengthen `agent-packet.md` so every turn reads progress and report state before acting.
- Keep the JSON report contract compatible.

## P1: Builder and Harness

Status: implemented in the current P1/P2 pass.

- Added a third Builder output mode: `Run Kit ZIP`.
- Generate initial `PROGRESS.md`, `RUNBOOK.md`, `reports.jsonl`, `decision.json`, and agent files from the browser.
- Added Harness fields for tools, official sources, browser verification, forbidden areas, and local secret-reading rules.
- Added source priority guidance: official docs and APIs first, then repo/tests/current files, then search, then model inference.
- Added cost strategy guidance: use stronger models for long-running design or repair loops, cheaper models for sync, formatting, and release checks.

## P2: Evidence UI and More Examples

Status: implemented in the current P1/P2 pass.

- Added real case packs for desktop app development, GitHub Pages publishing, bug repair, docs refactor, and OpenClaw scheduled work.
- Added a `reports.jsonl` visualization page for progress, passed verifiers, repeated failures, and next action.
- Added a read-only `ariadne-loop audit --dir <run-kit-dir>` command to check whether a run kit is complete and supervisable.

## Product Flow: Natural-Language Control

Status: implemented in the current product-flow pass.

- Added `CONTROL.md` to new Loop Run Kits so users can copy a plain-language continuation prompt.
- Added `ariadne-loop prompt --dir <run-kit-dir>` to generate the next prompt from the current `decision.json`.
- Updated Builder Run Kit ZIP, README, and workflow docs so the standard flow is: create kit, audit kit, generate prompt, run one verified agent turn, append report, supervise again.

## External Blocker

GitHub Pages is currently excluded from P0 acceptance because the repository is blocked by a GitHub account-level Actions disabled state. Repository settings already allow Actions and Pages, but workflow dispatch still returns `Actions has been disabled for this user`, and the public Pages URL remains 404 until GitHub restores the account capability.
