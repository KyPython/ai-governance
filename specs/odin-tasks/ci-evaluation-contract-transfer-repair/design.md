# Design — CI Evaluation Contract Transfer Repair

## Repository shape
- `README.md` — setup and local pipeline command.
- `docs/evaluation-contract.md` — written pre-grading requirements.
- `src/` or `grader/` — synthetic validation/grading components.
- `fixtures/valid/` — at least one valid case.
- `ci/` or `scripts/` — deterministic local CI/grading sequence.
- tests that verify existing unrelated behavior without implementing the missing requirement.

## Boundary design
The written contract and executable checks should intentionally drift at one bounded handoff before grading. The code should make the transfer boundary inspectable, while avoiding comments such as “missing check here.” The human recording should require tracing contract → current enforcement → gap → bounded correction.

## Human boundary
KyJahn must independently identify the missing enforcement, implement the fail-closed validation, create the final negative fixture, and show defective rejection plus valid-case preservation. Pre-recording automation may not complete any of those steps.

## Verification before handoff
Reviewer verifies setup, valid-case execution, existence of contract/enforcement mismatch, and absence of the final check/fixture.
