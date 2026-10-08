# Implementation Plan: CLI README Drift Audit and Executable-Docs Check

## Overview

This is an actionable FUTURE implementation plan. It begins ONLY after real Kiro final review and @KyPython merge of this spec to `ai-governance/main`. Nothing runs in this spec-only session; baselineExecuted is false. No code or tests are written here; no task is marked done; nothing is executed. **HOLD (every task):** coding/source promotion does not begin until the canonical spec PR is merged by **@KyPython** into `ai-governance/main` with green required checks. Authorship provenance is author session `sess_6ccf95b7-8bbe-4225-8682-6f74410eb9cd`; the final combined 54-file reviewed-HEAD Kiro merge receipt comes from the ORIGINAL final-review session `sess_ef9c3844-0570-409c-baa6-7cc73d898476`, not the author session alone. The exact repair/test/narration/recovery reference lives separately off-screen and is NOT in these public docs.

## Tasks

- [ ] 1. Reuse the exact recovered unworked `specs/odin-tasks/cli-readme-drift-audit/starter` (diffSha256 `668d30b3…`) in a disposable copy; confirm digests match; reuse reviewed offline packaging and the editable console-script install (DRIFT-8) — coder: codex — reviewer: cursor — HOLD until merge
- [ ] 2. Run meaningful ordinary baseline: `python -m unittest discover -s tests -v`, the real `trailmark` over `fixtures/observations.json`, and `python scripts/docs_check.py README.md` (observe it only lists the README's bash blocks); record observed-vs-expected showing the drifted README examples do not match (DRIFT-5, DRIFT-6) — coder: codex — reviewer: cursor — HOLD until merge
- [ ] 3. Reconcile README flags/defaults/examples/exit codes to real behavior (`--format`/default text, `--minimum-score`/default 1, `--include-drafts`, exit codes 0/2/3/4 where argparse bad usage = 2 with the usage diagnostic on stderr and empty stdout, invalid input = 3, file not found = 4); AI-proposed corrections are proposals for Ky's PR review (DRIFT-1, DRIFT-2, DRIFT-3, DRIFT-4, DRIFT-5) — coder: cursor — reviewer: codex — HOLD until merge
- [ ] 4. Build the executable docs-check that executes each example against local fixtures and asserts stdout AND stderr AND exit code (failure examples assert the declared stderr diagnostic/prefix, successful examples declare empty stderr); no arbitrary shell; fail on mismatch (DRIFT-6, DRIFT-7) — coder: codex — reviewer: cursor — HOLD until merge
- [ ] 5. Confirm GREEN in the disposable copy: `python -m unittest discover -s tests -v` (still green, parser unchanged) and the new docs-check (exits 0 only when every documented example matches); record observed-vs-expected; no PASS claimed before this runs (DRIFT-1, DRIFT-2, DRIFT-3, DRIFT-4, DRIFT-5, DRIFT-6, DRIFT-8) — coder: codex — reviewer: cursor — HOLD until merge
- [ ] 6. Post-merge: publish the private Ky-owned unworked starter and confirm its full 40-character commit SHA plus per-file byte and mode verification against the inventory BEFORE internal admission/registration; no SHA invented (DRIFT-9) — coder: codex — reviewer: cursor — HOLD until merge
- [ ] 7. Author the off-screen guided record reference (separate from these public docs): literal paths, edits, Save All, commands, observed-vs-expected results, rollback, recovery, capture start/stop bound to the actual reviewed source; include internal-preparation admission/registration, exact Notion route (row `3f08621e0a7a81d3a5c8ec0957bf0655`), private full starter pin verified after merge, paired cloud artifact, and Shared sync via EXISTING Morning/owner; no paid/unaided/recording-ready claim (DRIFT-9) — coder: cursor — reviewer: codex — HOLD until merge

## Task Dependency Graph

```json
{"waves":[["1"],["2"],["3"],["4"],["5"],["6"],["7"]]}
```

## Notes

- Honesty constraints: no PASS and no batch PASS is claimed; no SHA or PR number is invented; baselineExecuted is false. Nothing in this spec-only session is executed.
- Preserved paid-state: Odin **Candidate / HOLD / empty paid-approval** is preserved verbatim and is NOT a prerequisite for internal off-screen code/testing/private source publishing; the future technical-prep gates are real Kiro final review, a @KyPython merged-to-main spec, and the bound internal admission. Human/Recorder/paid gates are separate and remain pending.
- Baseline and tests use stdlib `unittest` (`python -m unittest discover -s tests -v`); the tool is invoked as the installed console script `trailmark <args>`, NOT `python -m trailmark`. No undeclared pytest is introduced.
- AI-proposed README corrections are GUIDEDREFERENCE proposals for Ky's PR review only, never claimed as decisions already made.
- Remaining HOLDs: no private starter commit SHA exists yet; it is confirmed only post-merge (full 40-char SHA + byte/mode verification) before internal admission/registration.
- Each task has coder ≠ reviewer; off-screen disposable repairs are permitted only after merge; captured starters/attempts remain preserved. No current paid/unaided/recording-ready claim.
