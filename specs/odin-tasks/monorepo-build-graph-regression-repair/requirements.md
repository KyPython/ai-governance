# Requirements Document

## Introduction

This spec is a Kiro spec review/enhancement performed in local session sess_ef9c3844-0570-409c-baa6-7cc73d898476 (executionTarget local) of a spec originally prepared under a prior owner/process. It preserves the prior scope, functional requirements, and task structure, normalizes headings to the Kiro canonical format required by `validate_spec_format`, and corrects over-strict framing. It does not claim prior authorship.

The following paragraph is the exact supplied Goal, reproduced verbatim.

Diagnose and repair a synthetic pnpm/Turborepo build regression so an engineering team can restore reliable builds after a shared workspace dependency gains its own build step and one build configuration still references an obsolete package name.

Task Factory row: https://app.notion.com/p/3f08621e0a7a818f8a72f73e8d4e4da0
Goal+LF SHA256: 54d506c1f74e626aa6126b9df52d0adbfd337a211606a85a1d320010f43e7160
Source pin: https://github.com/KyPython/monorepo-build-graph@2ddf3c8f2a0e054ea2e40ab077c5a48132c34a38

Downstream work MUST reuse this unchanged pinned source rather than rebuild the starter. The pinned commit is the single authoritative starter; no downstream task may regenerate, re-fork, or re-synthesize equivalent starter content.

Approval provenance: Odin Approval ID ODIN-ED6E74BA231E41F0A6386D49E67DE48F. Human approval, pay, and attempt fields are preserved unchanged and are NOT modified by this spec pass.

### Scope

Prepare a synthetic pnpm/Turborepo monorepo with a reproducible service build regression caused by two independently observable configuration problems described by the approved task: a shared workspace dependency now has its own build step, and one build/container configuration still references an obsolete package name. The pinned recording starter must remain unworked: do not include the final repairs. The current intended mode is GUIDED recording/practice: a separate, disclosed, AI-authored worked reference already exists off-screen in the TaskWorkPlan (authorized, analyzed, disposable-tested), and during capture the human manually executes edits/tests and narrates actual outcomes from the unchanged unworked starter with no AI interaction during capture. Manual typing from an unworked input does not by itself imply unaided execution. The separate, future human Transfer Test is a distinct UNAIDED assessment, not the current mode and not a prerequisite for guided world prep. Guided references do not establish unaided learning, mastery, paid eligibility, or human approval.

## Requirements

### Requirement 1: Synthetic monorepo only

**User Story:** As a task preparer, I want fabricated package/service names and configuration, so that no private source or data appears in a recording.

#### Acceptance Criteria

1. WHERE the starter is checked out at the pinned source commit, THE reviewer SHALL confirm all package/service names, source code, data, and configuration are fabricated/synthetic. (R1)

### Requirement 2: Workspace graph

**User Story:** As a task preparer, I want a service plus a shared workspace dependency, so that a transitive build relationship exists to regress.

#### Acceptance Criteria

1. THE starter SHALL include one service package and at least one shared workspace dependency consumed by that service. (R2)

### Requirement 3: Shared package build step

**User Story:** As a task preparer, I want the shared dependency to need its own build output, so that build ordering matters.

#### Acceptance Criteria

1. THE shared dependency SHALL require its own deterministic build output before the service can build successfully. (R3)

### Requirement 4: Broken build relationship

**User Story:** As a task preparer, I want the starter pipeline to fail to establish the transitive build, so that the regression is reproducible.

#### Acceptance Criteria

1. WHEN the reviewer runs `pnpm build:service` on the pinned starter, THE designated service build SHALL fail with exit code 1 and its output SHALL reference `packages/route-core/dist/routes.json`. (R2, R3, R4, R6)

### Requirement 5: Obsolete package reference

**User Story:** As a task preparer, I want a stale package identity in a config surface, so that the second independent defect is present.

#### Acceptance Criteria

1. WHEN the reviewer runs `pnpm check:container` on the pinned starter, THE container check SHALL fail with exit code 1 and its output SHALL contain `container target @harbor/dispatch-api is not a workspace package`. (R5)

### Requirement 6: Reproducible failure

**User Story:** As a reviewer, I want a documented command that reproduces the regression, so that the failure is deterministic from a clean checkout.

#### Acceptance Criteria

1. WHERE the starter is checked out at the pinned source commit, THE `pnpm install` (or equivalent via corepack) setup SHALL be reproducible with the pinned `pnpm==9.15.4` / `turbo==2.3.3`. (R1, R6)

### Requirement 7: Two root causes remain independent

**User Story:** As a reviewer, I want the two defects to be independent, so that fixing only one is demonstrably insufficient.

#### Acceptance Criteria

1. WHILE only one of the two root causes is hypothetically corrected, THE starter SHALL still demonstrate a remaining failure, proving that correcting only one problem is insufficient. (R7)

### Requirement 8: Unrelated workspace behavior

**User Story:** As a reviewer, I want at least one unrelated passing check, so that the eventual correction can be shown as bounded.

#### Acceptance Criteria

1. WHEN the reviewer runs `pnpm check:unrelated` on the pinned starter, THE unrelated check SHALL exit with code 0 and its output SHALL contain `status check passed`. (R8)

### Requirement 9: No final repair

**User Story:** As a task preparer, I want no pre-correction in the starter, so that the recording starter stays unworked.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE starter SHALL contain no completed repair of the build graph or stale package reference, no ready-to-paste final diff, and no verification note. (R9, R10)

### Requirement 10: Neutral recorder-visible docs

**User Story:** As a reviewer, I want README/setup to explain install and reproduction only, so that it does not label the answers.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE README SHALL NOT label exact files/lines as the answers and SHALL be limited to install and failure-reproduction instructions. (R10)

## Glossary

- **Pinned recording starter:** The unchanged, unworked monorepo at the pinned source commit that the human works from during capture.
- **Worked reference:** A separate, disclosed, AI-authored, analyzed, disposable-tested artifact off-screen in the TaskWorkPlan; it does not establish unaided human learning, mastery, paid eligibility, or human approval.
- **Guided recording/practice (current mode):** The human manually executes edits/tests and narrates actual outcomes from the unchanged unworked starter, with no AI interaction during capture. Manual typing from an unworked input does not by itself imply unaided execution.
- **Human Transfer Test (separate, future):** A distinct UNAIDED assessment; not the current mode and not a prerequisite for guided world prep.
- **Dependency profile:** `pnpm-workspace` with `pnpm==9.15.4` and `turbo==2.3.3` provided via corepack.

## Recording envelope

The designated failing service build and bounded verification commands should each complete fast enough to support diagnosis and reruns within a 15:00–45:59 recording.
