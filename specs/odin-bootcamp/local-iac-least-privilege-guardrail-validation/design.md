# Design: Local IaC Least-Privilege Guardrail Validation

Spec ID: IAC

## Overview

This design describes, from the observed recovered source only, how the later deliverable (a scoped IAM policy plus an extended policy validator) is intended to be built against the pinned synthetic stdlib IaC project. No source is executed, repaired, or promoted in this session (baselineExecuted = false). The Odin decision is **Rejected / REJECT**; this internal-prep spec does not change that.

Baseline (current) behavior — OBSERVED:
- `infra/stack.py` builds a CloudFormation-compatible dict (stdlib only, no AWS/CDK). Resources: `ParcelRecordsBucket` (S3, AES256 + full `PublicAccessBlockConfiguration` all true); `ParcelEventsQueue` (SQS, `KmsMasterKeyId alias/aws/sqs`, VisibilityTimeout 120); `ParcelIndexerRole` (IAM role assumed by `lambda.amazonaws.com`) whose inline policy `parcel-record-access` grants Action `s3:*` on Resource `*` — the concrete over-broad risk.
- `docs/workload-contract.md`: the worker only READS objects under the bucket's `incoming/` prefix; does not create/overwrite/delete/tag/administer; deployment admin is outside the worker role.
- `policy/validate.py` checks ONLY S3 public-access block and SQS KMS; does NOT catch the IAM over-permission.
- Tests cover policy and synthesis.

Intended corrected behavior (to build LATER):
- Scope the role's action from `s3:*` to the required read action(s) (e.g., `s3:GetObject`) and the Resource from `*` to the bucket's `incoming/*` ARN; extend `policy/validate.py` to flag over-broad IAM actions/resources.

Exact boundary of the change: modify only the `parcel-record-access` inline policy and add one validator check; preserve S3 public-access block, S3 encryption, SQS KMS, and the bucket/queue/role structure; no AWS/CDK/Terraform/cloud/credentials.

## Architecture

The recovered source is a stdlib-only Python IaC project (no AWS/CDK/Terraform, no credentials). Synthesis emits a CloudFormation-compatible template dict; a local policy validator inspects it. The change touches one inline IAM policy and adds one validator check.

- `infra/stack.py` (CHANGE BOUNDARY, minimal) — builds the resource dict; only the `ParcelIndexerRole` inline policy `parcel-record-access` is scoped down (action and resource). S3 bucket, SQS queue, and role structure are preserved.
- `infra/synth.py` (PRESERVED, invoked) — the synthesis entry point run as `python -m infra.synth --output build/template.json`.
- `infra/__init__.py` (PRESERVED) — package surface.
- `policy/validate.py` (CHANGE BOUNDARY) — currently checks S3 public-access block and SQS KMS only; extended with one check that flags `s3:*` on `*` (and equivalent over-broad grants). Run as `python -m policy.validate build/template.json`.
- `policy/__init__.py` (PRESERVED) — package surface.
- `docs/workload-contract.md` (PRESERVED, read-only) — authoritative source for the least-privilege boundary (read-only under `incoming/`).
- `tests/test_synthesis.py`, `tests/test_policy.py` (EXTENDED LATER) — synthesis and policy coverage.
- `README.md`, `.gitignore` (PRESERVED).

Baseline vs intended vs boundary: baseline synthesizes a role with `s3:*` on `*` that the validator does not flag; intended synthesizes a role scoped to the required read action(s) on `incoming/*` and a validator that flags the over-broad grant (fails pre-fix, passes post-fix). The exact boundary is the `parcel-record-access` inline policy plus one validator check; unrelated safeguards and resource structure are untouched. The Odin Rejected/REJECT decision is preserved and not reopened.

## Components and Interfaces

Interfaces described in prose from the observed source; no source code copied.

- Synthesis — `python -m infra.synth --output build/template.json` writes the CloudFormation-compatible template dict. (Invoked via the module, never `python infra/synth.py`.)
- Policy validation — `python -m policy.validate build/template.json` inspects the synthesized template; today it asserts the S3 public-access block and SQS KMS; the deliverable adds a check that flags over-broad IAM action/resource (`s3:*` on `*`).
- `ParcelIndexerRole` inline policy `parcel-record-access` — currently Action `s3:*` on Resource `*`; the change scopes the action to the required read action(s) and the resource to the bucket's `incoming/*` ARN, grounded in `docs/workload-contract.md`.
- `ParcelRecordsBucket` / `ParcelEventsQueue` — S3 and SQS resources whose safeguards (public-access block, AES256, SQS KMS) are preserved and still reported present.

## Data Models

Shapes described in prose; file contents are not reproduced.

- Synthesized template: a CloudFormation-compatible dict with a `Resources` map containing the three logical IDs `ParcelRecordsBucket` (S3), `ParcelEventsQueue` (SQS), and `ParcelIndexerRole` (IAM).
- S3 resource: AES256 server-side encryption plus a full `PublicAccessBlockConfiguration` (all four flags true).
- SQS resource: `KmsMasterKeyId alias/aws/sqs`, VisibilityTimeout 120.
- IAM role: assumed by `lambda.amazonaws.com`; inline policy `parcel-record-access` with an action list and a resource ARN — baseline `s3:*` / `*`, intended read action(s) / `incoming/*` ARN.
- Workload contract: prose stating read-only access under the `incoming/` prefix; the authoritative boundary for the scoped policy.

## Correctness Properties

### Property 1: Scoped least-privilege policy
**Validates: Requirements 1.1, 1.2, 2.1, 2.2, 8.1, 8.2** (aliases IAC-1, IAC-2, IAC-8)
The role grants only the required read action(s) scoped to `incoming/*`, derived from the workload contract. — observable check: synthesized role policy lists only read action(s) on `incoming/*` and cites the contract (RUN LATER).

### Property 2: Unrelated safeguards and structure preserved
**Validates: Requirements 3.1, 3.2, 4.1, 4.2** (aliases IAC-3, IAC-4)
S3 public-access block, S3 encryption, SQS KMS, and the three-resource structure are unchanged. — observable check: validator still reports the safeguards; synthesis still emits three resources with expected IDs (RUN LATER).

### Property 3: Validator catches over-broad IAM
**Validates: Requirements 5.1, 5.2** (alias IAC-5)
The policy validator flags `s3:*` on `*` (and equivalent over-broad grants). — observable check: validator fails pre-fix, passes post-fix (RUN LATER).

### Property 4: Local-only, before/after, honest
**Validates: Requirements 6.1, 6.2, 7.1, 7.2, 9.1, 9.2** (aliases IAC-6, IAC-7, IAC-9)
Synthesis is stdlib-only; before/after verification is recorded; no cloud calls, no real accounts, no mastery claim, Rejected/REJECT preserved. — observable check: no SDK/credential usage; before/after observed-vs-expected recorded (RUN LATER).

## Error Handling

- Over-broad grant detected: the extended validator reports a `PolicyViolation`-style failure (non-zero outcome) when it finds `s3:*` on `*` (or equivalently over-broad action/resource); it passes only after the scope-down.
- Preserved-safeguard checks: if the S3 public-access block, S3 encryption, or SQS KMS were altered, the existing validator checks would fail; the change must leave them reporting present and unchanged.
- Local-only constraint: synthesis and validation are stdlib-only against a local template file; no AWS/CDK/Terraform/cloud/credential call is made, so failures are local policy/parse outcomes, not cloud errors (Requirement 7.1 / IAC-7).
- Decision boundary: nothing in error handling reopens or overrides the Odin Rejected/REJECT decision (Requirement 9.1 / IAC-9).

## Testing Strategy

Outputs below are **expectations to verify LATER** in **disposable copies**. Nothing was executed in this session (baselineExecuted = false); these are expectations to verify LATER, not results.

| Command (literal) | Expected RED (pre-fix) | Expected GREEN (post-fix) | Requirements |
| --- | --- | --- | --- |
| `python -m unittest discover -s tests -v` (synthesis) | Synthesis emits the three resources incl. role with `s3:*` on `*` | Still emits three resources; role scoped to read + `incoming/*` | 1.1, 2.2, 4.2 (IAC-1, IAC-2, IAC-4) |
| `python -m unittest discover -s tests -v` (policy) | Passes but does not flag the IAM over-permission (gap) | New check flags over-broad IAM; passes only after scope-down; S3/SQS safeguards still asserted | 3.2, 5.1 (IAC-3, IAC-5) |
| `python -m infra.synth --output build/template.json` then `python -m policy.validate build/template.json` | Synthesizes template with over-broad policy; validator does not flag IAM | Synthesizes template with scoped policy; validator flags over-broad IAM pre-fix and passes post-fix | 2.2, 5.2, 6.1 (IAC-2, IAC-5, IAC-6) |
| `python -m unittest discover -s tests -v` (full) | Over-permission present/undetected | All policy + synthesis checks green after bounded fix | 5.2, 6.1 (IAC-5, IAC-6) |

HOLD: All coding and source promotion are **HELD** until the canonical spec PR is merged by **@KyPython** into `ai-governance/main` with green required checks. Authorship provenance is author session `sess_6ccf95b7-8bbe-4225-8682-6f74410eb9cd`; the final combined 54-file reviewed-HEAD Kiro merge receipt comes from the ORIGINAL final-review session `sess_ef9c3844-0570-409c-baa6-7cc73d898476`, not the author session alone. The Odin Rejected/REJECT decision is preserved and not reopened here. The exact read-action set and ARN form are AI-proposed GUIDEDREFERENCE for Ky's PR review, grounded in the workload contract — not decisions already made and not a mastery claim.

Reuse-first note: Reuse existing registration/Python profiles, the reviewed generatedFiles recipe, and existing registry/publisher/learning-map/paired-GHA-artifact/Morning owners and the existing Notion row. Do not create new controllers, world queues, or ledgers.
