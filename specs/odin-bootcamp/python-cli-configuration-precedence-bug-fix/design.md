# Design Document

> INTERNAL guided Bootcamp PREPARATION under an explicit user world-preparation exception. NOT externally approved Odin, paid acceptance UNVERIFIED, NOT recording-ready. Spec only. This Kiro session executes none of the implementation.

## Overview

Repair the recovered, unworked synthetic CLI so settings resolution follows the documented flag > non-empty-environment > config file > default precedence and empty env vars are not treated as set, then verify with a parametrized matrix plus live command runs. The real repair is confined to resolution ORDER (env currently applied after cli, so it wins) and empty-env-as-set; `load_settings` already accepts `environ` (defaulting to `os.environ`) and `cli.main` already calls it, so no new environment wiring is invented. All implementation is future work gated behind an actual Kiro review PASS and Ky's main merge of the new canonical 18-record spec PR.

## Architecture

- Confirmed read-only source identity (reuse the UNWORKED recovered source; do not re-create):
  - `extractedRoot`: `<private recovery cache>/extracted/task_e_6ac6cf4a80048322aa762d7aa8e4adcd`
  - `starterSubdirectory`: `starters/python-cli-configuration-precedence`
  - `cloudRecoveryTaskId`: `task_e_6ac6cf4a80048322aa762d7aa8e4adcd` (`cloudStatusAtRead`: ready)
  - `diffSha256`: `a6452d65e7c1b987e28ba5900a0c21c69acf00b2825e2749c3d163c6ccb3acfd`
  - `starterFileCount`: 11
  - `legacyRecoveryIssue`: https://github.com/KyPython/ai-governance/issues/155 (retired historical alias)
- Starter files (read-only; do NOT copy raw source bytes): `.gitignore`, `README.md`, `docs/behavior.md`, `pyproject.toml`, `src/waypoint_cli/__init__.py`, `src/waypoint_cli/__main__.py`, `src/waypoint_cli/cli.py`, `src/waypoint_cli/settings.py`, `tests/fixtures/waypoint.toml`, `tests/test_cli.py`, `tests/test_settings.py`.
- Authoritative contract: `docs/behavior.md` precedence, highest→lowest: (1) explicit `--region` flag, (2) a NON-EMPTY `WAYPOINT_REGION` env var, (3) the `region` key in the selected TOML config, (4) the built-in default `local-zone`. An unset OR empty env supplies no value. A missing config file is an error ONLY when explicitly selected with `--config`.

## Components and Interfaces

- `src/waypoint_cli/settings.py` `load_settings`: the primary repair target. It already accepts `environ` (defaulting to `os.environ` when `None`); the repair is to reorder resolution to flag > non-empty-env > config > default and treat empty env as unset. No new environment wiring is required.
- `src/waypoint_cli/settings.py` `read_config`: an explicitly supplied missing file raises `FileNotFoundError` (via `.open`); `config_path=None` means empty config (`{}`), NOT a fall-through error. These two paths MUST be distinguished.
- `src/waypoint_cli/cli.py` `main()`: already builds argparse (`--region`, `--config`) and already calls `load_settings`; no new wiring is invented.
- `src/waypoint_cli/__main__.py`: does `from waypoint_cli.cli import main; raise SystemExit(main())`, so the faithful offline live entrypoint is `PYTHONPATH=src python -m waypoint_cli` (NOT `-m waypoint_cli.cli`, which is a no-op). This is a concrete existing-entrypoint guided-reference proposal; it leaves no on-camera entrypoint choice and does not claim an editable install worked.
- `tests/test_settings.py` / `tests/test_cli.py`: extended with the conflict matrix and empty-env cases plus live runs.

## Data Models

- `Settings` dataclass: has ONLY `region`. `config_path` is a `load_settings` argument, NOT a `Settings` field.
- Source precedence tuple: `(flag, non-empty-env, config_file, default)` with flag highest.
- Config fixture (`tests/fixtures/waypoint.toml`): the config-file source for matrix rows.

## Correctness Properties

### Property 1: An explicit flag always wins over environment, config, and default.
**Validates: Requirements 1.1**
### Property 2: An unset OR empty-string env var supplies no value and falls through to the next lower-precedence source.
**Validates: Requirements 2.1**
### Property 3: The full four-source chain resolves the highest-precedence present source (flag > non-empty-env > config > default).
**Validates: Requirements 3.1**
### Property 4: `load_settings` already receives the environment (via its `environ` argument defaulting to `os.environ`), so precedence is testable end to end without new wiring.
**Validates: Requirements 4.1**

## Error Handling

- A config file explicitly selected with `--config` that is missing raises `FileNotFoundError`; this error behavior is OUTSIDE the precedence repair and is unchanged.
- `config_path=None` yields an empty config (`{}`), which is NOT an error and is distinct from an explicitly selected missing file.
- An unset or empty env var is treated as absent, not as an empty value.
- Unknown-argument handling is OUTSIDE the precedence repair and unchanged.

## Testing Strategy

- Parametrized precedence matrix across flag/env/config/default conflicts and empty-env cases, plus live command runs.
- A NARROW REVIEWED offline packaging adapter is required (real metadata gap): resolve `pytest>=8,<9` via reviewed `pyproject` metadata / prepared wheels and an explicit offline `--no-index` cache/helper. No fake `requirements-dev.txt`; no network pip. `PYTHONPATH=src` for tests.
- Meaningful strengthened tests MUST FAIL for the intended behavior BEFORE the smallest production repair and PASS after, with deterministic replay. The strengthened tests and the production repair MUST occur in a DISPOSABLE worked-reference copy — NEVER the published unworked starter, the original pinned input, or the Recorder-captured workspace before capture. Ordinary baseline runs are kept SEPARATE from any disposable guided worked reference, and source preservation MUST be VERIFIED. Published guided steps come from observed steps; on-camera edits and verification are HUMAN/manual only, no AI during capture.
- The exact matrix rows are settled during review from the exact Goal and the authoritative `docs/behavior.md`; the faithful offline live entrypoint is the existing `PYTHONPATH=src python -m waypoint_cli` guided-reference proposal (leaving no on-camera entrypoint choice). Execution results remain unobserved until a later authorized run.

## Human boundaries

- No AI during actual capture; the install strategy and authorship/consequential decisions stay human. The faithful live entrypoint is the existing-entrypoint guided-reference proposal `PYTHONPATH=src python -m waypoint_cli`.
- Paid acceptance UNVERIFIED (neither eligible nor ineligible). Only the EXTERNAL paid/HOLD release is NOT a prerequisite for internal preparation. The required FUTURE INTERNAL gates REMAIN: an actual Kiro review PASS, Ky's merge of the NEW canonical spec PR to `main`, and bound internal admission. Recorded external fields (Stage=Candidate, Fit Gate=HOLD, blank Approval ID/Approved Goal/pay) and the pending actual Recorder/human-capture and pay gates are preserved as facts.
