# Tasks: Engineering-stage enforcement (G0–G6), universal governed admission, V1–V6

Spec ID: ESE · Issue: #238 · Status: draft · Base: KyPython/ai-governance@`7213b3abef535700bea04680d2a4da8ede8e9d76`

## Authorization status (read first)
**Every task below is UNAUTHORIZED until all of the following are true:** (1) Ky reviews this spec; (2) the spec-only PR passes the existing `ai-governance / verdict` and policy/role checks on the base branch; (3) Ky merges it; and (4) Ky issues a **separate, non-agent-forgeable task receipt** naming the exact repo, base SHA, paths, and operations for that task (ESE-2, ESE-6, ESE-13.4). A merged spec is not implementation authority. No agent merges, deploys, or self-approves (AGENTS.md rules 1, 7, 11, 12).

Shared rules for every task: one named coder + a **different** named reviewer; exact repo + base SHA + exact authorized paths/operations carried in the Ky-issued task receipt; where a LamportLogic target is touched, run `pnpm ai:mutation:check --scope <catalog-scope> --target <repo-relative-path>` per target and stop on DENY; preserve `ai-governance / verdict`, Human Skill Retention, roles.yml/CODEOWNERS/workflows/pinned callers; do not touch protected enforcement files unless the task is explicitly a Ky-requested protected-file change (T10). Required evidence is real-boundary (dispatch/filesystem/credential/publisher), reproduced in ≥1 isolated local and ≥1 provider-managed cloud environment, distinguishing offline simulation from real provider rejection. Coder/reviewer identities are placeholders — Ky assigns actual agents at authorization time.

Dependency order: T1 → T2 → T3 → {T4, T5} → T6 → T7 → T8 → T9 → T10(gated) → T11.

---

- [ ] **1. Receipt authority + data model + revocation store** (ESE-2.1–2.5, ESE-6.1–6.7)
  Build the non-agent-forgeable owner-receipt issuer/validator and the `StageReceipt` store (fields per design receipt model), with expiry/revocation/freshness and lineage digests. No protected-file edits.
  Coder: coder-A · Reviewer: coder-B.
  Preflight: Ky task receipt (repo+SHA+paths); N/A mutation gate (not LamportLogic) unless a LamportLogic target is added.
  Evidence: `UNVERIFIABLE_APPROVER` BLOCKED path; forged/agent-issued receipt rejected; stale/replay/revoke/drift rejected; receipt-field completeness.
  Blocker: B1 (owner channel) must be resolved or this task ends at a documented BLOCKED boundary.

- [ ] **2. Stage state machine G0→G6** (ESE-1.1–1.9, ESE-6.7)
  Implement the transition engine (one-next-phase-only, HOLD on absent/ambiguous/expired/revoked/drifted, deploy separate from merge, terminal = "eligible for owner review only").
  Coder: coder-B · Reviewer: coder-C. Depends on T1.
  Evidence: per-gate transition positive + out-of-order negative (feeds V1/V6).

- [ ] **3. Pre-dispatch admission broker + local/cloud decision parity** (ESE-7.1–7.4, ESE-4.1–4.8)
  Blocking guard at task dispatch / writable-workspace handoff; identical decision+reason for same inputs locally and in cloud; offline fail-closed; per-file mutation authority where a stronger repo gate exists; report unenforceable surfaces.
  Coder: coder-C · Reviewer: coder-A. Depends on T1, T2.
  Evidence: same-input local vs cloud parity; code-pushed-to-unprotected-branch treated untrusted; offline PASS/FAIL/BLOCKED/UNKNOWN/NOT_RUN.

- [ ] **4. Disposable stage sandbox + trusted publisher** (ESE-5.1–5.6)
  Fresh unprivileged sandbox, read-only inputs, scoped output, no host Docker socket, no owner creds; coder cannot modify `features/`/`specs/`/`tests/`; separate publisher validates output tree + write perms before push; four boundaries kept separate; no single orchestrator holds all credentials.
  Coder: coder-A · Reviewer: coder-B. Depends on T1. (Parallel with T5.)
  Evidence: socket/creds/immutable-input negatives; publisher pre-push tree validation; `chmod 444`-is-not-a-boundary demonstrated.

- [ ] **5. Structured RED/GREEN + adequacy parsers** (ESE-8.1–8.7)
  Behavioral-assertion-failure vs harness/import/collection-failure classifier; vacuous-assertion detector; post-code mutation/contrast adequacy with honest UNKNOWN/FAIL; no mandated global mutation threshold; method contract over vendor tool.
  Coder: coder-B · Reviewer: coder-C. Depends on T1. (Parallel with T4.)
  Evidence: false-RED rejected; genuine behavioral RED eligible; `assert True` earns no adequacy.

- [ ] **6. Governed-intake / quarantine bootstrapper + coverage classifier** (ESE-3.1–3.9)
  Unready/quarantined repo creation, scaffold-only install (immutable full-SHA caller), no write creds while unready, `GOVERNED_READY` only after independent readback + negative & positive admission checks; classify owned repos `GOVERNED/QUARANTINED/NOT_APPLICABLE_BY_AUTHORIZED_SCOPE/BLOCKED_UNAVAILABLE`; authenticated owner `FULL/LIMITED/NOT_APPLICABLE` tool decision; no self-labeled exemption; no mandatory Cucumber install.
  Coder: coder-C · Reviewer: coder-A. Depends on T1, T2, T3.
  Evidence: unregistered-creation denied with no-write/no-publish proof; self-label-exempt denied; ownership-scope classification with source evidence.
  Blocker: B3 (org/repo protection reality is UNKNOWN) — classify, do not assert coverage.

- [ ] **7. V1–V5 adversarial controls at real boundaries** (ESE-9, ESE-10, ESE-11, ESE-12, ESE-13)
  V1 out-of-order pre-write rejection; V2 role/path forgery + spoofed author; V3 false RED vs genuine RED; V4 vacuous trace + agent-issued N/A denied / human-scoped applicability preserved; V5 replay/revoke/concurrent-change by lineage + drift detection keeping immutable pins. Plus forged-owner-approval, shared-credential-collision, fake-synthetic-RED, blanket-N/A, skipped-CI, concurrent-inputs cases.
  Coder: coder-A · Reviewer: coder-B. Depends on T1–T6.
  Evidence: each vector fails closed for the **correct reason at the correct boundary**, local + cloud; offline simulation distinguished from real provider rejection; PASS/FAIL/UNKNOWN per vector.

- [ ] **8. V6 positive control** (ESE-14.1–14.4)
  One existing scoped synthetic feature through authenticated G0→G6: valid RED, GREEN, adequacy, independent verification by a reviewer ≠ coder, reaching **"eligible for owner review only"**; plus the new-governed-creation positive control. **No auto-merge, no deploy, no cloud spend.**
  Coder: coder-B · Reviewer: coder-C. Depends on T1–T7.
  Evidence: recorded fixture/policy-version/actor/inputs/precondition/observed-execution evidence; owner-review-eligibility asserted; no merge/deploy.

- [ ] **9. Pin-promotion manifest + drift detection (shared callers)** (ESE-13.3)
  Independently reviewed drift detection + SHA-promotion process for shared callers; keep full immutable SHA pinning; no mutable tags, no auto-merge. Design/verify only against UNKNOWN external state (B2/B3) — report, do not mutate external repos.
  Coder: coder-C · Reviewer: coder-A. Depends on T1.
  Evidence: drift surfaced for a stale pinned caller without replacing the immutable SHA.

- [ ] **10. (GATED — Ky-requested only) Protected-enforcement wiring proposal** (ESE-1.*, ESE-7.2, ESE-13.4)
  Any change to `roles.yml`, `.github/workflows/*`, `CODEOWNERS`, `AGENTS*.md`, `.husky/`, `.claude/`, `.cursor/rules/`, branch protection, or a pinned caller SHA needed to make G0–G6 blocking in CI. **UNAUTHORIZED unless Ky explicitly requests it and Ky merges it** (AGENTS.md rule 7). This task exists so the dependency is visible; it is not pre-approved. Never edit a gate to make it pass.
  Coder: TBD by Ky · Reviewer: TBD by Ky. Depends on T1–T9 and a Ky-issued protected-file request.
  Evidence: proposal + diff for Ky's review only; no agent application.

- [ ] **11. End-to-end coverage report + honest disposition** (global DoD)
  Independently reproduced per-account/per-repo/per-provider/local-cloud report: each owned writable scope genuinely enforced or explicitly quarantined and unable to publish; new-creation positive control; bypass attempts fail for the right reason. If any GitHub/OS/admin surface is uncontrollable at the current plan/privilege, report **GLOBAL INVARIANT NOT ENFORCED**, never false 100%.
  Coder: coder-A · Reviewer: coder-B. Depends on T1–T9 (and T10 if Ky authorized it).
  Evidence: the reproduced report; OUTSIDE-ENFORCED-BOUNDARY items labeled; no enforcement claimed from documentation alone.

---

## Traceability matrix (every requirement → ≥1 task)
| Requirement | Tasks |
| --- | --- |
| ESE-1 (G0–G6 stage model) | T2, T7, T8, T10 |
| ESE-2 (genuine authorization) | T1, T7 |
| ESE-3 (mandatory admission) | T6, T11 |
| ESE-4 (local/cloud parity) | T3, T7, T8 |
| ESE-5 (isolation + publisher) | T4, T7 |
| ESE-6 (receipt contract/lineage) | T1, T2, T7 |
| ESE-7 (pre-dispatch broker) | T3, T7, T10 |
| ESE-8 (test adequacy) | T5, T7, T8 |
| ESE-9 (V1 out-of-order) | T7 |
| ESE-10 (V2 role/path forgery) | T4, T7 |
| ESE-11 (V3 false RED) | T5, T7 |
| ESE-12 (V4 vacuous trace) | T5, T7 |
| ESE-13 (V5 replay/revoke/drift) | T1, T7, T9, T10 |
| ESE-14 (V6 positive control) | T8 |
| Global DoD | T11 |

Reverse check — every task cites ≥1 requirement: T1→ESE-2,6; T2→ESE-1,6; T3→ESE-4,7; T4→ESE-5,10; T5→ESE-8,11,12; T6→ESE-3; T7→ESE-9..13; T8→ESE-14; T9→ESE-13; T10→ESE-1,7,13; T11→global DoD/ESE-3,4.
