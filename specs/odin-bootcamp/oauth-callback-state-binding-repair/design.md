# Design — OAuth Callback State-Binding Repair

## Overview

This design is a Kiro spec review/enhancement in local session sess_ef9c3844-0570-409c-baa6-7cc73d898476 (executionTarget local) of a spec originally prepared under a prior owner/process. It documents a pinned, already-published private starter and the diagnostic-level defect visible in it. It does not write the fix and does not claim human authorship. Existing design content is preserved and folded into Kiro canonical sections.

A synthetic OAuth callback handler accepts the redirect from an authorization server. It checks only that an authorization `code` is present and never validates the `state` value against the pending session, so unbound, mismatched, expired, and replayed state are accepted. The baseline suite is green and the valid fixture succeeds. In guided recording/practice mode the recorded human later diagnoses the missing state binding, repairs the handler to reject the invalid state cases while preserving the valid success path, and verifies with the deterministic local fixtures.

- Candidate Goal SHA256 (Goal+LF): 53aa8de22a4d56b96b893bd778b17f0d629b57b4a43de0d34883ada57016ff24
- Candidate-stage bootcamp item: Approved Goal and Approval ID are empty; there is no retrospective Odin approval. Human approval, pay, and attempt fields are empty and unchanged by this pass.

## Architecture

Synthetic reference shape at the pinned commit (described for review only; not rebuilt):
- `README.md` — setup and the local baseline/fixture commands.
- `callback.py` — synthetic callback handler (checks `code` presence; no `state` validation).
- `fixtures.py` — synthetic fixtures enumerating valid, missing, mismatched, expired, and replayed state.
- `run_fixtures.py` — deterministic local fixture runner.
- `tests/test_callback.py` — green baseline tests.

Dependencies and reproducibility (pinned profile):
- Dependency profile: **python-stdlib** — CPython only, no third-party packages, no network at runtime after checkout.
- Offline, pinned setup recipe (bound to the reviewed `PrepareTaskWork.py` helper, per-task): check out the pinned starter commit `c65f9343be723ea36289db541b8f373883cbfe8a`; use the pinned public CPython `{python}`; no third-party packages and no pip install required (stdlib-only profile; the helper runs no network install for this profile).
- Source reuse: reuse the pinned starter unchanged; downstream MUST NOT rebuild or re-synthesize the starter.

## Components and Interfaces

- **Callback handler (`callback.py`):** checks `code` presence; omits `state` validation against the pending session.
- **Fixtures (`fixtures.py`):** enumerate valid, missing, mismatched, expired, and replayed state cases.
- **Fixture runner (`run_fixtures.py`):** deterministic local runner exercising the fixtures.
- **Baseline tests (`tests/test_callback.py`):** green tests that pass the valid path without enforcing the negative cases.
- **Behavior contract (recorder-visible description):** states intended state-binding semantics while preserving the valid success path, without labeling the defect.

## Data Models

- **State-binding fixtures:** synthetic valid/missing/mismatched/expired/replayed state inputs; the vacancy lies in the handler never binding `state` to the pending session.
- **Pending session model:** synthetic session the callback should validate `state` against.

## Correctness Properties

### Property 1: invalid state rejected, valid path preserved (INV-1)
WHERE a callback request carries missing, unbound, mismatched, expired, or replayed `state` relative to the pending session, THE handler SHALL reject the request, while accepting the valid bound-state success path.
**Validates: Requirements 3**

### Property 2: baseline is green at the pin
WHEN the registry baseline commands run against the unchanged pinned starter, THE suite SHALL exit 0 with output containing `Ran 2 tests`, and the fixture runner SHALL exit 0 with output containing `"valid"`.
**Validates: Requirements 4**

- **INV-1 (governing invariant):** An OAuth callback MUST reject a request whose `state` is missing, unbound, mismatched, expired, or replayed relative to the pending session, while accepting the valid bound state. The pinned starter intentionally validates only `code` presence and violates this invariant without identifying the final repair.
- The seeded defect must be observable through the documented contract and ordinary execution.
- The baseline suite and valid fixture must remain meaningful while leaving the negative cases unenforced.

## Error Handling

Failure modes (reject and re-pin rather than alter the baseline):
- Baseline not green or valid case failing at the pin → fails R4; re-pin rather than edit the starter.
- No real gap (state already validated) → fails R3; INV-1 not demonstrably violated.
- Baseline checks weakened or non-meaningful → fails R7.
- Any completed state validator, final enforcement, diagnosis note, or patch diff present → fails R8.
- Baseline drifts from the registry exit codes/substrings (`Ran 2 tests`; `"valid"`) → fails R4 AC; do not alter the baseline to pass.

## Testing Strategy

Baseline / red-green shape:
- Focused baseline commands (registry baseline, deterministic, local): `{python} -m unittest discover -s tests -v` → exit 0, output contains `Ran 2 tests`; and `{python} run_fixtures.py` → exit 0, output contains `"valid"`.
- The baseline is green and the valid case passes on the starter; the recorded human later adds the decisive rejections for missing/mismatched/expired/replayed state alongside the repair. This spec does not add those checks.

Evidence boundaries a reviewer MAY verify pre-recording (read-only, non-authoring):
- the offline setup works and both baseline commands produce the exit codes and substrings above;
- the valid case passes;
- the handler never validates `state` against the pending session (defect present) and the invalid cases are not rejected (INV-1 violated);
- no completed state validator, final enforcement, or answer key exists in recorder-visible files.

Human-only during recording (not performed in this specification pass and absent from the unchanged pinned recording starter; separately disclosed TaskWorkPlan worked references were AI-authored, analyzed, and disposable-tested off-screen), in guided recording/practice mode: diagnosing the missing state binding; repairing the handler to reject missing/mismatched/expired/replayed state; preserving the valid success path; verifying with the deterministic fixtures. The human manually executes edits/tests and narrates actual outcomes from the unchanged unworked starter, with no AI interaction during capture; manual typing does not by itself imply unaided execution. A separate, future unaided Transfer Test is a distinct assessment. The disclosed off-screen worked reference and authorized guided practice do not substitute for that assessment or establish unaided mastery, paid eligibility, or human approval.

Explicit human gates:
- Human diagnosis, repair, recording, capture, and any Odin attempt/approval/pay remain human-owned and outside this spec. This spec does not fill approval, pay, metric, or judgment fields.
- All coding and source promotion are HELD until Ky merges the specs-only PR with green required checks (repo CI + `ai-governance / verdict`). Agents never merge, approve, deploy, or promote.
