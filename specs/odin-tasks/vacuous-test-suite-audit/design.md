# Design — Vacuous Test Suite Audit

## Intent
Create a small synthetic Python module whose written behavior contract is meaningful enough to audit, while its initial pytest coverage is superficially credible but logically insufficient.

## Repository shape
- `README.md` — neutral setup and baseline-run instructions; no diagnosis.
- `docs/behavior.md` — the intended behavior contract.
- `src/` — small production module containing one bounded seeded defect.
- `tests/` — initial weak pytest suite that passes.
- optional `scripts/` — deterministic local setup/baseline helper.

## Starter-state design
The seeded defect must be observable through the documented contract and ordinary execution, but the recorder-visible repository must not label it as a defect or describe its fix. The weak suite should exercise relevant code paths while using assertions that can pass even when the documented outcome is wrong. Avoid cartoonishly empty tests, unconditional `assert True`, or comments that reveal the trick.

## Human boundary
During TaskRecorder, KyJahn must independently:
- identify why the existing assertions are not proving the contract;
- replace them with meaningful checks;
- demonstrate failure on the defective build;
- apply the smallest corrective production change;
- demonstrate the strengthened suite passes.

The starter environment may not pre-create those final checks or the repair.

## Verification before handoff
The builder/reviewer may verify only:
- setup works;
- the baseline weak suite passes;
- the documented behavior and implementation are genuinely inconsistent;
- no answer key/final patch is present.
