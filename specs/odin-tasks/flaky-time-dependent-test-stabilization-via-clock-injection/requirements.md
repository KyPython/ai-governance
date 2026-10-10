# Requirements Document

## Introduction

This spec is a Kiro spec review/enhancement performed in local session sess_ef9c3844-0570-409c-baa6-7cc73d898476 (executionTarget local) of a spec originally prepared under a prior owner/process. It preserves the prior scope, functional requirements, and task structure, normalizes headings to the Kiro canonical format required by `validate_spec_format`, and corrects over-strict framing. It does not claim prior authorship.

The following paragraph is the exact supplied Goal, reproduced verbatim.

As a software engineer, diagnose a synthetic Python test that fails intermittently because the code under test reads the system clock and local timezone, refactor the function to accept an injected clock, rewrite the test to use fixed timestamps including a midnight and DST boundary, and verify the test passes deterministically across repeated runs and different TZ settings.

Task Factory row: https://app.notion.com/p/3f08621e0a7a813289fde5cad87aba40
Goal+LF SHA256: d416388e21c90e58bc75316bf7864589fb34850d3184bbb06e12b0a378d8000d
Source pin: https://github.com/KyPython/flaky-clock-injection@e5652bcb044cd24d2a7d1c2f8bb93b885cea2069

Downstream work MUST reuse this unchanged pinned source rather than rebuild the starter. The pinned commit is the single authoritative starter; no downstream task may regenerate, re-fork, or re-synthesize equivalent starter content.

Approval provenance: Odin Approval ID ODIN-7008E3C523BF49AAA591427B4F762EDB. Human approval, pay, and attempt fields are preserved unchanged and are NOT modified by this spec pass.

### Scope

Prepare a synthetic Python project with a deliberately time- and timezone-dependent test. The pinned recording starter must remain unworked and answer-key-free. The current intended mode is GUIDED recording/practice: a separate, disclosed, AI-authored worked reference already exists off-screen in the TaskWorkPlan (authorized, analyzed, disposable-tested), and during capture the human manually executes edits/tests and narrates the actual outcomes from the unchanged unworked starter with no AI interaction during capture. Manual typing from an unworked input does not by itself imply unaided execution. The separate, future human Transfer Test is a distinct UNAIDED assessment; it is not the current mode and not a prerequisite for guided world prep. Guided references do not establish unaided learning, mastery, paid eligibility, or human approval.

## Requirements

### Requirement 1: Synthetic-only project

**User Story:** As a task preparer, I want the starter to contain only fabricated content, so that no private source, credentials, or PII can leak into a recording.

#### Acceptance Criteria

1. WHERE the starter is checked out at the pinned source commit, THE reviewer SHALL confirm all recorder-visible module names, timestamps, and data are synthetic/fabricated with no private source, credentials, or PII. (R1)

### Requirement 2: Direct system-time dependency

**User Story:** As a task preparer, I want the production code to read ambient time directly, so that the nondeterminism the human must diagnose is genuinely present.

#### Acceptance Criteria

1. THE starter production code SHALL directly read system time/local timezone in a way that can change behavior across clock/TZ boundaries. (R2)

### Requirement 3: Flaky or environment-sensitive test

**User Story:** As a task preparer, I want the starter test to be reproducibly sensitive to time/TZ boundaries, so that the human can demonstrate the failure on camera.

#### Acceptance Criteria

1. THE starter test SHALL depend on ambient time/TZ and be reproducibly vulnerable to at least one midnight or timezone/DST boundary. (R3)
2. WHEN the reviewer runs `{python} -m unittest discover -s tests -v` on the pinned starter, THE baseline test command SHALL exit with code 0 or 1 and its output SHALL contain `Ran 1 test`. (R3, R5)

### Requirement 4: Intended behavior documented

**User Story:** As a reviewer, I want a neutral contract of intended time semantics, so that intended behavior is knowable without being told how to refactor.

#### Acceptance Criteria

1. THE pinned starter SHALL contain `docs/behavior.md`, AND its intended time semantics SHALL be stated neutrally and SHALL NOT instruct the engineer how to refactor. A missing `docs/behavior.md` SHALL NOT pass this criterion. (R4)

### Requirement 5: Deterministic reproduction helper

**User Story:** As a reviewer, I want a reproduction helper, so that environment dependence can be demonstrated without waiting for real wall-clock time.

#### Acceptance Criteria

1. WHEN the reviewer runs `{python} scripts/show_timezone_variation.py` on the pinned starter, THE reproduction helper SHALL exit with code 0 and its output SHALL contain `Timezone outcomes:`. (R2, R5, R8)

### Requirement 6: Standard-library-compatible path

**User Story:** As a task preparer, I want the eventual repair to be possible with the standard library only, so that no third-party time-freezing dependency is required.

#### Acceptance Criteria

1. IF the eventual repair is attempted, THE starter SHALL NOT require any third-party time-freezing library (standard-library-only path remains available). (R6)

### Requirement 7: No injected-clock solution in the starter

**User Story:** As a task preparer, I want the recording starter to omit the solution, so that the on-camera human work is not pre-done in the starter.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE starter SHALL contain no injected-clock abstraction, no dependency-injection clock parameter, no fixed-timestamp boundary suite, and no final midnight/DST assertions or answer key. (R7, R9)

### Requirement 8: Multi-TZ verification scaffolding

**User Story:** As a reviewer, I want TZ-rerun scaffolding, so that sensitivity across timezones can be shown without embedding the final corrected tests.

#### Acceptance Criteria

1. WHILE re-running the starter test under at least two different `TZ` environment values, THE starter SHALL demonstrate differing outcome or a failure attributable to the ambient clock/local-zone coupling. (R3, R8)

### Requirement 9: No answer key

**User Story:** As a task preparer, I want no answer key in recorder-visible files, so that the recording starter stays unworked.

#### Acceptance Criteria

1. WHERE recorder-visible files are inspected, THE starter SHALL state no final refactor or expected patch. (R9)

### Requirement 10: Pre-recording integrity

**User Story:** As a reviewer, I want to verify integrity before recording, so that the pinned starter exhibits the sensitivity and the on-camera human work remains pending.

#### Acceptance Criteria

1. WHILE the recording envelope is 15:00–45:59, EACH provided reproduction/repeat command SHALL complete within 60 seconds on the prepared local starter so multiple timezone runs can be demonstrated. (R5, R8, R10)

### Requirement 11: Goal-derived future repaired behavior

**User Story:** As a software engineer performing the future repair, I want the injected-clock refactor and its deterministic tests specified, so that the repaired behavior is verifiable against the Goal without altering the unworked starter or its exclusions.

#### Acceptance Criteria

1. THE future repair SHALL inject a clock into the function under test rather than reading the ambient system clock. (R11)
2. THE repaired tests SHALL use fixed injected instants including a normal instant, a midnight boundary, and a DST boundary. (R11)
3. WHERE a fixed injected instant and a fixed requested dispatch `location_timezone` input are supplied, THE computed calendar date/label SHALL honor the dispatch-location calendar date independent of the ambient process `TZ`; a different `location_timezone` INPUT MAY legitimately yield a different date. (R11)
4. THE repaired tests SHALL demonstrate identical, deterministic results across repeated runs and across different ambient process `TZ` settings. (R11)
5. THIS requirement describes FUTURE repaired behavior only; it SHALL NOT be present in the unworked pinned recording starter, and it does not alter the exact Goal or the starter's exclusion of the repair (Requirements 7, 9). (R11)

## Glossary

- **Pinned recording starter:** The unchanged, unworked repository at the pinned source commit that the human works from during capture.
- **Worked reference:** A separate, disclosed, AI-authored, analyzed, disposable-tested artifact that exists off-screen in the TaskWorkPlan; it does not establish unaided human learning, mastery, paid eligibility, or human approval.
- **Guided recording/practice (current mode):** The human manually executes edits/tests and narrates the actual outcomes from the unchanged unworked starter, with no AI interaction during capture. Manual typing from an unworked input does not by itself imply unaided execution.
- **Human Transfer Test (separate, future):** A distinct UNAIDED assessment; not the current mode and not a prerequisite for guided world prep.
- **`{python}`:** The pinned CPython interpreter (dependency profile `python-stdlib`, no third-party packages).
- **Recording envelope:** The 15:00–45:59 window within which reproduction/repeat commands must each complete within 60 seconds.
