# Use-Case Gallery

These are the cases Ariadne Loop is designed for.

## 1. Turn a Bug Report Into an Agent Loop

Input:

- failing behavior,
- known reproduction steps,
- files or modules likely involved,
- constraints,
- verifiers.

Output:

- an agent packet that inspects the bug first,
- a bounded fix action,
- a verifier list,
- rollback rules if the fix changes unrelated behavior.

Good verifiers:

- failing test now passes,
- related tests still pass,
- no unrelated file churn,
- reproduction steps no longer fail.

## 2. Resume a Long Coding-Agent Thread

Input:

- thread goal,
- current state,
- prior completed steps,
- blockers,
- next verifier.

Output:

- a clean loop report,
- missing inputs,
- an AI packet that does not require reading the whole old thread.

Good verifiers:

- linked artifact exists,
- command output matches expected result,
- remote state has been read back,
- stale assumptions are named.

## 3. Plan a Release With Safety Gates

Input:

- release target,
- artifacts,
- docs state,
- external effects such as tag, release, package publish.

Output:

- a loop that stops before irreversible actions,
- release verifiers,
- a rollback or no-publish rule.

Good verifiers:

- tests pass,
- generated examples validate,
- README quick start works,
- release notes match the version,
- GitHub release points to the intended commit.

## 4. Refactor a Large Codebase Incrementally

Input:

- target module,
- current boundaries,
- forbidden behavior changes,
- test commands.

Output:

- a loop that keeps each turn small,
- explicit non-goals,
- verifiers that prevent accidental behavior changes.

Good verifiers:

- focused unit tests pass,
- integration smoke passes,
- compile/lint passes,
- public APIs still import.

## 5. Make Contributor Tasks Reviewable

Input:

- issue title,
- desired outcome,
- acceptance criteria,
- files likely involved.

Output:

- a task packet a new contributor can follow,
- a report contract maintainers can quickly review.

Good verifiers:

- acceptance criteria linked to tests or screenshots,
- docs updated when behavior changes,
- no hidden manual steps.
