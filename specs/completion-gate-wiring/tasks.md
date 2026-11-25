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
  step regressed on main after #233 (commit 6c667f4); it was repaired in #309 (T9, merged 2026-11-25).
- [x] **T4. Agent rule in `AGENTS.governance.md`** (CGW-4.1–4.2). Governance-section PR with the exact rule text.
  Rule 7 applies as in T3. Depends on: T1.
  Done: #272 (also fixed optin.sh duplicating rules on refresh).
- [ ] **T5. User-level rule install on Ky's machine** (CGW-4.3–4.4). Local, not a PR. First confirm the
  Unknowns (Antigravity rule file, Kiro global steering location). Then insert the marked block into each
  confirmed file and report the files skipped. Depends on: T4 merged, so the text is final.
  Status: open verification, not done: block installed in the files below, but loading is unconfirmed for Codex,
  Antigravity and Cursor.
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
  Restored block (2026-11-24) stays as written. Still open: loading is NOT confirmed for Codex, Antigravity or
  Cursor, and the Kiro Stop hook's live output is unconfirmed. Confirm each with a fresh session asked to quote
  its completion-gate rule, and record the result here only after that check.
- [x] **T6. Kiro Stop hook** (CGW-5.1–5.4). Local hook plus README entry listing rule-only agents. Depends on: T1, T5.
  Done: script #275; installed as ~/.kiro/hooks/completion-gate-stop.json (copied from main da60770); an end-to-end run on main printed VERIFIED. Kiro showing the hook's output in a live session is not yet confirmed.
- [x] **T7. README limits** (CGW-6.1). Can ride with T1 or T6.
  Done with T1 (#271) and T6 (#275).
- [x] **T9. Repair the broken verdict step** (CGW-3.4). Code PR to `.github/workflows/governance.yml` and
  `tests/test_completion_step.py`. Restore the advisory step so the verdict step passes `bash -n` and the 9
  failing tests in `tests/test_completion_step.py` pass. This touches a governance workflow, which AGENTS rule 7
  protects; Ky merges. Depends on: nothing.
  Done: #309 (merge commit 2b480c0ce9852c92a45dd00a4184edd08449ca2f, 2026-11-25).
  Evidence before the fix (verified observation, Ky's audit 2026-11-24, main 6c667f4): #233 (commit 6c667f4) left
  an unclosed `if` in the verdict step; `bash -n` fails; 9 tests in `tests/test_completion_step.py` fail on main;
  the CGW completion gate returns FAILED on CHK-CGW-3 (contract_hash
  sha256:053ec81b13e8ba75f6423729e5d3aad059aaba67ecde450aeb84f16db9c2e829).
  How it merged (verified 2026-11-25): #309 combined three fixes because no single PR could pass the required
  `ai-governance / verdict` check alone: the verdict step broken by #233, `sweep.yml` broken by #263, and
  requirements pins dropped by #259. It also added `tests/test_workflow_shell_syntax.py`. The earlier attempts
  #304, #307 and #308 were closed as superseded.
  Observation (verified 2026-11-25, main at 2b480c0): `python3 completion-gate/completion_gate.py
  specs/completion-gate-wiring/completion-contract.json --evidence /tmp/cgw-main-ev/evidence.json` printed
  `VERIFIED /tmp/cgw-main-ev/evidence.json` with contract hash
  sha256:053ec81b13e8ba75f6423729e5d3aad059aaba67ecde450aeb84f16db9c2e829; CHK-CGW-1 to CHK-CGW-5 all exited 0.
  Before #309 the same run was FAILED on CHK-CGW-3. This is a dated observation, not a claim that the issue is
  complete: T5 and T8 remain open.
- [ ] **T8. Rollout (Ky only).** Ky bumps callers' pinned SHA repo by repo, watches advisory results, and later
  merges the separate PR that flips the default to `required` (CGW-3.7, 6.2). No agent does this task.
  T9 is merged (#309, 2026-11-25). A caller pin at 2b480c0 includes the repaired verdict step (verified by the
  completion gate and by CI on #309). `c2b9fc3` remains a known-good older pin that includes T3. The pin decision
  is Ky's; this task stays open.
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
