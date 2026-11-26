# Design: Engineering-stage enforcement (G0–G6), universal governed admission, V1–V6

Spec ID: ESE · Issue: #238 · Status: draft · Base: KyPython/ai-governance@`7213b3abef535700bea04680d2a4da8ede8e9d76`
Author: Kiro (spec-author). Design only; no implementation. Evidence-state tags: **[VERIFIED]** current observation, **[RULE]** governing rule, **[REPORTED/UNKNOWN]** reported-but-unverified, **[PROPOSED]** design constraint, **[HISTORICAL]**.

## Overview
This design separates (a) controls that exist and run today, (b) external controls reported but not verified from this workspace, and (c) controls this spec proposes for a later, separately-authorized implementation. It then defines trust boundaries, the stage state machine, the receipt data model, dependency-DAG invalidation, fail-closed/rollback behavior, and three incremental deployment alternatives. Nothing here is built by this spec.

Authority order used for reconciliation (per source-authority rule): current human instruction → governing SSOT (roles.yml, AGENTS.md, merged docs) → current implementation/runtime → logs/tests → older summaries. Contradictions are preserved, not smoothed.

---

## (a) Current / deployed controls — [VERIFIED] against this checkout @ 7213b3a

| Control | Where | What it actually does | Known limit |
| --- | --- | --- | --- |
| Role + spec-path policy | `roles.yml` (read by `governance.yml` policy job) | Only `spec-author` (`kiro-agent[bot]`, `KyPython`) may change `specs/`/`.kiro/specs/`; a spec PR must not change code; code PR openers/commit identities must be `coder`/owner | **git author/committer are self-declared; an agent pushing with Ky's token appears as `KyPython`** — stated verbatim in `roles.yml` and GATE-3 "Known limit" [RULE] |
| Syntactic spec + trace gate | `specs/ai-governance-gate` GATE-1.1–1.8, 3.x, 4.x | Code PR must link an issue, reference a base-branch spec with numbered EARS criteria, and add/modify a test that cites ≥1 criterion ID by string | **Syntactic only**: `assert True` and a single matching ID can satisfy it [C-V P0]. No RED/adequacy/stage semantics. [VERIFIED via GATE-1.4 wording] |
| Verdict scorecard | GATE-4 | Publishes JSON scorecard; parses pass/fail for known runners | Does not change pass/fail; no behavioral-adequacy judgement [VERIFIED] |
| Strict-repo parity + security job | GATE-5 | jwt/Prisma path rules, destructive-command block, deploy-workflow guardrails, Dockerfile root/latest block, zizmor/shellcheck/OSV | Pattern-based; not stage-aware [VERIFIED] |
| Merge/deploy gate | `AGENTS.md` | Required checks + `ai-governance / verdict` green **and** only Ky merges; only Ky deploys from main for exact revision | Enforced by branch protection + human rule, not by the policy job (reviewers/approvals not gate-enforced) [RULE] |
| Protected-governance rule | `AGENTS.md` rule 7 | Agents must not edit roles.yml, workflows, CODEOWNERS, AGENTS*, .husky/.claude/.cursor, branch protection, pinned caller SHA | This spec obeys it; changes to these are [PROPOSED] tasks needing Ky (ESE-13.4) |
| G0–G6 / universal admission | `docs/operations/cucumber-bdd-rollout.md` | **Documentation proposal only.** Doc states: "G0–G6 are proposed requirements, not functioning GitHub status checks"; universal admission "NOT YET ENFORCED" | **Not enforced** [VERIFIED from merged doc] |

Current CI pipeline (what a spec-only PR will actually be judged by): the reusable `ai-governance / verdict` (install + lint/type-check/test/build as defined + policy checks incl. spec gate + gitleaks). A **spec-only** PR that touches only `specs/` is exempt from the code spec-gate (GATE-1.5/1.8) but must pass the role gate (GATE-3.1: opener + every commit author/committer in `spec-author`). **UNKNOWN until the orchestrator pushes:** the actual verdict run result and whether the commit identity resolves to a `spec-author`. This is an authorization/identity dependency, not something this spec can self-assert (see Blockers).

---

## (b) Reported-but-unverified external controls — [REPORTED/UNKNOWN]

These are cited by issue #238 / the merged doc / the instruction but could NOT be verified read-only from this workspace (the control-plane repo is not cloned; LamportLogic is read-only reference; GitHub org/ruleset/billing state is outside this checkout). They are UNKNOWN and must be verified at implementation, not assumed.

| Reported control | Source | Status here |
| --- | --- | --- |
| `buildlogic-governance` shared caller pinned to `efd0e11dde73a70d4867293e4ac2308d28be057e` (predates current policy) | [C-V] P0; [DOC] blockers | **UNKNOWN** — not verified from this workspace; drift-detection/promotion is [PROPOSED] (ESE-13.3) |
| LamportLogic shared caller unmerged in PR #397 | [C-V] P0 | **UNKNOWN** — do not create a replacement PR or claim installed |
| `gateSideEffect.ts` / `gateAiSideEffect` / `AI_MONETIZATION_GATE` / `check-ai-monetization-gate.js` | [C-V]; [LL] | **REPORTED** as reusable; "only protect integrated call sites, do not auto-sandbox every coding agent" [C-V]. Reference evidence only; not verified executable here |
| Exact-path mutation admission (`pnpm ai:mutation:check --scope --target`) | [LL]; [DOC] | **REPORTED** — applies to LamportLogic targets; not exercised here |
| `ky-cloud-control-plane` PR #5 (OPEN DRAFT), `docs/CLOUD_PARITY.md`, its issue #4 (AWS cost/activation) | instruction; [DOC] | **UNKNOWN** — repo not cloned; PR #5 treated as reported-but-unverified reference. BLOCKER B2 |
| `KyLamportLogic` org ruleset `24443511` requires default-branch PRs but **not** `ai-governance / verdict`, CODEOWNERS review, or approvals; LamportLogic private ruleset read returned plan-related 403 | [DOC] blockers | **UNKNOWN/REPORTED** — "inability to verify protection is not evidence of protection" [DOC]. Enforcement blocker |
| Human Skill Retention gate | [LL]; [C-V] | **REPORTED** — must be preserved; not verified here |

Contradiction preserved: the merged doc asserts a mandatory-everywhere directive while simultaneously recording that several enforcement surfaces (org ruleset, private-plan protection, SHA pins, new-repo creation limits, unmanaged local authoring) are **not currently effective**. Both are true; the directive is desired behavior, the blockers are current reality.

---

## (c) Proposed controls — [PROPOSED] (implemented only after Ky merges this spec + issues task authority)

1. **Owner receipt authority + revocation store** — a non-agent-forgeable issuer that mints/validates stage receipts (ESE-2, ESE-6) and a revocation/expiry/freshness store. Trust anchor must be outside any agent's control.
2. **Pre-dispatch admission broker** — blocking guard at task dispatch / writable-workspace handoff (ESE-7); evaluates stage/role/path/receipt before any mutation; same decision locally and in cloud (ESE-4).
3. **Disposable stage sandboxes** — fresh unprivileged container/VM, read-only inputs, scoped writable output, no host Docker socket, no owner creds, immutable `features/`/`specs/`/`tests/` for coders (ESE-5).
4. **Independent verifier** — reviewer distinct from coder reproduces positive/negative cases, revision, suites, security/formal checks (ESE-8.4, ESE-14).
5. **Trusted publisher** — validates output tree + write permissions before push; the only principal that can publish upstream; separate from coder and from the receipt issuer (ESE-5.4, ESE-5.5).
6. **Structured RED/GREEN parsers** — distinguish behavioral assertion failure from harness/import/collection failure; detect vacuous assertions; drive adequacy with post-code mutation/contrast (ESE-8, ESE-11, ESE-12).
7. **Pin-promotion manifest + drift detection** — surface stale shared-caller SHAs, keep immutable pinning, promote only after spec approval (ESE-13.3).
8. **V1–V6 harness** — reproducible negative controls V1–V5 + positive control V6, run at real boundaries, local and cloud (ESE-9..ESE-14).
9. **Governed-intake / quarantine bootstrapper** — unready repo creation, scaffold-only install, `GOVERNED_READY` only after independent readback + negative & positive admission checks (ESE-3).

---

## Trust boundaries (four separated authorities — [C-V])
```
 Owner (Ky, authenticated, non-agent-forgeable)
   │  issues stage receipts (G0..G6)  ── cannot be minted by any agent/PAT-as-agent (ESE-2)
   ▼
 (1) Receipt issuance + pre-write authorization  ──────────────┐
   │                                                            │ recheck at dispatch AND before publish (ESE-6.3)
   ▼                                                            │
 (2) Fresh stage sandbox  (read-only inputs, scoped output)     │
   │   coder cannot touch features/ specs/ tests/ (ESE-5.2)     │
   ▼                                                            │
 (3) Independent verifier  +  Trusted publisher ───────────────┘
   │   verifier ≠ coder; publisher validates tree before push
   ▼
 (4) GitHub required checks / branch admission  +  Ky human merge/deploy
```
No single orchestrator holds all credentials or unilateral signing authority (ESE-5.5). Deployment authority is separate from merge authority (ESE-6.7; AGENTS rule 12).

---

## Stage state machine (G0→G6)
States: `G0_DISCOVERY_AUTHORIZED → G1_BEHAVIOR_ACCEPTED → G2_SPEC_MERGED → G3_SCENARIOS_ACCEPTED → G4_RED_ACCEPTED → G5_GREEN_ACCEPTED → G6_VERIFIED_ELIGIBLE`. Terminal `G6` is **"eligible for owner review only"** — never auto-merge/deploy (ESE-1.7, ESE-14).

Transition rule (every edge): a transition from Gᵢ to Gᵢ₊₁ fires only if a valid owner receipt for Gᵢ₊₁ exists, bound to the exact subject+content, with all predecessor receipts valid and unrevoked (ESE-6). Any of {missing, malformed, reused, expired, revoked, drifted} → **HOLD** (fail closed, ESE-6.6). An approval authorizes exactly one next phase (ESE-1.9).

Decision statuses surfaced at every node: `PENDING / BLOCKED / REJECTED / SUPERSEDED / VERIFIED` (ESE-6.6); plus execution statuses `PASS / FAIL / BLOCKED / UNKNOWN / NOT_RUN` (ESE-4.6).

---

## Receipt data model ([C-V] contract → ESE-6.1)
```
StageReceipt {
  stage                 : G0..G6
  feature_or_task_id    : string
  authorized_paths_ops  : [ {path_glob, operations[]} ]   # exact scope (ESE-6.1)
  issuer_principal      : authenticated owner identity     # non-agent-forgeable (ESE-2)
  role                  : spec-author | coder | verifier | publisher | owner
  policy_revision       : ai-governance main SHA / policy version
  predecessor_receipts  : [ {id, digest} ]                 # lineage (ESE-6, ESE-13)
  input_content_digests : [ digest ]                       # canonical relevant inputs
  candidate_output_digest : digest
  freshness             : { issued_at, expiry, revocation_ref }
  required_owner_decision : APPROVE | REJECT | REQUEST_CHANGES | DEFER
}
```
Binding: approval is valid only for the exact subject + content; any stale-SHA replay or scope expansion is rejected (ESE-6.2). No cross-repo / cross-issue inheritance (ESE-6.5).

---

## Dependency-DAG invalidation (ESE-6.4)
Receipts form a DAG by `predecessor_receipts`. On a material upstream change (changed behavior/spec/input, or revoked/expired receipt), invalidate **only** the transitive descendants of the changed node; unrelated branches stay valid. Concurrent changed inputs / concurrent creator-publisher → reject the incorrectly accepted work without duplicating a project or deadlocking legitimate setup (ESE-13.2).

---

## Error handling and failure modes (fail closed)
- Unavailable approval/issuer service → **HOLD**, never default-approve (ESE-6.6).
- No non-agent-forgeable owner proof → **BLOCKED / `UNVERIFIABLE_APPROVER`** (ESE-2.2).
- RED from harness/import/collection failure → reject RED (ESE-8.1, ESE-11.1).
- Vacuous trace → no adequacy authorization (ESE-8.3, ESE-12.1).
- Provider cannot meet isolation bar → that lane **BLOCKED** (ESE-4.7).
- Unenforceable surface (unmanaged laptop, org/admin creation) → report **OUTSIDE ENFORCED BOUNDARY / NOT PROVEN** or **GLOBAL INVARIANT NOT ENFORCED**, never false 100% (ESE-4.8, global DoD).
- **Rollback / no self-approved escape:** policy activates only through owner-controlled merges; rollback must not introduce a self-approved escape; an owner break-glass/pause must be separately authenticated, narrowly scoped, auditable, with reconciliation and later verification — never a silent admin escape or agent-controlled exemption ([DOC] "No accidental availability lockout"; security requirement 8). Avoid a gate that deadlocks authorized Kiro spec creation.

---

## Incremental deployment alternatives
All alternatives preserve: required CI + `ai-governance / verdict` stay mandatory; only Ky merges/deploys; full-SHA supply-chain pinning stays. All are UNAUTHORIZED until Ky merges this spec and issues task authority.

- **Alternative A — manual fail-closed pilot (RECOMMENDED FIRST).** One existing scoped synthetic feature. Owner decisions recorded out-of-band through a non-agent-forgeable channel; humans run V1–V5 + V6 by hand; no new infrastructure, no spend. Proves the authority invariant and the state machine before any automation. Matches [DOC] "first on one justified pilot" and "no new infrastructure by default".
- **Alternative B — repo-local verifier + protected environment.** Add repo-local structured RED/GREEN parsers, a pre-dispatch check, and a GitHub protected-environment gate for the publisher step. Higher assurance than A; still no always-on service. Requires [PROPOSED] protected-file changes → Ky-requested tasks only (ESE-13.4).
- **Alternative C — dedicated authority broker + trusted publisher service (HIGHEST ASSURANCE, NOT AUTHORIZED).** Standalone issuer/broker/publisher with disposable sandboxes across local and cloud. **May be incompatible with the no-new-spend constraint** (AWS/always-on) and the "no running EC2/AWS control plane" rule [DOC invariant 6]; control-plane facts are UNKNOWN (BLOCKER B2). Not to be pursued without explicit owner authorization and a cost decision via ky-cloud-control-plane issue #4.

Recommendation: start at **A**; graduate to **B** only with Ky-approved protected-file tasks; treat **C** as out of scope pending owner cost authorization.

---

## Testing strategy (criterion ID → future test/evidence; implementation-owned)
No tests are authored by this spec. The table names the evidence a later task must produce. "Real-boundary" = demonstrated at the dispatch/filesystem/credential/publisher boundary, not isolated logic, in ≥1 local and ≥1 cloud environment ([DOC] invariant 5).

| Criterion | Evidence method (deferred) |
| --- | --- |
| ESE-1.1–1.9 | Per-gate transition controls; V1 + V6 per-gate |
| ESE-2.1–2.5 | Forged-approval + shared-credential + spoofed-author controls; `UNVERIFIABLE_APPROVER` BLOCKED assertion |
| ESE-3.1–3.9 | Unready→readback→GOVERNED_READY positive; self-label-exempt + unregistered-creation negatives; ownership-scope classification evidence |
| ESE-4.1–4.8 | Same-input local vs cloud decision parity; offline fail-closed; OUTSIDE-ENFORCED-BOUNDARY classification |
| ESE-5.1–5.6 | Sandbox isolation negatives (socket/creds/immutable inputs); publisher pre-push tree validation |
| ESE-6.1–6.7 | Receipt field completeness; stale/replay/revoke/drift rejections; descendant-only invalidation |
| ESE-7.1–7.4 | Pre-dispatch block before write; final-CI block; per-file mutation authority; unenforceable-surface report |
| ESE-8.1–8.7 | Structured RED vs harness-failure; vacuous-trace rejection; post-code mutation/contrast; honest UNKNOWN/FAIL |
| ESE-9 (V1) | Out-of-order pre-write rejection, correct reason, local+cloud |
| ESE-10 (V2) | Role/path forgery + spoofed author rejection at sandbox/publisher |
| ESE-11 (V3) | False-RED rejection; genuine behavioral RED eligible |
| ESE-12 (V4) | Vacuous-trace no-adequacy; agent-issued N/A denied; human-scoped applicability preserved |
| ESE-13 (V5) | Replay/revoke/concurrent-change rejection by lineage; drift detection w/ immutable pins |
| ESE-14 (V6) | Positive control to "eligible for owner review only"; no merge/deploy; no spend; new-creation positive |

---

## Blockers / UNKNOWNs (carried into the return summary)
- **B1 — Owner authorization channel:** a non-agent-forgeable owner approval channel is a hard prerequisite (ESE-2). If unavailable, the correct status for enforced gates is **BLOCKED**, not a comment-based override [C-G]. UNKNOWN whether such a channel exists today.
- **B2 — ky-cloud-control-plane:** repo not cloned; PR #5 (OPEN DRAFT) and `CLOUD_PARITY.md` are reported-but-unverified. All control-plane facts are **UNKNOWN** here. Do not claim parity design is reused/verified.
- **B3 — Org/repo protection reality:** `KyLamportLogic` ruleset lacks required `ai-governance / verdict`/CODEOWNERS/approvals; LamportLogic private ruleset read returned 403; shared callers possibly on stale SHA. These are **enforcement blockers**, not deployment [DOC].
- **B4 — Spec-only PR identity:** whether the commit/opener resolves to the `spec-author` role (GATE-3.1) is determined at push time by the orchestrator; this authoring environment cannot self-assert it. If the commit appears as `KyPython`-via-token rather than a genuine owner action, that is the exact forgeability limit this spec warns about and must not be presented as owner approval.
- **B5 — Host boundary:** unmanaged local authoring cannot be prevented by any GitHub rule or repo file; it must be reported as OUTSIDE ENFORCED BOUNDARY (ESE-4.8).

---

<!-- KIRO-AUTHORED DESIGN AMENDMENT (R1) — HUMAN ADOPTION/MERGE PENDING. RUNTIME ACCEPTANCE NOT RUN.
Issue: https://github.com/KyPython/ai-governance/issues/238 · Source: KyPython/ai-governance@53462a0 · Author: Kiro (spec-author), local session 2026-11-25; model ID not exposed. -->

# Design — Amendment R1: capability-qualified assignment on fixed gates

Status: proposed; supports ESE-15 to ESE-17 in `requirements.md`. Nothing here changes ESE-1 to ESE-14. No protected path, role map, workflow or pinned caller is edited by this amendment (ESE-13.4).

## What changes and what does not

| Concern | Before R1 | After R1 | Changed? |
| --- | --- | --- | --- |
| Stage model G0 to G6 and one-next-phase-only approval | ESE-1 | Same | No |
| Owner approval channel, forgery rejection, B1 | ESE-2 | Same | No |
| Receipt lineage, replay, revocation | ESE-6, ESE-13 | Same, with new receipt fields below | Fields added |
| Who performs a stage | Placeholders coder-A, coder-B, coder-C in tasks | Capability class per task, principal named in Ky's grant | Yes |
| Reviewer independence | "reviewer distinct from the coder" (ESE-14.1) | Distinct principal and distinct execution context, with `INDEPENDENCE_LIMITED` recorded when only a same-family principal exists (ESE-16) | Made explicit |
| Spec-author role | Defined in `roles.yml` and AGENTS (protected) | Treated as a role, not a product. Wording change is a proposal for Ky (ESE-13.4, T10) | Proposal only |

## Receipt additions (ESE-15.2, ESE-17.1)

The existing receipt model (see "Receipt data model") gains these fields. They describe the performer of the phase. They carry no approval of their own.

| Field | Meaning |
| --- | --- |
| `capability_class` | The kind of work the phase needs (spec design, scenario authoring, test synthesis, coding, independent verification, security review, research) |
| `candidate` | Provider, model identifier or family and version, harness, environment, as observed |
| `principal` | The authenticated identity that acts, as verified by the enforcing boundary |
| `execution_context` | The session or execution identifier, used for independence and for rejecting reuse |
| `independence` | `INDEPENDENT`, `INDEPENDENCE_LIMITED` with reason, or not applicable |
| `selection_evidence_ref` | Reference to the stage evaluation under `specs/kiro-credit-failover` (CONT-14). A reference only. Never an approval |

The lineage digest (ESE-6.4) includes `principal` and `execution_context`, so a change of performer after dispatch invalidates dependent downstream use and does not carry forward silently.

## Admission checks added to the pre-dispatch broker (ESE-7.1)

In order, all fail closed and name the failing check:

1. The grant exists, matches repository, issue, spec SHA, stage, paths and operations, and has not expired or been revoked (ESE-6.3, ESE-17.1).
2. The presenting principal and execution context equal those in the grant (ESE-17.1, ESE-17.2).
3. For a review phase, the reviewer principal and context differ from those of the coder and of the test author for the same task (ESE-16.1, ESE-16.3).
4. The candidate named in the grant is still enrolled and not retired (ESE-17.4).
5. The owner decision required by the stage is verifiable by a channel that is not agent-forgeable. If not, report BLOCKED with reason `UNVERIFIABLE_APPROVER` (ESE-2.2, ESE-17.3).

The same checks run again immediately before publication (time-of-check to time-of-use).

## B1 criteria for leaving `UNVERIFIABLE_APPROVER`

B1 stays blocked until all of these are shown by observed execution, in evidence a reviewer other than the author can reproduce:

1. An owner-only signing step happens on a device or channel that agents do not control (the iPhone proposal is one candidate and is not demonstrated).
2. A trusted verifier, whose trust root an agent cannot change, checks the signature against the exact subject (repository, issue, spec SHA, stage, paths, expiry).
3. A forged, agent-issued, replayed, expired and revoked approval each fail the verifier for the correct reason.
4. An outage of the approver or issuer leaves the stage HOLD and never defaults to approve (ESE-6.6).

A chat message, a GitHub comment or an agent signature alone cannot show 1 or 2. This list restates the existing requirement as acceptance evidence. It does not add an approval path.

## Reviewer independence

Rank of evidence, strongest first, for the reviewer of a change:

1. A different underlying model family and a different execution context, with a distinct authenticated principal.
2. A distinct authenticated principal in the same model family. Record `INDEPENDENCE_LIMITED` and leave acceptance to Ky.
3. The same principal or the same session. Not acceptable. HOLD.

Deterministic tools (CI, CodeQL, the gitleaks scan, the existing `ai-governance / verdict`) stay independent of any generated success claim and do not replace the reviewer.

## Spec-author as a role

The two facts that matter, both unchanged here: Ky approves a spec only by merging it, and the gate reads the role map on `main` and checks the PR opener and every commit's author and committer. ESE-15.6 states the intended policy. The actual role-map wording lives in `roles.yml` and `AGENTS.governance.md`, both protected, so the proposed wording is prepared as text for Ky's separate exact request (T10) and is not applied. A catch-all identity or wildcard is out of scope and unsafe because git author fields are self-declared.

## Failure modes

| Failure | Behavior |
| --- | --- |
| Grant has no `principal` or `execution_context` | Reject at dispatch. HOLD. |
| Reviewer equals coder by principal or context | Reject with `NOT_INDEPENDENT`. |
| Candidate retired between dispatch and publication | Reject at publication. Preserve evidence. |
| Only same-family reviewer available | Record `INDEPENDENCE_LIMITED`. Wait for Ky. |
| No qualifying candidate | HOLD with `NO_QUALIFYING_CANDIDATE`. Draft-only output outside protected paths is allowed. |
| Owner channel unverifiable | BLOCKED, `UNVERIFIABLE_APPROVER`. |

## Testing strategy additions (criterion to future evidence)

| Criteria | Evidence |
| --- | --- |
| ESE-15.1 to 15.5 | Replace one candidate by a registry change, same contract passes without enforcement-code edit. No qualifying candidate yields HOLD. Coder asked to act as spec author is refused. |
| ESE-15.6 | Publish from an unrecognized identity is denied, draft stays outside Git. A recognized identity with a recorded delegation passes as a spec-only change. |
| ESE-16.1 to 16.5 | Same-session reviewer rejected. Distinct-principal reviewer accepted with the correct `independence` value. Reviewer merge and deploy attempts rejected. Test author cannot implement under the same grant. |
| ESE-17.1 to 17.4 | Wrong repository, issue, SHA, stage, path, principal and context each rejected at dispatch and publication. Model-name spoofing rejected. Expired, revoked and retired cases rejected. |
| ESE-17.3 | `UNVERIFIABLE_APPROVER` reported for a stage needing an owner decision until the B1 criteria above are met. |

Scenarios for these are in `scenarios-capability-routing.md`. They are an AI draft and are not a G3 receipt.

## Relationship to open G3 work

The 2026-11-03 #238 comment proposes corrections to the existing `scenarios.md` (adverse-authorization outline, TOCTOU case, ESE-1.3 and ESE-1.7 prerequisites). R1 does not apply those corrections and does not edit `scenarios.md`. That change needs its own spec-only revision and its own owner review. R1 adds scenarios for the new requirements in a separate file so the two reviews stay separate.
