# Design Document

> INTERNAL guided Bootcamp PREPARATION under an explicit user world-preparation exception. NOT externally approved Odin, paid acceptance UNVERIFIED, NOT recording-ready. Spec only. This Kiro session executes none of the implementation.

## Overview

Repair the recovered, unworked synthetic answer grader so legitimate equivalence still matches while sign, unit, and decimal-magnitude errors are rejected, then verify with golden positive and negative fixtures and a re-run of the per-submission JSONL output. All implementation is future work gated behind an actual Kiro review PASS and Ky's main merge of the new canonical 18-record spec PR.

## Architecture

- Confirmed read-only source identity (reuse the UNWORKED recovered source; do not re-create):
  - `extractedRoot`: `<private recovery cache>/extracted/task_e_6ac6d5fc882c8322be32454df931e3e3`
  - `starterSubdirectory`: `bootcamp/exact-match-grader`
  - `cloudRecoveryTaskId`: `task_e_6ac6d5fc882c8322be32454df931e3e3` (`cloudStatusAtRead`: ready)
  - `diffSha256`: `86e64757ef6adf3756de26567866677fcda85d753fc354a2b0f6d308316763c7`
  - `starterFileCount`: 7
  - `legacyRecoveryIssue`: https://github.com/KyPython/ai-governance/issues/183 (retired historical alias)
- Starter files (read-only; do NOT copy raw source bytes): `README.md`, `fixtures/answer_key.json`, `fixtures/evaluation_batch.json`, `grader/__init__.py`, `grader/cli.py`, `grader/core.py`, `tests/test_core.py`.
- Contract: equivalent answers match; sign/unit/magnitude errors are rejected. The exact equivalence-vs-rejection policy is an AI-designed guided-reference proposal for Ky's batch-PR review (see below), not a recorded human decision.

## Components and Interfaces

- `grader/core.py` `normalize_answer`: the repair target; currently NFKC-normalizes, casefolds, strips, then collapses to a digit-only `numeric_portion` string that discards sign/unit and collapses magnitude.
- `grader/cli.py`: emits ONE JSON line PER submission via `json.dumps(record, ensure_ascii=False, sort_keys=True)`, where `record = { "submission_id", "question_id", **asdict(GradeResult) }`. There is NO run summary and NO `matched` field. This JSONL interface is the EXISTING FACT read from source (execution results unobserved until a later authorized run).
- `tests/test_core.py`: unit tests, extended with strengthened sign/unit/magnitude negatives.

## Data Models

- Answer-key record (`fixtures/answer_key.json`): array of `{ "question_id", "answer" }`. The sample answer is `"−12.5 m/s"`, written with a Unicode minus glyph U+2212.
- Evaluation-batch record (`fixtures/evaluation_batch.json`): array of `{ "submission_id", "question_id", "response" }`. Samples: `"-12.5 m/s"` (equivalent / awarded), `"12.5 m/s"` (sign error / reject), `"-12.5 km/s"` (unit error / reject), `"-125 m/s"` (magnitude error / reject), `"not available"` (reject).
- `core.GradeResult`: `{ awarded, normalized_expected, normalized_response }`.
- Per-submission CLI record (EXISTING FACT): `{ "submission_id", "question_id", awarded, normalized_expected, normalized_response }`, one JSONL line each. Any aggregate report beyond this JSONL is EXPRESSLY a proposed addition, not an existing fact.

## Correctness Properties

### Property 1: Whitespace/case/minus-glyph equivalence continues to match (preserved). The U+2212 vs ASCII `-` equivalence is exactly what the awarded `"-12.5 m/s"` vs keyed `"−12.5 m/s"` sample exercises.
**Validates: Requirements 4.1**
### Property 2: Sign mismatches, unit mismatches, and decimal-magnitude mismatches are rejected.
**Validates: Requirements 1.1, 2.1, 3.1**
### Property 3: No unexplained unit conversions; no universal-equivalence claim.
**Validates: Requirements 2.1, 4.1**

## Error Handling

- Malformed fixture entries fail loudly during the re-run rather than silently awarding credit.
- The grader returns a deterministic reject rather than a false positive on numeric ambiguity.

## Testing Strategy

- Golden positive fixtures (true equivalence) and negative fixtures (sign/unit/magnitude errors), plus a deterministic re-run of the per-submission JSONL output whose format is read from `grader/cli.py` (one JSON line per submission; no summary; no `matched` field).
- Standard-library-only, so NO third-party dependency adapter is required for this world.
- Meaningful strengthened tests MUST FAIL for the intended behavior BEFORE the smallest production repair and PASS after, with deterministic replay. The strengthened tests and the production repair MUST occur in a DISPOSABLE worked-reference copy — NEVER the published unworked starter, the original pinned input, or the Recorder-captured workspace before capture. Ordinary baseline runs are kept SEPARATE from any disposable guided worked reference, and source preservation MUST be VERIFIED. Published guided steps come from observed steps; on-camera edits and verification are HUMAN/manual only, no AI during capture.
- The precise matching policy is the AI-designed guided-reference proposal below, submitted for Ky's batch-PR review; future unaided transfer / human judgment stays separate.

### Guided-reference matching-policy proposal (AI-designed INTERNAL guided reference, for Ky's batch-PR review)
- PRESERVE tested whitespace/case/minus-glyph equivalence; the U+2212 vs ASCII `-` equivalence is exactly what the awarded sample exercises.
- REJECT fixture sign, unit, and decimal-magnitude mismatches.
- NO unexplained unit conversions; NO universal-equivalence claim.
- Grounded in the Goal, the actual fixtures, and the existing tests. This records no human decision; execution RESULTS remain unobserved until a later authorized run.

## Prior-draft reconciliation

- Closed-unmerged draft spec PR #37 (`specs/exact-match-grader-normalization`) is a HISTORICAL reusable draft only. It MUST NOT be reopened or merged, and it is not canonical. The sole future spec-merge gate is Ky's main merge of the NEW canonical 18-record spec PR.

## Human boundaries

- No AI during actual capture; the final matching-policy and authorship decisions stay human.
- Paid acceptance UNVERIFIED (neither eligible nor ineligible). Only the EXTERNAL paid/HOLD release is NOT a prerequisite for internal preparation. The required FUTURE INTERNAL gates REMAIN: an actual Kiro review PASS, Ky's merge of the NEW canonical spec PR to `main`, and bound internal admission. Recorded external fields (Stage=Candidate, Fit Gate=HOLD, blank Approval ID/Approved Goal/pay) and the pending actual Recorder/human-capture and pay gates are preserved as facts.
