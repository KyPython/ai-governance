# Requirements Document

## Introduction

This spec is a Kiro spec review/enhancement performed in local session sess_82309770-7349-46bb-ab4b-ae3a937b8c7f (executionTarget local). It describes a synthetic starter that does **not yet exist**: the starter is prepared downstream only after @KyPython merges this specs-only PR. This pass does not create, build, or re-synthesize that starter, writes no code, and does not claim human authorship of the eventual repair. Downstream recorded human work performs the actual diagnosis and repair. The pass normalizes headings to the Kiro canonical format required by `validate_spec_format`, qualifies the candidate-task wording, and keeps guided-mode framing honest without redrafting the sourced content.

The following paragraph is the exact supplied Goal, reproduced verbatim.

As a requirements engineer, repair a synthetic change-request package whose updated requirement, acceptance criteria, and verification links are inconsistent, then produce a deterministic traceability report showing the approved change is complete and no obsolete acceptance path remains.

Task factory row: https://app.notion.com/p/3f68621e0a7a815da0b3d1f6ea87533e
ODIN_BOOTCAMP_SPEC_ROW_ID: 3f68621e-0a7a-815d-a0b3-d1f6ea87533e
Relates to #210.
Source pin: UNKNOWN — pending downstream preparation (to be bound at preparation time, after merge). No commit SHA, no Goal+LF SHA256, and no source-pin URL exist yet; none is invented here.

Downstream work MUST prepare the synthetic starter after merge and then bind the exact source pin; it MUST NOT be regenerated, re-forked, or re-synthesized once bound. Until that preparation occurs, every reference to "the pinned starter" below denotes the future pinned starter to be bound downstream, not an existing artifact.

Candidate stage. This is a Candidate-stage internal Bootcamp item. Its Approved Goal and Approval ID are empty, and its human approval, pay, and attempt fields are empty and are preserved unchanged; this spec does not fill them in and asserts no approval, pay, metric, or human judgment.

### Scope

Describe the future synthetic change-control starter: a self-contained local package holding a requirements baseline, one approved change request, acceptance criteria, a traceability matrix, deterministic fixtures, ordinary checks, and a repeatable validation command, with a seeded stale-link or misclassification defect so that the updated requirement, its acceptance criteria, and its verification links are mutually inconsistent. The starter preserves a green baseline and leaves the requirement-classification decision, the impact set, the artifact/validator repair, the decisive negative checks, and the deterministic traceability report to the recorded human. This is a review/preparation spec only: no code is written, and the future recording starter must be prepared unworked and answer-key-free (no human diagnosis, final fix, decisive negative checks, or answer key). The current intended mode is GUIDED recording/practice: a separate, disclosed, AI-authored worked reference may exist off-screen in the TaskWorkPlan (authorized, analyzed, disposable-tested), and during capture the human manually executes edits/checks and narrates the actual outcomes from the unchanged unworked starter with no AI interaction during capture. Manual typing from an unworked input does not by itself imply unaided execution. The separate, future human Transfer Test is a distinct UNAIDED assessment, not the current mode and not a prerequisite for guided world prep. Guided references do not establish unaided learning, mastery, paid eligibility, or human approval.

## Requirements

### Requirement 1: Synthetic-only starter

**User Story:** As a task preparer, I want the downstream package to contain only fabricated content, so that no private, production, network, or third-party data can appear.

#### Acceptance Criteria

1. WHERE recorder-visible names are inspected, THE prepared starter SHALL use fabricated requirements, change request, acceptance criteria, traceability matrix, and fixtures only (no private, production, network, or third-party data, no credentials, no PII). Reference shape, synthetic: a requirements baseline, one approved change request, acceptance criteria, a traceability matrix, deterministic fixtures, ordinary checks, and a repeatable validation command. (R1)
2. WHERE the starter is checked out at the future pinned source commit (to be bound downstream after merge), THE reviewer SHALL confirm all recorder-visible content is synthetic/fabricated with no private, production, network, or third-party data, and runs with the pinned local interpreter only (no third-party install required). (R1, R10)

### Requirement 2: Documented intended behavior

**User Story:** As a reviewer, I want a concise behavior contract, so that I can determine the intended behavior without being told the defect.

#### Acceptance Criteria

1. THE prepared starter SHALL include a recorder-visible description stating that the approved change must be traceable end to end — requirement identifiers and classifications are valid, the change connects to acceptance evidence, no stale or duplicate links remain, and unresolved trace gaps are reported — in clear and testable language. (R2)

### Requirement 3: Reproducible traceability/stale-link defect

**User Story:** As a task preparer, I want the change-request package to be internally inconsistent, so that the audit has a real defect to find.

#### Acceptance Criteria

1. WHILE inspecting the updated requirement against its acceptance criteria and verification links, THE reviewer SHALL identify that the updated requirement, acceptance criteria, and verification links are mutually inconsistent — a stale/obsolete acceptance path, duplicate identifier, or misclassification remains. This diagnostic-level defect is observable in the prepared starter. (R3)

### Requirement 4: Reproducible classification/impact defect

**User Story:** As a task preparer, I want the change-impact classification to be wrong or incomplete, so that the audit has a second real defect to find.

#### Acceptance Criteria

1. WHILE inspecting the change request against the baseline, THE reviewer SHALL identify that the requirement classification or the impact set is inconsistent with the approved change (an affected work product or acceptance link is misclassified or missing). This diagnostic-level defect is observable in the prepared starter. (R4)

### Requirement 5: Green baseline preserved

**User Story:** As a reviewer, I want the baseline checks to pass deterministically, so that the prepared starter is a known-good green starting point.

#### Acceptance Criteria

1. WHEN the reviewer runs the repeatable validation command documented in the prepared starter, THE baseline SHALL exit with code 0 and its output SHALL match the baseline exit code and output substring to be bound downstream at preparation time. (R5, R7)

### Requirement 6: Deliverable discoverable, not solved

**User Story:** As a task preparer, I want the deterministic traceability report and repair left for the human, so that the human performs the real repair.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE required deterministic traceability report and artifact/validator repair SHALL remain the human deliverable — the requirement-classification decision, the impact set, the repaired links, and the decisive negative checks are left for the human — and no recorder-visible file SHALL identify the exact final patch. (R6)

### Requirement 7: Deterministic local run

**User Story:** As a reviewer, I want a documented command, so that the baseline runs deterministically with no network dependence after checkout and serialized reports are byte-identical across repeated runs.

#### Acceptance Criteria

1. WHERE the starter is checked out at the future pinned commit, THE documented validation command SHALL run deterministically with no network access after checkout, using the pinned local interpreter only, and repeated runs SHALL produce byte-identical serialized reports. (R7)

### Requirement 8: Unrelated checks stay meaningful

**User Story:** As a reviewer, I want passing baseline checks to remain meaningful, so that a later correction can be shown to preserve unaffected requirements.

#### Acceptance Criteria

1. WHERE baseline checks are present, THE prepared starter SHALL keep them meaningful and runnable so a later correction can be shown to preserve unaffected requirements. (R8)

### Requirement 9: No answer key

**User Story:** As a task preparer, I want recorder-visible files free of solutions, so that the recording starter stays unworked.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE prepared starter SHALL contain no chosen requirement classification, no decided impact set, no repaired links or artifacts, no decisive negative checks, no completed deterministic traceability report, no diagnosis note, and no expected patch diff. (R9)

### Requirement 10: Pre-recording integrity

**User Story:** As a reviewer, I want to confirm the baseline is green and both defects exist while the human work is undone, so that integrity is verified before recording.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE reviewer SHALL be able to confirm (read-only) that the baseline is green, both the traceability/stale-link defect and the classification/impact defect exist, and the human work remains undone. (R10)

## Glossary

- **Future pinned recording starter:** The unchanged, unworked synthetic package to be prepared downstream after merge and bound at a source commit (UNKNOWN until preparation time) that the human works from during capture. No pin exists yet.
- **Change request:** The one approved change to the requirements baseline whose updated requirement, acceptance criteria, and verification links must be reconciled.
- **Traceability matrix:** The mapping from requirement identifiers to acceptance criteria and verification links, used to detect stale/duplicate links and unresolved trace gaps.
- **Obsolete/stale acceptance path:** An acceptance link that the approved change should have removed or redirected but which still remains.
- **Worked reference:** A separate, disclosed, AI-authored, analyzed, disposable-tested artifact off-screen in the TaskWorkPlan; it does not establish unaided human learning, mastery, paid eligibility, or human approval.
- **Guided recording/practice (current mode):** The human manually executes edits/checks and narrates actual outcomes from the unchanged unworked starter, with no AI interaction during capture. Manual typing from an unworked input does not by itself imply unaided execution.
- **Human Transfer Test (separate, future):** A distinct UNAIDED assessment; not the current mode and not a prerequisite for guided world prep.
- **Governing invariant INV-1:** The deterministic traceability report MUST show that the approved change is complete — every requirement identifier and classification is valid, unaffected requirements are preserved, the approved change is connected to acceptance evidence, stale or duplicate links are rejected, unresolved trace gaps are reported explicitly, and repeated runs produce byte-identical serialized reports — with no obsolete acceptance path remaining. The prepared starter intentionally leaves the updated requirement, acceptance criteria, and verification links inconsistent (a stale/obsolete link, duplicate identifier, or misclassification), violating this invariant without identifying the final repair.
