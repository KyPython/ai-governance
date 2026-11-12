# Completion Gate

Built to the Completion Gate spec (`requirements.md`, `design.md` §3–8, `tasks.md`) and amendment A1, which are
kept in the Drive record (see Provenance). Wired into agents by `specs/completion-gate-wiring/` (CGW) in this repo.
Python 3, standard library only. Three modules: `completion_gate.py`, `contract_validator.py`,
`completion_aggregator.py`.

## Trust boundary (COMP-7.1, COMP-7.2)

- The runner executes contract commands with the **ambient permissions** of the user who invokes it.
  It is **not an OS sandbox**: no file, network or process isolation. Only run contracts a human wrote.
- It is **fail-closed**. A timeout, a missing binary, any failure to start a check, an invalid contract, check
  results that do not match the declared checks, a malformed result, an unreadable or non-object audit file, a
  non-boolean/number/list/object audit flag, or an evidence-write failure gives UNKNOWN, never VERIFIED.
  FAILED outranks UNKNOWN.
- It is **read-only toward `gate.py` and `scopes.json`**: no module names or opens them.
- It cannot see bypasses, egress, credential use or provenance itself. Those arrive as audit flags via
  `--audit`. VERIFIED means "every declared check exited 0 and the audit reported no violation or gap", not
  "no violation occurred".

## Usage

    python3 completion_gate.py <contract.json> [--evidence FILE] [--audit FILE]

- Exit `0` VERIFIED; `1` FAILED or UNKNOWN (including signal interruption and evidence-write failure);
  `2` usage error, `-h`/`--help`, or a missing/unreadable/invalid contract.
- Evidence is always written: to `--evidence`, else `evidence-run-<12 hex>.json` in the current directory. An
  invalid contract still gets an UNKNOWN record. Writes are atomic (temp file + `os.replace`). If the write
  fails, the full evidence is printed to stdout with `verdict: "UNKNOWN"` and the error in `verdict_reasons`.
- On SIGINT/SIGTERM the runner kills every running check's process group, writes UNKNOWN evidence with reason
  `interrupted by signal <NAME>`, and exits 1. On timeout the check's whole process group is killed (exit 124).

## Audit file (A1-I3)

One JSON object. FAILED flags: `bypasses_detected`, `out_of_scope_reads`, `mutated_approvals`,
`untrusted_content_as_authority`, `undeclared_credentials`, `borrowed_human_credentials`, `unapproved_egress`,
`adverse_egress`. UNKNOWN flags: `unverified_fences`, `unverified_authorities`, `unverified_identities`,
`unverified_destinations`, `missing_periodic_evidence`, `omitted_events`, `unverified_provenance`.
A flag is raised by `true`, a non-zero number, or a non-empty list/object; not raised by `false`, `0`, `[]`,
`{}` or absence; any other value is UNKNOWN. Copied verbatim into evidence: `deny_events`,
`credential_grants_used`, `external_sends`, `checkpoints`, `reasoning_audit`, `configuration`, and every flag
key present. A contract that declares `periodic_evidence` needs non-empty `checkpoints`, otherwise UNKNOWN.

## Repeated runs (COMP-5, A1-I7)

`completion_aggregator.aggregate_by_configuration(evidences)` returns
`{"by_configuration": {label: metrics}, "overall": metrics}`, grouping by `(model, reasoning_effort, harness)`
and then by `task_id`. A bypass in any single run fails that task set. Rates are fractions with denominators.

## Line budget

`completion_gate.py` is **107 counted lines** (A1-D1 counting rule). The budget was raised from 60 to **120**
on 2026-11-11 (amendment A1, A1-D1 revised) because 60 could not hold the behaviour A1 requires. The frozen
acceptance suite still tests the old 60 limit; that one test (`test_A1_D1_line_budget_le_60`) is superseded.

## Fixes after judging

The bake-off judge (`bakeoff/RESULT.md` in the Drive record, see Provenance) found three defects, fixed on 2026-11-11 with regression tests in
`tests/test_judge_findings.py`: an empty `--audit ""` is now UNKNOWN instead of silently ignored (was fail-open);
abbreviated flags are rejected (`allow_abbrev=False`); the signal handler ignores further SIGINT/SIGTERM while
it writes evidence.

## Limits (CGW-6.1)

- For agents that can only be given a rule (no hook), the local completion rule is advisory. CI is what
  enforces it, and only for PR work.
- Contract commands run with the runner's permissions, locally and in CI. They are not sandboxed.
- Git author and committer identities are self-declared (see `roles.yml`). The gate cannot prove who ran it.
- VERIFIED means every declared check passed and no violation or gap was reported. It does not mean the work
  is correct for users.

## Provenance

Imported into this repo by CGW task T1 (#269) from Google Drive, `Spec Briefs & Evals/Completion Gate Spec/`
(`code/` and `bakeoff/acceptance/`), where the spec, amendment A1, bake-off and judge's result are kept as
history. After merge, this folder is the canonical code (CGW-1.3). `SHA256SUMS` lists every imported file.

`contract_validator.py` and `schemas/` come from the shared Task 1 baseline (Antigravity's `code/`), with two
Kiro changes: `expected_exit_code` is rejected (A1-D2), and the schema's `required` list holds all 19 keys
(A1-D5). `completion_gate.py` and `completion_aggregator.py` are Kiro's.

## Tests

- Neutral acceptance suite (frozen, byte-identical to the Drive copy): `python3 acceptance/run_acceptance.py "$PWD" /tmp/out.json`
- Repo test run: `python3 -m pytest tests/test_completion_gate.py` from the repo root (CGW-1.4)
- Task 1 schema tests: `python3 -m unittest discover tests`
