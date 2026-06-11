# Contributing

Thanks for improving Ariadne Loop. The most useful contributions are practical and evidence-based.

## Good First Contributions

- Add a real loop snapshot under `examples/`.
- Add a generated output that shows what changed.
- Improve verifier wording for a common toolchain.
- Add an input adapter for another task source.
- Tighten docs where the quick start is unclear.

## Local Checks

Run these before opening a pull request:

```bash
python -m pip install -e .
python -m pytest -q
python -m compileall loops_assistant
ariadne-loop --version
```

If your change touches examples, also run:

```bash
ariadne-loop write \
  --input examples/release-readiness-snapshot.json \
  --output examples/generated/release-readiness-loop-report.md \
  --format markdown

ariadne-loop make \
  --input examples/release-readiness-snapshot.json \
  --output examples/generated/release-readiness-loop.json \
  --format json

ariadne-loop check --input examples/generated/release-readiness-loop.json
```

## Pull Request Shape

Keep PRs small. A good PR usually includes:

- the problem it solves,
- the snapshot or fixture that reproduces it,
- the verifier that proves it works,
- any docs that users need to understand it.

Avoid broad rewrites unless they remove a concrete maintenance problem.
