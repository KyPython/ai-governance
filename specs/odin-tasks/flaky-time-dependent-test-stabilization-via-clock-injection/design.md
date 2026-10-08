# Design — Flaky Time-Dependent Test Stabilization via Clock Injection

## Overview

This design is a Kiro spec review/enhancement in local session sess_ef9c3844-0570-409c-baa6-7cc73d898476 (executionTarget local) of a spec originally prepared under a prior owner/process. Existing design content is preserved and folded into Kiro canonical sections; provenance, pinned-dependency, evidence-boundary, failure-mode, and human-gate material is retained. No prior authorship is claimed.

A compact synthetic Python rule computes an outcome whose result changes around date/time boundaries because it reads the ambient system clock and local timezone. The documented contract (`docs/behavior.md`) states the intended time semantics neutrally. The pinned recording starter is deliberately nondeterministic and unworked; in guided recording/practice mode the human later injects a clock and writes fixed-instant tests, manually executing and narrating actual outcomes from the unchanged starter.

- Approved Goal SHA256 (Goal+LF): d416388e21c90e58bc75316bf7864589fb34850d3184bbb06e12b0a378d8000d
- Approval ID: ODIN-7008E3C523BF49AAA591427B4F762EDB (human-owned; unchanged by this pass)

Evidence boundaries (what a reviewer MAY verify pre-recording, read-only and non-authoring):
- the pinned starter checks out and both baseline commands produce the exit codes and substrings in the acceptance criteria;
- time/TZ sensitivity is demonstrable by changing `TZ`;
- no injected-clock refactor, final boundary suite, diagnosis note, or answer key exists in recorder-visible files.

A separate, disclosed, AI-authored worked reference already exists off-screen in the TaskWorkPlan (authorized, analyzed, disposable-tested). It is distinct from the recording starter. Diagnosis, tests, and repair are NOT banned in authorized off-screen reference preparation; only the pinned recording starter must remain unworked and answer-key-free.

## Architecture

Repository shape (pinned starter layout):
- `README.md` — setup and reproduction commands only.
- `docs/behavior.md` — intended time semantics.
- `src/` — small Python function that reads ambient system/local time.
- `tests/` — deliberately environment-sensitive starter test.
- optional `scripts/repeat_tests.sh` or equivalent — repetition/TZ scaffolding without final fixed-time assertions.
- `scripts/show_timezone_variation.py` — reproduction helper (baseline command target).

Dependencies and reproducibility (pinned profile):
- Dependency profile: **python-stdlib** — CPython only, no third-party packages, no network at runtime after checkout.
- Source reuse: check out the pinned starter `https://github.com/KyPython/flaky-clock-injection@e5652bcb044cd24d2a7d1c2f8bb93b885cea2069` and reuse it unchanged. Downstream MUST NOT rebuild or re-synthesize the starter.
- Offline, pinned setup recipe: clone at the pinned commit, use the pinned CPython `{python}`; no `pip install` of third-party packages is required or permitted for the baseline. Setup binds to the existing PrepareTaskWork helper per-task profile/argv/env in the runtime registry; no bare-network pip step is used.

## Components and Interfaces

- **Production rule (`src/`):** reads ambient system clock/local timezone; exposes the boundary behavior the human will later make injectable.
- **Starter test (`tests/`):** depends on ambient time/TZ; reproducibly sensitive to a midnight or DST boundary.
- **Reproduction helper (`scripts/show_timezone_variation.py`):** prints `Timezone outcomes:` and exits 0; demonstrates environment dependence without waiting for wall-clock time.
- **TZ scaffolding (optional script):** reruns tests under multiple `TZ` values without embedding final corrected tests.

Focused baseline commands (registry baseline, deterministic, local):
- `{python} -m unittest discover -s tests -v` → allowed exit 0 or 1, output contains `Ran 1 test`.
- `{python} scripts/show_timezone_variation.py` → exit 0, output contains `Timezone outcomes:`.

## Data Models

- **Timestamp inputs:** fabricated instants chosen to straddle a midnight and a DST boundary (synthetic; no real-world PII).
- **Timezone outcome record:** mapping of a `TZ` value to the computed outcome, surfaced by the reproduction helper under the `Timezone outcomes:` heading.

## Correctness Properties

### Property 1: determinism under a fixed clock/TZ
WHERE the eventual injected-clock function is evaluated with a fixed injected instant AND a fixed requested `location_timezone` input, THE computed label SHALL be identical across repeated runs AND across different ambient process `TZ` settings. A DIFFERENT `location_timezone` INPUT MAY legitimately yield a different date/label; this property does NOT claim identical labels across different location-timezone inputs, and it rejects the blanket reading that ambient `TZ` may alter the repaired label for fixed domain inputs. (Requirement 8 describes defective-starter ambient sensitivity, not the repaired behavior.)
**Validates: Requirements 11.4**

### Property 2: baseline stays green at the pin
WHEN the registry baseline commands run against the unchanged pinned starter, THE suite SHALL exit 0 or 1 with output containing `Ran 1 test`, and the reproduction helper SHALL exit 0 with output containing `Timezone outcomes:`.
**Validates: Requirements 3, 5**

- The starter must be genuinely nondeterministic across clock/TZ boundaries; an accidentally deterministic starter fails the task intent.
- A standard-library-only repair path must remain available (no third-party time-freezing dependency required).

## Error Handling

Failure modes (reject and re-pin rather than alter the baseline):
- Starter accidentally deterministic (no boundary sensitivity) → fails Requirement 3, criterion 1; Requirement 8, criterion 1.
- Third-party time-freezing dependency leaks into starter → fails Requirement 6, criterion 1.
- Any injected-clock code, fixed-instant suite, or answer-key note present → fails Requirement 7, criterion 1; Requirement 9, criterion 1.
- Baseline command drifts from registry (wrong exit code or missing substring) → fails Requirement 3, criterion 2; Requirement 5, criterion 1; do not alter the baseline to pass.

## Testing Strategy

Human-only during TaskRecorder — the pending human-owned step performed in guided recording/practice mode (NOT performed in this spec pass):
- diagnosing the ambient-time coupling;
- designing and implementing the injected-clock refactor;
- writing fixed normal/midnight/DST tests;
- proving deterministic results across repeated runs and TZ settings.

Human-boundary scope qualifier: the current intended mode is guided recording/practice. The human manually executes edits/tests and narrates actual outcomes from the unchanged unworked starter, with no AI interaction during capture; manual typing does not by itself imply unaided execution. A separate, future unaided Transfer Test is a distinct assessment. Authorized guided practice and disclosed worked references do not substitute for that assessment or establish unaided mastery, paid eligibility, or human approval.

Explicit human gates:
- Human diagnosis, repair, recording, capture, and any Odin attempt/approval/pay remain human-owned and outside this spec.
- All coding and source promotion are HELD until Ky merges the specs-only PR with green required checks (repo CI + `ai-governance / verdict`).
