# Design — CI Evaluation Contract Transfer Repair

## Overview

This design is a Kiro spec review/enhancement in local session sess_ef9c3844-0570-409c-baa6-7cc73d898476 (executionTarget local) of a spec originally prepared under a prior owner/process. Existing design content is preserved and folded into Kiro canonical sections; provenance, pinned-dependency, evidence-boundary, failure-mode, and human-gate material is retained, and governing invariant INV-1 is preserved. No prior authorship is claimed.

A synthetic grading repository has written evaluation requirements that are not fully enforced before grading. The starter preserves a valid case that passes and leaves a bounded enforcement gap at the contract-to-CI transfer boundary. In guided recording/practice mode the human later identifies the missing check, implements one bounded fail-closed validation plus a negative fixture, and shows the defective case is rejected while the valid case is preserved — manually executing and narrating actual outcomes from the unchanged starter.

- Approved Goal SHA256 (Goal+LF): eae155012790178f9ef10a5f5decd7e9a73c2135d0309ae3491ce542ef80543c
- Approval ID: ODIN-219830EEEC244B30A7DE8FFF65B6AB7E (human-owned; unchanged by this pass)

Evidence boundaries (what a reviewer MAY verify pre-recording, read-only and non-authoring):
- setup works and both baseline commands produce the exit codes and substrings in the acceptance criteria;
- the valid case passes;
- at least one written mandatory requirement is unenforced at the transfer boundary (INV-1 violated);
- no final check, negative fixture, or answer key exists in recorder-visible files.

A separate, disclosed, AI-authored worked reference already exists off-screen in the TaskWorkPlan (authorized, analyzed, disposable-tested). It is distinct from the recording starter. Diagnosis, tests, and repair are NOT banned in authorized off-screen reference preparation; only the pinned recording starter must remain unworked and answer-key-free.

## Architecture

Repository shape (pinned starter layout):
- `README.md` — setup and local pipeline command.
- `docs/evaluation-contract.md` — written pre-grading requirements.
- `src/` or `grader/` — synthetic validation/grading components.
- `fixtures/valid/` — at least one valid case (`fixtures/valid/manifest.json`).
- `ci/` or `scripts/` — deterministic local CI/grading sequence (`scripts/verify.sh`).
- tests that verify existing unrelated behavior without implementing the missing requirement.

Dependencies and reproducibility (pinned profile):
- Dependency profile: **python-stdlib** — CPython only, no third-party packages, no network at runtime after checkout.
- Source reuse: check out the pinned starter `https://github.com/KyPython/ci-evaluation-contract@ca532d92ec3db02224061b3ceef105b2bc113b27` and reuse it unchanged. Downstream MUST NOT rebuild or re-synthesize the starter.
- Pinned setup recipe: clone at the pinned commit and use the pinned CPython `{python}` bound to the existing PrepareTaskWork helper per-task profile/argv/env; no third-party install required and no bare-network pip step is used.

## Components and Interfaces

- **Written contract (`docs/evaluation-contract.md`):** defines at least one mandatory pre-grading requirement in testable language.
- **Grader/pipeline (`grader/` or `src/`):** runs the validation/grading sequence; intentionally omits enforcement of one written mandatory requirement at the transfer boundary.
- **Valid fixture (`fixtures/valid/manifest.json`):** passes the starter pipeline (`sample_001: 3`).
- **Local CI runner (`scripts/verify.sh`):** deterministic local sequence producing `Ran 3 tests`.
- **Unrelated checks:** meaningful and runnable so a later correction can be shown to preserve them.

Focused baseline commands (registry baseline, deterministic, local):
- `sh scripts/verify.sh` → exit 0, output contains `Ran 3 tests`.
- `{python} -m grader.pipeline fixtures/valid/manifest.json` → exit 0, output contains `sample_001: 3`.

## Data Models

- **Evaluation contract clause:** a mandatory pre-grading requirement expressed in testable terms.
- **Manifest:** `fixtures/valid/manifest.json`, the valid grading input; the defective (negative) manifest is NOT shipped.
- **Grade record:** mapping of a sample id to its grade (e.g. `sample_001: 3`).

## Correctness Properties

### Property 1: fail-closed at the transfer boundary (INV-1)
WHERE any mandatory pre-grading requirement written in the contract is not explicitly validated as satisfied, THE grading sequence SHALL NOT begin. A written mandatory clause is NOT exempt merely because it was not previously represented in CI; the future repair enforces the specific written clause identified under Requirement 3, criterion 1, before scoring while preserving the valid case. This keeps ONE bounded validation target and does not claim the clearance-only worked reference proves every written clause.
**Validates: Requirements 3, 11**

### Property 2: valid case preserved
WHEN the registry baseline commands run against the starter state, THE local CI runner SHALL exit 0 with output containing `Ran 3 tests`, and the valid manifest SHALL grade with output containing `sample_001: 3`.
**Validates: Requirements 4**

- **INV-1 (governing invariant, preserved):** Grading must not begin unless every mandatory pre-grading requirement has been explicitly validated as satisfied. The starter intentionally violates enforcement of this invariant without identifying the final repair.
- The valid case must pass from the starter state; unrelated checks must remain meaningful so a later correction can be shown to preserve them.

## Error Handling

Failure modes (reject and re-pin rather than alter the baseline):
- Valid case does not pass from the starter → fails Requirement 4, criteria 1 and 2; re-pin.
- No real enforcement gap (contract fully enforced) → fails Requirement 3, criterion 1; INV-1 not demonstrably violated.
- Unrelated checks weakened or non-meaningful → fails Requirement 8, criterion 1.
- Any completed validator, final negative fixture, diagnosis note, or patch diff present → fails Requirement 9, criterion 1.
- Baseline drifts from registry exit codes/substrings → fails Requirement 4, criteria 1 and 2; do not alter the baseline to pass.

## Testing Strategy

Human-only during TaskRecorder — the pending human-owned step performed in guided recording/practice mode (NOT performed in this spec pass):
- identifying the missing enforcement;
- implementing the bounded fail-closed validation;
- creating the final negative fixture;
- showing defective rejection plus valid-case preservation.

Human-boundary scope qualifier: the current intended mode is guided recording/practice. The human manually executes edits/tests and narrates actual outcomes from the unchanged unworked starter, with no AI interaction during capture; manual typing does not by itself imply unaided execution. A separate, future unaided Transfer Test is a distinct assessment. Authorized guided practice and disclosed worked references do not substitute for that assessment or establish unaided mastery, paid eligibility, or human approval.

Explicit human gates:
- Human diagnosis, repair, recording, capture, and any Odin attempt/approval/pay remain human-owned and outside this spec.
- All coding and source promotion are HELD until Ky merges the specs-only PR with green required checks (repo CI + `ai-governance / verdict`).
