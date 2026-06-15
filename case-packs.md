# Ariadne Loop Case Packs

Use these snapshots as starting points for common long-running agent work. Copy one into a project, edit the real state, then build a run kit:

```bash
ariadne-loop make --input examples/desktop-app-loop-snapshot.json --output loop.json --format json
ariadne-loop quickstart --output .ariadne/run-kit
ariadne-loop audit --dir .ariadne/run-kit
```

## Desktop App Development

- Snapshot: [desktop-app-loop-snapshot.json](../examples/desktop-app-loop-snapshot.json)
- Use when a desktop app needs UI, packaging, and smoke-test evidence before handoff.

## GitHub Pages Publishing

- Snapshot: [github-pages-publish-snapshot.json](../examples/github-pages-publish-snapshot.json)
- Use when a static site must be checked locally and then verified after Pages publishes.

## Bug Repair

- Snapshot: [bug-repair-loop-snapshot.json](../examples/bug-repair-loop-snapshot.json)
- Use when there is a known failure and the agent must stay inside a small repair boundary.

## Documentation Refactor

- Snapshot: [docs-refactor-loop-snapshot.json](../examples/docs-refactor-loop-snapshot.json)
- Use when docs need restructuring without breaking links or losing examples.

## OpenClaw Scheduled Work

- Snapshot: [openclaw-scheduled-loop-snapshot.json](../examples/openclaw-scheduled-loop-snapshot.json)
- Use when recurring automation needs evidence, stop rules, and human gates.

