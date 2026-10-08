# Requirements Document

## Introduction

This spec is a Kiro spec review/enhancement performed in local session sess_ef9c3844-0570-409c-baa6-7cc73d898476 (executionTarget local) of a spec originally prepared under a prior owner/process. It describes a pinned private starter that already exists; it does not create, rebuild, or re-synthesize that starter, and it does not claim human authorship of the eventual repair. Downstream recorded human work performs the actual diagnosis and repair. The pass normalizes headings to the Kiro canonical format required by `validate_spec_format`, requalifies candidate-task wording, and corrects guided-mode framing without otherwise redrafting the sourced content.

The following paragraph is the exact supplied Goal, reproduced verbatim.

As a backend engineer, repair a synthetic client that incorrectly aggregates a cursor-paginated REST endpoint, preserving server order while handling repeated cursors, empty pages, and duplicate records, and verify the corrected behavior against deterministic response fixtures.

Task Factory row: https://app.notion.com/p/3f28621e0a7a81418d6edfb9a5b43054
Goal+LF SHA256: c08197cea0e65611a4f9d8979822968de9156e24a829c24fea2063e031fd6e86
Source pin: https://github.com/KyPython/cursor-pagination-aggregator@9c829c6ec7f85cf382f97e286bf8acce20a96fe7

Downstream work MUST reuse this unchanged pinned source rather than rebuild the starter. The pinned commit is the single authoritative starter; no downstream task may regenerate, re-fork, or re-synthesize equivalent starter content.

Candidate stage. This is a Candidate-stage bootcamp item. Its Approved Goal and Approval ID are empty, and its human approval, pay, and attempt fields are empty and are preserved unchanged; this spec does not fill them in and asserts no approval, pay, metric, or human judgment.

### Scope

Describe the pinned synthetic cursor-pagination client starter whose aggregator collects pages in response order but does not guard against repeated cursors, empty pages, or duplicate records as the contract requires. The starter preserves a green baseline and the ordinary case, and leaves the edge-case handling and the decisive verification to the recorded human. This is a review/preparation spec only: no code is written, and the pinned recording starter must remain unworked and answer-key-free (no human diagnosis, final fix, or answer key). The current intended mode is GUIDED recording/practice: a separate, disclosed, AI-authored worked reference already exists off-screen in the TaskWorkPlan (authorized, analyzed, disposable-tested), and during capture the human manually executes edits/tests and narrates the actual outcomes from the unchanged unworked starter with no AI interaction during capture. Manual typing from an unworked input does not by itself imply unaided execution. The separate, future human Transfer Test is a distinct UNAIDED assessment, not the current mode and not a prerequisite for guided world prep. Guided references do not establish unaided learning, mastery, paid eligibility, or human approval.

## Requirements

### Requirement 1: Synthetic-only starter

**User Story:** As a task preparer, I want the repository to contain only fabricated content, so that no private source, credentials, or personal data can appear.

#### Acceptance Criteria

1. WHERE recorder-visible names are inspected, THE starter SHALL use fabricated client code, transport, and response fixtures only (no private source, credentials, or PII). Reference shape, synthetic: `src/cursor_client/{__init__.py,aggregator.py,cli.py,fixture_transport.py}`, `tests/{test_aggregator.py,test_fixture_transport.py}`, `fixtures/{ordinary.json,repeated-cursor.json,empty-page.json,duplicate-records.json}`. (R1)
2. WHERE the starter is checked out at the pinned source commit `9c829c6ec7f85cf382f97e286bf8acce20a96fe7`, THE reviewer SHALL confirm all recorder-visible client code and fixtures are synthetic/fabricated with no private source, credentials, or PII, and run with CPython only (no third-party install required). (R1, R9)

### Requirement 2: Documented intended behavior

**User Story:** As a reviewer, I want a concise aggregation contract, so that I can determine the intended behavior without being told the defect.

#### Acceptance Criteria

1. THE starter SHALL include a recorder-visible description stating the aggregation contract — preserve server order while handling repeated cursors, empty pages, and duplicate records — in clear and testable language. (R2)

### Requirement 3: Reproducible aggregation defect

**User Story:** As a task preparer, I want the implementation to violate the documented contract, so that the audit has a real defect to find.

#### Acceptance Criteria

1. WHILE inspecting the aggregator against its documented contract, THE reviewer SHALL identify that the aggregator collects pages in response order but does not guard against repeated cursors, empty pages, or duplicate records. This diagnostic-level defect is observable in the pinned starter. (R3, R5)

### Requirement 4: Ordinary case preserved

**User Story:** As a reviewer, I want the ordinary fixture/flow that passes, so that a later correction can be shown to preserve it.

#### Acceptance Criteria

1. WHEN the reviewer runs `{python} -m unittest discover -s tests -v` with environment `PYTHONPATH=src` on the pinned starter, THE baseline suite SHALL exit with code 0 and its output SHALL contain `Ran 4 tests`. (R4, R6)
2. WHERE the fixtures are inspected, THE starter SHALL include the ordinary fixture plus the repeated-cursor, empty-page, and duplicate-records edge fixtures without wiring the contract-satisfying handling for the edge cases. (R4, R5)

### Requirement 5: Edge fixtures provided, not solved

**User Story:** As a task preparer, I want the edge cases provided but unenforced, so that the human performs the real repair.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE fixtures SHALL provide the ordinary case plus the repeated-cursor, empty-page, and duplicate-records edge cases while the handling that satisfies the contract on the edge cases is left for the human, and no recorder-visible file SHALL identify the exact final patch. (R5)

### Requirement 6: Deterministic local run

**User Story:** As a reviewer, I want a documented command, so that the baseline runs deterministically against the fixtures with no network dependence after checkout.

#### Acceptance Criteria

1. WHERE the starter is checked out at the pinned commit, THE documented baseline command SHALL run deterministically against the fixtures with no network access after checkout, using CPython only. (R6)

### Requirement 7: Unrelated checks stay meaningful

**User Story:** As a reviewer, I want passing baseline checks to remain meaningful, so that a later correction can be shown to preserve the ordinary case and server order.

#### Acceptance Criteria

1. WHERE baseline checks are present, THE starter SHALL keep them meaningful and runnable so a later correction can be shown to preserve the ordinary case and server order. (R7)

### Requirement 8: No answer key

**User Story:** As a task preparer, I want recorder-visible files free of solutions, so that the recording starter stays unworked.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE starter SHALL contain no completed edge-case aggregation, no final failing-then-passing edge-case tests wired to the contract, no diagnosis note, and no expected patch diff. (R8)

### Requirement 9: Pre-recording integrity

**User Story:** As a reviewer, I want to confirm the ordinary case passes and the edge-case gaps exist while the human work is undone, so that integrity is verified before recording.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE reviewer SHALL be able to confirm (read-only) that the ordinary case passes, the edge-case gaps exist, and the human work remains undone. (R9)

## Glossary

- **Pinned recording starter:** The unchanged, unworked repository at the pinned source commit `9c829c6ec7f85cf382f97e286bf8acce20a96fe7` that the human works from during capture.
- **Worked reference:** A separate, disclosed, AI-authored, analyzed, disposable-tested artifact off-screen in the TaskWorkPlan; it does not establish unaided human learning, mastery, paid eligibility, or human approval.
- **Guided recording/practice (current mode):** The human manually executes edits/tests and narrates actual outcomes from the unchanged unworked starter, with no AI interaction during capture. Manual typing from an unworked input does not by itself imply unaided execution.
- **Human Transfer Test (separate, future):** A distinct UNAIDED assessment; not the current mode and not a prerequisite for guided world prep.
- **`{python}`:** The pinned CPython interpreter (dependency profile `python-stdlib`; CPython only, no third-party packages, run with `PYTHONPATH=src`).
- **Governing invariant INV-1:** The aggregator MUST preserve server order while correctly handling repeated cursors, empty pages, and duplicate records across the paginated responses. The pinned starter intentionally aggregates in response order without those guards and violates this invariant without identifying the final repair.
