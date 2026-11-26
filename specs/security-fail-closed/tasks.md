# Tasks: trusted exact-SHA external validation evidence (SECFC-7)

Each task is one PR. Order is dependency order. No code is written for T2 to T4
until Ky merges this spec. AGENTS rule 7 protects `governance.yml`; Ky merges.

- [x] **T1. This spec** (SECFC-7.1–7.11). Spec-only PR by the spec author. Ky reviews and merges.
  Done: #314 (593f62f); correction #316 (482689e).
- [x] **T2. Failing tests first** (SECFC-7.9, 7.10). Code PR adding the negative-case tests; the
  hardcoded-success case must fail on current `main`. Depends on: T1 merged.
  Done in #315 (combined with T3): 29 of the new tests failed on 593f62f before the verdict change.
- [x] **T3. Verdict change** (SECFC-7.1–7.8). Code PR changing `.github/workflows/governance.yml`
  only as the design says, plus `README.md` and `docs/quality/system-evidence.md`. Depends on: T2.
  Reproduce U1 and decide U2 and U4 before merging; record the answers in the PR body.
  Done: #315 (merge 3dfd6c4f74fd1fcd3d4bf659e77e4a53a41afbce, 2026-11-25). Its first push hit
  `startup_failure` (F2), fixed by T3a. U1 answered (F2/F3); U2 decided: latest `completed_at` wins and any
  non-completed run of that name fails; U4 still open: `merge_group` is not handled and fails closed.
- [x] **T3a. Caller permission grant** (SECFC-7.8). In the T3 PR (#315), add `permissions:
  contents: read, checks: read` to the `ai-governance` job in `.github/workflows/self-test.yml`
  and in `templates/ai-governance.yml`, and say so in README. Both are governance workflow files
  (AGENTS rule 7); Ky merges. Acceptance: the self-test run starts and `ai-governance / verdict`
  reports at the PR head SHA. Depends on: this correction merged.
  Done in #315 (commit 11d7211); self-test started and verdict passed at head 046d791.
- [x] **T4. Independent evidence-hash review** (SECFC-7.11). In the T3 PR, recompute the sha256 of
  `docs/quality/system-evidence.md` from file contents and compare with `.quality/system.json`.
  Update the recorded value only if T3 legitimately changed that file. Depends on: T3.
  Done in #315: the file changed; recomputed sha256 48c487fc4c929754dff005e52dc0706ef8080bb0ed86d740799611de5ef2d4b6
  matches `.quality/system.json` at 046d791.
- [ ] **T5. Caller rollout (Ky only).** For each of the 13 callers in U3: first add
  `checks: read` to the calling job on the current pin, then move the pin to a commit with
  SECFC-7.8. Callers that set `run-quality: false` (none today) also add `prerequisite-check`.
  No agent does this task, and no agent moves a pin.
  Status: open. Scheduled for Ky (calendar, 2026-11-25); no caller changed yet.

| Requirement | Tasks |
|---|---|
| SECFC-7.1–7.7 | T3 |
| SECFC-7.8 | T3, T3a, T5 |
| SECFC-7.9–7.10 | T2, T3 |
| SECFC-7.11 | T4 |
