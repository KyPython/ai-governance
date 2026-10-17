# Design — Async Side-Effect Idempotency Hardening

## Repository shape
- `README.md` — local setup, passing baseline tests, and duplicate-delivery reproduction commands only.
- `docs/behavior.md` — neutral one-logical-job/one-effect contract and synthetic operating assumptions.
- service module — job model plus asynchronous worker entry point.
- local adapters — deterministic in-memory queue/delivery harness and inspectable fake effect sink.
- fixtures or example script — one stable job delivered twice and output showing the recorded effects.
- tests — normal single-delivery and distinct-job behavior, without the decisive duplicate-replay assertion.

## Starter-state design
Keep the service compact and deterministic. A worker consumes a fabricated job and asks a fake boundary adapter to record an external effect. The delivery harness can replay the same serialized job identity, and the starter records each processing attempt as another effect. The same-process fixture avoids scheduling races and makes the observed baseline repeatable.

The code should contain realistic seams for inspection, but recorder-visible names and documentation must not identify a preferred repair. Do not prebuild an idempotency abstraction, durable claim store, conditional write, duplicate suppression branch, or assertion that gives away the completed correction.

## Human boundary
KyJahn must inspect the replay, diagnose why repeated delivery repeats the effect, choose the bounded semantics and correction, implement it, add decisive regression coverage, run a duplicate replay proving one observable effect, and narrate tradeoffs and failure modes during TaskRecorder.

## Pre-recording verification
The reviewer runs the ordinary-path tests and duplicate fixture, confirms the former pass and the latter records the effect twice for one job identity, and checks that no completed guard, decisive replay assertion, final verification note, or hidden answer is present.
