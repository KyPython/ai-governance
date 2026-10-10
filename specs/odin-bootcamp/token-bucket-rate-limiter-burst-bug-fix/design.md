# Design Document

> INTERNAL guided Bootcamp PREPARATION under an explicit user world-preparation exception. NOT externally approved Odin, paid acceptance UNVERIFIED, NOT recording-ready. Spec only. This Kiro session executes none of the implementation.

## Overview

Correct the recovered, unworked token-bucket limiter so refill is continuous (fractional) and capped at capacity while preserving the injectable clock and backward-time rejection, then verify with fake-clock tests. All implementation is future work gated behind an actual Kiro review PASS and Ky's main merge of the new canonical 18-record spec PR.

## Architecture

- Confirmed read-only source identity (reuse the UNWORKED recovered source; do not re-create):
  - `extractedRoot`: `<private recovery cache>/extracted/task_e_6ac6d5fffbf483228e2111a2956bd9d7`
  - `starterSubdirectory`: `bootcamp/token-bucket-rate-limiter`
  - `cloudRecoveryTaskId`: `task_e_6ac6d5fffbf483228e2111a2956bd9d7` (`cloudStatusAtRead`: ready)
  - `diffSha256`: `cc432614f0dcfa728df956ced448d00e5bf1278e3c473ef5aa9b3ae3755fa092`
  - `starterFileCount`: 9
  - `legacyRecoveryIssue`: https://github.com/KyPython/ai-governance/issues/186 (retired historical alias)
- Starter files (read-only; do NOT copy raw source bytes): `.gitignore`, `README.md`, `examples/observe_limiter.py`, `pyproject.toml`, `src/harbor_gate/__init__.py`, `src/harbor_gate/limiter.py`, `tests/__init__.py`, `tests/fakes.py`, `tests/test_limiter.py`.
- Contract: continuous refill at a configured rate, tokens capped at capacity, injectable clock callable, backward-time rejection preserved.

## Components and Interfaces

- `src/harbor_gate/limiter.py` `_refill`: the repair target; cap tokens at capacity and compute fractional refill without `int(elapsed)` truncation; keep backward-clock rejection.
- `tests/fakes.py`: the injectable fake clock, preserved and reused by strengthened tests.
- `tests/test_limiter.py`: fake-clock suite extended with idle→burst and fractional-refill scenarios.
- `examples/observe_limiter.py`: observation entrypoint.

## Data Models

- Limiter state: `{ capacity, refill_rate, _tokens, _last_refill }`.
- Clock: an injectable callable returning the current time (monotonic-style float).

## Correctness Properties

### Property 1: After any idle period, `_tokens <= capacity` (capacity cap holds).
**Validates: Requirements 1.1**
### Property 2: Fractional elapsed time adds proportional tokens at `refill_rate` (no truncation).
**Validates: Requirements 2.1**
### Property 3: A single burst after idle admits at most capacity requests.
**Validates: Requirements 3.1**
### Property 4: A backward clock continues to be rejected; the injectable clock callable is preserved.
**Validates: Requirements 4.1**

## Error Handling

- Backward clock movement raises as before (preserved behavior).
- Invalid configuration continues to be rejected per the existing test.

## Testing Strategy

- Fake-clock tests driving idle → burst sequences and fractional-time refill; assert the capacity cap and the configured refill rate.
- Standard-library-only; tests run with `PYTHONPATH=src`, no editable install. No offline packaging adapter is needed for this world.
- Meaningful strengthened tests MUST FAIL for the intended behavior BEFORE the smallest production repair and PASS after, with deterministic replay. The strengthened tests and the production repair MUST occur in a DISPOSABLE worked-reference copy — NEVER the published unworked starter, the original pinned input, or the Recorder-captured workspace before capture. Ordinary baseline runs are kept SEPARATE from any disposable guided worked reference, and source preservation MUST be VERIFIED. Published guided steps come from observed steps; on-camera edits and verification are HUMAN/manual only, no AI during capture.
- `compileall` is only later disposable verification, not acceptance evidence.
- Preserve clock injection and backward-time rejection.

## Human boundaries

- No AI during actual capture; authorship/consequential decisions stay human.
- Paid acceptance UNVERIFIED (neither eligible nor ineligible). Only the EXTERNAL paid/HOLD release is NOT a prerequisite for internal preparation. The required FUTURE INTERNAL gates REMAIN: an actual Kiro review PASS, Ky's merge of the NEW canonical spec PR to `main`, and bound internal admission. Recorded external fields (Stage=Candidate, Fit Gate=HOLD, blank Approval ID/Approved Goal/pay) and the pending actual Recorder/human-capture and pay gates are preserved as facts.
