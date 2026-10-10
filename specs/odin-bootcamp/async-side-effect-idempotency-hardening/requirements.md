# Requirements Document

Spec: Async Side-Effect Idempotency Hardening · Spec ID: IDEM · Status: proposed (spec-only); @KyPython approves by merging this spec-only PR.

## Goal

As a software engineer, diagnose a synthetic asynchronous job-processing service that duplicates a side effect when a job is delivered more than once, implement a bounded idempotency correction, and verify with regression tests and a duplicate replay that only one externally observable effect occurs.

Task Factory row: https://app.notion.com/p/3f08621e0a7a81e3b4efcfea472d9930

Goal SHA256: f3ec1c43c1fdfd8f1030ac2b0d82f2ed29157e61790e836b3f0831cdd6d5b90e
Note: the value above is the SHA256 of UTF-8(verbatim Goal + one trailing LF).

## Introduction

This spec governs user-authorized guided INTERNAL Bootcamp, fully-disclosed AI-assisted advance preparation for the task above. It is **NOT** paid Odin approval and **NOT** a claim of unaided human ability. No source is executed, repaired, promoted, merged, or deployed by this spec. The later deliverable is a bounded process-local idempotency guard plus regression/replay tests for the synthetic `parcel_pulse` package.

The Odin Fit Gate is **PASS** and the Stage is **Awaiting Odin approval**. This spec does **NOT** grant Odin approval and does **NOT** change pay. External human recording, execution, and approval remain separate future decisions.

### Source identity and admission

Recovery identity (VERIFIED CURRENT OBSERVATION):
- cloudRecoveryTaskId: `task_e_6ac6cf2519fc8322bffc02abee6bc4e6`
- diffSha256: `6e81335d891d0d18ed9290822d76af54e50cf8536a31bcc68fab12130a9004d4`
- extractedRoot: `<private recovery cache>/extracted/task_e_6ac6cf2519fc8322bffc02abee6bc4e6`
- starterSubdirectory: `starters/async-side-effect-idempotency-hardening`
- starterFileCount: 8
- dependencyShape: Python standard library + editable package
- baselineExecuted: **false**
- sourcePromoted: **false**

The parent session confirmed the Goal SHA256 matches UTF-8(verbatim Goal + one LF), that the extractedRoot and starterSubdirectory exist, and that a sample of file-byte digests matched the inventory below (authentic, unaltered, unworked recovered source). This spec binds that recovery digest and the inventory below.

sourceFileDigests inventory (reference only — paths + mode + sha256, NOT contents):

| path | mode | sha256 |
| --- | --- | --- |
| starters/async-side-effect-idempotency-hardening/README.md | 100644 | 49f902b4bc4a854565963cbff2eed278617dc393f8f90ff25703669555e85a7c |
| starters/async-side-effect-idempotency-hardening/fixtures/replayed_deliveries.jsonl | 100644 | 0aaa37a4919226100dfc2147863f776738eb88e07f2b3193495183136b01c899 |
| starters/async-side-effect-idempotency-hardening/parcel_pulse/__init__.py | 100644 | 4c384bd2ca4a4db8ce93d3bebef8d223b4401151b9ca49a395a8bed07c01fdbd |
| starters/async-side-effect-idempotency-hardening/parcel_pulse/cli.py | 100644 | 4254a5c28affdbd043ea6fff34f29d1ae5e80deb0dc8ab1692d1f62a099366bf |
| starters/async-side-effect-idempotency-hardening/parcel_pulse/outbox.py | 100644 | 964452da0e49c9662a1f699dacf4f4efefe368175e03c8865d44f81d1438308b |
| starters/async-side-effect-idempotency-hardening/parcel_pulse/worker.py | 100644 | fa6db964415d573b14d9a307fff3594a73438416c8bff1ff743214a45e34003f |
| starters/async-side-effect-idempotency-hardening/pyproject.toml | 100644 | cc51490e65eee767ad04fa36c7ebabb8df18afc92bccd46eac2c0b0757df1143 |
| starters/async-side-effect-idempotency-hardening/tests/test_worker.py | 100644 | cebcef94f7f3c69275b1455b01b316ac9202f1f3d8ffaa25064ea2cd218cd7cd |

(8 tracked file digests, all Git mode 100644, consistent with starterFileCount = 8.)

Preserved paid-state (EXACTLY as given — unchanged by this spec): Stage: **Awaiting Odin approval** · Fit Gate: **PASS** · Approved Goal: (empty) · Approval ID: (empty) · Approved Pay: **0**.

The actual future technical-prep gates are: real Kiro final review, a @KyPython merged-to-main spec, and the bound internal admission. Human/Recorder/paid/approval gates are separate and remain pending. Separate FUTURE human decisions — recording, execution, capture, privacy, audio/narration, transfer, and the external Odin approval itself — are distinct from this technical preparation.

Post-merge requirement: AFTER @KyPython merges this spec, and BEFORE any internal admission/registration or cloud promotion, the private Ky-owned unworked starter must be published and its full 40-character commit SHA plus per-file byte and mode verification against the inventory above confirmed. No starter SHA is invented here.

Native Kiro session references: Authorship provenance is author session `sess_6ccf95b7-8bbe-4225-8682-6f74410eb9cd` (historical); the original final-review session `sess_ef9c3844-0570-409c-baa6-7cc73d898476` is retained as historical provenance only. Internal admission follows the ACTUAL latest committed-head Kiro PASS capture/receipt referenced by the canonical PR provenance markers — not an exclusive `sess_ef9c3844...` receipt — and the current correction-review execution is session `sess_ef2ac960-554a-4517-8662-aa42a8afd1e9`.

## Glossary

- **parcel_pulse**: the synthetic async job-processing package.
- **Delivery(job_id, recipient, parcel_code)**: a job delivery record.
- **ParcelWorker.process**: awaits `asyncio.sleep(0)`, then `self._notifications.send(delivery)`, THEN adds `job_id` to `completed_jobs` — no idempotency guard.
- **process_batch**: runs `asyncio.gather` over all deliveries CONCURRENTLY.
- **JsonlOutbox.send**: appends one JSONL record `"Parcel {parcel_code} is ready for pickup"` under an `asyncio.Lock`.
- **Replay fixture**: `fixtures/replayed_deliveries.jsonl` reproduces a duplicated job_id.
- **Process-local**: the correction's scope — in-process reservation, not cross-process/broker/durable.
- **RUN LATER**: an observable check to execute after merge in a disposable copy; nothing is executed in this spec.

## Requirements

### Requirement 1: Exactly one observable effect per job_id (IDEM-1)

**User Story:** As a service engineer, I want a duplicated job to produce only one notification, so that recipients are not notified twice.

#### Acceptance Criteria

1. IDEM-1.1 WHEN a job_id is delivered more than once AND the send succeeds THE worker SHALL produce exactly one externally observable outbox notification for that job_id; a failed or uncertain send MAY yield zero or one effect (the reservation is retained, the original exception is propagated, and further same-`job_id` attempts are suppressed in this worker). (Source: README contract; bug produces multiple.)
2. IDEM-1.2 WHEN the duplicate-replay test runs THE outbox SHALL contain a single record per job_id. (Acceptance RUN LATER.)

### Requirement 2: Reserve before side effect, race-safe (IDEM-2)

**User Story:** As a service engineer, I want the reservation to happen before the awaited send, so that concurrent duplicates cannot both notify.

#### Acceptance Criteria

1. IDEM-2.1 WHILE processing deliveries concurrently THE worker SHALL check-and-reserve the job_id BEFORE awaiting `self._notifications.send(delivery)`. (Source: current process sends before marking; process_batch uses asyncio.gather.)
2. IDEM-2.2 WHEN concurrent identical deliveries run THE worker SHALL perform exactly one send. (Acceptance RUN LATER.)

### Requirement 3: Preserve ordinary single/distinct behavior (IDEM-3)

**User Story:** As a service engineer, I want distinct jobs still each notified once.

#### Acceptance Criteria

1. IDEM-3.1 WHEN deliveries have distinct job_ids THE worker SHALL send one notification per distinct job_id, unchanged from baseline. (Source: baseline tests cover single + two distinct.)
2. IDEM-3.2 WHEN the single and distinct regression tests run THEY SHALL still pass. (Acceptance RUN LATER.)

### Requirement 4: Outbox record format preserved (IDEM-4)

**User Story:** As a service engineer, I want the outbox record text/format unchanged.

#### Acceptance Criteria

1. IDEM-4.1 WHEN a notification is sent THE outbox SHALL append one JSONL record `"Parcel {parcel_code} is ready for pickup"` under its `asyncio.Lock`, unchanged. (Source: JsonlOutbox.send.)
2. IDEM-4.2 WHEN a deduplicated job completes THERE SHALL be exactly one record with the unchanged format. (Acceptance RUN LATER.)

### Requirement 5: Duplicate-replay verification (IDEM-5)

**User Story:** As a service engineer, I want the replay fixture to prove single-effect behavior.

#### Acceptance Criteria

1. IDEM-5.1 WHEN the fixture `fixtures/replayed_deliveries.jsonl` is processed THE verification SHALL assert only one observable effect per job_id occurs. (Source: replay fixture reproduces the duplicate.)
2. IDEM-5.2 WHEN the replay test runs THE outbox SHALL contain exactly one notification per job_id. (Acceptance RUN LATER.) Depends on IDEM-1, IDEM-2.

### Requirement 6: Process-local scope only (IDEM-6)

**User Story:** As a service engineer, I want the fix bounded to process-local idempotency.

#### Acceptance Criteria

1. IDEM-6.1 THE correction MUST NOT claim or depend on cross-process, broker, or durable guarantees; the reservation is PROCESS-LOCAL. (Source: task boundary; CLI replaces the outbox per run.)
2. IDEM-6.2 WHEN the implementation is inspected THE reservation state SHALL be in-process with no external store assumed. (Acceptance RUN LATER.)

### Requirement 7: Explicit bounded failure/retry policy (IDEM-7)

**User Story:** As a service engineer, I want a single explicit, bounded failure/retry policy proposed and documented, so that failed-send behavior is defined rather than left ambiguous.

The README defines no failure/retry policy, so the deliverable MUST adopt one explicit, consistent, AI-proposed GUIDEDREFERENCE failure policy for Ky's PR review (Ky may choose a different consistent explicit policy at review). The observed `worker.py` sends BEFORE `completed_jobs.add` and has NO early duplicate check; reserve-before-send and the held-reservation failure handling below are the proposed guided correction grounded in the Goal's single-observable-effect contract, not existing implementation:

- reserve the `job_id` BEFORE the awaited send;
- on any uncertain or failed send outcome, KEEP the reservation for this process, propagate the original exception, and suppress a later same-`job_id` retry in this worker — a bounded **at-most-once ATTEMPT** per `job_id` in this process, NOT a confirmed-delivery guarantee;
- this makes no durable, restart, multi-process, or exactly-once promise.

#### Acceptance Criteria

1. IDEM-7.1 WHERE a send fails or an uncertain outcome occurs THE deliverable SHALL apply the explicit proposed policy: keep the reservation for this process, propagate the original exception, and suppress a later same-`job_id` retry in this worker (bounded at-most-once ATTEMPT). (Source: observed `worker.py` sends BEFORE `completed_jobs.add` and has NO early duplicate check; reserve-before-send with a held failed reservation is the explicitly AI-proposed guided correction grounded in the Goal's single-observable-effect contract, NOT existing implementation; README has no failure policy.)
2. IDEM-7.2 THE deliverable MUST NOT claim a failed or ambiguous send proves an effect occurred, and MUST label this failure policy as an AI-proposed GUIDEDREFERENCE for Ky's PR review, not a final human decision. (Acceptance RUN LATER: a controlled failure/uncertain-send test shows the reservation held, the exception propagated, and no second attempt for that job_id; successful controlled fixtures still prove one effect.)

### Requirement 8: No exactly-once overclaim (IDEM-8)

**User Story:** As KyJahn, I want out-of-scope limits stated honestly.

#### Acceptance Criteria

1. IDEM-8.1 THE spec and deliverable MUST NOT claim production exactly-once semantics, durable atomicity, or cross-process/broker guarantees. (Source: task boundary.)
2. IDEM-8.2 THE README/notes SHALL state these out-of-scope limits. (Acceptance RUN LATER.)

### Requirement 9: No approval / pay / mastery change (IDEM-9)

**User Story:** As KyJahn, I want the Awaiting-approval/PASS/pay-0 state preserved and status language honest.

#### Acceptance Criteria

1. IDEM-9.1 THE spec MUST NOT claim a passing baseline, grant Odin approval, change pay, or claim unaided human mastery. (Source: honesty rules; baselineExecuted = false; preserved paid-state.)
2. IDEM-9.2 WHERE evidence is incomplete THE artifacts SHALL state a HOLD and preserve the Awaiting-approval/PASS state. (Acceptance RUN LATER.)
