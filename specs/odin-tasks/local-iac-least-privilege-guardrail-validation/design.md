# Design — Local IaC Least-Privilege Guardrail Validation

## Repository shape
The `starter/` directory is a self-contained Python project using only the standard library:

- `README.md` provides setup and baseline commands;
- `docs/workload-contract.md` records the synthetic workload's required behavior;
- `infra/` defines and synthesizes a CloudFormation-compatible template;
- `policy/validate.py` implements a few unrelated local guardrails and an extension point;
- `tests/` checks determinism, resource wiring, and the existing guardrails.

## Starter-state design
The template contains a worker role, a private object bucket, and an encrypted queue. The worker's documented job is deliberately small, while its recorder-visible identity policy supplies the evidence needed for a permission audit. Existing validation covers unrelated invariants so a future correction cannot claim success merely because synthesis completed.

## Human boundary
KyJahn must independently compare the workload contract with the synthesized grant, identify the concrete risk, choose and implement the smallest least-privilege change, add decisive policy coverage, and run final verification. The starter does not contain that diagnosis, patch, or final test.

## Handoff verification
Before handoff, verify only that synthesis is deterministic, baseline tests pass, the intended inspection surfaces are present, and no solution artifact has been included.
