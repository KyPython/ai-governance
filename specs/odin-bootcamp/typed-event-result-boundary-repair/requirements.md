# Requirements Document

## Introduction

This spec is a Kiro spec authoring pass performed in local session UNKNOWN (executionTarget local) — no genuine Kiro execution/session identifier was available in this environment, so none is recorded; a `sess_...` value is intentionally NOT invented here. It describes a self-contained local TypeScript starter and the diagnostic-level, result-boundary defect to be repaired by downstream recorded human work. It does not create, rebuild, or re-synthesize that starter, does not write the fix, and does not claim human authorship of the eventual repair. The pass normalizes headings to the Kiro canonical format, states requirements with MUST/MUST NOT/SHALL language, and keeps the pinned recording starter unworked and answer-key-free.

The following paragraph is the exact supplied Goal, reproduced verbatim.

As a TypeScript engineer, repair a synthetic service boundary whose loosely handled success and failure results cause callers to treat an error payload as a successful value, then verify exhaustive result handling and deterministic API behavior.

Task Factory row: https://app.notion.com/p/3f58621e0a7a811998f1d9057fe5045a
ODIN_BOOTCAMP_SPEC_ROW_ID: 3f58621e-0a7a-8119-98f1-d9057fe5045a
Notion row link: https://app.notion.com/p/Typed-Event-Result-Boundary-Repair-3f58621e0a7a811998f1d9057fe5045a
Spec path: specs/odin-bootcamp/typed-event-result-boundary-repair

Downstream work MUST reuse the pinned local TypeScript starter unchanged rather than rebuild it. No downstream task may regenerate, re-fork, or re-synthesize equivalent starter content.

Variation axis (distinctness): discriminated result contract / exhaustive narrowing / success-failure boundary.

Candidate stage. This is a Candidate-stage bootcamp item. Its Approved Goal and Approval ID are empty, and its human approval, pay, and attempt fields are empty and are preserved unchanged; this spec does not fill them in and asserts no approval, pay, metric, or human judgment. No KIRO_RECEIPT_COMMIT or KIRO_RECEIPT_SHA256 is produced or claimed here; receipts are produced by a separate downstream publisher after an actual completed review and are out of scope.

### Scope

Describe the pinned, self-contained local TypeScript starter: a small service function, a written success/failure contract, a caller, synthetic fixtures, a seeded result-handling defect, ordinary tests, and a repeatable type-check/test command. The seeded defect is that success and failure results are handled loosely, so a caller treats an error payload as a successful value. The starter preserves ordinary (non-decisive) tests and leaves the typed success/failure repair and the decisive malformed-result verification to the recorded human.

This is a spec-only, preparation spec: no code is written, no diagnosis is performed, no decisive tests are added, no deliverable is completed, and no answer key appears. Automation preparing the starter MUST STOP before selecting the correct result abstraction, modifying the implementation, adding decisive malformed-result assertions, or including a solution diff.

Boundary of scope: no network, credentials, private code, or external package service may be required to check out, type-check, or run the starter. The decisive mechanism — typed success/failure representation and caller-side exhaustiveness (discriminated result contracts, exhaustive narrowing, runtime validation at a service boundary) — is distinct from Lambda event-shape normalization, OAuth state-binding validation, regex repair, CI contract transfer, and async idempotency.

Evidence states are kept distinct throughout: verified current behavior (the loose-handling defect observable in the starter), intended behavior (exhaustive, typed success/failure handling), verified failures (the strengthened error-boundary/malformed-result check fails on the defective starter), unknowns requiring reproduction (actual run output and exit codes, observed only after a later authorized run), and proposed implementation constraints (the typed-result/exhaustiveness mechanism). Local verification does NOT establish production transport or observability behavior.

## Requirements

### Requirement 1: Self-contained local TypeScript starter

**User Story:** As a task preparer, I want the starter to be a self-contained local TypeScript package, so that no network, credentials, private code, or external package service is required to work it.

#### Acceptance Criteria

1. WHERE the starter is inspected, THE starter SHALL be a self-contained local TypeScript package containing a small service function, a written success/failure contract, a caller, synthetic fixtures, a seeded result-handling defect, ordinary tests, and a repeatable type-check/test command. (R1)
2. WHERE checkout and setup are inspected, THE starter MUST NOT require network access, credentials, private code, or an external package service to check out, type-check, or run after setup. (R1, R3)

### Requirement 2: Documented success/failure contract

**User Story:** As a reviewer, I want a written success/failure contract, so that intended behavior is clear without being told the defect or the fix.

#### Acceptance Criteria

1. THE starter SHALL include a recorder-visible written contract stating the intended success and failure result semantics at the service boundary in clear and testable language, and SHALL NOT instruct the engineer how to repair the result handling. (R2)

### Requirement 3: Reproducible result-handling defect

**User Story:** As a task preparer, I want the implementation to violate the documented contract, so that the audit has a real defect to find.

#### Acceptance Criteria

1. WHILE inspecting the service boundary and caller against the documented contract, THE reviewer SHALL identify that success and failure results are handled loosely so that a caller treats an error payload as a successful value, and that failure, malformed, and unexpected-state results are not exhaustively narrowed. This diagnostic-level defect MUST be observable in the pinned starter. (R3, R4)

### Requirement 4: Defective starter fails a strengthened result-boundary check

**User Story:** As a reviewer, I want the defect to be detectable, so that a strengthened error-boundary/malformed-result check fails before repair.

#### Acceptance Criteria

1. WHERE a strengthened error-boundary/malformed-result check is applied to the pinned (unrepaired) starter, THE check SHALL fail, demonstrating that the caller can treat an error payload as a successful value. This spec DESCRIBES that failing check; it MUST NOT add, author, or include the decisive assertion. (R4)

### Requirement 5: Ordinary tests enumerated, decisive assertions not solved

**User Story:** As a task preparer, I want the ordinary tests present but the decisive malformed-result assertions absent, so that the human performs the real repair and verification.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE starter SHALL include ordinary tests and synthetic fixtures covering success, expected failure, malformed input, unexpected state, and caller propagation cases, WHILE the decisive malformed-result assertions and the typed exhaustiveness enforcement are left for the human. (R5)
2. WHERE recorder-visible files are inspected, no file SHALL contain the correct result abstraction, a modified implementation, decisive malformed-result assertions, or a solution diff. (R5, R8)

### Requirement 6: Repeatable, deterministic type-check/test command

**User Story:** As a reviewer, I want a repeatable command, so that type checking and tests run deterministically and produce identical results across repeated runs with no network dependence after setup.

#### Acceptance Criteria

1. WHERE the starter is checked out, THE documented type-check/test command SHALL run deterministically with no network access after setup and SHALL produce identical results across repeated runs. (R6, R1)

### Requirement 7: Preserved response shapes and status decisions

**User Story:** As a reviewer, I want the exact response shapes and status decisions preserved, so that a later correction can be shown to keep API behavior unchanged on the valid path.

#### Acceptance Criteria

1. WHERE the service boundary response is inspected, THE starter SHALL document the exact response shapes and status decisions that a later repair MUST preserve for success, expected failure, malformed input, unexpected state, and caller propagation, so a correction can be shown to keep them unchanged. (R7)

### Requirement 8: No answer key

**User Story:** As a task preparer, I want recorder-visible files free of solutions, so that the recording starter stays unworked.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE starter SHALL contain no completed typed-result abstraction, no final exhaustive-narrowing implementation, no decisive malformed-result assertions, no diagnosis note, and no expected patch diff. (R8)

### Requirement 9: Pre-recording integrity

**User Story:** As a reviewer, I want to confirm the ordinary tests behave and the gap exists while the human work is undone, so that integrity is verified before recording.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE reviewer SHALL be able to confirm (read-only) that the ordinary tests and type-check command run, the result-handling gap exists (caller can treat an error payload as success), and the human diagnosis, repair, and decisive verification remain undone. (R9)

### Requirement 10: Local-only verification claim

**User Story:** As KyJahn, I want out-of-scope limits stated honestly, so that local verification is not overclaimed.

#### Acceptance Criteria

1. THE starter and this spec MUST document that local verification establishes typed success/failure handling and deterministic local API behavior only, and MUST NOT claim it establishes production transport or observability behavior. (R10)

## Glossary

- **Pinned recording starter:** The unchanged, unworked self-contained local TypeScript package that the human works from during capture.
- **Discriminated result contract:** A typed representation of a boundary result that distinguishes success from failure by a discriminant, enabling exhaustive narrowing.
- **Exhaustive narrowing:** Caller-side handling that accounts for every variant of the result union, so no failure or unexpected state is silently treated as success.
- **Success-failure boundary:** The service boundary where a result crosses into a caller; the seeded defect lets an error payload be read as a successful value here.
- **Strengthened result-boundary check:** A decisive malformed-result/error-boundary assertion the recorded human adds; it fails on the defective starter and passes after repair. Not authored in this spec.
- **Ordinary tests:** Non-decisive tests present in the starter covering success, expected failure, malformed input, unexpected state, and caller propagation without enforcing the decisive malformed-result cases.
- **Local-only verification:** Type checking plus deterministic local tests; it does not establish production transport or observability behavior.
- **Candidate stage:** Approved Goal, Approval ID, human approval, pay, and attempt fields are empty and preserved empty; no approval, pay, metric, or human judgment is asserted.
- **Receipts (out of scope):** KIRO_RECEIPT_COMMIT / KIRO_RECEIPT_SHA256 are produced by a separate downstream publisher after an actual completed review; none is produced or claimed here.
