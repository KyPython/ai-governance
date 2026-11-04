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
