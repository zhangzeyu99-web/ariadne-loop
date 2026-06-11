# Verifier Recipes

Copy these sections into a snapshot when you need a concrete starting point.
Each recipe is written for coding-agent loops that need evidence before a task
counts as done.

## Python Package Release Loop

Goal:

```text
Prepare and publish a Python package release without shipping stale docs,
broken examples, or mismatched version metadata.
```

Constraints:

- Do not publish until tests, generated examples, and README quick start pass.
- Do not create tags, releases, or package uploads before human confirmation.
- Do not change public API behavior during release cleanup.

Verifiers:

- `python -m pytest -q` passes.
- `python -m compileall <package>` passes.
- `python -m pip install -e .` installs the intended version.
- CLI `--version` matches `pyproject.toml`, changelog, and release tag.
- README quick start works from the current checkout.
- GitHub release points to the intended commit after publishing.

Human gates:

- Confirm before `git tag`.
- Confirm before GitHub release creation.
- Confirm before package registry upload.

Example agent report:

```json
{
  "action_id": "verify",
  "status": "continue",
  "evidence": [
    "python -m pytest -q: 21 passed",
    "ariadne-loop --version: Ariadne Loop 0.7.0",
    "README quick start generated tmp/v060-loop.json and check returned valid"
  ],
  "next_step": "ask for human confirmation before creating the release tag",
  "passed_verifiers": ["gate-1", "gate-2", "gate-3", "gate-4", "gate-5"],
  "failed_verifiers": []
}
```

## Frontend Bugfix Loop

Goal:

```text
Fix a reproduced frontend bug while keeping layout, accessibility, and existing
flows stable.
```

Constraints:

- Do not rewrite unrelated components.
- Do not introduce a new UI framework for a narrow bug.
- Keep text inside its container on mobile and desktop.
- Preserve existing route and keyboard behavior unless the issue requires a change.

Verifiers:

- The original reproduction no longer fails.
- A browser smoke test covers the fixed path.
- Desktop and mobile screenshots show no obvious overlap or blank state.
- Console output has no new page errors.
- Related unit or component tests pass.
- Diff contains no unrelated formatting churn.

Human gates:

- Confirm before changing product copy that affects user-visible promises.
- Confirm before adding a dependency.
- Confirm before changing persistent data shape or network behavior.

Example agent report:

```json
{
  "action_id": "verify",
  "status": "continue",
  "evidence": [
    "Reproduction path opened /playground.html and output JSON rendered",
    "Preset switch to refactor updated title and verifier count",
    "Screenshot at 1365x900 showed no overlapping form or output text"
  ],
  "next_step": "run the same smoke path on a narrow viewport",
  "passed_verifiers": ["gate-1", "gate-2", "gate-3"],
  "failed_verifiers": []
}
```

## Documentation Refresh Loop

Goal:

```text
Refresh project documentation so a new user can understand the purpose, install
the tool, run a first example, and find the next workflow without reading old
internal notes.
```

Constraints:

- Do not keep internal planning notes in public docs.
- Do not claim CI, package publishing, or external integrations that are not live.
- Keep examples runnable from the current repository state.
- Prefer one clear first path over a long list of options.

Verifiers:

- README quick start commands still work.
- All newly linked files exist.
- Search finds no stale internal launch notes.
- Changelog mentions the user-facing change.
- Remote README readback contains the new entry after push.

Human gates:

- Confirm before deleting historical docs that might be user-facing.
- Confirm before changing the project name or public positioning.

Example agent report:

```json
{
  "action_id": "verify",
  "status": "continue",
  "evidence": [
    "README links docs/playground.html and docs/coding-agent-workflow.md",
    "stale internal planning-marker search returned no public doc matches",
    "GitHub Contents API readback contains ariadne-loop from-issue"
  ],
  "next_step": "push the docs refresh and read back GitHub Pages",
  "passed_verifiers": ["gate-1", "gate-2", "gate-3", "gate-4"],
  "failed_verifiers": []
}
```

## GitHub Issue Triage Loop

Goal:

```text
Turn a GitHub issue into an executable agent loop with acceptance criteria,
constraints, and a stop decision.
```

Constraints:

- Do not assume the issue body is current without reading repository state.
- Do not call external APIs if the task only requires text-in/text-out parsing.
- Preserve user-provided acceptance criteria as verifier candidates.
- Ask for human confirmation before closing the issue or pushing changes.

Verifiers:

- `ariadne-loop from-issue` generates snapshot JSON from the issue title and body.
- The generated snapshot keeps constraints and acceptance criteria.
- `ariadne-loop make --format json` creates a loop spec.
- `ariadne-loop check` returns `valid`.
- If implementation is completed, the issue is closed with a comment naming the release or commit.

Human gates:

- Confirm before changing labels, assignees, or milestones on someone else's issue.
- Confirm before closing an issue if the evidence is incomplete.
- Confirm before pushing implementation changes.

Example agent report:

```json
{
  "action_id": "verify",
  "status": "continue",
  "evidence": [
    "issue title: Add a GitHub issue to loop snapshot adapter",
    "from-issue generated tmp/issue-snapshot.json",
    "ariadne-loop check tmp/issue-loop.json returned valid"
  ],
  "next_step": "implement the parser and link docs before closing the issue",
  "passed_verifiers": ["gate-1", "gate-2", "gate-3", "gate-4"],
  "failed_verifiers": []
}
```
