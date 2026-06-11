# Security

Ariadne Loop generates task contracts. It does not execute external actions by itself.

## Sensitive Data

Do not put secrets, API keys, private credentials, or customer data into public examples or issue reports.

## Agent Safety Boundary

Generated loop packets should still be reviewed before use on tasks that can:

- publish releases,
- send messages,
- delete or overwrite data,
- spend money,
- change production systems,
- expose private data.

Use `human_gates` for those actions and require read-back verification after they happen.

## Reporting Issues

Open a private security advisory on GitHub if you find a vulnerability that could cause secret exposure, unsafe generated instructions, or misleading validation.
