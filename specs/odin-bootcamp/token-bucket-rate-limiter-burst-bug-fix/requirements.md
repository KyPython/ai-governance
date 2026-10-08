# Requirements Document

> INTERNAL guided Bootcamp PREPARATION under an explicit user world-preparation exception. This is NOT externally approved Odin, paid acceptance is UNVERIFIED, and it is NOT recording-ready. Spec documents only — no implementation, no execution, no publication in this Kiro session.

## Introduction

This spec covers the Token-Bucket Rate Limiter Burst Bug Fix world. It documents, as read-only static evidence, a synthetic Python token-bucket rate limiter that allows bursts above its configured capacity after idle periods, and it defines the future repair and verification work that will happen only AFTER an actual Kiro review PASS and Ky's human merge of the new canonical 18-record spec PR to `main`.

This Kiro session executes none of the implementation. It writes documentation only.

### Record identity

Task Factory row: https://app.notion.com/p/3f08621e0a7a815bb21edf440341ca13

- Verified Goal+LF hash (SHA256 of exact UTF-8 Goal + one trailing LF): `ccee7d10e633192742317009a437b6251877e742eae4d1a2cba0ccb2631c89a0`
- Candidate (NOT approved) older no-LF hash: `440469aa8bea8f8cfb90ed936744f73edfdbce94906208502b0e0db03489691c` — a recovery-map CANDIDATE only; NOT the approved Goal hash; MUST NOT be treated as current or approved.
- Provenance: actual author execution is local Kiro session `sess_74e2d316-c006-4a6b-883f-4809655cbd2b`.
- Current inventory FILE-BYTES SHA256 (`inventoryFileSha256`): `e2a1fb9e82bbbee7ed6bb76829247ffaa739f42de8e7f8f557a2db94c0695924` — SHA256 of the inventory file bytes.
- Current canonical semantic inventory SHA256 (`inventorySha256`): `8143891ad28dfac36b3dcc20217790c3d045659186416edc87d71e71e2519306` — SHA256 over all 18 records, sorted keys, compact JSON separators, UTF-8, `ensure_ascii=False`. Both hashes describe the SAME unchanged 18-record inventory; neither is old or superseded.

### Confirmed read-only source identity

- `extractedRoot`: `/Users/ky/Library/Caches/TaskWorkWorldRecovery/extracted/task_e_6ac6d5fffbf483228e2111a2956bd9d7`
- `starterSubdirectory`: `bootcamp/token-bucket-rate-limiter`
- `cloudRecoveryTaskId`: `task_e_6ac6d5fffbf483228e2111a2956bd9d7`
- `cloudStatusAtRead`: `ready`
- `diffSha256`: `cc432614f0dcfa728df956ced448d00e5bf1278e3c473ef5aa9b3ae3755fa092`
- `starterFileCount`: 9
- `legacyRecoveryIssue`: https://github.com/KyPython/ai-governance/issues/186 — a RETIRED historical alias, NOT the current owner.

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

As a backend engineer, diagnose a synthetic Python token-bucket rate limiter that allows bursts above its configured capacity after idle periods, correct the refill calculation so tokens are capped at capacity and fractional refill is handled, and verify with fake-clock tests that the limiter never admits more than capacity in a burst and refills at the configured rate.

## Requirements

### Evidence states

#### VERIFIED CURRENT OBSERVATION (static source review only — baseline NOT executed)
- `src/harbor_gate/limiter.py` `_refill` computes `elapsed = now - last_refill`, raises on backward clock (preserve this backward-time rejection), then does `whole_seconds = int(elapsed)`, `self._tokens += whole_seconds * refill_rate` (NO capacity cap), and `self._last_refill = now`.
- This truncates fractional refill and lets tokens exceed capacity after long idle (burst above capacity).
- Three baseline tests exist: `test_new_bucket_allows_requests_up_to_capacity`, `test_full_second_makes_a_token_available`, `test_invalid_configuration_is_rejected`. They omit the long-idle / fractional regression.
- Toolchain: Python standard library; tests/examples need `PYTHONPATH=src`; NO editable install required for tests.

#### INTENDED behavior
- Tokens are capped at capacity; fractional refill is handled correctly.
- Fake-clock tests show the limiter never admits more than capacity in a burst and refills at the configured rate.
- Fake-clock injection (clock callable) and the continuous-refill/capacity contract are preserved; backward-clock rejection is preserved.

#### VERIFIED failures (static only)
- STATIC DEFECT: `int(elapsed)` truncation drops fractional refill, and the missing capacity cap lets `self._tokens` exceed capacity after idle, producing an over-capacity burst. Static source observation; baseline NOT executed.

#### UNKNOWNS requiring reproduction after admission
- Actual baseline test pass/fail counts and exit code.
- The observed over-capacity burst under a fake clock (to be reproduced, not asserted now).
- These are source-level EXPECTATIONS until executed after admission; nothing has been run.

#### PROPOSED implementation constraints
- MUST cap tokens at capacity and handle fractional (continuous) refill.
- MUST preserve the fake-clock injection (clock callable) and backward-time rejection.
- MUST keep Python-standard-library-only; tests run with `PYTHONPATH=src`, no editable install. No offline packaging adapter is needed (standard library + built-ins).

### Human-boundary subsection
- Formative, consequential, and authorship judgments stay human.
- No AI during actual capture.
- External paid acceptance is UNVERIFIED (neither eligible nor ineligible).
- Manual capture and all human gates (recorded Fit Gate HOLD, admission, approval) are PENDING.
- Baseline counts and the observed over-capacity burst are source-level EXPECTATIONS until executed after admission; nothing has been run.

### Numbered requirements

#### REQ-1 — Cap tokens at capacity
- Subject: refill cap.
- `_refill` MUST NOT let `self._tokens` exceed configured capacity.
- EARS: WHEN a long idle period elapses, THE limiter SHALL cap available tokens at capacity.
- Rationale/source: Goal; static no-cap observation.
- Acceptance evidence 1.1: fake-clock burst test (post-admission).
- Prerequisite: internal admission.

#### REQ-2 — Handle fractional refill
- Subject: continuous refill.
- The refill MUST account for fractional elapsed time at the configured rate and MUST NOT truncate via `int(elapsed)`.
- EARS: WHEN fractional time elapses, THE limiter SHALL add the proportional token amount.
- Rationale/source: static `int(elapsed)` observation.
- Acceptance evidence 2.1: fake-clock refill-rate test (post-admission).

#### REQ-3 — Never admit more than capacity in a burst
- Subject: burst bound.
- The limiter MUST NOT admit more than capacity requests in a single burst.
- EARS: WHEN a burst follows idle, THE limiter SHALL admit at most capacity.
- Rationale/source: Goal.
- Acceptance evidence 3.1: fake-clock burst test (post-admission).

#### REQ-4 — Preserve clock injection and backward-time rejection
- Subject: contract preservation.
- The repair MUST preserve the injectable clock callable and the existing backward-clock rejection.
- EARS: WHEN the clock moves backward, THE limiter SHALL continue to reject it.
- Rationale/source: static `_refill` observation.
- Acceptance evidence 4.1: existing + new fake-clock tests (post-admission).

#### REQ-5 — Fake-clock verification
- Subject: verification approach.
- Verification SHALL use fake-clock tests only; `PYTHONPATH=src`, no editable install.
- EARS: WHEN verification runs after admission, THE tests SHALL use the injected fake clock.
- Rationale/source: Goal; toolchain observation.
- Acceptance evidence 5.1: executed fake-clock suite (post-admission; EXPECTATION only now). `compileall` bytecode is only later disposable verification.

## Glossary

- **Token-bucket refill**: adding tokens over elapsed time at a configured rate, capped at capacity.
- **Fractional refill**: proportional token addition for sub-second elapsed time; must not be truncated by `int(elapsed)`.
- **Capacity cap**: the maximum token count; tokens must never exceed it after idle.
- **Fake-clock injection**: an injectable clock callable used by deterministic tests; preserved by the repair.
- **Backward-time rejection**: the existing behavior of raising when the clock moves backward; preserved.
- **Internal admission**: the bound internal preparation gate after Kiro review PASS and Ky's main merge.
- **compileall**: disposable later bytecode verification only; not acceptance evidence.
