# Requirements Document

## Introduction

This spec is a Kiro spec-authoring pass for the Odin bootcamp item "Resilient Architecture Decision Matrix Repair." It describes a synthetic starter that downstream automation will later prepare and pin; this spec does not create, rebuild, or re-synthesize that starter, does not select the correct architecture, does not state the decision-rule fix, and does not claim human authorship of the eventual repair. Downstream recorded human work performs the actual diagnosis and repair. The pass follows the Kiro canonical headings required by `validate_spec_format`, keeps candidate-task framing, and leaves all solution content out.

The following paragraph is the exact supplied Goal, reproduced verbatim.

As a cloud architect, repair a synthetic architecture decision evaluator that selects an unsuitable disaster-recovery design under changed workload constraints, then verify that its deterministic scenario matrix selects the defensible resilient architecture and explains the decisive tradeoffs.

ODIN_BOOTCAMP_SPEC_ROW_ID:3f68621e-0a7a-81c9-8b3e-d3d2e5695ea7
Task Factory row: https://app.notion.com/p/3f68621e0a7a81c98b3ed3d2e5695ea7
KIRO_SPEC_EXECUTION_ID:6f62ebf4-6d71-4d73-91c5-7bdabf1ac08f

Relates to #209
Relates to #12

Downstream work MUST reuse the prepared pinned source unchanged rather than rebuild the starter. The eventual pinned commit is the single authoritative starter; no downstream task may regenerate, re-fork, or re-synthesize equivalent starter content.

Candidate stage. This is a Candidate-stage bootcamp item. Its Approved Goal and Approval ID are empty (internal practice only; Odin approval pending), and its human approval, pay, and attempt fields are empty and are preserved unchanged; this spec does not fill them in and asserts no approval, pay, metric, or human judgment.

HOLD status. This item stays on HOLD until captured evidence, a spec PASS, a private receipt, and a human (Ky) merge all exist together. `KIRO_RECEIPT_COMMIT` and `KIRO_RECEIPT_SHA256` are produced only by the real authenticated publisher after a completed review and human merge; they remain HOLD/pending here and MUST NEVER be manufactured. A PASS receipt MUST NOT be fabricated.

### Scope

Describe the prepared synthetic disaster-recovery architecture-decision starter: a written synthetic recovery policy; deterministic workload and failure scenarios; three abstract architecture options; a deterministic scenario-matrix evaluator that currently selects an unsuitable disaster-recovery design under changed workload constraints (a seeded selection-or-boundary defect); ordinary tests that preserve a green baseline; and a repeatable report command. The starter stops before selecting the correct architecture, changing the decision rule, adding the decisive changed scenarios, or including any solution diff. No AWS account, credentials, cloud deployment, network access, or provider interaction is required at any point. The variation axis is disaster-recovery taxonomy / resilience constraints / architecture tradeoff evaluation. The architecture options and the recovery policy are abstract and synthetic; this spec names no real cloud provider service as the required answer. This is a review/preparation spec only: no code, tests, fixtures, scenarios, decision rule, diagnosis, or answer key are written here, and the recording starter must remain unworked and answer-key-free. The current intended mode is GUIDED recording/practice: during capture the human manually executes edits/tests and narrates actual outcomes from the unchanged unworked starter with no AI interaction during capture. Manual typing from an unworked input does not by itself imply unaided execution. A separate, future human Transfer Test is a distinct UNAIDED assessment, not the current mode and not a prerequisite for guided world prep. Guided references do not establish unaided learning, mastery, paid eligibility, or human approval.

### Distinctness

No existing factory fingerprint centers on deterministic disaster-recovery pattern selection from RTO/RPO and dependency constraints. This item differs from the asynchronous side-effect idempotency and SLO/cost-gate tasks because the central mechanism is architecture option comparison under resilience constraints, not duplicate side-effect prevention or telemetry accounting; it provides a focused SAA D2 resilience practice lane rather than generic architecture documentation.

### Human transfer requirement (human-only; not performed here)

Unaided, the human will inspect the written recovery policy, synthetic workload scenarios, architecture options, current evaluator, fixtures, and failing evidence; diagnose why the current decision is wrong; choose and implement the smallest defensible repair to the decision model or scenario evaluation; verify ordinary, exact-threshold, conflicting-constraint, dependency-failure, and repeated-run cases; compare the selected option with at least one alternative; then teach back the decisive resilience mechanism, tradeoff, and evidence boundary without revealing or relying on a solution key. This spec does not perform or pre-empt any of that work.

### Professional judgment (documented, not resolved here)

The human will translate recovery-time, recovery-point, dependency, cost, and operational constraints into explicit acceptance rules; distinguish pilot light, warm standby, and active-active behavior; decide how conflicting constraints and boundary values are handled; and explain why the selected design satisfies the stated failure-domain and recovery requirements. This spec records that these are the judgment points; it does not make them.

## Requirements

### Requirement 1: Synthetic-only starter

**User Story:** As a task preparer, I want the repository to contain only fabricated content, so that no private source, credentials, or personal data can appear.

#### Acceptance Criteria

1. WHERE recorder-visible names are inspected, THE starter SHALL use fabricated evaluator code, workload/failure scenarios, recovery policy, and architecture options only (no private source, credentials, or PII). (R1)
2. WHERE the starter is checked out at its pinned source commit, THE reviewer SHALL confirm all recorder-visible evaluator code, scenarios, recovery policy, and architecture options are synthetic/fabricated with no private source, credentials, or PII, and that no AWS account, credentials, cloud deployment, network access, or provider interaction is required. (R1, R10)

### Requirement 2: Documented intended behavior

**User Story:** As a reviewer, I want a concise behavior contract, so that I can determine the intended behavior without being told the defect or the answer.

#### Acceptance Criteria

1. THE starter SHALL include a recorder-visible description stating that the deterministic scenario matrix must select the defensible resilient architecture by consistently applying the written RTO/RPO, dependency, cost, and operational constraints — distinguishing pilot light, warm standby, and active-active behavior — and must explain the decisive tradeoffs, in clear and testable language, without naming the correct option. (R2)

### Requirement 3: Reproducible selection/boundary defect under changed constraints

**User Story:** As a task preparer, I want the evaluator to select an unsuitable disaster-recovery design under the changed workload constraints, so that the audit has a real defect to find.

#### Acceptance Criteria

1. WHILE inspecting the evaluator's output against the written recovery policy under the changed workload constraints, THE reviewer SHALL identify that the evaluator selects an unsuitable disaster-recovery design because of a seeded selection or boundary defect in the decision model or scenario evaluation. This diagnostic-level defect is observable in the pinned starter and is described without stating the fix. (R3)

### Requirement 4: Strengthened changed-scenario / recovery-boundary failure exists

**User Story:** As a task preparer, I want the defective evaluator to fail at least one strengthened changed-scenario or recovery-boundary check, so that the defect is demonstrable.

#### Acceptance Criteria

1. WHERE a strengthened changed-scenario or recovery-boundary check is applied, THE defective evaluator SHALL fail at least one such check, demonstrating the seeded defect without the check itself being added to the recorder-visible starter by this spec. (R4)

### Requirement 5: Green baseline preserved

**User Story:** As a reviewer, I want the ordinary baseline suite to pass deterministically, so that the starter is a known-good green starting point.

#### Acceptance Criteria

1. WHEN the reviewer runs the documented repeatable report/test command on the pinned starter, THE ordinary baseline suite SHALL pass deterministically (exit code 0) as recorded in the prep registry. (R5, R7)

### Requirement 6: Deliverable discoverable, not solved

**User Story:** As a task preparer, I want the defensible selection and rationale left for the human, so that the human performs the real repair.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE defensible resilient-architecture selection, the corrected decision rule, the decisive changed scenarios, and the tradeoff rationale SHALL remain the human deliverable, and no recorder-visible file SHALL identify the correct option, the decision-rule fix, or the final patch. (R6)

### Requirement 7: Deterministic, offline local run

**User Story:** As a reviewer, I want a documented command, so that the baseline and report run deterministically with no network dependence after checkout.

#### Acceptance Criteria

1. WHERE the starter is checked out at the pinned commit, THE documented repeatable report command SHALL run deterministically with no network access, no cloud deployment, and no provider interaction after checkout, and SHALL emit identical serialized reports across repeated runs. (R7)

### Requirement 8: Unrelated checks stay meaningful

**User Story:** As a reviewer, I want passing baseline checks to remain meaningful, so that a later correction can be shown to preserve them.

#### Acceptance Criteria

1. WHERE baseline checks are present, THE starter SHALL keep them meaningful and runnable so a later correction can be shown to preserve them. (R8)

### Requirement 9: No answer key

**User Story:** As a task preparer, I want recorder-visible files free of solutions, so that the recording starter stays unworked.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE starter SHALL contain no correct architecture selection, no corrected decision rule, no decisive changed scenarios, no diagnosis note, and no expected patch diff. (R9)

### Requirement 10: Pre-recording integrity

**User Story:** As a reviewer, I want to confirm the baseline is green and the defect exists while the human work is undone, so that integrity is verified before recording.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE reviewer SHALL be able to confirm (read-only) that the baseline is green, the seeded selection/boundary defect exists under the changed constraints, and the human work remains undone. (R10)

### Requirement 11: Safe handling of incomplete or contradictory scenario data

**User Story:** As a reviewer, I want the intended behavior to require rejecting incomplete or contradictory scenario data, so that the repaired evaluator cannot silently select an unsafe option.

#### Acceptance Criteria

1. THE recorder-visible behavior contract SHALL state that the repaired evaluator must reject incomplete or contradictory scenario data rather than silently selecting an unsafe option, expressed as a testable requirement, without stating how the repair implements it. (R11)

## Glossary

- **Pinned recording starter:** The unchanged, unworked repository at the prepared pinned source commit that the human works from during capture.
- **Scenario matrix:** The deterministic mapping from workload/failure scenarios and the written recovery policy to a selected architecture option, evaluated with no network access.
- **Recovery policy:** The written synthetic statement of RTO/RPO, dependency, cost, and operational constraints the selection must honor.
- **Architecture options (abstract):** Three synthetic, provider-neutral recovery designs under comparison; characterized here only by resilience behavior (e.g., pilot light / warm standby / active-active families) and never resolved to a correct choice.
- **Worked reference:** A separate, disclosed, AI-authored, analyzed, disposable-tested artifact off-screen in the TaskWorkPlan; it does not establish unaided human learning, mastery, paid eligibility, or human approval.
- **Guided recording/practice (current mode):** The human manually executes edits/tests and narrates actual outcomes from the unchanged unworked starter, with no AI interaction during capture. Manual typing from an unworked input does not by itself imply unaided execution.
- **Human Transfer Test (separate, future):** A distinct UNAIDED assessment; not the current mode and not a prerequisite for guided world prep.
- **Governing invariant INV-1:** The evaluator MUST select the defensible resilient architecture by consistently applying the written RTO/RPO, dependency, cost, and operational constraints — distinguishing pilot light / warm standby / active-active behavior — rather than the unsuitable option, without this spec stating the final repair.
