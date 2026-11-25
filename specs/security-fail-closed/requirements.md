# Requirements: security fail-closed paths

Spec ID: SECFC · Issue: #245 · Status: proposed; Ky approves by merging this spec-only PR

## Introduction

Evaluators and the governance verdict fail open in six places: the verdict
trusts a defaulted prerequisite result, approval scorers accept hidden SENDs
and loose approval flags, revocation accepts non-boolean values, delegation
parsing accepts glued tokens, the S3 guard accepts partial blocks, and
published specs carry a live relay content hash. This spec defines the
fail-closed behavior; the code PR implements it.

## Requirements

### Requirement 1: Fail-closed verdict prerequisite (SECFC-1)

**User Story:** As Ky, I want the verdict to distrust a missing prerequisite,
so that skipping quality cannot pass without an explicit success.

#### Acceptance Criteria

1. SECFC-1.1 WHEN run-quality is false THEN the verdict SHALL pass only when
   prerequisite-result is success.
2. SECFC-1.2 WHEN run-quality is true THEN the verdict SHALL accept an empty
   or success prerequisite-result.
3. SECFC-1.3 The prerequisite-result input default SHALL be empty, never
   success.

### Requirement 2: Approval scorer token handling (SECFC-2)

**User Story:** As Ky, I want approval scoring to catch hidden SENDs, so that
a later SEND cannot hide behind an ASK.

#### Acceptance Criteria

1. SECFC-2.1 WHEN output contains multiple ACTION lines THEN any SEND SHALL
   win, otherwise the last token SHALL win.
2. SECFC-2.2 WHEN approval metadata is not exactly True THEN a SEND action
   SHALL score INCORRECT.
3. SECFC-2.3 WHEN matching ACTION tokens THEN the match SHALL be anchored to
   a line start with a word boundary.

### Requirement 3: Revocation strictness (SECFC-3)

**User Story:** As Ky, I want revocation checks to reject malformed values, so
that a truthy non-boolean cannot pass as active.

#### Acceptance Criteria

1. SECFC-3.1 WHEN a grant revoked value is not a boolean THEN evaluation
   SHALL finish approval_revoked_invalid.
2. SECFC-3.2 WHEN revoked is True THEN evaluation SHALL finish
   approval_revoked.

### Requirement 4: Delegation decision parsing (SECFC-4)

**User Story:** As Ky, I want delegation parsing to take the last clean token,
so that glued tokens cannot spoof a decision.

#### Acceptance Criteria

1. SECFC-4.1 WHEN output contains DECISION lines THEN the last
   line-anchored whole-token match SHALL win, and a glued token SHALL NOT
   match.

### Requirement 5: S3 guard completeness (SECFC-5)

**User Story:** As Ky, I want the S3 guard to require full blocks, so that a
partial public-access block cannot pass.

#### Acceptance Criteria

1. SECFC-5.1 WHEN validating an S3 bucket THEN all four
   PublicAccessBlock keys SHALL be boolean True.

### Requirement 6: Identifier redaction (SECFC-6)

**User Story:** As Ky, I want live identifiers out of published specs, so
that recovered content hashes stay in the private record.

#### Acceptance Criteria

1. SECFC-6.1 WHEN publishing specs THEN the content SHALL NOT include live
   relay content hashes.

### Requirement 7: Trusted exact-SHA external validation evidence (SECFC-7)

**User Story:** As Ky, I want the verdict to check that the external validation
job really ran and passed on the PR head commit, so that a caller cannot pass the
gate by typing `success` into an input.

**Source:** audit of PR #233 (Oct 27); SECFC-1 closed the defaulted-success case
but left the supplied string trusted. Closes the remaining finding. Issue #245.

#### Evidence states (as of `main` 28452a6, read 2026-11-25)

Verified current behavior:
- V1. The `v` step of the `verdict` job in `.github/workflows/governance.yml`
  sets `prerequisite_ok=true` when `RUN_QUALITY` is `false` and
  `PREREQUISITE_RESULT` equals `success`. No other check applies to that value.
- V2. `bash -n` on the extracted `v` step exits 0. The recomputed sha256 of
  `docs/quality/system-evidence.md` equals the value in `.quality/system.json`
  (`6a87ac92...1ebe`).
- V3. The `verdict` job declares `permissions: {}` and `needs: quality, policy,
  security, secret-scan`. It makes no API call.

Verified failure:
- F1. Running the extracted `v` step with `QUALITY=skipped POLICY=success
  SECRETS=success SECURITY=success RUN_QUALITY=false PREREQUISITE_RESULT=success`
  and no validation job anywhere exits 0 with `verdict=pass`. The same run with
  `PREREQUISITE_RESULT` set to `skipped`, empty, or with `SECURITY=failure` or
  `QUALITY=failure` exits 1.

Intended existing behavior: SECFC-1.1 to SECFC-1.3 (merged in #233).

Unknowns (reproduce before the implementation PR relies on them):
- U1. Whether a caller that grants only `contents: read` makes the check-runs
  API return 403 to the `verdict` job. Reproduce in a throwaway repo.
- U2. Which check run to trust when a re-run leaves several runs with the same
  name on one SHA.
- U3. Whether any repo outside `KyPython/ai-governance` passes
  `prerequisite-result`. Code search found no caller inside this repo.
- U4. How `push` and `merge_group` events should resolve the head SHA.

Residual limit (not fixed by this requirement): the check name is chosen by the
caller. The gate proves a job of that name completed successfully on the head
SHA. It does not prove the job tests anything. Ky's required-check ruleset and
review of the caller workflow remain the control for that.

#### Acceptance Criteria

1. SECFC-7.1 WHEN run-quality is false THEN the verdict MUST NOT treat
   prerequisite-result alone as proof. It SHALL also require API evidence under
   SECFC-7.2 to SECFC-7.5.
2. SECFC-7.2 The workflow SHALL add an input `prerequisite-check` (string,
   default empty) naming the external validation check run. WHEN run-quality is
   false AND `prerequisite-check` is empty THEN the verdict MUST fail.
3. SECFC-7.3 The verdict SHALL read check runs for the PR head SHA with the
   GitHub check-runs API: `github.event.pull_request.head.sha` on
   `pull_request`, and `github.sha` on `push`. It MUST NOT use the merge commit
   SHA. Every run it considers MUST have `head_sha` equal to that SHA.
4. SECFC-7.4 The verdict SHALL pass the evidence test only WHEN the latest
   completed run named `prerequisite-check` has `status` `completed`,
   `conclusion` `success`, and `app.slug` `github-actions`. A run that is
   `queued`, `in_progress`, `skipped`, `neutral`, `cancelled`, `failure` or
   `timed_out`, or from another app, MUST fail.
5. SECFC-7.5 The verdict MUST fail closed WHEN the API call errors, returns a
   non-200 status, returns an incomplete page set, returns no matching run, or
   returns a body it cannot parse. An empty result MUST NOT be read as success.
6. SECFC-7.6 `prerequisite-check` MUST NOT name the verdict's own check
   (`ai-governance / verdict`). The verdict MUST fail WHEN it does.
7. SECFC-7.7 WHEN run-quality is true THEN SECFC-1.2 applies unchanged and the
   API evidence is not required.
8. SECFC-7.8 The `verdict` job SHALL request `checks: read` and nothing more,
   and SHALL NOT request any write permission.
9. SECFC-7.9 The verdict step SHALL stay one shell script that passes
   `bash -n`, and `tests/test_workflow_shell_syntax.py` SHALL cover it.
10. SECFC-7.10 Tests SHALL cover these negative cases, each ending in
    `verdict=fail`: hardcoded `success` with validation skipped or absent;
    skipped native `needs.validate.result`; stale SHA; false, missing or
    `neutral` evidence; failed `security`; bad shell syntax.
11. SECFC-7.11 `.quality/system.json` MUST NOT be edited to silence CI. The
    implementation PR SHALL recompute the sha256 of
    `docs/quality/system-evidence.md` from file contents, and SHALL update the
    recorded value only WHEN that file legitimately changed, with the reason in
    the PR body.

**Acceptance evidence:** the tests of SECFC-7.10 failing before and passing
after the change; the `bash -n` result; the recomputed hash; CI results at the PR head SHA.
**Depends on:** SECFC-1; Ky merges this spec before any code (design in `design.md`).
