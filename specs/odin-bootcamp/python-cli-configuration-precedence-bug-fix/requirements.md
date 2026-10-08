# Requirements Document

> INTERNAL guided Bootcamp PREPARATION under an explicit user world-preparation exception. This is NOT externally approved Odin, paid acceptance is UNVERIFIED, and it is NOT recording-ready. Spec documents only — no implementation, no execution, no publication in this Kiro session.

## Introduction

This spec covers the Python CLI Configuration Precedence Bug Fix world. It documents, as read-only static evidence, a synthetic Python command-line tool whose settings resolution lets environment variables override explicit command-line flags and treats empty environment variables as set, and it defines the future repair and verification work that will happen only AFTER an actual Kiro review PASS and Ky's human merge of the new canonical 18-record spec PR to `main`.

This Kiro session executes none of the implementation. It writes documentation only.

### Record identity

Task Factory row: https://app.notion.com/p/3f08621e0a7a815ebc8ae59c7a517514

- Verified Goal+LF hash (SHA256 of exact UTF-8 Goal + one trailing LF): `d0c7f52b8edfafc19c527494223c76f7ec92a6e7dc005a6dbf70514bd1c14626`
- Candidate (NOT approved) older no-LF hash: `174489b3bbf81318ea12eb961234d39aec20ae6382952e7baabbf9e87d06b937` — a recovery-map CANDIDATE only; NOT the approved Goal hash; MUST NOT be treated as current or approved.
- Provenance: actual author execution is local Kiro session `sess_74e2d316-c006-4a6b-883f-4809655cbd2b`.
- Current inventory FILE-BYTES SHA256 (`inventoryFileSha256`): `e2a1fb9e82bbbee7ed6bb76829247ffaa739f42de8e7f8f557a2db94c0695924` — SHA256 of the inventory file bytes.
- Current canonical semantic inventory SHA256 (`inventorySha256`): `8143891ad28dfac36b3dcc20217790c3d045659186416edc87d71e71e2519306` — SHA256 over all 18 records, sorted keys, compact JSON separators, UTF-8, `ensure_ascii=False`. Both hashes describe the SAME unchanged 18-record inventory; neither is old or superseded.

### Confirmed read-only source identity

- `extractedRoot`: `/Users/ky/Library/Caches/TaskWorkWorldRecovery/extracted/task_e_6ac6cf4a80048322aa762d7aa8e4adcd`
- `starterSubdirectory`: `starters/python-cli-configuration-precedence`
- `cloudRecoveryTaskId`: `task_e_6ac6cf4a80048322aa762d7aa8e4adcd`
- `cloudStatusAtRead`: `ready`
- `diffSha256`: `a6452d65e7c1b987e28ba5900a0c21c69acf00b2825e2749c3d163c6ccb3acfd`
- `starterFileCount`: 11
- `legacyRecoveryIssue`: https://github.com/KyPython/ai-governance/issues/155 — a RETIRED historical alias, NOT the current owner.

The confirmed recovered UNWORKED source MUST be reused. Do NOT invent a future repo or source commit and do NOT propose a duplicate new build. Do not copy raw source bytes into the docs.

### External human record fields (preserved as recorded facts, do not alter)

- Stage: Candidate (recorded fact; internal guided Bootcamp preparation only)
- Fit Gate: HOLD (recorded fact)
- Approval ID: (empty)
- Approved Goal: (empty — never fabricate an approved Goal)
- Pay / attempt / human fields: (empty)
- Source: recovered PRIVATE cache (NOT a published GitHub starter). No source commit and no current Build Issue for this row. Closed wrong-lane alias issues are history, not canonical builds.

### Internal preparation gates

The explicit-user world-preparation exception PERMITS off-screen coding, testing, source publication, and registration DESPITE the recorded Candidate stage, the Fit Gate HOLD, and the blank external Approval ID / Approved Goal. Those recorded paid/HOLD properties are preserved as facts and are NOT prerequisites for internal preparation.

The actual future internal-prep gates are:
1. an actual Kiro review PASS;
2. Ky's human merge of this NEW canonical 18-record spec PR to `main`;
3. bound internal admission.

Actual Recorder/human capture and paid-acceptance gates remain PENDING. Paid acceptance is UNVERIFIED (neither eligible nor ineligible). No AI during actual capture.

### Verbatim Goal

As a software engineer, fix a synthetic Python command-line tool whose settings resolution lets environment variables override explicit command-line flags and treats empty environment variables as set, implement the documented precedence of flag over environment over config file over default, and verify with a parametrized test matrix and live command runs that each source wins only when it should.

## Requirements

### Evidence states

#### VERIFIED CURRENT OBSERVATION (static source review only — baseline NOT executed)
- `src/waypoint_cli/settings.py` `load_settings` applies default -> config -> cli_region -> environment, i.e. environment is applied AFTER explicit CLI, so env wrongly overrides a flag.
- `if environment_region is not None` treats an empty-string env var as present, so an empty env var wrongly counts as set.
- Documented intended precedence (`docs/behavior.md`) is flag > environment > config file > default.
- `cli.py` `main()` builds argparse (`--region`, `--config`) and calls `load_settings`; it does NOT pass `environ`, and `cli.py` has no explicit `__main__` guard.
- There IS a `src/waypoint_cli/__main__.py`, but the recovery/promotion audit records that `python -m waypoint_cli.cli` is a no-op (`cli.py` has no `__main__` invocation).
- Six ordinary tests exist; they omit the conflict matrix and empty-env cases.
- Toolchain: Python + pytest; `pyproject.toml` declares `pytest>=8,<9` and `setuptools>=68`; NO `requirements-dev.txt`; `PYTHONPATH=src` for tests.

#### INTENDED behavior
- Precedence is flag > environment > config file > default (per `docs/behavior.md`, which is authoritative for the flag/env/config/default contract).
- An empty-string environment variable is NOT treated as set.
- Verification is a parametrized precedence test matrix plus live command runs; each source wins only when it should.

#### VERIFIED failures (static only)
- STATIC DEFECT (ordering): environment is applied after CLI, so env wrongly overrides an explicit flag.
- STATIC DEFECT (empty env): `is not None` admits an empty-string env var as set.
- Static source observations; baseline NOT executed.

#### UNKNOWNS requiring reproduction after admission
- Actual baseline test pass/fail counts and exit code.
- The faithful console-entrypoint / install strategy — whether to run via `python -m waypoint_cli` vs a console script — MUST be explicitly reviewed, given that `python -m waypoint_cli.cli` is recorded as a no-op. The actual flag/env/config/default contract in `docs/behavior.md` is authoritative.
- These are source-level EXPECTATIONS until executed after admission; nothing has been run.

#### PROPOSED implementation constraints
- MUST implement documented precedence flag > environment > config file > default.
- MUST NOT treat empty-string env vars as set.
- MUST keep Python + pytest; MUST NOT add a fake `requirements-dev.txt`. A NARROW REVIEWED offline packaging adapter is required because a real metadata gap exists: supply `pytest>=8,<9` via reviewed `pyproject` metadata / prepared wheels and an explicit offline `--no-index` cache/helper; never network pip.
- Entry-point/console strategy MUST be reviewed; `PYTHONPATH=src` for tests.

### Human-boundary subsection
- Formative, consequential, and authorship judgments stay human — including the entrypoint/install strategy decision.
- No AI during actual capture.
- External paid acceptance is UNVERIFIED (neither eligible nor ineligible).
- Manual capture and all human gates (recorded Fit Gate HOLD, admission, approval) are PENDING.
- Baseline counts, matrix results, and live-run contracts are source-level EXPECTATIONS until executed after admission; nothing has been run.

### Numbered requirements

#### REQ-1 — Correct precedence ordering
- Subject: settings resolution order.
- `load_settings` MUST resolve in the documented order so an explicit CLI flag wins over environment.
- EARS: WHEN both a flag and an env var are provided, THE tool SHALL use the flag.
- Rationale/source: `docs/behavior.md`; static ordering observation.
- Acceptance evidence 1.1: parametrized matrix row (post-admission).
- Prerequisite: internal admission.

#### REQ-2 — Empty env not treated as set
- Subject: empty-string env.
- An empty-string environment variable MUST NOT be treated as a set value.
- EARS: WHEN an env var is empty, THE tool SHALL fall through to the next lower-precedence source.
- Rationale/source: static `is not None` observation.
- Acceptance evidence 2.1: empty-env matrix row (post-admission).

#### REQ-3 — Full documented precedence chain
- Subject: four-source precedence.
- The tool SHALL implement flag > environment > config file > default end to end.
- EARS: WHEN sources conflict, THE highest-precedence present source SHALL win.
- Rationale/source: `docs/behavior.md`.
- Acceptance evidence 3.1: parametrized conflict matrix (post-admission).

#### REQ-4 — Verify existing environment/default wiring
- Subject: wiring verification.
- `load_settings` already defaults `environ` to `os.environ`, so the environment IS available to resolution without added plumbing; REQ-4 SHALL verify, via live CLI runs, that env participates at its correct precedence through this existing default. It MUST NOT require adding an `environ` argument to `main()` or any other unnecessary plumbing.
- EARS: WHEN `main()` runs, THE environment SHALL already be available to resolution via the existing `os.environ` default and SHALL be exercised live.
- Rationale/source: `main()` relies on the existing `os.environ` default in `load_settings`, which is correct wiring; verification exercises it live rather than treating it as a gap.
- Acceptance evidence 4.1: live command runs confirming env participation at correct precedence (post-admission).

#### REQ-5 — Console-entrypoint strategy (review-decided)
- Subject: entrypoint.
- The faithful console-entrypoint/install strategy MUST be explicitly reviewed (console script vs `python -m waypoint_cli`); the recorded `python -m waypoint_cli.cli` no-op MUST NOT be assumed functional.
- EARS: WHEN the entrypoint is chosen, THE decision SHALL follow the authoritative `docs/behavior.md` contract.
- Rationale/source: recovery/promotion audit; static `__main__` observation.
- Acceptance evidence 5.1: reviewed entrypoint decision (pending).

#### REQ-6 — Parametrized matrix + live runs
- Subject: verification.
- Verification SHALL use a parametrized precedence test matrix AND live command runs covering conflicts and empty-env cases.
- EARS: WHEN verification runs after admission, THE matrix SHALL assert each source wins only when it should.
- Rationale/source: Goal.
- Acceptance evidence 6.1: executed matrix + live runs (post-admission; EXPECTATION only now).

#### REQ-7 — Offline packaging adapter (required; real metadata gap)
- Subject: tooling registration.
- A narrow reviewed `pyproject`/offline `--no-index` adapter SHALL supply `pytest>=8,<9`; the team MUST NOT add a fake requirements file and MUST NOT use network pip.
- EARS: WHEN tests run after admission, THE tooling SHALL resolve pytest from reviewed metadata/prepared wheels only.
- Rationale/source: `pyproject.toml`; no `requirements-dev.txt` (real metadata gap).
- Acceptance evidence 7.1: reviewed adapter + cached run (pending).

## Glossary

- **Precedence chain**: flag > environment > config file > default, per `docs/behavior.md` (authoritative).
- **Empty env not set**: an empty-string environment variable falls through rather than counting as a set value.
- **Console-entrypoint strategy**: the reviewed decision between a console script and `python -m waypoint_cli`; the recorded `python -m waypoint_cli.cli` no-op is not assumed functional.
- **Offline packaging adapter**: reviewed `pyproject`/`--no-index` resolution of `pytest>=8,<9` from prepared wheels; no fake requirements file, no network pip.
- **Internal admission**: the bound internal preparation gate after Kiro review PASS and Ky's main merge.
