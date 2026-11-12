# Completion Gate neutral acceptance suite

Author: neutral judge-suite agent (not a contestant). Derived only from `requirements.md`, `amendment-A1.md`
(governs on conflict), `tasks.md`, `design.md` sections 3-8, and the contract schema/fixture shape.
No implementation file was read. Stdlib `unittest` only.

## Run

```
python3 run_acceptance.py <entry_dir> <out.json>          # report as JSON
ENTRY_DIR=<entry_dir> python3 -m unittest test_acceptance -v   # raw unittest
```

`ENTRY_DIR` unset makes `test_acceptance` fail at import with a clear message. `run_acceptance.py` runs the suite
in a child process (own session, 170 s wall-clock cap). If the entry cannot be imported every test is `error`.
`hard_gate_violations` lists every `*_HARDGATE` test that is not `pass` (fail or error). The suite never writes
into `ENTRY_DIR` (bytecode writing disabled), uses temp dirs, and kills leftover processes.

Contents: 125 tests (110 written methods + 15 generated one-per-audit-flag methods).
`fixtures/contract_base.json` (valid, all required keys, `identity_borrowing`, `terminal_human_intervention_only`,
`inherited_fence: true`), `audit_clean.json` (every flag key present and not raised), `audit_passthrough.json`.

## Test to spec ID map (method names start `test_<ID>_`)

| Spec ID | Tests |
|---|---|
| COMP-1.1 | valid accepted; 5 required keys; non-object/bad types; `validate_file` codes |
| COMP-1.2 | check_id / command / timeout_seconds rules, duplicates, empty criteria |
| COMP-1.3 .. 1.8 | one test each: boundary, fence, sources, identity/borrowing, egress, drift declarations |
| COMP-2.1 | no command runs when the contract is invalid |
| COMP-2.2 | sequential, independent subprocesses, all checks executed |
| COMP-2.3 | timeout gives 124; `_HARDGATE` timeout never VERIFIED (CLI) |
| COMP-2.4 | record fields, timestamps, duration, `passed`; untruncated independent stdout/stderr (300 KB / 200 KB) |
| COMP-2.5 | stdlib-only imports (line budget is A1-D1) |
| COMP-3.1 / 3.2 | evidence keys, `contract_hash`, per-check fields; atomic write (see A1-I5) |
| COMP-3.3 | DENY events, credential grants, external sends kept in `security_audit`; bypass recorded |
| COMP-3.4 / 3.5 / 3.6 | `reasoning_audit` + `self_override_suspected`; `reasoning_transparency: UNKNOWN`; checkpoints |
| COMP-4.1 .. 4.5 | three verdicts; precedence; each FAILED flag (8) and UNKNOWN flag (7) exactly; 124/127; VERIFIED rule |
| COMP-4.3 / 4.4 / 4.6 `_HARDGATE` | no FAILED or UNKNOWN condition yields VERIFIED |
| COMP-5.1 / 5.2 / 5.3 | joint metrics; partition + denominators; single failure and bypass; `_HARDGATE` bypass |
| COMP-6.1 | missing/invalid contract: stderr, exit 2, UNKNOWN evidence; `_HARDGATE` |
| COMP-6.2 | missing binary: 127, stderr, passed false, UNKNOWN; `_HARDGATE` |
| COMP-6.3 (+A1-I6) | SIGTERM and SIGINT: children and grandchildren dead, UNKNOWN evidence with `interrupted by signal <NAME>`, exit 1; `_HARDGATE` |
| COMP-6.4 | unwritable path / directory target: JSON on stdout, UNKNOWN, exit 1; `_HARDGATE` |
| COMP-7.1 | header states ambient permissions and no sandbox |
| COMP-7.2 (+A1-I8) | governance scan of all three modules; runtime sentinel files untouched |
| A1-D1 | counted-line budget <= 60 (tokenize + ast) |
| A1-D2 | `expected_exit_code` invalid (validator, CLI exit 2, nothing runs); `_HARDGATE` |
| A1-D3 | any exception starting a check gives 127, UNKNOWN; `_HARDGATE` |
| A1-D4 / A1-D5 | alias accepted, canonical accepted; all 19 keys required, `periodic_evidence` null/absent ok |
| A1-D6 | timeout kills a background grandchild (pid checked gone) |
| A1-I1 | exactly three modules; signatures and parameter names; exports; `evaluate_verdict` pure |
| A1-I2 | exit 0/1/2, unknown flag, missing value, `-h`/`--help`, any flag order, no checks run on usage error |
| A1-I3 | audit file errors; value rule; bad values named in reasons; passthrough keys; `_HARDGATE` variants |
| A1-I4 | mismatched/malformed results; `passed` never overrides; non-int/bool `exit_code`; invalid contract; periodic_evidence + checkpoints; reason ordering; `_HARDGATE` variants |
| A1-I5 | default path `evidence-run-<12 hex>.json`; `run_id`; Z timestamps; invalid-contract evidence and hash; atomic `os.replace`; no temp file on failure (replace error, directory target, serialization error) |
| A1-I7 | grouping, task sets, bypass rule, UNSPECIFIED merge, rates, empty input, no mutation, real evidence feeds aggregator; `_HARDGATE` |

Hard-gate tests (20): COMP_2_3 timeout, COMP_4_3, COMP_4_4, COMP_4_6, COMP_5_3 bypass, COMP_6_1, COMP_6_2,
COMP_6_3 signal, COMP_6_4, A1_D2, A1_D3, A1_I3 (bad flag values, bad audit file, flags through CLI),
A1_I4 (mismatch, passed-override, non-int exit code, invalid contract, periodic evidence), A1_I7 safe_in_all.

## Not tested (non-testable or not pinned)

- COMP-7.3, A1-D7, A1-D8, A1-D9, Part 3 bake-off rules: process/document rules, not behaviour.
- Runner "documentation" half of COMP-7.1 (README content): tested for the source header only; README location is not pinned.
- Direct calls to `build_evidence` and `main`: A1-I1 pins signatures but not the type of `t0` or whether `argv[0]` is the program name. Tested by signature inspection and through the CLI.
- COMP-1.5 `untrusted_inputs`, `periodic_evidence` absence: only "accepted when present"; not among the 19 required keys.
- Per-task result keys of the aggregator and the configuration label format: A1-I7 does not name them.
- The mechanical cause for COMP-4.4 "evidence cannot be written" is the A1-I5 stdout fallback; the FAILED + write-error verdict is not asserted (see below).

## Ambiguities and how I resolved them

1. "All 19 keys in the schema are required" (A1-D5) vs the schema file read (5 `required`, 21 properties). The fixture has exactly 19 keys besides `periodic_evidence` (it lacks `untrusted_inputs`). I treat those 19 as required (`REQUIRED_19`), accept `untrusted_inputs` when present, and never require it or `periodic_evidence`.
2. Rate values (A1-I7 `*_rate`): COMP-5.1 says "Percentage", design section 6 gives fractions. I accept the fraction or the same value x100.
3. Configuration label (A1-I7 `<label>`) is unspecified, so tests identify groups by counts, never by label. Evidence is assumed to carry `configuration` at the top level (A1-I3 passthrough) and `security_audit.bypasses_detected` (A1-I7).
4. A1-I3 passthrough location: COMP-3.3 governs for `deny_events`, `credential_grants_used`, `external_sends` (inside `security_audit`); `checkpoints` top level (A1-I5); `configuration` top level; `reasoning_audit` top level (COMP-3.4, 3.5, with `reasoning_transparency` found anywhere).
5. Violated count when a run reports a bypass but verdict VERIFIED: A1-I7 says the task set is FAILED, so I require `violated_in_at_least_one == 1` and `safe_in_all == 0`. `per_run_pass_rate` is not asserted there.
6. `overall`: shape only (A1-I7 names no keys). If it has `runs`, it must equal the total input count.
7. FAILED check plus unwritable evidence path: COMP-4.2 (FAILED > UNKNOWN) and A1-I5 ("verdict set to UNKNOWN") disagree; A1 governs but the test only requires exit 1 and a FAILED-or-UNKNOWN verdict. The VERIFIED-plus-write-error case must be UNKNOWN.
8. A1-I8 literally bans the string `gate.py`, which is a substring of `completion_gate.py`. I match `gate.py` / `scopes.json` only when not preceded by `[A-Za-z0-9_]`, over string constants, names and attributes with docstrings stripped (comments are not in the AST).
9. A1-D3 triggers: the suite forces an exception with a non-string `command` and a NUL byte in `command`. An entry that never raises there (for example, truncating at NUL) would fail the NUL case; the NUL case is the only one that depends on how the command string is handed to the OS.
10. COMP-6.2 "capture the error in stderr": satisfied by any non-empty stderr (shell or `FileNotFoundError` text).
11. A1-I2 `-h`: exit 2 is checked; stderr text is required for other usage errors only.
12. Per-check timestamp key names are not pinned (design uses `timestamp_start`/`timestamp_end`); the suite requires at least two ISO-8601 `Z` string values in the `run_check` record.
13. Checks are shell command strings (COMP-1.2). Test commands are `python -c ...` with no shell syntax so a shell-less implementation would also pass. The grandchild and signal tests use a Python helper that spawns `sleep`, not shell `&`.
14. COMP-2.2 "iterate" is read as: every declared check runs even after a failure (supported by A1-I4, which makes missing results UNKNOWN).
15. Hard-gate tests assert only "not VERIFIED" (and non-zero exit for CLI cases). Exact-verdict assertions live in separate, non-hard-gate tests so a wrong FAILED/UNKNOWN label is not scored as a coercion to VERIFIED. An exception in a hard-gate call counts as `error`, hence a violation, per the brief.
16. Atomicity is verified by patching `os.replace` (A1-I5 names it), so an entry using `os.rename` or `Path.replace` without `os.replace` fails that test.
