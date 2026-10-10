# Requirements Document

## Introduction

This spec is a Kiro spec review/enhancement performed in local session sess_ef9c3844-0570-409c-baa6-7cc73d898476 (executionTarget local) of a spec originally prepared under a prior owner/process. It describes a pinned private starter that already exists; it does not create, rebuild, or re-synthesize that starter, and it does not claim human authorship of the eventual repair. Downstream recorded human work performs the actual diagnosis and repair. The pass normalizes headings to the Kiro canonical format required by `validate_spec_format`, requalifies candidate-task wording, and corrects guided-mode framing without otherwise redrafting the sourced content.

The following paragraph is the exact supplied Goal, reproduced verbatim.

As a Python engineer, repair a synthetic batch command whose nested exception handling incorrectly treats a failed item as successfully processed, then verify the corrected propagation, cleanup, and reporting behavior with deterministic tests.

Task Factory row: https://app.notion.com/p/3f38621e0a7a81498dd1c3e0ef4bff3d
Goal+LF SHA256: a519473d08c3e12ec135b069285a123814414356e2bef0bc27c4a37d8792d717
Source pin: https://github.com/KyPython/python-exception-propagation@ac4aaa7d95fd07d3bdc58aa88128d24e533ec4c2

Downstream work MUST reuse this unchanged pinned source rather than rebuild the starter. The pinned commit is the single authoritative starter; no downstream task may regenerate, re-fork, or re-synthesize equivalent starter content.

Candidate stage. This is a Candidate-stage bootcamp item. Its Approved Goal and Approval ID are empty, and its human approval, pay, and attempt fields are empty and are preserved unchanged; this spec does not fill them in and asserts no approval, pay, metric, or human judgment.

### Scope

Describe the pinned synthetic batch-command starter in which nested exception handling misclassifies a failed item as successfully processed. The starter preserves a green baseline and leaves the propagation/cleanup/reporting repair and the decisive failing-then-passing tests to the recorded human. This is a review/preparation spec only: no code is written, and the pinned recording starter must remain unworked and answer-key-free (no human diagnosis, strengthened final tests, defect repair, completed deliverable, or answer key). The current intended mode is GUIDED recording/practice: a separate, disclosed, AI-authored worked reference already exists off-screen in the TaskWorkPlan (authorized, analyzed, disposable-tested), and during capture the human manually executes edits/tests and narrates the actual outcomes from the unchanged unworked starter with no AI interaction during capture. Manual typing from an unworked input does not by itself imply unaided execution. The separate, future human Transfer Test is a distinct UNAIDED assessment, not the current mode and not a prerequisite for guided world prep. Guided references do not establish unaided learning, mastery, paid eligibility, or human approval.

## Requirements

### Requirement 1: Synthetic-only starter

**User Story:** As a task preparer, I want the repository to contain only fabricated content, so that no private source, credentials, or personal data can appear.

#### Acceptance Criteria

1. WHERE recorder-visible names are inspected, THE starter SHALL use fabricated module names, items, and data only (no private source, credentials, or PII). Reference package shape, synthetic: `src/batch_command/{__init__.py,command.py,errors.py}`, `tests/{conftest.py,test_baseline.py}`. (R1)
2. WHERE the starter is checked out at the pinned source commit `ac4aaa7d95fd07d3bdc58aa88128d24e533ec4c2`, THE reviewer SHALL confirm all recorder-visible module names and data are synthetic/fabricated with no private source, credentials, or PII. (R1, R9)

### Requirement 2: Documented intended behavior

**User Story:** As a reviewer, I want a concise behavior contract, so that I can determine the intended behavior without being told the defect.

#### Acceptance Criteria

1. THE starter SHALL include a recorder-visible description stating that a failed item must be reported as failed (not processed), with cleanup still performed, and that an unhandled/non-recoverable exception must propagate out of the batch runner after proper classification and cleanup, in clear and testable language. (R2)
2. WHERE the intended behavior is documented, THE description SHALL state the failed-item reporting, cleanup, and exception-propagation semantics neutrally and SHALL NOT instruct the engineer how to patch the runner. (R2)

### Requirement 3: Reproducible classification defect

**User Story:** As a task preparer, I want the implementation to violate a documented behavior, so that the audit has a real defect to find.

#### Acceptance Criteria

1. WHILE inspecting the batch runner against its documented intended behavior, THE reviewer SHALL identify that the `finally`-block processed-count path reports a failed item as processed and that no baseline test covers the failed-item processed/failures classification. This diagnostic-level defect is observable in the pinned starter. (R3, R5)

### Requirement 4: Green baseline preserved

**User Story:** As a reviewer, I want the baseline suite to pass deterministically, so that the starter is a known-good green starting point.

#### Acceptance Criteria

1. WHEN the reviewer runs `{venvPython} -m pytest` with environment `PYTHONPATH=src` on the pinned starter, THE baseline suite SHALL exit with code 0 and its output SHALL contain `2 passed`. (R4, R6)

### Requirement 5: Coverage gap is discoverable, not solved

**User Story:** As a reviewer, I want the classification coverage gap to be inspectable but unsolved, so that the human performs the real audit and repair.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE baseline tests SHALL NOT cover a failed item's processed/failures classification and no recorder-visible file SHALL identify the exact final patch. (R5)

### Requirement 6: Deterministic local run

**User Story:** As a reviewer, I want a single documented command, so that the baseline runs deterministically with no network dependence after checkout.

#### Acceptance Criteria

1. WHERE the starter is checked out at the pinned commit and the pinned toolchain is installed into `.venv`, THE single documented baseline command SHALL run deterministically with no network access after checkout. (R6)

### Requirement 7: Unrelated checks stay meaningful

**User Story:** As a reviewer, I want passing baseline checks to remain meaningful, so that a later correction can be shown to preserve them.

#### Acceptance Criteria

1. WHERE baseline checks are present, THE starter SHALL keep them meaningful and runnable so a later correction can be shown to preserve them. (R7)

### Requirement 8: No answer key

**User Story:** As a task preparer, I want recorder-visible files free of solutions, so that the recording starter stays unworked.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE starter SHALL contain no corrected runner, no final failing-then-passing classification test, no diagnosis note, and no expected patch diff. (R8)

### Requirement 9: Pre-recording integrity

**User Story:** As a reviewer, I want to confirm the baseline is green and the defect exists while the human work is undone, so that integrity is verified before recording.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE reviewer SHALL be able to confirm (read-only) that the baseline is green, the classification defect exists, and the human work remains undone. (R9)

## Glossary

- **Pinned recording starter:** The unchanged, unworked repository at the pinned source commit `ac4aaa7d95fd07d3bdc58aa88128d24e533ec4c2` that the human works from during capture.
- **Worked reference:** A separate, disclosed, AI-authored, analyzed, disposable-tested artifact off-screen in the TaskWorkPlan; it does not establish unaided human learning, mastery, paid eligibility, or human approval.
- **Guided recording/practice (current mode):** The human manually executes edits/tests and narrates actual outcomes from the unchanged unworked starter, with no AI interaction during capture. Manual typing from an unworked input does not by itself imply unaided execution.
- **Human Transfer Test (separate, future):** A distinct UNAIDED assessment; not the current mode and not a prerequisite for guided world prep.
- **`{venvPython}`:** The `.venv` interpreter (dependency profile `python-pytest`, `pytest==8.3.5`, dev deps pinned in `requirements-dev.txt`, run with `PYTHONPATH=src`).
- **Governing invariant INV-1:** A batch item whose child operation raises an UNHANDLED / NON-RECOVERABLE exception MUST be reported as failed and MUST NOT be counted as processed, while required cleanup still runs exactly once, and the exception MUST propagate out of the batch runner after classification and cleanup complete. A `HandledItemError` is deliberately recovered and is RETAINED as a processed success with its cleanup performed once (per the source error hierarchy and recoverable fixture); INV-1 does NOT reclassify it as failed. The pinned starter intentionally violates this reporting invariant for unhandled/non-recoverable failures without identifying the final repair.
