# Requirements Document

Spec: Local IaC Least-Privilege Guardrail Validation · Spec ID: IAC · Status: proposed (spec-only); @KyPython approves by merging this spec-only PR.

## Goal

As a cloud/software engineer, inspect a synthetic infrastructure-as-code project containing an intentionally over-broad permission or unsafe configuration, identify the concrete risk, apply the smallest least-privilege correction, and verify the synthesized infrastructure and automated policy tests before and after the change.

Task Factory row: https://app.notion.com/p/3f08621e0a7a81418692ed974ac073a0

Goal SHA256: 13d54d59f0ef16331ec88b83f55fdc130748a3c3590b34e4098de884ca79b3ba
Note: the value above is the SHA256 of UTF-8(verbatim Goal + one trailing LF).

## Introduction

This spec governs user-authorized guided INTERNAL Bootcamp, fully-disclosed AI-assisted advance preparation for the task above. It is **NOT** paid Odin approval and **NOT** a claim of unaided human ability. No source is executed, repaired, promoted, merged, or deployed by this spec. The later deliverable is a scoped IAM policy plus an extended policy validator for the synthetic stdlib IaC project.

This task's Odin decision is **Rejected / REJECT** with Approved Pay 0. This spec is INTERNAL Bootcamp preparation only and does **NOT** change, reopen, or override that decision; the Rejected/REJECT/0 state is preserved verbatim.

### Source identity and admission

Recovery identity (VERIFIED CURRENT OBSERVATION):
- cloudRecoveryTaskId: `task_e_6ac6d6166f448322abbe99123432ae3c`
- diffSha256: `01c2f01272f9d932682f5d6243f4c1a174a621021b8849630d6f9e41a44addcc`
- extractedRoot: `/Users/ky/Library/Caches/TaskWorkWorldRecovery/extracted/task_e_6ac6d6166f448322abbe99123432ae3c`
- starterSubdirectory: `specs/odin-tasks/local-iac-least-privilege-guardrail-validation/starter`
- starterFileCount: 10
- dependencyShape: Python standard library
- baselineExecuted: **false**
- sourcePromoted: **false**

The parent session confirmed the Goal SHA256 matches UTF-8(verbatim Goal + one LF), that the extractedRoot and starterSubdirectory exist, and that a sample of file-byte digests matched the inventory below (authentic, unaltered, unworked recovered source). This spec binds that recovery digest and the inventory below.

sourceFileDigests inventory (reference only — paths + mode + sha256, NOT contents):

| path | mode | sha256 |
| --- | --- | --- |
| specs/odin-tasks/local-iac-least-privilege-guardrail-validation/starter/.gitignore | 100644 | 1d8d2e528f590165b4846c70eeb0388cc93119d2147937e4888da84f06c4d9f4 |
| specs/odin-tasks/local-iac-least-privilege-guardrail-validation/starter/README.md | 100644 | 76a15cb4fb445531ce3059e8e00643ba2711cd9c78de57aff6eea375000ba0c6 |
| specs/odin-tasks/local-iac-least-privilege-guardrail-validation/starter/docs/workload-contract.md | 100644 | 68345d98e111fc67ea4d538cb8ab4fffa4fb5297bf9457957075369132fd4239 |
| specs/odin-tasks/local-iac-least-privilege-guardrail-validation/starter/infra/__init__.py | 100644 | 5cbf1edb3d1779821474b7541d88bf09c37c0ebe6f74d9ca3dda780e20276f88 |
| specs/odin-tasks/local-iac-least-privilege-guardrail-validation/starter/infra/stack.py | 100644 | 96cd8e761122e23624118439a21663804302b6ed46874090b1f7ffccb7080ab5 |
| specs/odin-tasks/local-iac-least-privilege-guardrail-validation/starter/infra/synth.py | 100644 | 9dcd1bc66d3b857da97a050738c43bf8d1b05a924c167cbe1366e0bdc212d78a |
| specs/odin-tasks/local-iac-least-privilege-guardrail-validation/starter/policy/__init__.py | 100644 | 11040cd452967786d4bbc0e5ceeab705267e3d3f5dba640aea7138438908f2fa |
| specs/odin-tasks/local-iac-least-privilege-guardrail-validation/starter/policy/validate.py | 100644 | f81a9abd1134114cf9e5c18314fc4d118a16622acce506ca82a9585a156f4ea8 |
| specs/odin-tasks/local-iac-least-privilege-guardrail-validation/starter/tests/test_policy.py | 100644 | b67d1564969222b1e21d11eb22efe7a53880e0bd873e9c58cd4ea53261444bad |
| specs/odin-tasks/local-iac-least-privilege-guardrail-validation/starter/tests/test_synthesis.py | 100644 | 1c5666133992db6db91f5562ab63ed6aecd14e1557f4dbff1318d6b197f8391e |

(10 tracked file digests, all Git mode 100644, consistent with starterFileCount = 10.)

Preserved paid-state (EXACTLY as given — unchanged by this spec): Stage: **Rejected** · Fit Gate: **REJECT** · Approved Goal: (empty) · Approval ID: (empty) · Approved Pay: **0**.

The actual future technical-prep gates are: real Kiro final review, a @KyPython merged-to-main spec, and the bound internal admission. Human/Recorder/paid gates are separate — and for this task the Odin outcome is already Rejected. Separate FUTURE human decisions — recording, execution, capture, privacy, audio/narration, transfer — are distinct from this technical preparation.

Post-merge requirement: AFTER @KyPython merges this spec, and BEFORE any internal admission/registration or cloud promotion, the private Ky-owned unworked starter must be published and its full 40-character commit SHA plus per-file byte and mode verification against the inventory above confirmed. No starter SHA is invented here.

Native Kiro session references: authorship provenance is the author session `sess_6ccf95b7-8bbe-4225-8682-6f74410eb9cd`; the final combined 54-file reviewed-HEAD Kiro merge receipt comes from the ORIGINAL final-review session `sess_ef9c3844-0570-409c-baa6-7cc73d898476`, not the author session alone.

## Glossary

- **stack.py**: builds a CloudFormation-compatible dict (stdlib only, no AWS/CDK).
- **ParcelRecordsBucket**: S3 bucket with AES256 encryption and full `PublicAccessBlockConfiguration` (all true).
- **ParcelEventsQueue**: SQS queue with `KmsMasterKeyId alias/aws/sqs`, VisibilityTimeout 120.
- **ParcelIndexerRole**: IAM role (assumed by `lambda.amazonaws.com`) whose inline policy `parcel-record-access` grants Action `s3:*` on Resource `*` — the concrete over-broad risk.
- **workload-contract.md**: states the worker only READS objects under the bucket's `incoming/` prefix; does not create/overwrite/delete/tag/administer; deployment admin is outside the worker role.
- **validate.py**: checks only S3 public-access block and SQS KMS; does NOT catch the IAM over-permission.
- **RUN LATER**: an observable check to execute after merge in a disposable copy; nothing is executed in this spec.

## Requirements

### Requirement 1: Identify the concrete over-broad permission (IAC-1)

**User Story:** As a cloud engineer, I want the concrete risk named precisely, so that the correction targets the right resource.

#### Acceptance Criteria

1. IAC-1.1 WHEN inspecting the synthesized stack THE analysis SHALL identify the `ParcelIndexerRole` inline policy `parcel-record-access` granting Action `s3:*` on Resource `*` as the concrete over-broad risk. (Source: stack.py.)
2. IAC-1.2 THE analysis MUST NOT fabricate business authorization or reference real cloud accounts; the boundary SHALL be derived from `docs/workload-contract.md`. (Acceptance RUN LATER.)

### Requirement 2: Apply the smallest least-privilege correction (IAC-2)

**User Story:** As a cloud engineer, I want the minimal correction, so that only the required access is granted.

#### Acceptance Criteria

1. IAC-2.1 WHEN correcting the risk THE change SHALL scope the role action from `s3:*` to the read action(s) required (e.g., `s3:GetObject`) and the Resource from `*` to the bucket's `incoming/*` ARN. (Source: workload-contract.md — read-only under `incoming/`.)
2. IAC-2.2 WHEN synthesis runs after the change THE role policy SHALL list only the required read action(s) scoped to `incoming/*`. (Acceptance RUN LATER.)

### Requirement 3: Preserve unrelated safeguards (IAC-3)

**User Story:** As a cloud engineer, I want the unrelated safeguards untouched.

#### Acceptance Criteria

1. IAC-3.1 WHILE correcting the IAM permission THE change MUST NOT alter the S3 full `PublicAccessBlockConfiguration` (all true), the S3 AES256 encryption, or the SQS `KmsMasterKeyId`. (Source: stack.py resources.)
2. IAC-3.2 WHEN the policy validator runs THE S3 public-access block and SQS KMS SHALL still be reported present and unchanged. (Acceptance RUN LATER.)

### Requirement 4: Preserve resource structure (IAC-4)

**User Story:** As a cloud engineer, I want the resource structure preserved.

#### Acceptance Criteria

1. IAC-4.1 WHILE correcting the permission THE change MUST NOT remove or restructure the bucket, queue, or role resources beyond the scoped-down policy. (Source: smallest-correction boundary.)
2. IAC-4.2 WHEN synthesis runs THE three resources SHALL still be present with expected logical IDs. (Acceptance RUN LATER.)

### Requirement 5: Policy validator catches the IAM over-permission (IAC-5)

**User Story:** As a cloud engineer, I want the validator to detect the over-broad IAM grant.

#### Acceptance Criteria

1. IAC-5.1 WHEN the policy validator runs THE validator SHALL be extended to flag an IAM policy granting `s3:*` on `*` (or equivalently over-broad action/resource), in addition to its existing checks. (Source: validate.py currently misses this.)
2. IAC-5.2 WHEN run before the fix THE validator SHALL fail; WHEN run after the fix THE validator SHALL pass. (Acceptance RUN LATER.)

### Requirement 6: Verify synthesis before and after (IAC-6)

**User Story:** As a cloud engineer, I want before/after verification.

#### Acceptance Criteria

1. IAC-6.1 WHEN verifying THE process SHALL run synthesis and policy tests both before (risk present) and after (risk corrected) the change. (Source: Goal.)
2. IAC-6.2 THE before/after runs SHALL be recorded as observed-vs-expected. (Acceptance RUN LATER.)

### Requirement 7: Local stdlib synthesis only (IAC-7)

**User Story:** As a cloud engineer, I want the exercise confined to local stdlib synthesis.

#### Acceptance Criteria

1. IAC-7.1 THE exercise MUST NOT make AWS/CDK/Terraform/cloud/deployment calls or use credentials. (Source: stack.py is stdlib-only; task boundary.)
2. IAC-7.2 WHEN code/tests are inspected THEN no cloud SDK/credential usage SHALL appear. (Acceptance RUN LATER.)

### Requirement 8: Boundary grounded in the workload contract (IAC-8)

**User Story:** As a cloud engineer, I want the least-privilege boundary derived from the contract.

#### Acceptance Criteria

1. IAC-8.1 THE risk and correction SHALL cite `docs/workload-contract.md`. (Source: task boundary.)
2. IAC-8.2 THE deliverable MUST NOT include real account IDs. (Acceptance RUN LATER.)

### Requirement 9: No settled-fact / mastery / status-change claims (IAC-9)

**User Story:** As KyJahn, I want the Rejected/REJECT state preserved and status language honest.

#### Acceptance Criteria

1. IAC-9.1 THE spec MUST NOT claim a passing baseline, reopen or override the Odin Rejected/REJECT decision, or claim unaided human mastery. (Source: honesty rules; baselineExecuted = false; preserved Rejected/REJECT.)
2. IAC-9.2 WHERE evidence is incomplete THE artifacts SHALL state a HOLD and preserve the Rejected/REJECT state. (Acceptance RUN LATER.)
