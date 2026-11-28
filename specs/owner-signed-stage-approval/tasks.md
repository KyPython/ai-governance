<!-- KIRO-AUTHORED SPEC (spec-author subagent) — HUMAN ADOPTION/MERGE PENDING. Not an owner approval. Drafted 2026-11-28; model ID not exposed. Issue: #238. Source: KyPython/ai-governance@90bcd70. -->
<!-- Completion: no completion contract; not gate-verified. -->

# Tasks: Owner-signed stage approval

Spec ID: OSA · Issue: #238 · Status: proposed

## Authorization status (read first)
Every task below is UNAUTHORIZED until: (1) Ky reviews this spec; (2) the spec-only PR passes `ai-governance / verdict` and the role checks; (3) Ky merges it; and (4) Ky issues a separate task grant naming repository, base SHA, paths, operations, principal and expiry. A merged spec is not implementation authority.

T3 and T4 touch protected paths and each needs Ky's separate, exact protected-file request and Ky's own merge (AGENTS rule 7, ESE-13.4). No agent edits a gate to make it pass.

Shared rules: one coder per task; a reviewer who is a different authenticated principal in a different execution context (ESE-16). Coder and reviewer are capability classes, and Ky names principals in each grant. No model is run, no spend, no credential changed. No private key enters any repository, CI secret, agent environment or agent session (OSA-6). Implementing tasks ship tests with behavior; the first commit is tests only and its CI run is the recorded genuine RED, reviewed by Ky (ESE-8.1). No test is skipped or loosened to reach green (AGENTS rule 4). PRs carry `Spec: specs/owner-signed-stage-approval` on its own line and `Relates to #238`.

Dependency order: T1 → T2 → T3 → T4 → T5 → T6.

---

- [ ] **T1. Device spike (Ky only, before any code)** (OSA-9.3, OSA-9.4, OSA-9.5, OSA-6.1)
  Ky tries on his own device: (a) create a key in an iPhone SSH app, noting whether it is Secure-Enclave-backed and whether use needs biometrics; (b) sign a test file in namespace `ai-governance-spike@v1` (never the stage-approval namespace); (c) check on any computer that `ssh-keygen -Y verify` accepts it. Report only: app name and version, algorithm, public key, whether (c) passed, and whether Ed25519 is possible. Never send the private key, and never use a spike signature as an approval.
  Executor: Ky. Depends on: spec merge. Agents do nothing here.
  Evidence: Ky's report on #238. Outcomes: A works; B only; `NO_CHANNEL` (stop; spec revision, OSA-9.4). Answers D1.

- [ ] **T2. Verifier library, tests first** (OSA-1, OSA-2, OSA-4, OSA-5, OSA-6.4, OSA-9.3)
  Implement the verifier (new unprotected directory, proposed `owner_approval/`, standard library plus the system `ssh-keygen`; candidate chosen by T1) with its tests: record schema and canonicalization, the verification order and each reason, namespace separation, the HOLD on tool outage, replay and revocation logic. Tests use throwaway keys only. Add no change to a workflow or the pinned file. Confirm the runner's `ssh-keygen -Y verify -r` behavior and record the OpenSSH version.
  Coder: capability `coding, security-sensitive` · Reviewer: capability `independent-verification, security review`, distinct principal and context. Depends on T1 and D2, D3, D5, D6.
  Evidence: first commit tests only, CI RED with assertion failures (not harness errors); final head tests and full suite green; always-pass and always-deny verifier controls fail as intended; scan shows no private key material.

- [ ] **T3. Owner-only pinned key file and change rule** (OSA-3, OSA-5.1, OSA-5.2) — PROTECTED, needs Ky's exact request
  Add the pinned public key file, an empty revocation list, the owner-only change rule (same pattern as GATE-3.3 and SAD-2.4), and the CODEOWNERS line. Ky supplies the public key from T1; an agent generates or holds no key. State the bootstrap limit in the PR body (OSA-3.4).
  Coder: capability `coding, security-sensitive` · Reviewer: capability `independent-verification, security review`, distinct principal and context. Depends on T2 and Ky's protected-file request and D4.
  Evidence: tests for A9, A10, A17 first and RED; final head green; the file on `main` holds only the public key Ky named.

- [ ] **T4. Policy and pre-dispatch integration** (OSA-4.1, OSA-4.2, OSA-4.5, OSA-5.4, OSA-7) — PROTECTED, needs Ky's exact request
  Call the verifier from the policy job (and from the pre-dispatch broker when it exists), re-check before publication, emit the named reasons, and use the OSA-7 wording. Do not change ESE-2.
  Coder: capability `coding, security-sensitive` · Reviewer: capability `independent-verification, security review`, distinct principal and context. Depends on T3 and Ky's protected-file request.
  Evidence: tests for A11, A13, A15 first and RED; final head green; `ai-governance / verdict` passing on that SHA; no edit to a gate to make it pass.

- [ ] **T5. Demonstration run (Ky signs)** (OSA-8.1 to OSA-8.4)
  Run every scenario in `scenarios.md` in real CI. Ky produces the genuine signature for P1 on his device at the time of the run. The forged, agent-produced, replayed, expired, revoked and outage cases are prepared by an agent from unsigned or throwaway-key material. Write one evidence file with the OSA-8.3 fields. Run location per D7.
  Executor: agent prepares and runs; Ky signs P1. Reviewer: capability `independent-verification`, not the evidence author, reproduces each verdict. Depends on T4.
  Evidence: per-scenario run URL, SHA, quoted reason; always-pass and always-deny controls; no private key material.

- [ ] **T6. Disposition** (OSA-8.5, OSA-8.6, OSA-7.2)
  Report observed results only, name each unmet criterion and each remaining blocker (B2 to B5). Ky decides whether B1 is closed and records it on #238 or by owner merge. Only then may a separate, owner-merged change update the ESE-17.3 and SAD-4.3 wording. Until then B1 stays `UNVERIFIABLE_APPROVER` and ESE-17.3 stays BLOCKED.
  Executor: Ky decides; agent drafts the report. Depends on T5.
  Evidence: Ky's recorded decision with source.

---

## Traceability matrix
| Requirement | Tasks |
| --- | --- |
| OSA-1 | T2 |
| OSA-2 | T1, T2 |
| OSA-3 | T2, T3 |
| OSA-4 | T2, T4 |
| OSA-5 | T2, T3, T4 |
| OSA-6 | T1, T2, T5 |
| OSA-7 | T4, T6 |
| OSA-8 | T5, T6 |
| OSA-9 | T1, T3, T4 |

Reverse check: T1 cites OSA-2, 6, 9; T2 cites OSA-1, 2, 4, 5, 6, 9; T3 cites OSA-3, 5; T4 cites OSA-4, 5, 7; T5 cites OSA-8; T6 cites OSA-7, 8.

## Stop and rollback conditions
Stop on a missing grant, missing protected-file request, unreadable base, failed required check, or a T1 result of `NO_CHANNEL`. Preserve evidence. Rollback is Ky's revert of the merge. Never replay a possibly completed request, edit a gate or contract to proceed, or ask for a private key.
