# Design — Flaky Time-Dependent Test Stabilization via Clock Injection

## Repository shape
- `README.md` — setup and reproduction commands only.
- `docs/behavior.md` — intended time semantics.
- `src/` — small Python function that reads ambient system/local time.
- `tests/` — deliberately environment-sensitive starter test.
- optional `scripts/repeat_tests.sh` or equivalent — repetition/TZ scaffolding without final fixed-time assertions.

## Starter-state design
Use a compact rule whose result changes around date/time boundaries. The starter should make ambient clock/local-zone coupling visible through ordinary inspection and controlled environment changes. Do not add a `clock` parameter, injectable callable, or finished fixed-instant tests.

## Human boundary
KyJahn must diagnose the ambient-time coupling, decide and implement the injected-clock design, write fixed normal/midnight/DST tests, and prove deterministic results across repeated runs/TZ settings during TaskRecorder.

## Pre-recording verification
Reviewer verifies the environment-sensitive starter behavior and ensures no final refactor/tests are prewritten.
