# Loop Governance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add execution authority, stall protection, and evidence-based L0-L3 Run Kit auditing without breaking existing Ariadne Loop inputs.

**Architecture:** Keep loop generation and supervision policy in `loops_assistant.core`; keep filesystem audit and CLI rendering in `loops_assistant.cli`. Extend the static Builder with the same JSON shape, while retaining the existing no-build-tool architecture.

**Tech Stack:** Python 3.11+, pytest, argparse, static HTML/CSS/JavaScript.

## Global Constraints

- Existing snapshots without `execution_policy` retain current external-effect blocking behavior.
- Existing report JSON field names and required fields remain unchanged.
- Do not add dependencies or a frontend build chain.
- Do not push, tag, release, deploy, or publish.
- Use one red-green test cycle per behavior.

---

### Task 1: Execution Policy Module

**Files:**
- Modify: `loops_assistant/core.py`
- Test: `tests/test_core.py`

**Interfaces:**
- Consumes: optional snapshot field `execution_policy`
- Produces: normalized `loop["execution_policy"]` and policy-aware `supervise_loop()` decisions

- [ ] **Step 1: Write failing tests**

Add tests proving that the default policy blocks push, assisted mode allows only explicit effects, human-required effects override the allowlist, and unattended mode allows only effects declared by the loop.

- [ ] **Step 2: Verify red**

Run: `python -m pytest tests/test_core.py -q`

Expected: the new policy assertions fail because `build_loop()` does not emit `execution_policy` and supervision blocks every external effect.

- [ ] **Step 3: Implement the minimal policy**

Add normalization and effect matching helpers. Preserve absent-field behavior. Include requested, allowed, and blocked effects in supervision decisions.

- [ ] **Step 4: Verify green**

Run: `python -m pytest tests/test_core.py -q`

Expected: all core tests pass.

### Task 2: Mechanical Circuit Breaker

**Files:**
- Modify: `loops_assistant/core.py`
- Test: `tests/test_core.py`

**Interfaces:**
- Consumes: existing normalized agent reports
- Produces: `needs_human` decisions with `circuit_breaker` equal to `stagnation` or `no_progress`

- [ ] **Step 1: Write failing tests**

Add one test with three semantically identical reports whose evidence differs only by volatile numbers, and one test with three reports that add no verifier coverage while repeating the same next step.

- [ ] **Step 2: Verify red**

Run: `python -m pytest tests/test_core.py -q`

Expected: Ariadne returns `continue` or budget exhaustion instead of a circuit-breaker reason.

- [ ] **Step 3: Implement stable signatures and no-progress detection**

Normalize timestamps, paths, line numbers, numbers, case, and whitespace. Check the breaker before absolute iteration budget and after verifier completion/external-effect policy.

- [ ] **Step 4: Verify green**

Run: `python -m pytest tests/test_core.py -q`

Expected: all core tests pass.

### Task 3: L0-L3 Readiness Audit

**Files:**
- Modify: `loops_assistant/cli.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: `_audit_run_kit()` integrity results, loop, reports, and expected decision
- Produces: `score`, `level`, `assessment`, and `signals` in text and JSON audit output

- [ ] **Step 1: Write failing tests**

Add tests proving an invalid kit is L0, a fresh valid report-only kit is L1, an assisted kit with evidence is L2, and an evidenced unattended kit with an allowlist is L3.

- [ ] **Step 2: Verify red**

Run: `python -m pytest tests/test_cli.py -q`

Expected: audit output lacks readiness fields and levels.

- [ ] **Step 3: Implement readiness scoring**

Use explicit signals for integrity, report history, verifier evidence, current supervision, and execution policy. Cap levels when mandatory evidence is absent.

- [ ] **Step 4: Verify green**

Run: `python -m pytest tests/test_cli.py -q`

Expected: all CLI tests pass.

### Task 4: Builder and Documentation

**Files:**
- Modify: `docs/playground.html`
- Modify: `docs/reports.html`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `docs/loop-spec.md`
- Modify: `tests/test_docs.py`

**Interfaces:**
- Consumes: the execution-policy JSON and readiness-level semantics from Tasks 1-3
- Produces: Builder controls, matching browser supervision, and short user documentation

- [ ] **Step 1: Write failing documentation assertions**

Require `execution_policy`, `report_only`, `assisted`, `unattended`, and `L0-L3` to appear in the relevant public surfaces.

- [ ] **Step 2: Verify red**

Run: `python -m pytest tests/test_docs.py -q`

Expected: new public-surface assertions fail.

- [ ] **Step 3: Update Builder and docs**

Add a compact mode selector plus allowed/human-required effect inputs. Update browser supervision to follow the same policy and breaker semantics. Add one minimal English and Chinese usage block.

- [ ] **Step 4: Verify green**

Run: `python -m pytest tests/test_docs.py -q`

Expected: all docs tests pass.

### Task 5: Full Verification

**Files:**
- Update generated examples only if their authoritative output changes.

**Interfaces:**
- Consumes: all completed tasks
- Produces: fresh proof that the repository and public examples remain valid

- [ ] **Step 1: Run all automated checks**

Run:

```powershell
python -m pytest -q
python -m compileall loops_assistant
python -m loops_assistant check --input examples\generated\openclaw-loop.json
```

Expected: zero failures and `valid`.

- [ ] **Step 2: Exercise a fresh Run Kit**

Generate a temporary quickstart directory, audit it in text and JSON modes, and confirm its decision matches reports.

- [ ] **Step 3: Run output quality gates**

Run the repository CJK gate against `README.zh-CN.md` and `docs/playground.html`.

- [ ] **Step 4: Inspect final diff**

Confirm every changed line belongs to execution policy, circuit breaking, readiness audit, tests, or their documentation. Leave the feature branch unpushed.

