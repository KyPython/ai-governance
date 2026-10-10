# Design: Async Side-Effect Idempotency Hardening

Spec ID: IDEM

## Overview

This design describes, from the observed recovered source only, how the later deliverable (a bounded process-local idempotency guard plus regression/replay tests) is intended to be built against the pinned synthetic `parcel_pulse` package. No source is executed, repaired, or promoted in this session (baselineExecuted = false). The Odin state is **Awaiting approval / Fit Gate PASS**; this spec does not grant approval or change pay.

Baseline (current) behavior — OBSERVED:
- `worker.py`: `Delivery(job_id, recipient, parcel_code)`; `ParcelWorker.process` awaits `asyncio.sleep(0)`, then `self._notifications.send(delivery)`, THEN adds `job_id` to `completed_jobs` — no idempotency guard. `process_batch` runs `asyncio.gather` over all deliveries CONCURRENTLY.
- `outbox.py`: `JsonlOutbox.send` appends one JSONL record `"Parcel {parcel_code} is ready for pickup"` under an `asyncio.Lock`.
- The bug: a duplicated job_id (and `fixtures/replayed_deliveries.jsonl`) produces MULTIPLE outbox notifications; the contract requires exactly ONE per job_id.
- Baseline `tests/test_worker.py` covers only single delivery and two distinct deliveries — not duplicates.
- The CLI replaces the outbox at the start of each run.

Intended corrected behavior (to build LATER):
- A process-local check-and-reserve of `job_id` performed BEFORE awaiting `send`, so concurrent identical deliveries cannot both pass; ordinary single/distinct behavior preserved.
- An explicit, bounded failure policy (AI-proposed GUIDEDREFERENCE for Ky's PR review; the README defines none): on a failed or uncertain send, keep the reservation for this process, propagate the original exception, and suppress a later same-`job_id` retry in this worker — a bounded at-most-once ATTEMPT, not a confirmed-delivery guarantee.

Exact boundary of the change: add the reservation in `ParcelWorker.process` before the awaited send; do NOT change the outbox record format or the `asyncio.Lock`; scope is process-local only.

## Architecture

The recovered source is a single editable Python package `parcel_pulse` (stdlib + editable package, no broker, no external store). The intended change is confined to one module; everything else is baseline-vs-intended context.

- `parcel_pulse/worker.py` (CHANGE BOUNDARY) — defines `Delivery` and `ParcelWorker`. `ParcelWorker.process` is the single site where the process-local check-and-reserve is inserted, before the awaited `send`. `process_batch` fans out with `asyncio.gather` and is the concurrency path the reservation must be race-safe against.
- `parcel_pulse/outbox.py` (PRESERVED) — `JsonlOutbox.send`, the externally observable effect. Record format and the `asyncio.Lock` are unchanged.
- `parcel_pulse/cli.py` (PRESERVED) — entry point that replaces the outbox at the start of each run and drives the worker over a JSONL input.
- `parcel_pulse/__init__.py`, `pyproject.toml` (PRESERVED) — editable-package packaging.
- `fixtures/replayed_deliveries.jsonl` (PRESERVED, read-only) — reproduces a duplicated job_id; the replay evidence source.
- `tests/test_worker.py` (EXTENDED LATER) — baseline single/distinct coverage, extended with duplicate + concurrent-identical regression tests.

Baseline vs intended: baseline sends then marks `completed_jobs`, so a duplicate (or a concurrent identical pair under `asyncio.gather`) sends twice. Intended reserves the `job_id` before the awaited send, so the second delivery short-circuits. The exact boundary of change is the reservation inside `ParcelWorker.process`; no new controller, queue, or ledger is introduced.

## Components and Interfaces

Interfaces are described in prose from the observed source; no source code is copied.

- `Delivery(job_id, recipient, parcel_code)` — the job delivery record consumed by the worker; `job_id` is the idempotency key.
- `ParcelWorker.process(delivery)` — the async method that currently awaits `asyncio.sleep(0)`, calls `self._notifications.send(delivery)`, then records `job_id` in `completed_jobs`. The intended deliverable inserts a check-and-reserve of `job_id` before the awaited send; on an already-reserved `job_id` it skips the send so, for a successful send, exactly one effect occurs.
- `ParcelWorker.process_batch(deliveries)` — fans out `process` over all deliveries with `asyncio.gather` concurrently; the reservation must be correct under this concurrency.
- `JsonlOutbox.send(delivery)` — appends exactly one JSONL notification line per call under an `asyncio.Lock`; this is the externally observable effect and is left unchanged.
- CLI (`parcel_pulse/cli.py`) — observed to replace the outbox at the start of each run and process a JSONL deliveries file; used for the duplicate-replay observation.

## Data Models

Shapes described in prose; fixture contents are not reproduced.

- `Delivery`: fields `job_id`, `recipient`, `parcel_code`.
- Outbox record (JSONL): one line per send carrying the notification text `"Parcel {parcel_code} is ready for pickup"`; one appended record per observable effect.
- Reservation state (intended, process-local): an in-memory set/collection of reserved `job_id` values held for the lifetime of the process; no external/durable store.
- Replay fixture `fixtures/replayed_deliveries.jsonl`: a JSONL sequence of delivery records that includes at least one repeated `job_id`.

## Correctness Properties

### Property 1: Single effect per job_id, race-safe
**Validates: Requirements 1.1, 1.2, 2.1, 2.2, 5.1, 5.2** (aliases IDEM-1, IDEM-2, IDEM-5)
For a SUCCESSFUL send / duplicate replay, a duplicated job_id yields exactly one observable effect; a FAILED or UNCERTAIN send MAY yield zero or one effect under the retained reservation (bounded at-most-once ATTEMPT, not a confirmed-delivery guarantee). The reservation precedes the awaited send so concurrent identical deliveries cannot both notify. — observable check: duplicate-replay and concurrent-identical tests show one record per job_id for successful sends (RUN LATER).

### Property 2: Ordinary behavior and record format preserved
**Validates: Requirements 3.1, 3.2, 4.1, 4.2** (aliases IDEM-3, IDEM-4)
Distinct job_ids each notify once; the outbox record text/format and `asyncio.Lock` are unchanged. — observable check: single/distinct regression tests pass; record format unchanged (RUN LATER).

### Property 3: Process-local, honest, no overclaim
**Validates: Requirements 6.1, 6.2, 7.1, 7.2, 8.1, 8.2, 9.1, 9.2** (aliases IDEM-6, IDEM-7, IDEM-8, IDEM-9)
The reservation is in-process only; failure/retry and concurrent behavior are described honestly; no exactly-once/durable/cross-process claim; approval/pay/mastery unchanged. — observable check: in-process reservation; out-of-scope limits stated; HOLD where unresolved (RUN LATER).

## Error Handling

- Reserve-before-send: the `job_id` is reserved BEFORE the awaited send, so a second identical delivery short-circuits.
- Failed / uncertain send (explicit proposed policy — AI-proposed GUIDEDREFERENCE for Ky's PR review; the README defines no failure policy): on any failed or uncertain send outcome the worker KEEPS the reservation for this process, propagates the original exception, and suppresses a later same-`job_id` retry in this worker. This is a bounded **at-most-once ATTEMPT** per `job_id` in this process, NOT a confirmed-delivery guarantee: a failed or ambiguous send does not prove an effect occurred. Ky may choose a different consistent explicit policy at review (Requirement 7.1, 7.2 / IDEM-7).
- Concurrent identical deliveries: under `process_batch`'s `asyncio.gather`, the check-and-reserve must be atomic enough that only one of two identical deliveries proceeds to send; the other is a no-op effect.
- Scope boundary: reservation is process-local; a process restart or a second process is explicitly out of scope and must not be described as exactly-once/durable/multi-process (Requirement 8.1 / IDEM-8).

## Testing Strategy

Outputs below are **expectations to verify LATER** against the reviewed pinned source in **disposable copies**. Nothing was executed in this session (baselineExecuted = false); these are expectations to verify LATER, not results.

| Command (literal) | Expected RED (pre-fix) | Expected GREEN (post-fix) | Requirements |
| --- | --- | --- | --- |
| `python -m unittest discover -s tests -v` (baseline worker tests) | Baseline passes (single + distinct only); no duplicate coverage | Still passes | 3.1, 3.2 (IDEM-3) |
| `python -m unittest discover -s tests -v` (new duplicate + concurrent-identical tests) | Fails/absent: duplicated job_id yields multiple outbox records | One record per job_id; concurrent identical deliveries yield one send | 1.1, 1.2, 2.1, 2.2, 5.1, 5.2 (IDEM-1, IDEM-2, IDEM-5) |
| `python -m parcel_pulse.cli fixtures/replayed_deliveries.jsonl` (observed CLI; replaces outbox per run) | Outbox contains duplicate notifications for the replayed job_id | Outbox contains exactly one notification per job_id | 1.1, 1.2, 5.1, 5.2, 6.1 (IDEM-1, IDEM-5, IDEM-6) |
| `python -m unittest discover -s tests -v` (new failure-policy test) | Fails/absent: no failed/uncertain-send policy test exists | Controlled failure/uncertain-send test shows the reservation held, the original exception propagated, and no second attempt for that job_id; a failed/ambiguous send is not treated as a proven effect | 7.1, 7.2 (IDEM-7) |

HOLD: All coding and source promotion are **HELD** until the canonical spec PR is merged by **@KyPython** into `ai-governance/main` with green required checks. Authorship provenance is author session `sess_6ccf95b7-8bbe-4225-8682-6f74410eb9cd` (historical); the original final-review session `sess_ef9c3844-0570-409c-baa6-7cc73d898476` is retained as historical provenance only. Internal admission follows the ACTUAL latest committed-head Kiro PASS capture/receipt referenced by the canonical PR provenance markers — not an exclusive `sess_ef9c3844...` receipt — and the current correction-review execution is session `sess_ef2ac960-554a-4517-8662-aa42a8afd1e9`. This spec does not grant Odin approval or change pay; external human recording/execution/approval remain separate pending decisions. The explicit bounded failure policy (reserve-before-send; keep reservation and propagate the exception on a failed/uncertain send; suppress later same-job retry; bounded at-most-once ATTEMPT, no durable/restart/multi-process/exactly-once promise) is an AI-proposed GUIDEDREFERENCE for Ky's PR review — not a decision already made and not a mastery claim.

Reuse-first note: Reuse existing registration/Python profiles, the reviewed generatedFiles recipe, and existing registry/publisher/learning-map/paired-GHA-artifact/Morning owners and the existing Notion row. Do not create new controllers, world queues, or ledgers.
