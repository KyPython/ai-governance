# Requirements Document

## Introduction

This spec is a Kiro spec review/enhancement performed in local session sess_ef9c3844-0570-409c-baa6-7cc73d898476 (executionTarget local) of a spec originally prepared under a prior owner/process. It preserves the prior scope, functional requirements, governing invariant, and task structure, normalizes headings to the Kiro canonical format required by `validate_spec_format`, and corrects over-strict framing. It does not claim prior authorship.

The following paragraph is the exact supplied Goal, reproduced verbatim.

As a software engineer, audit a synthetic grading repository where written evaluation requirements are not fully enforced before grading, identify the missing transfer/CI check, implement one bounded fail-closed validation plus a negative fixture, and verify that the pipeline rejects the defective case while preserving the valid case.

Task Factory row: https://app.notion.com/p/3f08621e0a7a81b49fd3f290ce5e6d8b
Goal+LF SHA256: eae155012790178f9ef10a5f5decd7e9a73c2135d0309ae3491ce542ef80543c
Source pin: https://github.com/KyPython/ci-evaluation-contract@ca532d92ec3db02224061b3ceef105b2bc113b27

Downstream work MUST reuse this unchanged pinned source rather than rebuild the starter. The pinned commit is the single authoritative starter; no downstream task may regenerate, re-fork, or re-synthesize equivalent starter content.

Approval provenance: Odin Approval ID ODIN-219830EEEC244B30A7DE8FFF65B6AB7E. Human approval, pay, and attempt fields are preserved unchanged and are NOT modified by this spec pass.

### Scope

Prepare a synthetic grading repository in which written evaluation requirements are not fully enforced before grading. The environment must expose a real enforcement gap without pre-implementing the final fail-closed validation or final negative fixture. The pinned recording starter must remain unworked. The current intended mode is GUIDED recording/practice: a separate, disclosed, AI-authored worked reference already exists off-screen in the TaskWorkPlan (authorized, analyzed, disposable-tested), and during capture the human manually executes edits/tests and narrates actual outcomes from the unchanged unworked starter with no AI interaction during capture. Manual typing from an unworked input does not by itself imply unaided execution. The separate, future human Transfer Test is a distinct UNAIDED assessment, not the current mode and not a prerequisite for guided world prep. Guided references do not establish unaided learning, mastery, paid eligibility, or human approval.

## Requirements

### Requirement 1: Synthetic-only repository

**User Story:** As a task preparer, I want fabricated requirements, fixtures, and CI config, so that no private content appears.

#### Acceptance Criteria

1. WHERE the starter is checked out at the pinned source commit, THE reviewer SHALL confirm all recorder-visible requirements, fixtures, and config are synthetic/fabricated and run with CPython only (no third-party install required). (R1, R7)

### Requirement 2: Written evaluation contract

**User Story:** As a reviewer, I want a written pre-grading requirement in testable language, so that the enforcement gap can be identified against it.

#### Acceptance Criteria

1. THE recorder-visible document SHALL define at least one mandatory pre-grading requirement in clear, testable language. (R2)

### Requirement 3: Incomplete enforcement boundary

**User Story:** As a task preparer, I want the starter flow to omit enforcement of a written mandatory requirement, so that a defective case can progress farther than the contract permits.

#### Acceptance Criteria

1. WHILE inspecting the written contract against the enforced checks, THE reviewer SHALL identify at least one written mandatory requirement that is not enforced at the transfer/CI boundary. (R2, R3, R6)

### Requirement 4: Valid case preserved

**User Story:** As a reviewer, I want a valid fixture that passes the starter pipeline, so that a later correction can be shown to preserve it.

#### Acceptance Criteria

1. WHEN the reviewer runs `sh scripts/verify.sh` on the pinned starter, THE local pipeline SHALL exit with code 0 and its output SHALL contain `Ran 3 tests`. (R4, R7)
2. WHEN the reviewer runs `{python} -m grader.pipeline fixtures/valid/manifest.json` on the pinned starter, THE grading pipeline SHALL exit with code 0 and its output SHALL contain `sample_001: 3`. (R4, R7)

### Requirement 5: Reproducible defective case

**User Story:** As a reviewer, I want starter scaffolding to expose the unenforced case, so that the human can construct it during recording without the final negative fixture shipping.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE starter SHALL include scaffolding sufficient to expose the unenforced case but SHALL NOT ship the final negative fixture required by the approved deliverable. (R5, R9)

### Requirement 6: Fail-closed target is discoverable, not solved

**User Story:** As a reviewer, I want a bounded validation boundary, so that a human can add one enforcement check without the starter identifying the exact patch.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE code structure SHALL contain a bounded transfer/validation boundary where a human can add one enforcement check, and no recorder-visible file SHALL identify the exact final patch. (R6)

### Requirement 7: Deterministic local CI simulation

**User Story:** As a reviewer, I want a local command that runs the validation/grading sequence deterministically, so that results do not depend on network behavior.

#### Acceptance Criteria

1. THE starter SHALL provide a local command that runs the same validation/grading sequence deterministically. (R7)

### Requirement 8: No weakening

**User Story:** As a reviewer, I want unrelated checks to stay meaningful, so that the eventual correction can be shown to preserve them.

#### Acceptance Criteria

1. WHERE unrelated checks are present, THE starter SHALL keep them meaningful and runnable so a later correction can be shown to preserve them. (R8)

### Requirement 9: No answer key

**User Story:** As a task preparer, I want no completed solution in recorder-visible files, so that the recording starter stays unworked.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE starter SHALL contain no completed fail-closed validator, no final negative fixture, no diagnosis note, and no expected patch diff. (R5, R9)

### Requirement 10: Handoff integrity

**User Story:** As a reviewer, I want to confirm the valid case passes, the gap exists, and the task is undone, so that integrity is verified before recording.

#### Acceptance Criteria

1. WHERE the starter is inspected before recording, THE reviewer SHALL be able to verify the valid case passes, the enforcement gap exists, and the final task remains undone. (R10)

## Glossary

- **Pinned recording starter:** The unchanged, unworked repository at the pinned source commit that the human works from during capture.
- **Worked reference:** A separate, disclosed, AI-authored, analyzed, disposable-tested artifact off-screen in the TaskWorkPlan; it does not establish unaided human learning, mastery, paid eligibility, or human approval.
- **Guided recording/practice (current mode):** The human manually executes edits/tests and narrates actual outcomes from the unchanged unworked starter, with no AI interaction during capture. Manual typing from an unworked input does not by itself imply unaided execution.
- **Human Transfer Test (separate, future):** A distinct UNAIDED assessment; not the current mode and not a prerequisite for guided world prep.
- **INV-1:** The governing invariant (see design `## Correctness Properties`): grading must not begin unless every mandatory pre-grading requirement represented at the transfer boundary has been explicitly validated as satisfied.
- **`{python}`:** The pinned CPython interpreter (dependency profile `python-stdlib`, no third-party packages).
