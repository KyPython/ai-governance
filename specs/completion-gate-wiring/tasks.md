# Tasks: Completion Gate wiring (CGW)

Each task is one coder in its own PR, reviewed by a different agent. Ky merges. Order is dependency order.
No code is written for these tasks until Ky merges this spec.

- [x] **T1. Import the gate** (CGW-1.1–1.4). Code PR adding `completion-gate/` from the Drive copies, with a
  per-file SHA-256 table, and adding its tests to the repo's test run with the 120-line check. Depends on: spec
  merge.
  Done: #271.
- [x] **T2. Contract template and first real contract** (CGW-2.1–2.4). Spec-only PR by the spec author: add
  `templates/spec/completion-contract.json` and one contract for an existing spec as the pilot. Depends on: T1.
  Done: template #273; pilot contract #276 (split because templates/*.json counts as code). Contract extended to every task here.
- [x] **T3. CI completion step, advisory** (CGW-3.1–3.6). Code PR to `governance.yml` plus tests in
  `tests/test_policy.py` or a new `tests/test_completion_step.py` citing CGW IDs. This touches a governance
  workflow, which AGENTS rule 7 protects; Ky's 2026-11-11 instruction is the explicit request, and Ky merges.
  Depends on: T1, T2.
  Done: #274 (advisory). Regression (verified observation, Ky's audit 2026-11-24, main 6c667f4): the advisory
  step regressed on main after #233 (commit 6c667f4); it is repaired by T9.
- [x] **T4. Agent rule in `AGENTS.governance.md`** (CGW-4.1–4.2). Governance-section PR with the exact rule text.
  Rule 7 applies as in T3. Depends on: T1.
  Done: #272 (also fixed optin.sh duplicating rules on refresh).
- [ ] **T5. User-level rule install on Ky's machine** (CGW-4.3–4.4). Local, not a PR. First confirm the
  Unknowns (Antigravity rule file, Kiro global steering location). Then insert the marked block into each
  confirmed file and report the files skipped. Depends on: T4 merged, so the text is final.
  Status: open for Codex only (loading unconfirmed); Gemini, Kiro and Cursor are done.
  Original note (2026-11-11, historical): installed in ~/.codex/AGENTS.md, ~/.gemini/GEMINI.md,
  ~/.kiro/steering/completion-gate.md, ~/.cursor/rules/completion-gate.mdc (marked blocks; originals in
  ~/.local/share/cgw-t5-backup/). Skipped: ~/.claude/CLAUDE.md (absent, CGW-4.4). Kiro load confirmed in a live
  session; Codex, Antigravity and Cursor loading not confirmed.
  Correction (verified observation, Ky's audit 2026-11-24):
  - Before the audit, `~/.codex/AGENTS.md` did not exist, so the 2026-11-11 note that it was installed was stale.
  - The backup `~/.local/share/cgw-t5-backup/20261111T221424/_Users_ky_.codex_AGENTS.md` contains no completion
    gate block; it is the pre-install original.
  - The Gemini, Kiro steering and Cursor blocks are byte-identical to the rule 13 text.
  Update (verified observation, 2026-11-24): `~/.codex/AGENTS.md` was recreated with the marked block only,
  byte-identical to the block in `~/.gemini/GEMINI.md`. The pre-install original is not restored; it remains in
  the backup at `~/.local/share/cgw-t5-backup/20261111T221424/`.
  Still open: Codex loading is NOT confirmed. Confirm it with a fresh Codex session asked to quote its
  completion-gate rule, and record the result here only after that check.
- [x] **T6. Kiro Stop hook** (CGW-5.1–5.4). Local hook plus README entry listing rule-only agents. Depends on: T1, T5.
  Done: script #275; installed as ~/.kiro/hooks/completion-gate-stop.json (copied from main da60770); an end-to-end run on main printed VERIFIED. Kiro showing the hook's output in a live session is not yet confirmed.
- [x] **T7. README limits** (CGW-6.1). Can ride with T1 or T6.
  Done with T1 (#271) and T6 (#275).
- [ ] **T9. Repair the broken verdict step** (CGW-3.4). Code PR to `.github/workflows/governance.yml` and
  `tests/test_completion_step.py`, from branch `fix/verdict-step-merge-defect`. Restore the advisory step so the
  verdict step passes `bash -n` and the 9 failing tests in `tests/test_completion_step.py` pass. This touches a
  governance workflow, which AGENTS rule 7 protects; Ky merges. Depends on: nothing.
  Evidence (verified observation, Ky's audit 2026-11-24, main 6c667f4): #233 (commit 6c667f4) left an unclosed
  `if` in the verdict step; `bash -n` fails; 9 tests in `tests/test_completion_step.py` fail on main; the CGW
  completion gate returns FAILED on CHK-CGW-3 (contract_hash
  sha256:053ec81b13e8ba75f6423729e5d3aad059aaba67ecde450aeb84f16db9c2e829).
  Status (verified observation, 2026-11-24): NOT done. Code PR https://github.com/KyPython/ai-governance/pull/304
  is open and not merged; its commit is 88d600e. Its own CI is red: `ai-governance / quality` and `system-quality`
  fail on 3 tests that also fail on origin/main (`test_policy.py::SpecGate::test_GATE_1_2_kiro_spec_dir_on_base_passes`,
  `test_sweep.py::SweepWorkflow::test_GBD_3_1_failed_sweep_opens_one_issue` and
  `test_sweep.py::SweepWorkflow::..._updates_the_open_issue_instead_of_duplicating`). The verdict job is red
  because quality is red. Mark this task done only after #304 merges.
- [ ] **T8. Rollout (Ky only).** Ky bumps callers' pinned SHA repo by repo, watches advisory results, and later
  merges the separate PR that flips the default to `required` (CGW-3.7, 6.2). No agent does this task.
  Do not bump any caller to `main` until T9 merges. `c2b9fc3` is a known-good candidate pin.
  Input, unconfirmed (from Ky's audit 2026-11-24; not re-verified by the spec author):
  - pinned `bacf04c` (before T3): KyPython/KyPython, repo-starter, odin-tasks, odin-recording-preparation,
    skills-hello-github-actions, claim-checker `local/`.
  - pinned `8da4ed4` (before T3): ple-verified-harness.
  - pinned `c2b9fc3` (has T3, predates #233, verdict step passes `bash -n`): claim-checker root, repair-bench,
    visit-taniti, KyLamportLogic/buildlogic-governance.
  Further inputs, unconfirmed (observed 2026-11-24; for Ky to confirm):
  - The ruleset on ai-governance `main` requires `ai-governance / verdict` and `diff-hygiene / hygiene`
    (0 approvals).
  - `ple-verified-harness` and `KyLamportLogic/buildlogic-governance` have no required `ai-governance / verdict`
    check.
  - `KyLamportLogic/LamportLogic` has no `ai-governance.yml` and does not call the reusable workflow; it has only
    a local `governance-advisory.yml`.
  - buildlogic-governance's last 10 PR runs were 1 success and 9 `startup_failure`.
  - No caller sets the `completion-gate:` input.
  - Advisory completion verdicts for the `c2b9fc3` callers could not be read from logs (UNKNOWN), so there is no
    measured false-FAILED rate.
  - With `run-quality: false`, `required` fails every PR (input description in `governance.yml`).
  Before flipping to `required` (CGW-3.7), Ky defines, and records here: the number of PRs observed, the
  acceptable false-FAILED rate, and how UNKNOWN is treated. These are Ky's decisions; no values are proposed.

| Requirement | Tasks |
|---|---|
| CGW-1 | T1 |
| CGW-2 | T2 |
| CGW-3 | T3, T8, T9 |
| CGW-4 | T4, T5 |
| CGW-5 | T6 |
| CGW-6 | T7, T8 |
