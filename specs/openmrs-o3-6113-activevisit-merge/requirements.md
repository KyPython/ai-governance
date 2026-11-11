# Requirements: OpenMRS O3-6113 merge with upstream activeVisit rename

Spec ID: OAV · Issue: #217 · Status: proposed; Ky approves by merging this spec-only PR

Provenance: drafted by Kiro on 2026-11-10 from Ky's chat instructions in the cloud-triage
session ("1a" local merge only, "2c" decide the patient value from commit history, "1b" hold
the push and spec the delta first, "2a" keep the hook's reformat). The delta's review targets
come from the Notion page "OpenMRS O3-6113 - Kiro spec request (not approved)", entry dated
November 9, 2026 23:20 ET. Ky owns the sentences; coders must not paraphrase them to fit the code.

## Introduction

OpenMRS PR [#3798](https://github.com/openmrs/openmrs-esm-patient-chart/pull/3798) (fork
`KyPython/openmrs-esm-patient-chart`, branch `fix/O3-6113-unavailable-patient`, head
`bf7dccd7`) implements [O3-6113](https://openmrs.atlassian.net/browse/O3-6113). GitHub reports it
`CONFLICTING`. On 2026-11-09 maintainer Bodeayman asked the author to check the conflict.

The conflict comes from upstream commit `c329ff88` (O3-6032, PR #3781, merged 2026-11-06,
marked BREAKING). It renamed `visitContext` to `activeVisit` in the patient chart store and in
the workspace-group props. The PR branch still uses the old names.

This spec covers only merging upstream `main` into the PR branch while keeping the PR's
unavailable-patient behavior. It does not cover the other #217 audit items: already-open
clinical forms that stay writable, backend write authorization, navigation cleanup, and the
missing-data fallback. The Notion entry records that navigation cleanup and the missing-data
fallback already exist in the PR's five-file patch.

Ordering note: a candidate merge already exists as local, unpushed commit `961389cf` (parents
`bf7dccd7` and upstream `0039b3f1`). Kiro made it under Ky's "1a" instruction before this
spec existed. This spec is the review basis for that commit; the commit is not evidence that
the spec is satisfied until the review task in `tasks.md` records it.

Re-pin, 2026-11-11: upstream `main` moved to `326be2f9` (openmrs-bot, "(chore) Update OpenMRS
dependencies (#3870)"). As task 1 requires, Kiro redid the merge: local, unpushed commit
`6a3a033f` merges `961389cf` with `326be2f9`, with no conflicts; that upstream commit changes only
`yarn.lock` and none of this PR's files. `6a3a033f` is now the candidate and `326be2f9` the base.

## Requirements

### Requirement 1: Upstream store and group contracts (OAV-1)

**User Story:** As an OpenMRS maintainer, I want the PR to use the store and workspace-group
names now on `main`, so that it merges without reintroducing removed identifiers.

#### Acceptance Criteria

1. OAV-1.1 WHEN the hook reads the stored visit THEN it SHALL read the store's `activeVisit` field and SHALL write it through `setActiveVisit`.
2. OAV-1.2 WHEN the hook builds `PatientWorkspaceGroupProps` for `launchWorkspaceGroup2` THEN it SHALL set the visit under the key `activeVisit`.
3. OAV-1.3 The merged source and tests SHALL NOT reference `isValidatingVisitContext`, `setVisitContext`, or a store field named `visitContext`.

### Requirement 2: External slot contract (OAV-2)

**User Story:** As an extension author in another app, I want the patient header and info
slot state to keep its key, so that my extension keeps reading the visit.

#### Acceptance Criteria

1. OAV-2.1 The state returned by `usePatientChartPatientAndVisit` SHALL keep the key `visitContext`, with the stored active visit as its value, as upstream `main` does.

### Requirement 3: Unavailable-patient behavior (OAV-3)

**User Story:** As a clinician, I want a voided or missing patient never to get a writable
chart, so that I cannot record data against an unavailable patient.

#### Acceptance Criteria

1. OAV-3.1 IF the patient request returns an error THEN the returned state SHALL carry that error and SHALL NOT substitute `{}` for the patient.
2. OAV-3.2 IF loading settles with no patient and no error THEN the returned `patient` SHALL remain `null` or `undefined`.
3. OAV-3.3 WHILE the patient is unavailable, or the store's `patientUuid` differs from the patient's id, the hook SHALL NOT launch a workspace group and SHALL clear its latest group props.
4. OAV-3.4 IF a pending workspace-group launch resolves while the patient is still unavailable THEN the hook SHALL NOT launch a queued visit and SHALL NOT publish that visit's uuid. When the patient has recovered before the launch resolves, OAV-3.5 applies instead.
5. OAV-3.5 WHEN the patient becomes available again THEN the hook SHALL launch the group only after the store's patient identity is restored, and SHALL reconcile the framework group after an invalidated in-flight launch.

### Requirement 4: Healthy-patient behavior (OAV-4)

**User Story:** As a maintainer, I want the merge to leave available-patient behavior as it is
on `main`, so that the rename does not regress visit switching or launches.

#### Acceptance Criteria

1. OAV-4.1 WHEN the merge is complete THEN every test that exists on upstream `main` in `esm-patient-chart-app` SHALL pass without edits to its assertions.

### Requirement 5: Test expectations (OAV-5)

**User Story:** As a reviewer, I want the PR's own tests renamed rather than weakened, so that
they still prove the unavailable-patient behavior.

#### Acceptance Criteria

1. OAV-5.1 WHEN a PR-only test refers to the store or to group props THEN it SHALL use `setActiveVisit` and the key `activeVisit`, matching the rename `c329ff88` applied to upstream tests.
2. OAV-5.2 The merge SHALL NOT remove, skip, or loosen any PR-only test or assertion.

### Requirement 6: Scope, evidence, and publication (OAV-6)

**User Story:** As Ky, I want the PR to change only what O3-6113 needs and the evidence to say
what was actually run, so that I decide publication with accurate facts.

#### Acceptance Criteria

1. OAV-6.1 The diff from upstream `main` SHALL contain only the PR's O3-6113 files plus formatting that the repository's own pre-commit hook enforces. Ky decided on 2026-11-10 to keep the hook's Prettier reformat of one import in `useDeleteVisit.tsx`.
2. OAV-6.2 Evidence for this delta SHALL label every check as local, and SHALL NOT describe an author-run check as maintainer CI or as independent review.
3. OAV-6.3 The merge SHALL NOT be pushed to the fork branch, and no comment SHALL be posted on PR #3798, until Ky has validated this spec and authorized that exact action.
