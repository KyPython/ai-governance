# Requirements Document

## Introduction

This spec is a Kiro spec review/enhancement performed in local session sess_ef9c3844-0570-409c-baa6-7cc73d898476 (executionTarget local) of a spec originally prepared under a prior owner/process. It describes a pinned private starter that already exists; it does not create, rebuild, or re-synthesize that starter, and it does not claim human authorship of the eventual repair. Downstream recorded human work performs the actual diagnosis and repair. The pass normalizes headings to the Kiro canonical format required by `validate_spec_format`, requalifies candidate-task wording, and corrects guided-mode framing without otherwise redrafting the sourced content.

The following paragraph is the exact supplied Goal, reproduced verbatim.

As a backend engineer, repair a synthetic OAuth callback handler that accepts an unbound or mismatched state value, preserve the intended success path, and verify the corrected behavior with deterministic local fixtures for valid, missing, mismatched, expired, and replayed state.

Task Factory row: https://app.notion.com/p/3f38621e0a7a81ac95c5dc0a9aaa211a
Goal+LF SHA256: 53aa8de22a4d56b96b893bd778b17f0d629b57b4a43de0d34883ada57016ff24
Source pin: https://github.com/KyPython/oauth-callback-state@c65f9343be723ea36289db541b8f373883cbfe8a

Downstream work MUST reuse this unchanged pinned source rather than rebuild the starter. The pinned commit is the single authoritative starter; no downstream task may regenerate, re-fork, or re-synthesize equivalent starter content.

Candidate stage. This is a Candidate-stage bootcamp item. Its Approved Goal and Approval ID are empty, and its human approval, pay, and attempt fields are empty and are preserved unchanged; this spec does not fill them in and asserts no approval, pay, metric, or human judgment.

### Scope

Describe the pinned synthetic OAuth callback starter whose handler validates only the presence of an authorization `code` and never validates the `state` value against the pending session. The starter preserves a green baseline and the valid success path, and leaves the state-binding repair and the decisive negative-case verification to the recorded human. This is a review/preparation spec only: no code is written, and the pinned recording starter must remain unworked and answer-key-free (no human diagnosis, final fix, or answer key). The current intended mode is GUIDED recording/practice: a separate, disclosed, AI-authored worked reference already exists off-screen in the TaskWorkPlan (authorized, analyzed, disposable-tested), and during capture the human manually executes edits/tests and narrates the actual outcomes from the unchanged unworked starter with no AI interaction during capture. Manual typing from an unworked input does not by itself imply unaided execution. The separate, future human Transfer Test is a distinct UNAIDED assessment, not the current mode and not a prerequisite for guided world prep. Guided references do not establish unaided learning, mastery, paid eligibility, or human approval.

## Requirements

### Requirement 1: Synthetic-only starter

**User Story:** As a task preparer, I want the repository to contain only fabricated content, so that no private source, credentials, or personal data can appear.

#### Acceptance Criteria

1. WHERE recorder-visible names are inspected, THE starter SHALL use fabricated handler logic, sessions, and fixtures only (no private source, credentials, or PII). Reference shape, synthetic: `callback.py`, `fixtures.py`, `run_fixtures.py`, `tests/test_callback.py`. (R1)
2. WHERE the starter is checked out at the pinned source commit `c65f9343be723ea36289db541b8f373883cbfe8a`, THE reviewer SHALL confirm all recorder-visible handler logic and fixtures are synthetic/fabricated with no private source, credentials, or PII, and run with CPython only (no third-party install required). (R1, R9)

### Requirement 2: Documented intended behavior

**User Story:** As a reviewer, I want a concise behavior contract, so that I can determine the intended behavior without being told the defect.

#### Acceptance Criteria

1. THE starter SHALL include a recorder-visible description stating that the callback must bind and validate `state` against the pending session, in clear and testable language, while preserving the valid success path, and SHALL NOT instruct the engineer how to patch the handler. (R2)

### Requirement 3: Reproducible state-binding defect

**User Story:** As a task preparer, I want the implementation to violate a documented behavior, so that the audit has a real defect to find.

#### Acceptance Criteria

1. WHILE inspecting the callback handler against its documented intended behavior, THE reviewer SHALL identify that the handler checks only for presence of `code` and never validates `state` against the pending session, so missing, mismatched, expired, and replayed state are not rejected. This diagnostic-level defect is observable in the pinned starter. (R3, R5)

### Requirement 4: Valid success path preserved

**User Story:** As a reviewer, I want a valid fixture/flow that succeeds, so that a later correction can be shown to preserve it.

#### Acceptance Criteria

1. WHEN the reviewer runs `{python} -m unittest discover -s tests -v` on the pinned starter, THE baseline suite SHALL exit with code 0 and its output SHALL contain `Ran 2 tests`. (R4, R6)
2. WHEN the reviewer runs `{python} run_fixtures.py` on the pinned starter, THE fixture runner SHALL exit with code 0 and its output SHALL contain `"valid"`. (R4, R6)

### Requirement 5: Negative fixtures enumerated, not solved

**User Story:** As a task preparer, I want the invalid-state cases enumerated but unenforced, so that the human performs the real repair.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE fixtures SHALL enumerate valid, missing, mismatched, expired, and replayed state cases while the enforcement that rejects the invalid cases is left for the human, and no recorder-visible file SHALL identify the exact final patch. (R5)

### Requirement 6: Deterministic local run

**User Story:** As a reviewer, I want documented commands, so that the baseline suite and fixture runner run deterministically with no network dependence after checkout.

#### Acceptance Criteria

1. WHERE the starter is checked out at the pinned commit, THE documented baseline suite and fixture runner commands SHALL run deterministically with no network access after checkout, using CPython only. (R6)

### Requirement 7: Unrelated checks stay meaningful

**User Story:** As a reviewer, I want passing baseline checks to remain meaningful, so that a later correction can be shown to preserve the valid success path.

#### Acceptance Criteria

1. WHERE baseline checks are present, THE starter SHALL keep them meaningful and runnable so a later correction can be shown to preserve the valid success path. (R7)

### Requirement 8: No answer key

**User Story:** As a task preparer, I want recorder-visible files free of solutions, so that the recording starter stays unworked.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE starter SHALL contain no completed state validator, no final enforcement of the negative cases, no diagnosis note, and no expected patch diff. (R8)

### Requirement 9: Pre-recording integrity

**User Story:** As a reviewer, I want to confirm the valid case passes and the gap exists while the human work is undone, so that integrity is verified before recording.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE reviewer SHALL be able to confirm (read-only) that the valid case passes, the state-binding gap exists, and the human work remains undone. (R9)

## Glossary

- **Pinned recording starter:** The unchanged, unworked repository at the pinned source commit `c65f9343be723ea36289db541b8f373883cbfe8a` that the human works from during capture.
- **Worked reference:** A separate, disclosed, AI-authored, analyzed, disposable-tested artifact off-screen in the TaskWorkPlan; it does not establish unaided human learning, mastery, paid eligibility, or human approval.
- **Guided recording/practice (current mode):** The human manually executes edits/tests and narrates actual outcomes from the unchanged unworked starter, with no AI interaction during capture. Manual typing from an unworked input does not by itself imply unaided execution.
- **Human Transfer Test (separate, future):** A distinct UNAIDED assessment; not the current mode and not a prerequisite for guided world prep.
- **`{python}`:** The pinned CPython interpreter (dependency profile `python-stdlib`; CPython only, no third-party packages).
- **Governing invariant INV-1:** An OAuth callback MUST reject a request whose `state` is missing, unbound, mismatched, expired, or replayed relative to the pending session, while accepting the valid bound state. The pinned starter intentionally validates only `code` presence and violates this invariant without identifying the final repair.
