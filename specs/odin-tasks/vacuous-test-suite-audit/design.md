# Design — Vacuous Test Suite Audit

## Overview

This design is a Kiro spec review/enhancement in local session sess_ef9c3844-0570-409c-baa6-7cc73d898476 (executionTarget local) of a spec originally prepared under a prior owner/process. Existing design content is preserved and folded into Kiro canonical sections; provenance, pinned-dependency, evidence-boundary, failure-mode, and human-gate material is retained. No prior authorship is claimed.

A small synthetic Python module has a written behavior contract and a pytest suite that passes despite a seeded defect that breaks the documented behavior, because one or more assertions are vacuous. The pinned recording starter is unworked and answer-key-free. In guided recording/practice mode the human later identifies the vacuous assertions, strengthens them, demonstrates failure on the defective build, applies the smallest corrective change, and demonstrates the strengthened suite passes — manually executing and narrating actual outcomes from the unchanged starter.

- Approved Goal SHA256 (Goal+LF): ad882a58279d4809c1a4c036554a3400509b50c46bbb58e41f9665d54a30b135
- Approval ID: ODIN-5959D60FB16547A0A846BB836D8D0C3F (human-owned; unchanged by this pass)

Evidence boundaries (what a reviewer MAY verify pre-recording, read-only and non-authoring):
- setup works and the baseline weak suite passes (`8 passed`, exit 0);
- the documented behavior and implementation are genuinely inconsistent;
- no answer key / final patch / strengthened suite is present in recorder-visible files.

A separate, disclosed, AI-authored worked reference already exists off-screen in the TaskWorkPlan (authorized, analyzed, disposable-tested). It is distinct from the recording starter. Diagnosis, tests, and repair are NOT banned in authorized off-screen reference preparation; only the pinned recording starter must remain unworked.

## Architecture

Repository shape (pinned starter layout):
- `README.md` — neutral setup and baseline-run instructions; no diagnosis.
- `docs/behavior.md` — the intended behavior contract.
- `src/` — small production module containing one bounded seeded defect.
- `tests/` — initial weak pytest suite that passes.
- optional `scripts/` — deterministic local setup/baseline helper.

Dependencies and reproducibility (pinned profile):
- Dependency profile: **python-pytest** — `pytest==8.3.5`, virtual environment rooted at `.venv`, dev dependencies in `requirements-dev.txt`.
- Source reuse: check out the pinned starter `https://github.com/KyPython/vacuous-test-suite-audit@c5986e93719cfd4b08a57104576c04a78d1f16ee` and reuse it unchanged. Downstream MUST NOT rebuild or re-synthesize the starter.
- Pinned setup recipe: create `.venv`, install the pinned `pytest==8.3.5` from `requirements-dev.txt` bound to the existing PrepareTaskWork helper per-task profile and the public pinned runtime wheels (no-index/find-links). A bare-network `pip install` is NOT treated as offline; setup uses the registry's declared profiles/argv/env.
- Focused baseline test (registry baseline, deterministic, local): `{venvPython} -m pytest -q` → exit 0, output contains `8 passed`.

## Components and Interfaces

- **Production module (`src/`):** implements the documented behavior but contains one bounded seeded defect that makes a documented behavior false.
- **Weak suite (`tests/`):** exercises relevant code paths with assertions that can pass even when the documented outcome is wrong; avoids obvious placeholders.
- **Behavior contract (`docs/behavior.md`):** states intended behavior meaningfully enough to audit, without labeling the defect.
- **Baseline helper (optional `scripts/`):** deterministic local setup/baseline run proving `8 passed`.

## Data Models

- **Behavior contract clauses:** enumerated intended outcomes against which the implementation can be checked.
- **Test case fixtures:** synthetic inputs/expected values; the vacuity lies in assertions that fail to bind the documented outcome.

## Correctness Properties

### Property 1: strengthened assertion separates defective and corrected builds
WHERE an assertion is strengthened to bind the documented behavior, THE test SHALL fail on the defective build and pass on the corrected build.
**Validates: Requirements 3**

### Property 2: baseline is green at the pin
WHEN the registry baseline command runs against the unchanged pinned starter, THE weak suite SHALL exit 0 with output containing `8 passed`.
**Validates: Requirements 4**

- The seeded defect must be observable through the documented contract and ordinary execution.
- The weak suite must exercise relevant code paths (not `assert True` / empty tests) while remaining logically insufficient.

## Error Handling

Failure modes (reject and re-pin rather than alter the baseline):
- Seeded defect not observable via the documented contract → fails Requirement 3, criterion 1; re-pin.
- Weak suite that is obviously empty (`assert True`, no path coverage) → fails R4.
- Any strengthened assertion, corrective patch, or diagnosis note present → fails Requirement 7, criterion 1; Requirement 10, criterion 1.
- Baseline drifts from registry (not exit 0 or missing `8 passed`) → fails Requirement 4, criterion 1; do not alter the baseline to pass.

## Testing Strategy

Human-only during TaskRecorder — the pending human-owned step performed in guided recording/practice mode (NOT performed in this spec pass):
- identifying why the existing assertions are not proving the contract;
- replacing them with meaningful checks;
- demonstrating failure on the defective build;
- applying the smallest corrective production change;
- demonstrating the strengthened suite passes.

Human-boundary scope qualifier: the current intended mode is guided recording/practice. The human manually executes edits/tests and narrates actual outcomes from the unchanged unworked starter, with no AI interaction during capture; manual typing does not by itself imply unaided execution. A separate, future unaided Transfer Test is a distinct assessment. Authorized guided practice and disclosed worked references do not substitute for that assessment or establish unaided mastery, paid eligibility, or human approval.

Explicit human gates:
- Human diagnosis, repair, recording, capture, and any Odin attempt/approval/pay remain human-owned and outside this spec.
- All coding and source promotion are HELD until Ky merges the specs-only PR with green required checks (repo CI + `ai-governance / verdict`).
