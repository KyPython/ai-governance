# Design — Cost-Sensitive Evaluation Threshold Repair

## Overview

This design is a Kiro spec review/enhancement in local session sess_ef9c3844-0570-409c-baa6-7cc73d898476 (executionTarget local) of a spec originally prepared under a prior owner/process. It documents a pinned, already-published private starter and the diagnostic-level defects visible in it. It does not write the fix and does not claim human authorship. Existing design content is preserved and folded into Kiro canonical sections.

A synthetic evaluation tool reads observations and a cost policy and produces a binary-classifier threshold report. The report selects the threshold by accuracy and ignores the policy's stated false-negative/false-positive costs (`total_cost` is computed but not used for selection), and the confusion-matrix counts are miscategorised relative to the actual/predicted labels. The baseline suite is green. In guided recording/practice mode the recorded human later diagnoses both defects, repairs the cost-based selection and the confusion matrix, and produces a deterministic report identifying the lowest-cost threshold.

- Candidate Goal SHA256 (Goal+LF): 7df67f3a13654442be4f04c14cabb7a15eb9fab1c5ff52058c06775e867c47cb
- Candidate-stage bootcamp item: Approved Goal and Approval ID are empty; there is no retrospective Odin approval. Human approval, pay, and attempt fields are empty and unchanged by this pass.

## Architecture

Synthetic reference shape at the pinned commit (described for review only; not rebuilt):
- `README.md` — setup and the local baseline command.
- `pyproject.toml` — synthetic package metadata.
- `src/threshold_lab/__init__.py`, `src/threshold_lab/cli.py`, `src/threshold_lab/evaluation.py`, `src/threshold_lab/io.py` — synthetic evaluation, CLI, and IO.
- `tests/test_evaluation.py`, `tests/test_io.py` — green baseline tests.
- `fixtures/observations.json`, `fixtures/policy.json` — synthetic observations and the cost policy.

Dependencies and reproducibility (pinned profile):
- Dependency profile: **python-stdlib** — CPython only, no third-party packages, no network at runtime after checkout.
- Offline, pinned setup recipe (bound to the reviewed `PrepareTaskWork.py` helper, per-task): check out the pinned starter commit `aca7a6ac52a9a2dee2d7bc3a0a77dca09f2a6fe5`; use the pinned public CPython `{python}`; run with `PYTHONPATH=src`; no third-party packages and no pip install required (stdlib-only profile; the helper runs no network install for this profile).
- Source reuse: reuse the pinned starter unchanged; downstream MUST NOT rebuild or re-synthesize the starter.

## Components and Interfaces

- **Evaluation module (`src/threshold_lab/evaluation.py`):** selects threshold by accuracy, computes `total_cost` but does not use it for selection, and miscategorises the confusion-matrix counts.
- **IO module (`src/threshold_lab/io.py`):** reads synthetic observations and the cost policy.
- **CLI (`src/threshold_lab/cli.py`):** synthetic entry point producing the report.
- **Fixtures (`fixtures/observations.json`, `fixtures/policy.json`):** synthetic observations and the stated false-negative/false-positive cost policy.
- **Baseline tests (`tests/`):** green tests that do not enforce cost-based selection or the corrected matrix.
- **Behavior contract (recorder-visible description):** states intended cost-based selection and correct confusion matrix without labeling the defects.

## Data Models

- **Observations fixture:** synthetic actual/predicted labels used to compute the matrix and costs.
- **Cost policy fixture:** stated false-negative/false-positive costs the selection must honour; the vacancy lies in `total_cost` being computed but ignored for selection.
- **Threshold report:** the lowest-cost-threshold deliverable, left for the human.

## Correctness Properties

### Property 1: threshold minimizes total cost (INV-1)
WHERE the policy's stated false-negative and false-positive costs apply, THE threshold report SHALL select the threshold that minimizes total cost (not the one that maximizes accuracy).
**Validates: Requirements 3**

### Property 2: confusion-matrix counts match labels
WHERE the confusion matrix is computed, THE matrix counts SHALL match the actual/predicted labels, and the baseline SHALL exit 0 with output containing `Ran 4 tests`.
**Validates: Requirements 4, 5**

- **INV-1 (governing invariant):** The threshold report MUST select the lowest-cost threshold using the policy's stated false-negative and false-positive costs, with a confusion matrix correctly categorised against the actual/predicted labels. The pinned starter intentionally selects by accuracy and miscategorises the matrix, violating this invariant without identifying the final repair.
- Both seeded defects must be observable through the documented contract and ordinary execution.
- The baseline suite must remain meaningful while leaving both defects unsolved.

## Error Handling

Failure modes (reject and re-pin rather than alter the baseline):
- Baseline not green at the pin → fails R5; re-pin rather than edit the starter.
- No real selection gap (costs already drive selection) → fails R3; INV-1 not demonstrably violated.
- Confusion matrix already correct → fails R4.
- Baseline checks weakened or non-meaningful → fails R8.
- Any cost-based selection, corrected matrix, final lowest-cost report, diagnosis note, or patch diff present → fails R9.
- Baseline drifts from the registry exit code/substring (`Ran 4 tests`) → fails R5 AC; do not alter the baseline to pass.

## Testing Strategy

Baseline / red-green shape:
- Focused baseline command (registry baseline, deterministic, local): `{python} -m unittest discover -s tests -v` with env `PYTHONPATH=src` → exit 0, output contains `Ran 4 tests`.
- The baseline is green on the starter; the recorded human later adds the decisive failing-then-passing checks for cost-based selection and the corrected confusion matrix alongside the repair. This spec does not add those checks.

Evidence boundaries a reviewer MAY verify pre-recording (read-only, non-authoring):
- the offline setup works and the baseline command produces exit 0 and `Ran 4 tests`;
- threshold selection is driven by accuracy and `total_cost` is computed but unused for selection (defect present);
- the confusion-matrix counts are miscategorised against actual/predicted labels (defect present; INV-1 violated);
- no cost-based selection, corrected matrix, final lowest-cost report, or answer key exists in recorder-visible files.

Human-only during recording (not performed in this specification pass and absent from the unchanged pinned recording starter; separately disclosed TaskWorkPlan worked references were AI-authored, analyzed, and disposable-tested off-screen), in guided recording/practice mode: diagnosing the cost-ignoring selection and the miscategorised confusion matrix; repairing the selection to use the stated costs and correcting the matrix; producing the deterministic lowest-cost-threshold report; verifying the corrected behavior. The human manually executes edits/tests and narrates actual outcomes from the unchanged unworked starter, with no AI interaction during capture; manual typing does not by itself imply unaided execution. A separate, future unaided Transfer Test is a distinct assessment. The disclosed off-screen worked reference and authorized guided practice do not substitute for that assessment or establish unaided mastery, paid eligibility, or human approval.

Explicit human gates:
- Human diagnosis, repair, recording, capture, and any Odin attempt/approval/pay remain human-owned and outside this spec. This spec does not fill approval, pay, metric, or judgment fields.
- All coding and source promotion are HELD until Ky merges the specs-only PR with green required checks (repo CI + `ai-governance / verdict`). Agents never merge, approve, deploy, or promote.
