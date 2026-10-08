# Requirements Document

> INTERNAL guided Bootcamp PREPARATION under an explicit user world-preparation exception. This is NOT externally approved Odin, paid acceptance is UNVERIFIED, and it is NOT recording-ready. Spec documents only — no implementation, no execution, no publication in this Kiro session.

## Introduction

This spec covers the Exact-Match Grader Normalization False-Positive Repair world. It documents, as read-only static evidence, a synthetic deterministic answer grader whose normalization step awards credit to wrong answers, and it defines the future repair and verification work that will happen only AFTER an actual Kiro review PASS and Ky's human merge of the new canonical 18-record spec PR to `main`.

This Kiro session executes none of the implementation. It writes documentation only.

### Record identity

Task Factory row: https://app.notion.com/p/3f08621e0a7a811aa81dc7a39ac80b91

- Verified Goal+LF hash (SHA256 of exact UTF-8 Goal + one trailing LF): `1487d10f0b8f853e20856ffe19a23d01a0808fb023936f39370ab4589c2831ee`
- Candidate (NOT approved) older no-LF hash: `ff4e9a3d199e37e7482bb309771577d160abf194ce5bd10bc9dbca41c446ee5c` — a recovery-map CANDIDATE only; NOT the approved Goal hash; MUST NOT be treated as current or approved.
- Provenance: actual author execution is local Kiro session `sess_74e2d316-c006-4a6b-883f-4809655cbd2b`.
- Current inventory FILE-BYTES SHA256 (`inventoryFileSha256`): `e2a1fb9e82bbbee7ed6bb76829247ffaa739f42de8e7f8f557a2db94c0695924` — SHA256 of the inventory file bytes.
- Current canonical semantic inventory SHA256 (`inventorySha256`): `8143891ad28dfac36b3dcc20217790c3d045659186416edc87d71e71e2519306` — SHA256 over all 18 records, sorted keys, compact JSON separators, UTF-8, `ensure_ascii=False`. Both hashes describe the SAME unchanged 18-record inventory; neither is old or superseded.

### Confirmed read-only source identity

- `extractedRoot`: `/Users/ky/Library/Caches/TaskWorkWorldRecovery/extracted/task_e_6ac6d5fc882c8322be32454df931e3e3`
- `starterSubdirectory`: `bootcamp/exact-match-grader`
- `cloudRecoveryTaskId`: `task_e_6ac6d5fc882c8322be32454df931e3e3`
- `cloudStatusAtRead`: `ready`
- `diffSha256`: `86e64757ef6adf3756de26567866677fcda85d753fc354a2b0f6d308316763c7`
- `starterFileCount`: 7
- `legacyRecoveryIssue`: https://github.com/KyPython/ai-governance/issues/183 — a RETIRED historical alias, NOT the current owner.

The confirmed recovered UNWORKED source MUST be reused. Do NOT invent a future repo or source commit and do NOT propose a duplicate new build. Do not copy raw source bytes into the docs.

### External human record fields (preserved as recorded facts, do not alter)

- Stage: Candidate (recorded fact; internal guided Bootcamp preparation only)
- Fit Gate: HOLD (recorded fact)
- Approval ID: (empty)
- Approved Goal: (empty — never fabricate an approved Goal)
- Pay / attempt / human fields: (empty)
- Source: recovered PRIVATE cache (NOT a published GitHub starter). No source commit and no current Build Issue for this row. Closed wrong-lane alias issues are history, not canonical builds.

### Internal preparation gates

The explicit-user world-preparation exception PERMITS off-screen coding, testing, source publication, and registration DESPITE the recorded Candidate stage, the Fit Gate HOLD, and the blank external Approval ID / Approved Goal. Those recorded paid/HOLD properties are preserved as facts and are NOT prerequisites for internal preparation.

The actual future internal-prep gates are:
1. an actual Kiro review PASS;
2. Ky's human merge of this NEW canonical 18-record spec PR to `main`;
3. bound internal admission.

Actual Recorder/human capture and paid-acceptance gates remain PENDING. Paid acceptance is UNVERIFIED (neither eligible nor ineligible). No AI during actual capture.

### Verbatim Goal

As an evaluation engineer, diagnose a synthetic deterministic answer grader whose normalization step awards credit to wrong answers, correct the normalization so equivalent answers still match while sign, unit, and magnitude errors are rejected, and verify with golden positive and negative fixtures and a re-run score report.

## Requirements

### Evidence states

#### VERIFIED CURRENT OBSERVATION (static source review only — baseline NOT executed)
- `grader/core.py` `normalize_answer` performs NFKC + casefold + strip, then `numeric_portion = re.sub(r"[^0-9]", "", normalized)` and returns that digit string when present.
- Returning the digit-only string strips sign and unit and collapses magnitude, so wrong answers can match (false positive).
- Five ordinary tests exist: `test_ignores_surrounding_whitespace_for_text`, `test_collapses_repeated_whitespace_for_text`, `test_text_comparison_is_case_insensitive`, `test_unrelated_text_is_rejected`, `test_common_minus_glyphs_have_the_same_numeric_form`. They omit sign/unit/magnitude rejection.
- The re-run score-report output format is a READABLE FACT from source (`grader/cli.py`), read directly from source; execution RESULTS remain unobserved until a later authorized run.
- Toolchain: Python standard library only; no third-party install.

#### INTENDED behavior
- Equivalent answers still match; sign errors, unit errors, and magnitude errors are rejected.
- Verification via golden positive and negative fixtures plus a re-run score report.

#### VERIFIED failures (static only)
- STATIC DEFECT: digit-only `numeric_portion` normalization discards sign/unit and collapses magnitude, awarding credit to wrong answers. This is a static source observation; baseline NOT executed.

#### UNKNOWNS requiring reproduction after admission
- Actual baseline test pass/fail counts and exit code.
- The observed re-run score-report execution results (format is read from source; results are unobserved until a later authorized run).
- The content of golden fixtures as finalized for review.
- These are source-level EXPECTATIONS until executed after admission; nothing has been run.

#### PROPOSED implementation constraints
- MUST keep Python-standard-library-only.
- MUST preserve legitimate text equivalence (whitespace/case/minus-glyph) while rejecting sign/unit/magnitude errors.
- The matching policy MAY be stated as an AI-DESIGNED INTERNAL GUIDED-REFERENCE PROPOSAL for Ky's concrete batch-PR review, grounded in the actual Goal/fixtures/tests. It MUST NOT claim a human already decided, and the future unaided transfer / human judgment stays separate.

### Guided-reference matching-policy proposal (for Ky's batch-PR review)
- PRESERVE the tested whitespace/case/minus-glyph equivalence.
- REJECT fixture sign mismatches, unit mismatches, and decimal-magnitude mismatches.
- NO unexplained unit conversions and NO universal-equivalence claim.
- This is an AI-designed guided-reference proposal grounded in the Goal, fixtures, and existing tests; it does not record a human decision.

### Human-boundary subsection
- Formative, consequential, and authorship judgments stay human — including the final matching-policy decision and future unaided transfer.
- No AI during actual capture.
- External paid acceptance is UNVERIFIED (neither eligible nor ineligible).
- Manual capture and all human gates (recorded Fit Gate HOLD, admission, approval) are PENDING.
- Baseline counts and score-report execution results are source-level EXPECTATIONS until executed after admission; nothing has been run.

### Numbered requirements

#### REQ-1 — Reject sign errors
- Subject: numeric normalization.
- The grader MUST NOT award credit when the candidate answer differs from the key only by sign.
- EARS: WHEN a candidate differs from the key only in sign, THE grader SHALL reject it.
- Rationale/source: Goal; static `numeric_portion` observation.
- Acceptance evidence 1.1: negative golden fixture (post-admission).
- Prerequisite: internal admission.

#### REQ-2 — Reject unit errors
- Subject: unit handling.
- The grader MUST reject answers whose unit differs from the key as the guided-reference proposal defines non-equivalent (no unexplained unit conversions).
- EARS: WHEN a candidate carries a non-equivalent unit, THE grader SHALL reject it.
- Rationale/source: Goal; guided-reference proposal.
- Acceptance evidence 2.1: negative golden fixture (post-admission).

#### REQ-3 — Reject magnitude errors
- Subject: magnitude.
- The grader MUST NOT collapse magnitude; answers differing in decimal magnitude MUST be rejected.
- EARS: WHEN a candidate differs in magnitude, THE grader SHALL reject it.
- Rationale/source: static digit-collapse observation.
- Acceptance evidence 3.1: negative golden fixture (post-admission).

#### REQ-4 — Preserve legitimate equivalence
- Subject: text/numeric equivalence.
- The grader SHALL continue to match genuinely equivalent answers (whitespace, case, minus-glyph normalization).
- EARS: WHEN equivalent answers are graded, THE grader SHALL award credit.
- Rationale/source: existing five tests; contract.
- Acceptance evidence 4.1: positive golden fixtures (post-admission).

#### REQ-5 — Golden fixtures + re-run score report
- Subject: verification.
- Verification SHALL use golden positive AND negative fixtures and produce a re-run score report whose output format is read from `grader/cli.py`.
- EARS: WHEN verification runs after admission, THE suite SHALL evaluate both fixture classes and emit a score report.
- Rationale/source: Goal; source-read report format.
- Acceptance evidence 5.1: executed report (post-admission; EXPECTATION only now).

## Glossary

- **Equivalence**: whitespace/case/minus-glyph normalization that the grader must preserve as a legitimate match.
- **Sign/unit/magnitude error**: a candidate answer differing from the key by sign, unit, or decimal magnitude — rejected per the guided-reference proposal.
- **Guided-reference proposal**: an AI-designed internal matching policy for Ky's batch-PR review; not a recorded human decision.
- **Score report**: the re-run output produced by `grader/cli.py`; its format is read from source, its execution results unobserved until a later authorized run.
- **Internal admission**: the bound internal preparation gate after Kiro review PASS and Ky's main merge.
- **PR #37**: a closed-unmerged HISTORICAL reusable draft; not reopened, not merged, not canonical.
