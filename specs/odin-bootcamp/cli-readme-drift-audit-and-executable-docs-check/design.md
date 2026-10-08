# Design: CLI README Drift Audit and Executable-Docs Check

Spec ID: DRIFT

## Overview

This design describes, from the observed recovered source only, how the later deliverable (a corrected README plus an executable docs-check) is intended to be built against the pinned synthetic `trailmark` tool. No source is executed, repaired, or promoted in this session (baselineExecuted = false).

Baseline (current) behavior — OBSERVED:
- Tool `trailmark` (`src/trailmark/cli.py`, stdlib argparse). Actual parser: positional `input`; `--format {text,json}` default `text`; `--minimum-score N` default `1`; `--include-drafts` (store_true). Installed as an editable console script named `trailmark`.
- Exit codes: `0` success; `3` invalid input (OSError/JSONDecodeError/ValueError, prints `trailmark: invalid input:`); `4` FileNotFoundError (prints `trailmark: input not found:`); argparse error for bad usage.
- Default text render prints `Observations: N` then `- name (score)` lines; json output is sorted-keys `{"count":N,"observations":[...]}`.
- README is drifted: wrongly documents `--output text|json` default `json`; `--min-score N` default `2`; `--drafts`; exit codes `1` and `2`; and example outputs inconsistent with actual defaults.
- `tests/test_cli.py` asserts real behavior (default over `fixtures/observations.json` → `Observations: 2` / `- fox tracks (3)` / `- owl call (1)`; `--format json --minimum-score 3 --include-drafts` → count 2, names [fox tracks, moss sample]; `invalid.json` → exit 3, `invalid input`).
- `scripts/docs_check.py` only LISTS ```bash blocks; it does NOT execute them.

Intended corrected behavior (to build LATER):
- README corrected so every flag, default, example, and exit code matches the real parser.
- An executable docs-check that runs each documented example against local fixtures and asserts stdout, STDERR, and exit code, failing on mismatch.

The corrected README documents exit `0` success, `2` argparse bad usage (diagnostic on stderr, empty stdout), `3` invalid input, and `4` file not found; the OLD README's documenting `2` as file-not-found is the drift (`2` is correct for argparse bad usage; `1` is wrong). The corrected README includes ONE deterministic declared bad-usage example (e.g. `trailmark --minimum-score -1`) that exits `2` with the argparse usage diagnostic on stderr and empty stdout, without changing the CLI.

Exact boundary of the change: edit `README.md` and replace `scripts/docs_check.py` list-only logic with execution + assertion; do NOT change `cli.py`. Examples use the installed console script `trailmark <args>` (not `python -m trailmark`), operate on local fixtures only, no arbitrary shell, no success-only grading.

## Architecture

The recovered source is an editable Python package `trailmark` (Python standard library + editable console script). The change touches documentation and the docs-check tool only; the parser is preserved.

- `README.md` (CHANGE BOUNDARY) — the drifted documentation reconciled to the real parser (flags, defaults, example outputs, exit codes).
- `scripts/docs_check.py` (CHANGE BOUNDARY) — replace list-only logic with execution of each documented example and assertion of stdout, stderr, and exit code.
- `src/trailmark/cli.py` (PRESERVED) — the stdlib argparse CLI; its parser behavior is the source of truth and is not changed to fit the README.
- `src/trailmark/__init__.py`, `pyproject.toml`, `.gitignore` (PRESERVED) — package/editable-console-script packaging.
- `fixtures/observations.json`, `fixtures/invalid.json` (PRESERVED, read-only) — the only inputs the documented examples and docs-check run against.
- `tests/test_cli.py` (PRESERVED) — asserts the real parser behavior; must still pass unchanged after the audit.

Baseline vs intended vs boundary: baseline README documents flags/defaults/exit codes that contradict the real parser, and `docs_check.py` only lists bash blocks without running them. Intended README matches the parser, and the docs-check executes each example and asserts stdout + exit code. The exact boundary is `README.md` plus the docs-check logic; `cli.py` and `test_cli.py` are untouched.

## Components and Interfaces

Interfaces described in prose from the observed source; no source code copied.

- `trailmark <input> [--format {text,json}] [--minimum-score N] [--include-drafts]` — the real console-script interface: positional `input`; `--format` default `text`; `--minimum-score` default `1`; `--include-drafts` store_true. Invoked as the installed console script, not `python -m trailmark`.
- Text render — prints `Observations: N` then `- name (score)` lines.
- JSON render — sorted-keys object `{"count":N,"observations":[...]}`.
- Exit codes — `0` success; `2` argparse bad usage (diagnostic on stderr, empty stdout); `3` invalid input (prefix `trailmark: invalid input:`); `4` file not found (prefix `trailmark: input not found:`).
- `scripts/docs_check.py` — currently lists ```bash blocks; intended to execute each documented example against local fixtures and assert stdout, stderr, and exit code, exiting non-zero on any mismatch, with no arbitrary shell and no success-only grading.

## Data Models

Shapes described in prose; fixture contents are not reproduced.

- Observations input JSON: an object `{"observations":[{"name":..., "score":..., "draft":...}, ...]}` consumed by `trailmark` (name/score/draft per observation).
- Text output: a header line `Observations: N` followed by `- name (score)` lines.
- JSON output: sorted-keys object `{"count":N,"observations":[...]}`.
- Docs-check example record (intended): per documented example, the literal command, the expected stdout, the expected STDERR (declared diagnostic/prefix for failure examples; empty stderr for successful examples), and the expected exit code to assert.

## Correctness Properties

### Property 1: Flags and defaults match the parser
**Validates: Requirements 1.1, 1.2, 2.1, 2.2, 3.1, 3.2** (aliases DRIFT-1, DRIFT-2, DRIFT-3)
Documented `--format`/default text, `--minimum-score`/default 1, and `--include-drafts` match the real parser. — observable check: docs-check runs each flag example and the real tool agrees on name/default (RUN LATER).

### Property 2: Exit codes match the code
**Validates: Requirements 4.1, 4.2** (alias DRIFT-4)
Documented exit codes `0` success, `2` argparse bad usage (stderr diagnostic, empty stdout), `3` invalid input, `4` file not found match the tool's observed exit codes and message prefixes; the OLD README's `2`-as-file-not-found is the drift. — observable check: docs-check asserts the observed exit code and stderr per documented failure example, including the declared bad-usage example (RUN LATER).

### Property 3: Example outputs match real runs
**Validates: Requirements 5.1, 5.2, 5.3, 5.4** (alias DRIFT-5)
Documented example outputs equal real stdout for the three canonical invocations. — observable check: each documented example executed; stdout and exit code match (RUN LATER).

### Property 4: Executable, fixture-only docs-check
**Validates: Requirements 6.1, 6.2, 7.1, 7.2** (aliases DRIFT-6, DRIFT-7)
The docs-check executes fixture-only examples and asserts stdout, stderr, and exit code, failing on mismatch; failure examples assert the declared stderr diagnostic/prefix and successful examples declare empty stderr; no arbitrary shell; no success-only grading. — observable check: docs-check exits non-zero if any example's stdout, stderr, or exit code differs; only known `trailmark` invocations over fixtures (RUN LATER).

### Property 5: Tool behavior preserved; honest status
**Validates: Requirements 8.1, 8.2, 9.1, 9.2** (aliases DRIFT-8, DRIFT-9)
`cli.py` and `tests/test_cli.py` are unchanged by the audit; no fabricated results or mastery claims. — observable check: baseline tests still pass unchanged; language audit (RUN LATER).

## Error Handling

- Invalid input: the tool exits `3` and prints the prefix `trailmark: invalid input:` (OSError/JSONDecodeError/ValueError); the corrected README documents this and the docs-check asserts it.
- File not found: the tool exits `4` and prints the prefix `trailmark: input not found:`; documented and asserted.
- Bad usage: argparse emits a usage error exiting `2` with the diagnostic on stderr and empty stdout; documented as the argparse bad-usage exit `2` (the drifted `2`-as-file-not-found and `1` are corrected), with one declared bad-usage example (e.g. `trailmark --minimum-score -1`).
- Docs-check mismatch: if any documented example's stdout, stderr, or exit code differs from the real run, the docs-check exits non-zero (no success-only grading); it runs only known `trailmark` invocations over local fixtures, never arbitrary shell (Requirements 6.2, 7.1 / DRIFT-6, DRIFT-7).

## Testing Strategy

Outputs below are **expectations to verify LATER** in **disposable copies**. Nothing was executed in this session (baselineExecuted = false); these are expectations to verify LATER, not results.

| Command (literal) | Expected RED (pre-fix) | Expected GREEN (post-fix) | Requirements |
| --- | --- | --- | --- |
| `python -m unittest discover -s tests -v` | Tool tests pass; README still drifted | Still pass; parser unchanged | 8.1, 8.2 (DRIFT-8) |
| `trailmark fixtures/observations.json` | Prints `Observations: 2` / `- fox tracks (3)` / `- owl call (1)` — contradicts drifted README default `json` | README documents this exact output | 1.1, 5.1 (DRIFT-1, DRIFT-5) |
| `trailmark --format json --minimum-score 3 --include-drafts fixtures/observations.json` | Count 2, names [fox tracks, moss sample]; flags differ from documented `--output/--min-score/--drafts` | README documents these flag names/defaults and output | 1.1, 2.1, 3.1, 5.2 (DRIFT-1, DRIFT-2, DRIFT-3, DRIFT-5) |
| `trailmark fixtures/invalid.json` | Exit 3, `trailmark: invalid input:`; README wrongly says exit 1 | README documents exit `0/2/3/4` (argparse bad usage = `2`, invalid input = `3`, file not found = `4`) | 4.1 (DRIFT-4) |
| `python scripts/docs_check.py README.md` | Only lists the README's bash blocks; does not execute them | The later PROPOSED executable docs-check executes each example and asserts stdout, stderr, and exit code, exits non-zero on mismatch (not the existing list-only script) | 6.1, 7.1 (DRIFT-6, DRIFT-7) |

HOLD: All coding and source promotion are **HELD** until the canonical spec PR is merged by **@KyPython** into `ai-governance/main` with green required checks. Authorship provenance is author session `sess_6ccf95b7-8bbe-4225-8682-6f74410eb9cd` (historical); the original final-review session `sess_ef9c3844-0570-409c-baa6-7cc73d898476` is retained as historical provenance only. Internal admission follows the ACTUAL latest committed-head Kiro PASS capture/receipt referenced by the canonical PR provenance markers — not an exclusive `sess_ef9c3844...` receipt — and the current correction-review execution is session `sess_ef2ac960-554a-4517-8662-aa42a8afd1e9`. No PR number, PASS, result, or human-mastery claim is asserted here. AI-proposed README corrections are GUIDEDREFERENCE proposals for Ky's PR review only.

Reuse-first note: Reuse existing registration/Python profiles, the reviewed generatedFiles recipe, and existing registry/publisher/learning-map/paired-GHA-artifact/Morning owners and the existing Notion row. Do not create new controllers, world queues, or ledgers.
