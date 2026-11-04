# Requirements — Async Side-Effect Idempotency Hardening

## Scope
Prepare a synthetic asynchronous job-processing service that produces a duplicate externally observable effect when the same job is delivered more than once. The starter must reproduce the defect deterministically while leaving the diagnosis, bounded correction, decisive regression coverage, replay proof, and final engineering narration for the human recording.

## Functional requirements
1. **R1 — Synthetic-only service.** Use fabricated service, queue, job, recipient, payload, and effect data.
2. **R2 — Asynchronous processing path.** A small worker shall accept queued jobs and perform an observable effect through a local fake adapter.
3. **R3 — Duplicate delivery fixture.** Include a deterministic fixture or harness that can deliver one logical job at least twice with the same stable job identity.
4. **R4 — Observable duplicate.** In the starter state, replaying that job shall record more than one externally observable effect.
5. **R5 — No real external systems.** Queue behavior, storage, and the side-effect boundary shall run locally without credentials, network calls, hosted services, or nondeterministic timing.
6. **R6 — Ordinary-path coverage.** Starter tests shall cover successful processing of distinct jobs and the normal single-delivery path without asserting the final duplicate-replay guarantee.
7. **R7 — Neutral behavior contract.** Document that one logical job is intended to cause at most one effect, while avoiding a diagnosis or prescribed implementation.
8. **R8 — Deterministic baseline commands.** Provide setup, ordinary test, and duplicate-reproduction commands that complete quickly and emit inspectable effect records.
9. **R9 — Bounded human task.** The eventual correction must be possible within this service and its local collaborators without redesigning the queue or introducing production infrastructure.
10. **R10 — No final solution.** Do not include the final guard, claim/ledger mechanism, deduplication implementation, decisive duplicate regression assertion, completed replay proof, answer key, or ready-to-paste patch.
11. **R11 — Pre-recording integrity.** A reviewer can verify both the deterministic duplicate and that the approved human diagnosis and repair remain undone.

## Acceptance criteria
- AC1: The starter installs and runs from a local integrated terminal.
- AC2: The ordinary-path starter tests pass before human changes.
- AC3: A documented replay command deterministically shows two effect records for one stable job identity.
- AC4: No decisive test already enforces the one-effect replay contract.
- AC5: No external credentials, services, or internet access are required after setup.
- AC6: The remaining work includes diagnosis, implementation, regression verification, and human narration.

## Recording envelope
- Setup and each baseline/replay command should complete within 60 seconds so diagnosis, correction, and repeated verification fit a 15:00–45:59 recording.
