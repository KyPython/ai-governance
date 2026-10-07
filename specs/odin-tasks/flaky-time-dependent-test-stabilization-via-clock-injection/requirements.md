# Requirements — Flaky Time-Dependent Test Stabilization via Clock Injection

## Scope
Prepare a synthetic Python project with a deliberately time- and timezone-dependent test. The starter must make the nondeterminism reproducible while leaving the injected-clock refactor and final deterministic boundary tests for the human recording.

## Functional requirements
1. **R1 — Synthetic-only project.** Use fabricated module names, business rules, timestamps, and data.
2. **R2 — Direct system-time dependency.** The starter production code shall directly read system time/local timezone in a way that can change behavior across clock/TZ boundaries.
3. **R3 — Flaky or environment-sensitive test.** The starter test shall depend on ambient time/TZ and be reproducibly vulnerable to at least one midnight or timezone/DST boundary.
4. **R4 — Intended behavior documented.** A short neutral contract shall state the intended time semantics without instructing the engineer how to refactor.
5. **R5 — Deterministic reproduction helper.** Provide setup/commands that let the human demonstrate environment dependence during the recording without waiting for real wall-clock time.
6. **R6 — Standard-library-compatible path.** The starter shall not require a third-party time-freezing library for the eventual repair.
7. **R7 — No injected-clock solution.** Do not add the final clock abstraction, dependency-injection parameter, fixed timestamp suite, or final midnight/DST assertions.
8. **R8 — Multi-TZ verification scaffolding.** Provide a small shell/script pattern or documented commands for rerunning tests under multiple `TZ` values, without embedding the final corrected tests.
9. **R9 — No answer key.** Recorder-visible files shall not state the final refactor or expected patch.
10. **R10 — Pre-recording integrity.** Reviewer can verify the starter exhibits time/TZ sensitivity and that the approved human work remains undone.

## Acceptance criteria
- AC1: Starter installs/runs locally in VS Code's integrated terminal.
- AC2: At least one provided reproduction path demonstrates differing behavior or a failure under a changed time/TZ condition.
- AC3: No final injected-clock implementation or deterministic boundary test suite exists.
- AC4: Setup and reproduction commands are short enough for a 15–45:59 recording.
