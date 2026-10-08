# Design — Python Exception-Propagation Repair

## Overview

This design is a Kiro spec review/enhancement in local session sess_ef9c3844-0570-409c-baa6-7cc73d898476 (executionTarget local) of a spec originally prepared under a prior owner/process. It documents a pinned, already-published private starter and the diagnostic-level defect visible in it. It does not write the fix and does not claim human authorship. Existing design content is preserved and folded into Kiro canonical sections.

A synthetic batch command processes a list of items. Its nested exception handling records every item as processed in a `finally` block, so an item whose child operation raises an UNHANDLED / NON-RECOVERABLE exception is still reported as processed instead of failed. The deliberate recoverable `HandledItemError` path is distinct: it is recovered and correctly reported as a processed success with its cleanup performed once, and the repair must RETAIN that behavior. The baseline test suite is green and does not assert the failed-item processed/failures classification. In guided recording/practice mode the recorded human later diagnoses the propagation defect, repairs the reporting so unhandled/non-recoverable failures are classified correctly while cleanup still runs, and verifies with deterministic failing-then-passing tests.

- Candidate Goal SHA256 (Goal+LF): a519473d08c3e12ec135b069285a123814414356e2bef0bc27c4a37d8792d717
- Candidate-stage bootcamp item: Approved Goal and Approval ID are empty; there is no retrospective Odin approval. Human approval, pay, and attempt fields are empty and unchanged by this pass.

## Architecture

Synthetic reference shape at the pinned commit (described for review only; not rebuilt):
- `README.md` — setup and the local baseline command.
- `pyproject.toml`, `requirements-dev.txt` — pinned dev dependencies.
- `src/batch_command/__init__.py`, `src/batch_command/command.py`, `src/batch_command/errors.py` — synthetic batch runner and error types.
- `tests/conftest.py`, `tests/test_baseline.py` — green baseline tests that do not cover failed-item classification.

Dependencies and reproducibility (pinned profile):
- Dependency profile: **python-pytest** — `pytest==8.3.5` installed into an isolated project `.venv` from `requirements-dev.txt`; no network at runtime after checkout.
- Offline, pinned setup recipe (bound to the reviewed `PrepareTaskWork.py` helper, per-task): check out the pinned starter commit `ac4aaa7d95fd07d3bdc58aa88128d24e533ec4c2`; the helper creates the venv with the pinned public CPython (`python3 -I -m venv .venv`) and installs offline from the public pinned runtime wheels — `python -I -m pip install --no-index --find-links <wheels> -r requirements-dev.txt` under `PIP_NO_INDEX=1`/`PIP_NO_CACHE_DIR=1`. Bare networked `pip install` is NOT used and is not offline. The helper then asserts the installed pytest equals the pinned `8.3.5`. Run with `PYTHONPATH=src`.
- Source reuse: reuse the pinned starter unchanged; downstream MUST NOT rebuild or re-synthesize the starter.

## Components and Interfaces

- **Batch runner (`src/batch_command/`):** implements item processing but records every item as processed in a `finally` block, misclassifying a failed item.
- **Error types (`src/batch_command/errors.py`):** synthetic error types raised during item processing.
- **Baseline tests (`tests/`):** green tests that exercise paths without covering the failed-item processed/failures classification.
- **Behavior contract (recorder-visible description):** states intended failed-item reporting and cleanup semantics without labeling the defect.

## Data Models

- **Processing report:** processed-count and failures classification against which the implementation can be checked; the vacancy lies in the `finally`-block processed-count path.
- **Item fixtures:** synthetic inputs including an item that raises during processing.

## Correctness Properties

### Property 1: failed item classified failed, cleanup still runs (INV-1)
WHERE a batch item raises an UNHANDLED / NON-RECOVERABLE child-operation exception during processing, THE processing report SHALL count that item as failed and SHALL NOT count it as processed, while required cleanup still runs. The deliberate recoverable `HandledItemError` path is EXPLICITLY PRESERVED: a handled item continues and is reported processed (success), not failed.
**Validates: Requirements 3**

### Property 2: baseline is green at the pin
WHEN the registry baseline command runs against the unchanged pinned starter, THE suite SHALL exit 0 with output containing `2 passed`.
**Validates: Requirements 4**

- **INV-1 (governing invariant):** A batch item that fails with an unhandled / non-recoverable child-operation exception MUST be reported as failed and MUST NOT be counted as processed, while required cleanup still runs; the deliberate recoverable `HandledItemError` path is preserved and remains reported processed (success). The pinned starter intentionally violates this reporting invariant without identifying the final repair.
- The seeded defect must be observable through the documented contract and ordinary execution.
- The baseline suite must exercise relevant code paths while remaining logically insufficient to catch the classification defect.

## Error Handling

Failure modes (reject and re-pin rather than alter the baseline):
- Baseline not green at the pin → fails R4/AC (baseline); re-pin rather than edit the starter.
- Defect not reproducible (failed item already classified correctly) → fails R3; INV-1 not demonstrably violated.
- Baseline checks weakened or non-meaningful → fails R7.
- Any corrected runner, final classification test, diagnosis note, or patch diff present → fails R8.
- Baseline drifts from the registry exit code/substring (`2 passed`) → fails the baseline AC; do not alter the baseline to pass.

## Testing Strategy

Baseline / red-green shape:
- Focused baseline command (registry baseline, deterministic, local): `{venvPython} -m pytest` with env `PYTHONPATH=src` → exit 0, output contains `2 passed`.
- The baseline is green on the starter; the recorded human later adds the decisive failing-then-passing classification test alongside the repair. This spec does not add that test.

Evidence boundaries a reviewer MAY verify pre-recording (read-only, non-authoring):
- the offline setup works and the baseline command produces exit 0 and `2 passed`;
- the `finally`-block processed-count path reports a failed item as processed (defect present);
- no baseline test covers the failed-item processed/failures classification (gap present);
- no corrected runner, final classification test, diagnosis note, or answer key exists in recorder-visible files.

Human-only during recording (not performed in this specification pass and absent from the unchanged pinned recording starter; separately disclosed TaskWorkPlan worked references were AI-authored, analyzed, and disposable-tested off-screen), in guided recording/practice mode: diagnosing the propagation/reporting defect; repairing failed-item classification while preserving cleanup; writing the decisive failing-then-passing deterministic tests; demonstrating corrected propagation, cleanup, and reporting. The human manually executes edits/tests and narrates actual outcomes from the unchanged unworked starter, with no AI interaction during capture; manual typing does not by itself imply unaided execution. A separate, future unaided Transfer Test is a distinct assessment. The disclosed off-screen worked reference and authorized guided practice do not substitute for that assessment or establish unaided mastery, paid eligibility, or human approval.

Explicit human gates:
- Human diagnosis, repair, recording, capture, and any Odin attempt/approval/pay remain human-owned and outside this spec. This spec does not fill approval, pay, metric, or judgment fields.
- All coding and source promotion are HELD until Ky merges the specs-only PR with green required checks (repo CI + `ai-governance / verdict`). Agents never merge, approve, deploy, or promote.
