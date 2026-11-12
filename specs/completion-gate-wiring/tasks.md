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
  Done: #274 (advisory).
- [x] **T4. Agent rule in `AGENTS.governance.md`** (CGW-4.1–4.2). Governance-section PR with the exact rule text.
  Rule 7 applies as in T3. Depends on: T1.
  Done: #272 (also fixed optin.sh duplicating rules on refresh).
- [x] **T5. User-level rule install on Ky's machine** (CGW-4.3–4.4). Local, not a PR. First confirm the
  Unknowns (Antigravity rule file, Kiro global steering location). Then insert the marked block into each
  confirmed file and report the files skipped. Depends on: T4 merged, so the text is final.
  Done 2026-11-11 on Ky's machine: ~/.codex/AGENTS.md, ~/.gemini/GEMINI.md, ~/.kiro/steering/completion-gate.md, ~/.cursor/rules/completion-gate.mdc (marked blocks; originals in ~/.local/share/cgw-t5-backup/). Skipped: ~/.claude/CLAUDE.md (absent, CGW-4.4). Kiro load confirmed in a live session; Codex, Antigravity and Cursor loading not confirmed.
- [x] **T6. Kiro Stop hook** (CGW-5.1–5.4). Local hook plus README entry listing rule-only agents. Depends on: T1, T5.
  Done: script #275; installed as ~/.kiro/hooks/completion-gate-stop.json (copied from main da60770); an end-to-end run on main printed VERIFIED. Kiro showing the hook's output in a live session is not yet confirmed.
- [x] **T7. README limits** (CGW-6.1). Can ride with T1 or T6.
  Done with T1 (#271) and T6 (#275).
- [ ] **T8. Rollout (Ky only).** Ky bumps callers' pinned SHA repo by repo, watches advisory results, and later
  merges the separate PR that flips the default to `required` (CGW-3.7, 6.2). No agent does this task.

| Requirement | Tasks |
|---|---|
| CGW-1 | T1 |
| CGW-2 | T2 |
| CGW-3 | T3, T8 |
| CGW-4 | T4, T5 |
| CGW-5 | T6 |
| CGW-6 | T7, T8 |
