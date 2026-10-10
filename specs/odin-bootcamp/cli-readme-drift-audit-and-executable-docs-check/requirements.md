# Requirements Document

Spec: CLI README Drift Audit and Executable-Docs Check · Spec ID: DRIFT · Status: proposed (spec-only); @KyPython approves by merging this spec-only PR.

## Goal

As a technical writer for a developer tool, audit the README of a synthetic Python command-line tool against its actual behavior, correct every documented flag, default, example, and exit code that no longer matches, and verify the corrected README by running each documented example and a small docs-check script that confirms the examples' outputs and exit codes match.

Task Factory row: https://app.notion.com/p/3f08621e0a7a81d3a5c8ec0957bf0655

Goal SHA256: f48bd9f83bbea4d2a7bb878f57a35beee74ba02aa9c9e62c2cdcc4c5fa4e60d6
Note: the value above is the SHA256 of UTF-8(verbatim Goal + one trailing LF).

## Introduction

This spec governs user-authorized guided INTERNAL Bootcamp, fully-disclosed AI-assisted advance preparation for the task above. It is **NOT** paid Odin approval and **NOT** a claim of unaided human ability. No source is executed, repaired, promoted, merged, or deployed by this spec. The later deliverable is a corrected README plus an executable docs-check for the synthetic `trailmark` tool.

### Source identity and admission

Recovery identity (VERIFIED CURRENT OBSERVATION):
- cloudRecoveryTaskId: `task_e_6ac6d281600083228055d038ed616cca`
- diffSha256: `668d30b3e363c8fd6cd48d33e1c58fbc8311ed44588345b24ee4d32602a38cc6`
- extractedRoot: `<private recovery cache>/extracted/task_e_6ac6d281600083228055d038ed616cca`
- starterSubdirectory: `specs/odin-tasks/cli-readme-drift-audit/starter`
- starterFileCount: 9
- dependencyShape: Python standard library + editable console script
- baselineExecuted: **false**
- sourcePromoted: **false**

The parent session confirmed the Goal SHA256 matches UTF-8(verbatim Goal + one LF), that the extractedRoot and starterSubdirectory exist, and that a sample of file-byte digests matched the inventory below (authentic, unaltered, unworked recovered source). This spec binds that recovery digest and the inventory below.

sourceFileDigests inventory (reference only — paths + mode + sha256, NOT contents):

| path | mode | sha256 |
| --- | --- | --- |
| specs/odin-tasks/cli-readme-drift-audit/starter/.gitignore | 100644 | 02ffcd9794dc2000d8a4c246f07cceb9de94f6a5b9aa6d649a2c41d5ce103b62 |
| specs/odin-tasks/cli-readme-drift-audit/starter/README.md | 100644 | 2f1651688eaa3c3bcda9fe4692016047083e63ff8762bcb2ec54d0a680b1239b |
| specs/odin-tasks/cli-readme-drift-audit/starter/fixtures/invalid.json | 100644 | bcedc7da27dca581475b9342c5e857428e8fac347fbab59c5a048fdb1b3e8f0d |
| specs/odin-tasks/cli-readme-drift-audit/starter/fixtures/observations.json | 100644 | 67fe1c69111eedf8e55dd354f8e7c91f94f91fdc830d8c167257b06ba4ca3a00 |
| specs/odin-tasks/cli-readme-drift-audit/starter/pyproject.toml | 100644 | 8feef1a0b0603fdb1d35e7b6c3f184a5fd589bd67e659b2ee433f28b3920db27 |
| specs/odin-tasks/cli-readme-drift-audit/starter/scripts/docs_check.py | 100644 | f3400852f0c202ebf7f1dcf31a2f52e09f720096a011cdf75f6ebff93a522590 |
| specs/odin-tasks/cli-readme-drift-audit/starter/src/trailmark/__init__.py | 100644 | 4b542601cb5c5b6227fc82fd50bfd53b7e34a0a8d396c546e2bcd279deb5bd62 |
| specs/odin-tasks/cli-readme-drift-audit/starter/src/trailmark/cli.py | 100644 | 8c144de6541a4662f45ec9fbb9904c24572a49115f885c479f87f314ec2c355c |
| specs/odin-tasks/cli-readme-drift-audit/starter/tests/test_cli.py | 100644 | 4e531e32a1ad4021d9440bced858e6d8ac7632b2f53b2309ffb34a157679b06d |

(9 tracked file digests, all Git mode 100644, consistent with starterFileCount = 9.)

Preserved paid-state (EXACTLY as given — unchanged by this spec): Stage: Candidate · Fit Gate: HOLD · Approved Goal: (empty) · Approval ID: (empty) · Approved Pay: (empty).

The preserved Candidate/HOLD/empty state is the Odin state and is not changed here; it is not a prerequisite for internal off-screen code/testing/private source publishing. The actual future technical-prep gates are: real Kiro final review, a @KyPython merged-to-main spec, and the bound internal admission. Human/Recorder/paid gates are separate and remain pending. Separate FUTURE human decisions — recording, execution, capture, privacy, audio/narration, transfer — are distinct from this technical preparation.

Post-merge requirement: AFTER @KyPython merges this spec, and BEFORE any internal admission/registration or cloud promotion, the private Ky-owned unworked starter must be published and its full 40-character commit SHA plus per-file byte and mode verification against the inventory above confirmed. No starter SHA is invented here.

Native Kiro session references: Authorship provenance is author session `sess_6ccf95b7-8bbe-4225-8682-6f74410eb9cd` (historical); the original final-review session `sess_ef9c3844-0570-409c-baa6-7cc73d898476` is retained as historical provenance only. Internal admission follows the ACTUAL latest committed-head Kiro PASS capture/receipt referenced by the canonical PR provenance markers — not an exclusive `sess_ef9c3844...` receipt — and the current correction-review execution is session `sess_ef2ac960-554a-4517-8662-aa42a8afd1e9`.

## Glossary

- **trailmark**: the synthetic Python CLI (`src/trailmark/cli.py`, stdlib argparse) installed as an editable console script named `trailmark`.
- **Drift**: a documented flag, default, example output, or exit code in the README that no longer matches real tool behavior.
- **docs-check**: `scripts/docs_check.py`; currently lists ```bash blocks only; the deliverable makes it execute each example and assert stdout and exit code.
- **Fixtures**: `fixtures/observations.json` and `fixtures/invalid.json`.
- **RUN LATER**: an observable check to execute after merge in a disposable copy; nothing is executed in this spec.

Note on invocation: the tool is invoked via its installed console script `trailmark <args>` (editable install), not `python -m trailmark`; the observed source exposes a console-script entry point, not a package `__main__`.

## Requirements

### Requirement 1: Reconcile the output-format flag (DRIFT-1)

**User Story:** As a technical writer, I want the README to document the real format flag, so that readers use the correct option.

#### Acceptance Criteria

1. DRIFT-1.1 THE corrected README SHALL document `--format {text,json}` with default `text`. (Source: actual parser; README wrongly documents `--output text|json` default `json`.)
2. DRIFT-1.2 WHEN the docs-check runs the documented format example THE documented flag and default SHALL match real behavior. (Acceptance RUN LATER.)

### Requirement 2: Reconcile the score-threshold flag (DRIFT-2)

**User Story:** As a technical writer, I want the README to document the real minimum-score flag and default.

#### Acceptance Criteria

1. DRIFT-2.1 THE corrected README SHALL document `--minimum-score N` with default `1`. (Source: actual parser; README wrongly documents `--min-score N` default `2`.)
2. DRIFT-2.2 WHEN the docs-check runs the documented example THE flag name and default SHALL match real behavior. (Acceptance RUN LATER.)

### Requirement 3: Reconcile the drafts flag (DRIFT-3)

**User Story:** As a technical writer, I want the README to document the real drafts flag.

#### Acceptance Criteria

1. DRIFT-3.1 THE corrected README SHALL document `--include-drafts` (store_true). (Source: actual parser; README wrongly documents `--drafts`.)
2. DRIFT-3.2 WHEN the docs-check runs the documented example THE flag name SHALL match real behavior. (Acceptance RUN LATER.)

### Requirement 4: Reconcile exit codes (DRIFT-4)

**User Story:** As a technical writer, I want documented exit codes to match the tool, so that automation relying on them is correct.

#### Acceptance Criteria

1. DRIFT-4.1 THE corrected README SHALL document `0` success, `2` argparse bad usage (diagnostic to stderr, empty stdout), `3` invalid input (OSError/JSONDecodeError/ValueError, message prefix `trailmark: invalid input:`), and `4` file not found (message prefix `trailmark: input not found:`). (Source: code exit codes 0/3/4 + argparse exit `2`; the OLD README's documenting `2` as file-not-found is the drift — `2` is correct for argparse bad usage, and `1` is wrong.) THE corrected README SHALL additionally include ONE deterministic declared bad-usage example (e.g. `trailmark --minimum-score -1`) that exits `2` with the argparse usage diagnostic on stderr and empty stdout, WITHOUT changing the CLI.
2. DRIFT-4.2 WHEN the docs-check runs each documented failure example (including the bad-usage example) THE asserted exit code SHALL match the observed exit code, AND the bad-usage example SHALL assert the usage diagnostic on stderr with empty stdout. (Acceptance RUN LATER.)

### Requirement 5: Reconcile example outputs (DRIFT-5)

**User Story:** As a technical writer, I want documented example outputs to match real runs, so that examples are trustworthy.

#### Acceptance Criteria

1. DRIFT-5.1 THE corrected README SHALL show the default run over `fixtures/observations.json` as `Observations: 2` then `- fox tracks (3)` and `- owl call (1)`. (Source: `tests/test_cli.py`.)
2. DRIFT-5.2 THE corrected README SHALL show `--format json --minimum-score 3 --include-drafts` as count 2 with names [fox tracks, moss sample]. (Source: `tests/test_cli.py`.)
3. DRIFT-5.3 THE corrected README SHALL show `invalid.json` as exit 3 with `invalid input`. (Source: `tests/test_cli.py`.)
4. DRIFT-5.4 WHEN each documented example is executed THE stdout and exit code SHALL match. (Acceptance RUN LATER.)

### Requirement 6: Executable docs-check asserts stdout AND exit code (DRIFT-6)

**User Story:** As a technical writer, I want the docs-check to execute examples and assert both outputs and exit codes, so that drift is caught automatically.

#### Acceptance Criteria

1. DRIFT-6.1 WHEN the docs-check runs a documented example THE docs-check SHALL execute it against local fixtures and assert the stdout, the STDERR, and the exit code; each documented example record SHALL carry expected stdout, expected stderr, and expected exit code. Failure examples SHALL assert the declared stderr diagnostic/prefix (e.g. `trailmark: invalid input:`, `trailmark: input not found:`, or the argparse usage diagnostic); successful examples SHALL declare empty stderr. (Source: task boundary; current `docs_check.py` only lists ```bash blocks.)
2. DRIFT-6.2 IF any example's stdout, stderr, or exit code differs from its declared expectation THEN the docs-check SHALL exit non-zero. (Acceptance RUN LATER.)

### Requirement 7: Safe, fixture-only examples (DRIFT-7)

**User Story:** As a maintainer, I want the docs-check limited to fixture-only `trailmark` runs, so that it cannot execute arbitrary commands.

#### Acceptance Criteria

1. DRIFT-7.1 THE docs-check MUST NOT run arbitrary shell commands and MUST NOT grade on success-only. (Source: task boundary.)
2. DRIFT-7.2 THE docs-check examples SHALL operate only against local fixtures. (Acceptance RUN LATER: only known `trailmark` invocations over fixtures.)

### Requirement 8: Preserve real tool behavior (DRIFT-8)

**User Story:** As a maintainer, I want the README corrected to match the tool, not the reverse.

#### Acceptance Criteria

1. DRIFT-8.1 THE audit MUST NOT change `src/trailmark/cli.py` parser behavior to fit the README. (Source: Goal.)
2. DRIFT-8.2 WHEN the audit completes THE baseline `tests/test_cli.py` SHALL still pass unchanged. (Acceptance RUN LATER.)

### Requirement 9: No fabricated results / mastery claims (DRIFT-9)

**User Story:** As KyJahn, I want honest status language.

#### Acceptance Criteria

1. DRIFT-9.1 THE process MUST NOT claim a passing baseline, invent example outputs, or claim unaided human mastery. (Source: honesty rules; baselineExecuted = false.)
2. DRIFT-9.2 WHERE evidence is incomplete THE artifacts SHALL state a HOLD. (Acceptance RUN LATER.)
