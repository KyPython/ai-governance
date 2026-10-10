# Design — Cursor-Pagination Aggregator Contract Repair

## Overview

This design is a Kiro spec review/enhancement in local session sess_ef9c3844-0570-409c-baa6-7cc73d898476 (executionTarget local) of a spec originally prepared under a prior owner/process. It documents a pinned, already-published private starter and the diagnostic-level defect visible in it. It does not write the fix and does not claim human authorship. Existing design content is preserved and folded into Kiro canonical sections.

A synthetic client aggregates records from a cursor-paginated REST endpoint, served locally from response fixtures. The aggregator collects pages in response order but does not guard against repeated cursors, empty pages, or duplicate records as the contract requires. The baseline suite is green and the ordinary case passes. In guided recording/practice mode the recorded human later diagnoses the contract gaps, repairs the aggregator to handle the edge cases while preserving server order, and verifies against the deterministic response fixtures.

- Candidate Goal SHA256 (Goal+LF): c08197cea0e65611a4f9d8979822968de9156e24a829c24fea2063e031fd6e86
- Candidate-stage bootcamp item: Approved Goal and Approval ID are empty; there is no retrospective Odin approval. Human approval, pay, and attempt fields are empty and unchanged by this pass.

## Architecture

Synthetic reference shape at the pinned commit (described for review only; not rebuilt):
- `README.md` — setup and the local baseline command.
- `pyproject.toml` — synthetic package metadata.
- `src/cursor_client/__init__.py`, `src/cursor_client/aggregator.py`, `src/cursor_client/cli.py`, `src/cursor_client/fixture_transport.py` — synthetic client, aggregator, CLI, and fixture-backed transport.
- `tests/test_aggregator.py`, `tests/test_fixture_transport.py` — green baseline tests.
- `fixtures/ordinary.json`, `fixtures/repeated-cursor.json`, `fixtures/empty-page.json`, `fixtures/duplicate-records.json` — ordinary case plus the three edge cases.

Dependencies and reproducibility (pinned profile):
- Dependency profile: **python-stdlib** — CPython only, no third-party packages, no network at runtime after checkout (fixtures stand in for the REST endpoint).
- Offline, pinned setup recipe (bound to the reviewed `PrepareTaskWork.py` helper, per-task): check out the pinned starter commit `9c829c6ec7f85cf382f97e286bf8acce20a96fe7`; use the pinned public CPython `{python}`; run with `PYTHONPATH=src`; no third-party packages and no pip install required (stdlib-only profile; the helper runs no network install for this profile).
- Source reuse: reuse the pinned starter unchanged; downstream MUST NOT rebuild or re-synthesize the starter.

## Components and Interfaces

- **Aggregator (`src/cursor_client/aggregator.py`):** collects pages in response order; omits guards for repeated cursors, empty pages, and duplicate records.
- **Fixture transport (`src/cursor_client/fixture_transport.py`):** fixture-backed stand-in for the REST endpoint.
- **CLI (`src/cursor_client/cli.py`):** synthetic entry point.
- **Response fixtures (`fixtures/*.json`):** ordinary case plus repeated-cursor, empty-page, and duplicate-records edge cases.
- **Baseline tests (`tests/`):** green tests exercising the ordinary case without wiring the contract-satisfying edge-case handling.

## Data Models

- **Paginated response fixtures:** ordinary and edge-case cursor pages; the vacancy lies in the aggregator not guarding repeated cursors, empty pages, or duplicate records.
- **Aggregated record set:** server-ordered records the aggregator must produce under the contract.

## Correctness Properties

### Property 1: server order preserved with edge-case guards (INV-1)
WHERE paginated responses contain repeated cursors, empty pages, or duplicate records, THE aggregator SHALL preserve server order with these explicit observable outcomes from the source contract / existing guided route: (a) STOP before re-requesting a cursor already seen and return the records already collected (a repeated cursor neither loops nor raises a new error); (b) FOLLOW a supplied next cursor even when that page's records are empty; (c) EMIT each record id exactly once, retaining its FIRST-seen payload and order. Bound fixtures: ordinary → `rec-101`, `rec-102`, `rec-103` with requests `[null, page-2]`; repeated → `rec-201`, `rec-202` with requests `[null, repeat]`; empty → `rec-301`, `rec-302` with requests `[null, gap, after-gap]`; duplicates → `rec-401`, `rec-402`, `rec-403` with requests `[null, overlap]`. This restates the disclosed guided reference; no repeated-cursor error, HTTP/network/malformed policy, or human judgment is invented.
**Validates: Requirements 3**

### Property 2: baseline is green at the pin
WHEN the registry baseline command runs against the unchanged pinned starter, THE suite SHALL exit 0 with output containing `Ran 4 tests`.
**Validates: Requirements 4**

- **INV-1 (governing invariant):** The aggregator MUST preserve server order while correctly handling repeated cursors, empty pages, and duplicate records across the paginated responses. The pinned starter intentionally aggregates in response order without those guards and violates this invariant without identifying the final repair.
- The seeded defect must be observable through the documented contract and ordinary execution.
- The baseline suite and ordinary fixture must remain meaningful while leaving the edge cases unsolved.

## Error Handling

Failure modes (reject and re-pin rather than alter the baseline):
- Baseline not green or ordinary case failing at the pin → fails R4; re-pin rather than edit the starter.
- No real gap (edge cases already handled) → fails R3; INV-1 not demonstrably violated.
- Baseline checks weakened or non-meaningful → fails R7.
- Any completed edge-case aggregation, final edge-case tests tied to the contract, diagnosis note, or patch diff present → fails R8.
- Baseline drifts from the registry exit code/substring (`Ran 4 tests`) → fails R4 AC; do not alter the baseline to pass.

## Testing Strategy

Baseline / red-green shape:
- Focused baseline command (registry baseline, deterministic, local): `{python} -m unittest discover -s tests -v` with env `PYTHONPATH=src` → exit 0, output contains `Ran 4 tests`.
- The baseline is green and the ordinary case passes on the starter; the recorded human later adds the decisive failing-then-passing edge-case checks (repeated cursors, empty pages, duplicate records) alongside the repair. This spec does not add those checks.

Evidence boundaries a reviewer MAY verify pre-recording (read-only, non-authoring):
- the offline setup works and the baseline command produces exit 0 and `Ran 4 tests`;
- the ordinary case passes;
- the aggregator does not guard against repeated cursors, empty pages, or duplicate records (defect present; INV-1 violated);
- the three edge fixtures exist and no completed edge-case handling or answer key is present in recorder-visible files.

Human-only during recording (not performed in this specification pass and absent from the unchanged pinned recording starter; separately disclosed TaskWorkPlan worked references were AI-authored, analyzed, and disposable-tested off-screen), in guided recording/practice mode: diagnosing the aggregation contract gaps; repairing handling of repeated cursors, empty pages, and duplicate records while preserving server order; verifying against the deterministic response fixtures. The human manually executes edits/tests and narrates actual outcomes from the unchanged unworked starter, with no AI interaction during capture; manual typing does not by itself imply unaided execution. A separate, future unaided Transfer Test is a distinct assessment. The disclosed off-screen worked reference and authorized guided practice do not substitute for that assessment or establish unaided mastery, paid eligibility, or human approval.

Explicit human gates:
- Human diagnosis, repair, recording, capture, and any Odin attempt/approval/pay remain human-owned and outside this spec. This spec does not fill approval, pay, metric, or judgment fields.
- All coding and source promotion are HELD until Ky merges the specs-only PR with green required checks (repo CI + `ai-governance / verdict`). Agents never merge, approve, deploy, or promote.
