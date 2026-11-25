# Tasks: trusted exact-SHA external validation evidence (SECFC-7)

Each task is one PR. Order is dependency order. No code is written for T2 to T4
until Ky merges this spec. AGENTS rule 7 protects `governance.yml`; Ky merges.

- [ ] **T1. This spec** (SECFC-7.1–7.11). Spec-only PR by the spec author. Ky reviews and merges.
- [ ] **T2. Failing tests first** (SECFC-7.9, 7.10). Code PR adding the negative-case tests; the
  hardcoded-success case must fail on current `main`. Depends on: T1 merged.
- [ ] **T3. Verdict change** (SECFC-7.1–7.8). Code PR changing `.github/workflows/governance.yml`
  only as the design says, plus `README.md` and `docs/quality/system-evidence.md`. Depends on: T2.
  Reproduce U1 and decide U2 and U4 before merging; record the answers in the PR body.
- [ ] **T4. Independent evidence-hash review** (SECFC-7.11). In the T3 PR, recompute the sha256 of
  `docs/quality/system-evidence.md` from file contents and compare with `.quality/system.json`.
  Update the recorded value only if T3 legitimately changed that file. Depends on: T3.
- [ ] **T5. Caller rollout (Ky only).** Ky adds `prerequisite-check` and `checks: read` to any
  caller that sets `run-quality: false` (U3). No agent does this task.

| Requirement | Tasks |
|---|---|
| SECFC-7.1–7.8 | T3 |
| SECFC-7.9–7.10 | T2, T3 |
| SECFC-7.11 | T4 |
