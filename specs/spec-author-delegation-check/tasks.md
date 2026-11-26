<!-- KIRO-AUTHORED SPEC — HUMAN ADOPTION/MERGE PENDING. Not an owner approval. Drafted 2026-11-25; model ID not exposed.
Issue: #238 · Source: KyPython/ai-governance@593f62f · Completion: no completion contract; not gate-verified. -->

# Tasks: Spec-author delegation check

Spec ID: SAD · Issue: #238 · Status: proposed

## Authorization status (read first)

Every task below is UNAUTHORIZED until all of these are true: (1) Ky reviews this spec; (2) the spec-only PR passes `ai-governance / verdict` and the role checks; (3) Ky merges it; and (4) Ky issues a separate task grant that names the exact repository, base SHA, paths, operations, principal and expiry. A merged spec is not implementation authority.

Tasks T3 to T5 touch protected paths. Each also needs Ky's separate, exact protected-file request and Ky's own merge (AGENTS rule 7, ESE-13.4, ESE task T10). No agent edits a gate to make it pass.

Shared rules: one coder per task and a different authenticated principal in a different execution context as reviewer (ESE-16). Coder and reviewer are capability classes here, not vendors. Ky names the principals in each grant. Where a task cites a repo gate, run it and stop on DENY. No model is launched, no paid call is made and no credential is changed by any task.

Dependency order: T1 → T2 → T4 → T3 → T5 → T6. Each implementing task's green requirement covers only the scenarios it delivers, so no task needs a later task's behavior to pass (one task per PR).

---

- [ ] **T1. Owner decisions** (SAD-1.2, SAD-1.4, SAD-2.6, SAD-5.2)
  Ky decides: which identities are standing; whether `kiro-agent[bot]` needs a delegation; the file name and location (default proposed: a new owner-only `delegations.yml`); the maximum delegation lifetime; and which identities to enroll. Each answer is recorded by a merged change or an owner comment on #238. Unanswered items stay UNKNOWN and are not defaulted.
  Executor: Ky. Depends on: spec merge.
  Evidence: decisions recorded with source. No agent chooses a value.

- [ ] **T2. Tests first, genuine RED** (SAD-1 to SAD-6)
  Add policy-job tests for P1 to P3 and A1 to A15, each citing its SAD IDs, and show a genuine assertion RED for each unmet requirement (not a harness, import or collection failure). Include the negative controls: always-deny, always-pass, read-from-PR-head, accept-comment-as-delegation, pattern-match identity, ignore-introduction-time. Each test is tagged with the task that turns it green (T4, T3 or T5).
  Coder: capability `test-synthesis, adversarial testing` · Reviewer: capability `independent-verification, security review`, a distinct principal in a distinct execution context. Depends on T1.
  Evidence: RED output for each scenario with the failing assertion named; existing GATE-3 tests still pass.

- [ ] **T4. Delegation file, designations and owner-only rule** (SAD-2.2, SAD-2.4, SAD-2.6, SAD-1.4, SAD-5.2, SAD-3.1) — PROTECTED, needs Ky's exact request
  Add the delegation file schema, the per-identity designation field with `kiro-agent[bot]` and `KyPython` recorded as standing, the owner-only change rule, and the CODEOWNERS line if the file is new. Ship no delegation records. Enrolling an identity is a separate owner merge.
  Coder: capability `coding` · Reviewer: capability `independent-verification, security review`, distinct principal and context. Depends on T2 and a Ky-issued protected-file request.
  Evidence (green scope): T2 tests tagged T4 — A7 (schema, `DELEGATION_UNREADABLE`), A10 (owner-only), P3 (listed identities standing); existing GATE-3 tests still pass. The file on `main` contains no delegation records.

- [ ] **T3. Policy-job delegation check** (SAD-1, SAD-2.1, SAD-2.3, SAD-2.5, SAD-3.2 to SAD-3.4, SAD-5.1) — PROTECTED, needs Ky's exact request
  Implement the check in the policy job: read delegations from `main` only, require the introducing commit to precede PR creation, read expiry and revocation from current `main`, emit the named reasons, fail closed, and leave GATE-1 to GATE-5 unchanged for standing identities.
  Coder: capability `coding, security-sensitive` · Reviewer: capability `independent-verification, security review`, distinct principal and context. Depends on T4 and a Ky-issued protected-file request.
  Evidence (green scope): T2 tests tagged T3 — P1, P2, A1 to A6, A8, A9, A11, A14, A15 — on the exact head SHA; `ai-governance / verdict` passes on that SHA; no change to the check's own gate to make it pass.

- [ ] **T5. Reporting wording and claims check** (SAD-4)
  Make the check's pass and fail messages say "recorded on the base branch by an owner-identity merge" and never "owner-authenticated" or "verified human approval" while B1 is open. Confirm a delegation authorizes spec publication only.
  Coder: capability `coding, reporting` · Reviewer: capability `independent-verification`, distinct principal and context. Depends on T3.
  Evidence (green scope): T2 tests tagged T5 — A12 and A13 — on real job output.

- [ ] **T6. Rollout verification and honest disposition** (SAD-5.6, SAD-6)
  In an isolated test, show the positive cases and each adverse case from real policy-job runs. Then Ky bumps pinned SHAs one repository at a time. Report only observed results and name each repository still on an older pin.
  Coder: capability `coding, reporting` · Reviewer: capability `independent-verification`, distinct principal and context. Depends on T3, T4 and T5.
  Evidence: quoted job results per scenario and per repository; no claim of portfolio-wide enforcement without an observed rollout.

---

## Traceability matrix

| Requirement | Tasks |
| --- | --- |
| SAD-1 | T1, T2, T3, T4 |
| SAD-2 | T1, T2, T3, T4 |
| SAD-3 | T2, T3, T4 |
| SAD-4 | T2, T3, T5 |
| SAD-5 | T1, T3, T4, T6 |
| SAD-6 | T2, T3, T6 |

Reverse check: T1 cites SAD-1, 2, 5; T2 cites SAD-1 to 6; T4 cites SAD-1, 2, 3, 5; T3 cites SAD-1, 2, 3, 5; T5 cites SAD-4; T6 cites SAD-5, 6. Every task cites at least one requirement.

## Stop and rollback conditions

Stop on a missing grant, a missing protected-file request, an unreadable base, a failed required check, or a conflict with an owner decision. Preserve the evidence. Rollback is Ky's revert of the merge. Never replay a possibly completed request, and never edit a gate or a contract to proceed.
