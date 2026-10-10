# Requirements Document

## Introduction

This spec is a Kiro spec review/enhancement performed in local session sess_ef9c3844-0570-409c-baa6-7cc73d898476 (executionTarget local) of a spec originally prepared under a prior owner/process. It describes a pinned private starter that already exists; it does not create, rebuild, or re-synthesize that starter, and it does not claim human authorship of the eventual repair. Downstream recorded human work performs the actual diagnosis and repair. The pass normalizes headings to the Kiro canonical format required by `validate_spec_format`, requalifies candidate-task wording, and corrects guided-mode framing without otherwise redrafting the sourced content.

The following paragraph is the exact supplied Goal, reproduced verbatim.

As an evaluation engineer, diagnose a synthetic binary-classifier report whose threshold-selection code ignores the stated false-negative and false-positive costs, repair the selection and confusion-matrix calculations, and produce a deterministic report identifying the lowest-cost threshold.

Task Factory row: https://app.notion.com/p/3f28621e0a7a81bcabb6c65d74863966
Goal+LF SHA256: 7df67f3a13654442be4f04c14cabb7a15eb9fab1c5ff52058c06775e867c47cb
Source pin: https://github.com/KyPython/threshold-evaluation@aca7a6ac52a9a2dee2d7bc3a0a77dca09f2a6fe5

Downstream work MUST reuse this unchanged pinned source rather than rebuild the starter. The pinned commit is the single authoritative starter; no downstream task may regenerate, re-fork, or re-synthesize equivalent starter content.

Candidate stage. This is a Candidate-stage bootcamp item. Its Approved Goal and Approval ID are empty, and its human approval, pay, and attempt fields are empty and are preserved unchanged; this spec does not fill them in and asserts no approval, pay, metric, or human judgment.

### Scope

Describe the pinned synthetic binary-classifier evaluation starter whose report selects a threshold by accuracy and ignores the policy's stated false-negative/false-positive costs, and whose confusion-matrix counts are miscategorised relative to the actual/predicted labels. The starter preserves a green baseline, and leaves the cost-based selection, the confusion-matrix correction, and the decisive verification to the recorded human. This is a review/preparation spec only: no code is written, and the pinned recording starter must remain unworked and answer-key-free (no human diagnosis, final fix, or answer key). The current intended mode is GUIDED recording/practice: a separate, disclosed, AI-authored worked reference already exists off-screen in the TaskWorkPlan (authorized, analyzed, disposable-tested), and during capture the human manually executes edits/tests and narrates the actual outcomes from the unchanged unworked starter with no AI interaction during capture. Manual typing from an unworked input does not by itself imply unaided execution. The separate, future human Transfer Test is a distinct UNAIDED assessment, not the current mode and not a prerequisite for guided world prep. Guided references do not establish unaided learning, mastery, paid eligibility, or human approval.

## Requirements

### Requirement 1: Synthetic-only starter

**User Story:** As a task preparer, I want the repository to contain only fabricated content, so that no private source, credentials, or personal data can appear.

#### Acceptance Criteria

1. WHERE recorder-visible names are inspected, THE starter SHALL use fabricated evaluation code, observations, and policy only (no private source, credentials, or PII). Reference shape, synthetic: `src/threshold_lab/{__init__.py,cli.py,evaluation.py,io.py}`, `tests/{test_evaluation.py,test_io.py}`, `fixtures/{observations.json,policy.json}`. (R1)
2. WHERE the starter is checked out at the pinned source commit `aca7a6ac52a9a2dee2d7bc3a0a77dca09f2a6fe5`, THE reviewer SHALL confirm all recorder-visible evaluation code, observations, and policy are synthetic/fabricated with no private source, credentials, or PII, and run with CPython only (no third-party install required). (R1, R10)

### Requirement 2: Documented intended behavior

**User Story:** As a reviewer, I want a concise behavior contract, so that I can determine the intended behavior without being told the defect.

#### Acceptance Criteria

1. THE starter SHALL include a recorder-visible description stating that the lowest-cost threshold must be selected using the policy's stated false-negative/false-positive costs, with a correct confusion matrix, in clear and testable language. (R2)

### Requirement 3: Reproducible selection defect

**User Story:** As a task preparer, I want the selection code to violate the cost policy, so that the audit has a real defect to find.

#### Acceptance Criteria

1. WHILE inspecting the report against the policy, THE reviewer SHALL identify that threshold selection is driven by accuracy and that `total_cost` is computed but not used for selection. This diagnostic-level defect is observable in the pinned starter. (R3)

### Requirement 4: Reproducible confusion-matrix defect

**User Story:** As a task preparer, I want the confusion matrix to be miscategorised, so that the audit has a second real defect to find.

#### Acceptance Criteria

1. WHILE inspecting the confusion-matrix computation against the actual/predicted labels, THE reviewer SHALL identify that the counts are miscategorised. This diagnostic-level defect is observable in the pinned starter. (R4)

### Requirement 5: Green baseline preserved

**User Story:** As a reviewer, I want the baseline suite to pass deterministically, so that the starter is a known-good green starting point.

#### Acceptance Criteria

1. WHEN the reviewer runs `{python} -m unittest discover -s tests -v` with environment `PYTHONPATH=src` on the pinned starter, THE baseline suite SHALL exit with code 0 and its output SHALL contain `Ran 4 tests`. (R5, R7)

### Requirement 6: Deliverable discoverable, not solved

**User Story:** As a task preparer, I want the lowest-cost report left for the human, so that the human performs the real repair.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE required deterministic lowest-cost-threshold report SHALL remain the human deliverable with the cost-based selection and corrected matrix left for the human, and no recorder-visible file SHALL identify the exact final patch. (R6)

### Requirement 7: Deterministic local run

**User Story:** As a reviewer, I want a documented command, so that the baseline runs deterministically with no network dependence after checkout.

#### Acceptance Criteria

1. WHERE the starter is checked out at the pinned commit, THE documented baseline command SHALL run deterministically with no network access after checkout, using CPython only. (R7)

### Requirement 8: Unrelated checks stay meaningful

**User Story:** As a reviewer, I want passing baseline checks to remain meaningful, so that a later correction can be shown to preserve them.

#### Acceptance Criteria

1. WHERE baseline checks are present, THE starter SHALL keep them meaningful and runnable so a later correction can be shown to preserve them. (R8)

### Requirement 9: No answer key

**User Story:** As a task preparer, I want recorder-visible files free of solutions, so that the recording starter stays unworked.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE starter SHALL contain no cost-based selection, no corrected confusion matrix, no final lowest-cost report, no diagnosis note, and no expected patch diff. (R9)

### Requirement 10: Pre-recording integrity

**User Story:** As a reviewer, I want to confirm the baseline is green and both defects exist while the human work is undone, so that integrity is verified before recording.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE reviewer SHALL be able to confirm (read-only) that the baseline is green, both defects exist, and the human work remains undone. (R10)

## Glossary

- **Pinned recording starter:** The unchanged, unworked repository at the pinned source commit `aca7a6ac52a9a2dee2d7bc3a0a77dca09f2a6fe5` that the human works from during capture.
- **Worked reference:** A separate, disclosed, AI-authored, analyzed, disposable-tested artifact off-screen in the TaskWorkPlan; it does not establish unaided human learning, mastery, paid eligibility, or human approval.
- **Guided recording/practice (current mode):** The human manually executes edits/tests and narrates actual outcomes from the unchanged unworked starter, with no AI interaction during capture. Manual typing from an unworked input does not by itself imply unaided execution.
- **Human Transfer Test (separate, future):** A distinct UNAIDED assessment; not the current mode and not a prerequisite for guided world prep.
- **`{python}`:** The pinned CPython interpreter (dependency profile `python-stdlib`; CPython only, no third-party packages, run with `PYTHONPATH=src`).
- **Governing invariant INV-1:** The threshold report MUST select the lowest-cost threshold using the policy's stated false-negative and false-positive costs, with a confusion matrix correctly categorised against the actual/predicted labels. The pinned starter intentionally selects by accuracy and miscategorises the matrix, violating this invariant without identifying the final repair.
