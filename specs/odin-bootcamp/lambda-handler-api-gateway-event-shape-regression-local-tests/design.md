# Design Document

> INTERNAL guided Bootcamp PREPARATION under an explicit user world-preparation exception. NOT externally approved Odin, paid acceptance UNVERIFIED, NOT recording-ready. Spec only. This Kiro session executes none of the implementation.

## Overview

Add a bounded event-normalization layer to the recovered, unworked Lambda handler so both REST v1.0 and HTTP API v2.0 event shapes (and missing query parameters) are handled, then verify locally with fixture events for both formats. All implementation is future work gated behind an actual Kiro review PASS and Ky's main merge of the new canonical 18-record spec PR.

## Architecture

- Confirmed read-only source identity (reuse the UNWORKED recovered source; do not re-create):
  - `extractedRoot`: `<private recovery cache>/extracted/task_e_6ac6d2786b8c8322971aeb8206acf6eb`
  - `starterSubdirectory`: `starters/lambda-event-shape-regression`
  - `cloudRecoveryTaskId`: `task_e_6ac6d2786b8c8322971aeb8206acf6eb` (`cloudStatusAtRead`: ready)
  - `diffSha256`: `ce2045dd8c2685dc99c45320825c1613225a93ba6e705c3429c9cd5a876af4fa`
  - `starterFileCount`: 9
  - `legacyRecoveryIssue`: https://github.com/KyPython/ai-governance/issues/169 (retired historical alias)
- Starter files (read-only; do NOT copy raw source bytes): `.gitignore`, `README.md`, `fixtures/http-v2-search.json`, `fixtures/rest-v1-search.json`, `orbit_catalog/__init__.py`, `orbit_catalog/handler.py`, `pyproject.toml`, `scripts/invoke.py`, `tests/test_handler.py`.
- Contract: the handler returns the existing status/body/envelope for match / not-found / non-GET across both REST v1.0 and HTTP API v2.0 shapes, including missing query parameters.

## Components and Interfaces

- `orbit_catalog/handler.py`: the repair target; add a bounded normalization layer in front of the existing logic rather than rewriting it.
- `scripts/invoke.py`: local fixture invoke used to reproduce the v2 `KeyError` after admission. It imports the ROOT package (`from orbit_catalog.handler import handler`); future non-editable offline invocation needs an explicit root import-path/helper context (e.g. `PYTHONPATH` set to the starter root), rather than assuming a README editable `pip install` succeeded offline.
- `tests/test_handler.py`: pytest suite extended with v2 and absent-query cases.
- Existing response contract (200 match / 404 unknown / 405 non-GET) is read from source and preserved, including the full envelope.

## Data Models

- REST v1.0 event (`fixtures/rest-v1-search.json`): top-level `httpMethod` for the method and `queryStringParameters.name` for the query.
- HTTP API v2.0 event (`fixtures/http-v2-search.json`): `requestContext.http.method` for the method and STILL top-level `queryStringParameters.name` for the query.
- Normalized internal event: `{ method, query }` consumed by the existing handler logic.
- Response envelope (read from source, COMPLETE): every response is `{ "statusCode", "headers": {"content-type": "application/json"}, "body": json.dumps(payload, sort_keys=True) }`. Existing bodies: 405 `{"error":"method not allowed"}`, 404 `{"error":"object not found"}`, 200 the catalog match object. The `headers` key is always present.

## Correctness Properties

### Property 1: Method validation runs FIRST — both v1/v2 NON-GET requests return the existing 405 method-not-allowed envelope even without query/name. Only for GET do both shapes normalize to the same internal `{ method, query }` before handler logic runs — v1 method from top-level `httpMethod`, v2 from `requestContext.http.method`, with the query from top-level `queryStringParameters.name` in both.
**Validates: Requirements 1.1**
### Property 2: For a GET request, a missing/null `queryStringParameters` OR a PRESENT query mapping that LACKS `name` yields the bounded absent-query response using the same envelope (a 400 with a defined error body; see the guided-reference proposal), never a crash. This 400 does NOT overlap 405: a non-GET request missing query/name still returns 405, because method validation precedes query evaluation.
**Validates: Requirements 2.1**
### Property 3: The repair is confined to the normalization layer (bounded change); the preserved responses keep the full `{statusCode, headers, body}` envelope.
**Validates: Requirements 3.1, 4.1**

## Error Handling

- Method validation runs FIRST: NON-GET methods return the existing 405 contract (`{"error":"method not allowed"}`) across both shapes, even when query/name is absent.
- Only for GET: absent/null `queryStringParameters` OR a present query mapping that lacks `name` returns a bounded 400 with a defined JSON error body using the same `{statusCode, headers, body}` envelope (AI-designed guided-reference proposal below) instead of raising `KeyError`.

## Testing Strategy

- Local fixture events for both formats (`fixtures/rest-v1-search.json`, `fixtures/http-v2-search.json`) plus an absent-query case, asserting status codes and bodies via pytest.
- A NARROW REVIEWED offline packaging adapter is required (real metadata gap): resolve `pytest>=8,<9` via reviewed `pyproject` metadata / prepared wheels and an explicit offline `--no-index` cache/helper. No fake `requirements-dev.txt`; no network pip. The Lambda root package permits cached-pytest testing WITHOUT editable installation.
- Meaningful strengthened tests MUST FAIL for the intended behavior BEFORE the smallest bounded repair and PASS after, with deterministic replay. The strengthened tests and the production repair MUST occur in a DISPOSABLE worked-reference copy — NEVER the published unworked starter, the original pinned input, or the Recorder-captured workspace before capture. Ordinary baseline runs are kept SEPARATE from any disposable guided worked reference, and source preservation MUST be VERIFIED. Published guided steps come from observed steps; on-camera edits and verification are HUMAN/manual only, no AI during capture.
- The absent-query response is the AI-designed guided-reference proposal below (a bounded 400 with a defined error body in the same envelope) for Ky's batch-PR review; execution results remain unobserved until a later authorized run.

### Guided-reference absent-query proposal (AI-designed INTERNAL guided reference that actual Kiro CHOOSES and LABELS, for Ky's batch-PR review)
- PRESERVE the existing status/body/envelope for 200 match, 404 unknown, 405 non-GET (read from source), including the `{statusCode, headers: {content-type: application/json}, body}` envelope.
- VALIDATE method FIRST: non-GET requests on either shape return the existing 405 envelope even without query/name; only GET requests then evaluate the query.
- CHOOSE a concrete bounded absent-query response for GET requests with missing/null `queryStringParameters` OR a present query mapping that lacks `name`: a `400` using the same envelope with body `json.dumps({"error": "missing query parameter: name"}, sort_keys=True)`. This specific status and body is the AI-designed guided-reference choice, LABELED as such; it is NOT presented as a human-decided outcome and is NOT deferred to on-camera design.
- AI-designed and grounded in the Goal and fixtures; records no human decision. Execution results remain unobserved until a later authorized run.

## Prior-draft reconciliation

- Closed-unmerged draft spec PR #42 (`specs/lambda-apigw-event-shape-regression`) is a HISTORICAL reusable draft only. It MUST NOT be reopened or merged, and it is not canonical. The sole future spec-merge gate is Ky's main merge of the NEW canonical 18-record spec PR.

## Human boundaries

- No AI during actual capture; the final absent-query policy and authorship decisions stay human.
- Paid acceptance UNVERIFIED (neither eligible nor ineligible). Only the EXTERNAL paid/HOLD release is NOT a prerequisite for internal preparation. The required FUTURE INTERNAL gates REMAIN: an actual Kiro review PASS, Ky's merge of the NEW canonical spec PR to `main`, and bound internal admission. Recorded external fields (Stage=Candidate, Fit Gate=HOLD, blank Approval ID/Approved Goal/pay) and the pending actual Recorder/human-capture and pay gates are preserved as facts.
