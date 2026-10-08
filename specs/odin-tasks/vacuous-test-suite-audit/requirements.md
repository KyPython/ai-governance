# Requirements Document

## Introduction

This spec is a Kiro spec review/enhancement performed in local session sess_ef9c3844-0570-409c-baa6-7cc73d898476 (executionTarget local) of a spec originally prepared under a prior owner/process. It preserves the prior scope, functional requirements, and task structure, normalizes headings to the Kiro canonical format required by `validate_spec_format`, and corrects over-strict framing. It does not claim prior authorship.

The following paragraph is the exact supplied Goal, reproduced verbatim.

As a QA engineer, audit a synthetic Python module whose pytest suite passes even though a seeded defect breaks the documented behavior, identify the vacuous assertions that let it pass, rewrite them into meaningful checks, and verify that the strengthened suite fails on the defective build and passes on the corrected build.

Task Factory row: https://app.notion.com/p/3f08621e0a7a81eda36bdd125c60221c
Goal+LF SHA256: ad882a58279d4809c1a4c036554a3400509b50c46bbb58e41f9665d54a30b135
Source pin: https://github.com/KyPython/vacuous-test-suite-audit@c5986e93719cfd4b08a57104576c04a78d1f16ee

Downstream work MUST reuse this unchanged pinned source rather than rebuild the starter. The pinned commit is the single authoritative starter; no downstream task may regenerate, re-fork, or re-synthesize equivalent starter content.

Approval provenance: Odin Approval ID ODIN-5959D60FB16547A0A846BB836D8D0C3F. Human approval, pay, and attempt fields are preserved unchanged and are NOT modified by this spec pass.

### Scope

Prepare a synthetic Python/pytest starter repository for the approved Odin task. This specification governs only the pre-recording starter environment. The pinned recording starter must remain unworked and answer-key-free: it must not contain the human diagnosis, strengthened final assertions, defect repair, completed deliverable, or an answer key. The current intended mode is GUIDED recording/practice: a separate, disclosed, AI-authored worked reference already exists off-screen in the TaskWorkPlan (authorized, analyzed, disposable-tested), and during capture the human manually executes edits/tests and narrates the actual outcomes from the unchanged unworked starter with no AI interaction during capture. Manual typing from an unworked input does not by itself imply unaided execution. The separate, future human Transfer Test is a distinct UNAIDED assessment, not the current mode and not a prerequisite for guided world prep. Guided references do not establish unaided learning, mastery, paid eligibility, or human approval.

## Requirements

### Requirement 1: Synthetic project only

**User Story:** As a task preparer, I want the repository to contain only fabricated content, so that no private source, credentials, or personal data can appear.

#### Acceptance Criteria

1. WHERE recorder-visible names are inspected, THE starter SHALL use only neutral, synthetic names and values and SHALL contain no private source, credentials, Mercor/Odin admin content, or personal data. (R1)

### Requirement 2: Documented behavior

**User Story:** As a reviewer, I want a concise behavior contract, so that I can determine intended behavior without being told the defect.

#### Acceptance Criteria

1. THE starter SHALL include a concise product/module behavior contract that a reviewer can use to determine the intended behavior without being told the defect. (R2)

### Requirement 3: Seeded behavioral defect

**User Story:** As a task preparer, I want the implementation to violate a documented behavior, so that the audit has a real defect to find.

#### Acceptance Criteria

1. WHILE comparing `docs/behavior.md` to the implementation, THE reviewer SHALL be able to demonstrate that a real documented behavior is false while the weak suite remains green. (R3, R6)

### Requirement 4: Vacuous passing suite

**User Story:** As a task preparer, I want the initial suite to pass despite the defect, so that the human can audit why the assertions are insufficient.

#### Acceptance Criteria

1. WHEN the reviewer runs `{venvPython} -m pytest -q` on the pinned starter, THE baseline suite SHALL exit with code 0 and its output SHALL contain `8 passed`. (R4, R5)
2. THE weak assertions SHALL look superficially plausible rather than being obvious placeholders. (R4)

### Requirement 5: Independent reproduction

**User Story:** As a reviewer, I want a single documented command, so that the passing suite reproduces from a clean checkout.

#### Acceptance Criteria

1. WHERE the starter is checked out at the pinned source commit and the pinned toolchain is installed from `requirements-dev.txt` into `.venv`, THE clean setup SHALL complete using the declared Python/pytest toolchain (`pytest==8.3.5`). (R1, R5, R8)

### Requirement 6: Human-discoverable evidence

**User Story:** As a reviewer, I want enough observable behavior and documentation, so that a QA engineer can discover the suite is insufficient through inspection and execution.

#### Acceptance Criteria

1. THE repository SHALL provide enough observable behavior and documentation for a software/QA engineer to discover that the suite is insufficient through inspection and execution during TaskRecorder. (R6)

### Requirement 7: No solution leakage

**User Story:** As a task preparer, I want recorder-visible files free of solutions, so that the recording starter stays unworked.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE starter SHALL state no final correction, SHALL identify no vacuous assertion, and SHALL provide no ready-to-paste strengthened assertions or hidden solution suite. (R7)

### Requirement 8: Deterministic tooling

**User Story:** As a reviewer, I want deterministic local setup and baseline commands, so that runs do not depend on network behavior after install.

#### Acceptance Criteria

1. WHILE the recording envelope is 15:00–45:59, THE baseline command SHALL complete quickly enough to support diagnosis and at least two verification runs without long idle waits, and no completed solution SHALL be present. (R8, R10)

### Requirement 9: Packaging

**User Story:** As a reviewer, I want a neutral README with setup/run instructions only, so that packaging reveals no diagnosis.

#### Acceptance Criteria

1. WHERE the repository root is inspected, THE starter SHALL include a neutral README limited to setup/run instructions plus one documented baseline command/script. (R9)

### Requirement 10: Pre-recording integrity

**User Story:** As a reviewer, I want to confirm the defect and weak suite exist and no solution exists, so that integrity is verified before recording.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE starter SHALL contain the defective code and weak suite and SHALL contain no completed solution before recording. (R10)

## Glossary

- **Pinned recording starter:** The unchanged, unworked repository at the pinned source commit that the human works from during capture.
- **Worked reference:** A separate, disclosed, AI-authored, analyzed, disposable-tested artifact off-screen in the TaskWorkPlan; it does not establish unaided human learning, mastery, paid eligibility, or human approval.
- **Guided recording/practice (current mode):** The human manually executes edits/tests and narrates actual outcomes from the unchanged unworked starter, with no AI interaction during capture. Manual typing from an unworked input does not by itself imply unaided execution.
- **Human Transfer Test (separate, future):** A distinct UNAIDED assessment; not the current mode and not a prerequisite for guided world prep.
- **`{venvPython}`:** The `.venv` interpreter (dependency profile `python-pytest`, `pytest==8.3.5`, dev deps in `requirements-dev.txt`).
- **Recording envelope:** The 15:00–45:59 window supporting diagnosis and at least two verification runs.
