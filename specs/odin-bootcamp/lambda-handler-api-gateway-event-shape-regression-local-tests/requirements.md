# Requirements Document

> INTERNAL guided Bootcamp PREPARATION under an explicit user world-preparation exception. This is NOT externally approved Odin, paid acceptance is UNVERIFIED, and it is NOT recording-ready. Spec documents only — no implementation, no execution, no publication in this Kiro session.

## Introduction

This spec covers the Lambda Handler API Gateway Event-Shape Regression (Local Tests) world. It documents, as read-only static evidence, a synthetic Python AWS Lambda handler that crashes after its API Gateway integration moves from the REST (payload v1.0) format to the HTTP API (payload v2.0) format, and it defines the future repair and verification work that will happen only AFTER an actual Kiro review PASS and Ky's human merge of the new canonical 18-record spec PR to `main`.

This Kiro session executes none of the implementation. It writes documentation only.

### Record identity

Task Factory row: https://app.notion.com/p/3f08621e0a7a81559019c1739de4151c

- Verified Goal+LF hash (SHA256 of exact UTF-8 Goal + one trailing LF): `924393d8173209796bec7bbf123169d0fbed71d45d73ed21a8718a6fb50fb3dc`
- Candidate (NOT approved) older no-LF hash: `73c3fdc549bc882686b384eeb2d663039f135a84d9f8dd89d1f1f2a6d013f1e1` — a recovery-map CANDIDATE only; NOT the approved Goal hash; MUST NOT be treated as current or approved.
- Provenance: actual author execution is local Kiro session `sess_74e2d316-c006-4a6b-883f-4809655cbd2b`.
- Current inventory FILE-BYTES SHA256 (`inventoryFileSha256`): `e2a1fb9e82bbbee7ed6bb76829247ffaa739f42de8e7f8f557a2db94c0695924` — SHA256 of the inventory file bytes.
- Current canonical semantic inventory SHA256 (`inventorySha256`): `8143891ad28dfac36b3dcc20217790c3d045659186416edc87d71e71e2519306` — SHA256 over all 18 records, sorted keys, compact JSON separators, UTF-8, `ensure_ascii=False`. Both hashes describe the SAME unchanged 18-record inventory; neither is old or superseded.

### Confirmed read-only source identity

- `extractedRoot`: `<private recovery cache>/extracted/task_e_6ac6d2786b8c8322971aeb8206acf6eb`
- `starterSubdirectory`: `starters/lambda-event-shape-regression`
- `cloudRecoveryTaskId`: `task_e_6ac6d2786b8c8322971aeb8206acf6eb`
- `cloudStatusAtRead`: `ready`
- `diffSha256`: `ce2045dd8c2685dc99c45320825c1613225a93ba6e705c3429c9cd5a876af4fa`
- `starterFileCount`: 9
- `legacyRecoveryIssue`: https://github.com/KyPython/ai-governance/issues/169 — a RETIRED historical alias, NOT the current owner.

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

As a cloud software engineer, diagnose a synthetic Python AWS Lambda handler that crashes after its API Gateway integration moves from the REST (payload v1.0) event format to the HTTP API (payload v2.0) format, add a bounded event-normalization layer that handles both shapes and missing query parameters, and verify locally with fixture events for both formats that the handler returns correct status codes and bodies.

## Requirements

### Evidence states

#### VERIFIED CURRENT OBSERVATION (static source review only — baseline NOT executed)
- `orbit_catalog/handler.py` reads `event["httpMethod"]` and `event["queryStringParameters"]["name"]` directly (REST v1 shape only).
- The HTTP API v2 fixture and absent-query handling are unrepaired, so a v2 event raises `KeyError`.
- Three ordinary REST tests exist: `test_rest_event_returns_catalog_match`, `test_rest_event_returns_not_found_for_unknown_object`, `test_rest_event_rejects_non_get_method`. They only cover v1.
- The existing response format (status/body/envelope) for 200 match / 404 unknown / 405 non-GET is a READ-ONLY FACT in `orbit_catalog/handler.py`; execution results remain unobserved until a later authorized run.
- Toolchain: Python + pytest. `pyproject.toml` declares optional-dependency `test = ["pytest>=8,<9"]`, build-system `setuptools>=68`. There is NO `requirements-dev.txt`.

#### INTENDED behavior
- A bounded event-normalization layer handles BOTH REST v1.0 and HTTP API v2.0 shapes and missing query parameters.
- Local fixture events for both formats return correct status codes and bodies.

#### VERIFIED failures (static only)
- STATIC DEFECT: direct `event["httpMethod"]` / `event["queryStringParameters"]["name"]` access assumes v1 only; a v2 event will raise `KeyError`. This is a static source observation; the v2 invoke failure MUST be OBSERVED after admission (not claimed now).

#### UNKNOWNS requiring reproduction after admission
- Actual baseline pytest pass/fail counts and exit code.
- The observed v2 `KeyError` at runtime (to be reproduced, not asserted now).
- Execution results of the status/body matrix (the response format itself is read from source; results unobserved until a later authorized run).
- These are source-level EXPECTATIONS until executed after admission; nothing has been run.

#### PROPOSED implementation constraints
- MUST add a BOUNDED normalization layer (both shapes + missing query), not a broad rewrite.
- A NARROW REVIEWED offline packaging adapter is required because a real metadata gap exists: supply `pytest>=8,<9` via reviewed `pyproject` metadata / prepared wheels and an explicit offline `--no-index` cache/helper. MUST NOT add a fake `requirements-dev.txt`; MUST NOT use network pip.
- The Lambda root package permits cached-pytest testing WITHOUT editable installation.
- The absent-query response MAY be stated as an AI-DESIGNED INTERNAL GUIDED-REFERENCE PROPOSAL for Ky's batch-PR review, grounded in the Goal/fixtures/tests; it MUST NOT claim a human already decided, and future unaided transfer / human judgment stays separate.

### Guided-reference absent-query proposal (for Ky's batch-PR review)
- PRESERVE the existing status/body/envelope contract for 200 match, 404 unknown, and 405 non-GET (read from source).
- PROPOSE a bounded absent-query response for review (when `queryStringParameters` is absent/null, return a defined, non-crashing status/body).
- This is an AI-designed guided-reference proposal; it records no human decision. Existing response format is a read-only fact; execution results remain unobserved until a later authorized run.

### Human-boundary subsection
- Formative, consequential, and authorship judgments stay human — including the final absent-query policy and future unaided transfer.
- No AI during actual capture.
- External paid acceptance is UNVERIFIED (neither eligible nor ineligible).
- Manual capture and all human gates (recorded Fit Gate HOLD, admission, approval) are PENDING.
- Baseline counts, the v2 crash, and status/body execution results are source-level EXPECTATIONS until executed after admission; nothing has been run.

### Numbered requirements

#### REQ-1 — Handle both event shapes
- Subject: event normalization.
- The handler MUST normalize both REST v1.0 and HTTP API v2.0 event shapes before use.
- EARS: WHEN a v2.0 event is received, THE handler SHALL extract method/query equivalently to v1.0.
- Rationale/source: Goal; static v1-only observation.
- Acceptance evidence 1.1: both-format fixture runs (post-admission).
- Prerequisite: offline packaging adapter reviewed; internal admission.

#### REQ-2 — Handle missing query parameters
- Subject: absent query.
- The handler MUST handle missing/absent query parameters without raising, returning the bounded absent-query response from the guided-reference proposal. This applies, for a GET request, both when `queryStringParameters` is absent/null AND when a query mapping is PRESENT but LACKS `name`; method validation precedes query evaluation, so a non-GET request returns 405 rather than this 400.
- EARS: WHEN a GET request has `queryStringParameters` absent/null OR present-but-without `name`, THE handler SHALL return the defined bounded 400 status/body rather than crash; WHEN the request method is non-GET, THE handler SHALL return the existing 405 before evaluating the query.
- Rationale/source: Goal; static direct-index observation; guided-reference proposal (handler returns 405 for non-GET before touching query).
- Acceptance evidence 2.1: v1/v2 GET fixtures for absent/null query AND present-query-without-`name`, plus non-GET-missing-query/name cases returning 405 (post-admission).

#### REQ-3 — Correct status codes and bodies
- Subject: response contract.
- The handler SHALL return the existing read-from-source status/body/envelope for 200 match, 404 unknown, and 405 non-GET across both shapes.
- EARS: WHEN each fixture event runs, THE handler SHALL return the contract status/body.
- Rationale/source: existing REST tests; source-read response format; Goal.
- Acceptance evidence 3.1: executed fixture matrix (post-admission; EXPECTATION only now).

#### REQ-4 — Bounded change
- Subject: scope.
- The normalization MUST be bounded; it MUST NOT broadly rewrite handler logic.
- EARS: WHILE repairing, THE change SHALL be confined to a normalization layer.
- Rationale/source: Goal "bounded".
- Acceptance evidence 4.1: diff review (pending).

#### REQ-5 — Offline packaging adapter (required; real metadata gap)
- Subject: tooling registration.
- A narrow reviewed `pyproject`/offline `--no-index` adapter SHALL supply `pytest>=8,<9`; the team MUST NOT add a fake requirements file and MUST NOT use network pip.
- EARS: WHEN tests are run after admission, THE tooling SHALL resolve pytest from reviewed metadata/prepared wheels only.
- Rationale/source: `pyproject.toml`; no `requirements-dev.txt` (real metadata gap).
- Acceptance evidence 5.1: reviewed adapter + cached run (pending).

## Glossary

- **REST v1.0 shape**: API Gateway REST payload with `event["httpMethod"]` and `event["queryStringParameters"]`.
- **HTTP API v2.0 shape**: API Gateway HTTP payload with method/query nested differently, which crashes the v1-only handler.
- **Bounded normalization layer**: a confined adapter mapping both shapes to a common internal form; not a broad rewrite.
- **Absent-query response**: the bounded, non-crashing response for a missing query parameter; proposed as an AI-designed guided reference for Ky's review.
- **Offline packaging adapter**: reviewed `pyproject`/`--no-index` resolution of `pytest>=8,<9` from prepared wheels; no fake requirements file, no network pip.
- **Internal admission**: the bound internal preparation gate after Kiro review PASS and Ky's main merge.
- **PR #42**: a closed-unmerged HISTORICAL reusable draft; not reopened, not merged, not canonical.
