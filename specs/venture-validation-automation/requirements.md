# Requirements: Venture validation automation

Spec ID: VVA · Issue: #206 · Status: proposed; Ky approves by merging this spec-only PR

Provenance: Kiro drafted these sentences from Ky's issue #206 goal captured October 10, 2026, reconciled with the sources Ky named: the EXISTING Make research owner (Venture Radar) and its READ-ONLY biweekly trigger; the Notion Idea Mining & Validation Prompts, Creative Industries Idea Mining, Venture & Consulting Research/Validation Firewall, Venture/B2B SaaS Runtime, current Life Blueprint, and Human Agency doctrine; the Kiro-first cloud plan; the two ODIN-ONLY Make scenarios (the Kiro scenario and the Codex scenario), which must not be retargeted; and the existing KyLamportLogic/LamportLogic artifacts #398, PR #409, PR #414, internal cockpit #400, recovery #399. Ky owns the sentences, and coders implement them exactly; they do not paraphrase them to fit the code. The drafting agent (Kiro) does not build the mechanism; coders do, in a later PR, after Ky merges this spec. This issue is a first-party conditional owner goal, not a claim that buyer demand has passed or that a build has been authorized.

## Introduction

Ky wants one conditional, source-grounded orchestration contract that carries a human-recorded problem from venture discovery through validation fact-checking, into a Kiro spec-only issue, then (only after Ky merges) to an eligible coder, and finally to measured distribution and sales-validation learning. The point is to stop asking Ky for repeated approval of unchanged, already-bound, low-risk mechanical research or preparation, while still handing every consequential, authorship, or material-commitment decision to Ky.

Evidence-state note (steering 10-source-authority). The two current candidate diagnoses are RESEARCH ONLY and have NOT passed buyer willingness-to-pay, reachability, or the creative/venture gates:

- VERIFIED CURRENT OBSERVATION: The Venture Radar research owner is ACTIVE on demand; its October 10 corrected run identified candidate (A) indie-game player-experience/release-readiness evidence and (B) AI-assisted studio human-authorship/source-to-claim/approval provenance, both labeled RESEARCH ONLY. The READ-ONLY biweekly trigger is ACTIVE at a 1209600-second interval; its live wrapper execution succeeded and returned verifier state `RESEARCH_ONLY`, `external_effects_authorized:false`; next execution October 24, 2026.
- INFERENCE / UNKNOWN: whether a specific economic buyer exists for either candidate, and whether any buyer will pay for the narrow wedge, is UNKNOWN. Earlier failed/unsupported AI PASS outputs are quarantined and are not evidence.
- VERIFIED GOVERNING RULE: production scope elsewhere is ZeroAPI + SupaCRM at $0 MRR with no real end users; nothing here may describe venture candidates as more than RESEARCH ONLY, and the internal-only LamportLogic #400 cockpit MUST NOT be converted into a SaaS.

This spec is for Ky (who owns and runs the mechanism and makes every consequential call) and for the coders who will build it in a later PR after Ky merges.

Out of scope for this PR: writing any workflow YAML, Make scenario, Python, product code, config, tests, landing pages, or marketing assets; editing `AGENTS.md`, `AGENTS.governance.md`, `README.md`, `roles.yml`, `.github/`, `scripts/`, `templates/`, or any file outside `specs/venture-validation-automation/`. This is a spec-only PR. The mechanism this spec describes MUST NOT, in its own operation, write to `specs/`, push commits, open or merge a PR, deploy, publish, send outbound contact, buy subscriptions, or spend money; coders build the mechanism after Ky merges this spec, and even then every consequential action stays behind Ky's explicit authorization.

## Requirements

### Requirement 1: Human-origin problem admission (VVA-1)

**User Story:** As Ky, I want the pipeline to act only on a named, human-recorded problem, so that no agent invents a buyer, a demand signal, or a product to justify work.

#### Acceptance Criteria

1. VVA-1.1 WHEN the pipeline begins for a candidate THEN the system SHALL require a human-recorded problem statement with a named human origin, and IF the problem is imagined, agent-generated, or of unknown origin THEN the system SHALL set state HOLD and open no spec and start no build.
2. VVA-1.2 The system SHALL NOT invent, infer, or paraphrase into fact any buyer, user, economic buyer, demand signal, metric, traction, pricing, or personal fact about Ky; absent first-party evidence it SHALL record the value as UNKNOWN.
3. VVA-1.3 WHEN the pipeline records any claim THEN it SHALL label its evidence state as one of VERIFIED CURRENT OBSERVATION, VERIFIED GOVERNING RULE, HISTORICAL EVIDENCE, INFERENCE, or UNKNOWN, and SHALL NOT silently promote an INFERENCE or an AI output into a VERIFIED state.
4. VVA-1.4 IF a source conflict exists between a human-recorded problem and a research finding THEN the system SHALL preserve the conflict and name the higher-authority source rather than smoothing it, following the authority order (explicit current human instruction > current governing source of truth > current implementation/runtime evidence > recent logs/tests > older summaries).

### Requirement 2: Five validation questions fact-checked before any product spec (VVA-2)

**User Story:** As Ky, I want each admitted problem run through the five plain-English validation questions and fact-checked, so that only evidence-backed problems earn further work.

#### Acceptance Criteria

1. VVA-2.1 WHEN a human-origin problem is admitted THEN the system SHALL answer and fact-check all five questions before any speculative product spec: (1) who specifically has this problem, with actual users, economic buyer, decision owner, and a dated first-party observation; (2) what they do today, with manual workaround, named competitors, platform-native alternative, spending/time/consequences, primary URLs, and counterevidence; (3) why they would pay or commit, with real independent buyer statements, paid substitutes, identifiable budget, and measured behavior; (4) the cheapest falsifiable proof, with exact success and kill conditions, before any product code; (5) the economics, with evidence-backed pricing/cost/fulfillment/reachability and the mechanical requirement for a $10k-monthly (or retainer/service equivalent) outcome, marking every conversion, CAC, margin, churn, and recurrence assumption UNKNOWN.
2. VVA-2.2 The system SHALL NOT treat market size, a vendor's own pricing, or a vendor marketing page as direct willingness-to-pay for the specific proposed wedge, and SHALL NOT treat a mathematical $10k example as revenue validation.
3. VVA-2.3 WHEN any of the five questions lacks supporting first-party evidence THEN the system SHALL resolve that candidate to RESEARCH or HOLD, never PASS.
4. VVA-2.4 WHEN venture research is evaluated THEN the system SHALL require three independent evidence TYPES supporting buyer problem, exact ICP and economic buyer, workaround, displacement/substitute risk, actual first-ten-users path, differentiation, capacity, and the zero-new-spend constraint; and WHEN creative work is evaluated THEN the system SHALL apply the Love, Distribution, Math, Build-for-self, and Sequencing rules against recorded evidence.
5. VVA-2.5 The system SHALL count a signed real buyer response or payment only with an attributable source, exact date, and verification receipt, SHALL NOT derive it from generic web research, and SHALL NOT manufacture customer replies.

### Requirement 3: Deterministic rejection of unsupported AI PASS (VVA-3)

**User Story:** As Ky, I want an AI-reported PASS treated as untrusted unless independently supported, so that a single marketing citation can never promote a candidate.

#### Acceptance Criteria

1. VVA-3.1 WHEN an AI report claims PASS THEN the system SHALL treat the claim as untrusted and SHALL require exact source, date, and a verification receipt plus the independent-evidence-types rule (VVA-2.4) before advancing the candidate.
2. VVA-3.2 IF an AI report claims PASS from a single source OR with a missing buyer OR citing only a company marketing page THEN the system SHALL reject that PASS deterministically and SHALL resolve the candidate to RESEARCH or HOLD; a cite to a company marketing page SHALL NOT establish an independent customer. (Acceptance case C.)
3. VVA-3.3 WHEN earlier failed or unsupported AI PASS outputs exist THEN the system SHALL treat them as quarantined and SHALL NOT use them as evidence.

### Requirement 4: Pipeline states and transitions (VVA-4)

**User Story:** As Ky, I want the seven pipeline states and their transitions fixed, so that a candidate can only advance through defined, evidence-gated steps.

#### Acceptance Criteria

1. VVA-4.1 The system SHALL implement the state sequence HUMAN-RECORDED PROBLEM -> RESEARCH -> QUESTION-PACKET FACT CHECK -> one of HOLD, REJECT, RESEARCH, or DEMAND-READY, and SHALL NOT skip or reorder these states.
2. VVA-4.2 WHEN a candidate reaches DEMAND-READY by passing the live research-demand hard gates THEN the system SHALL emit exactly one source-linked Kiro spec-only issue scoped to the exact admitted validation question, after deduplicating against existing issues, PRs, and Notion records.
3. VVA-4.3 WHEN Kiro drafts validation questions or experiment specs for a held candidate THEN the system SHALL label them non-production and not build-authorized, and SHALL NOT treat them as a product build authorization.
4. VVA-4.4 WHEN an actual human-owned goal/problem selection and a trusted task/action-bound permission are both present THEN the system MAY prepare an eligible disposable validation MVP only when the current Venture Firewall conditions are met: zero-production infrastructure, fake/safe data, no auth, no payment, no paid hosting, and exactly one falsifiable buyer question; otherwise the system SHALL NOT prepare an MVP.
5. VVA-4.5 The system SHALL NOT generate automated signatures, fabricated approvals, coders, deploys, or routes around a repository DENY at any state.

### Requirement 5: Spec-only PR to Ky; coders only after merge (VVA-5)

**User Story:** As Ky, I want the spec-only PR to come to me for merge and no code to move until I merge, so that I keep the merge, release, and acceptance decisions.

#### Acceptance Criteria

1. VVA-5.1 WHEN a Kiro spec-only issue is emitted THEN Kiro SHALL produce `requirements.md`, `design.md`, and `tasks.md` with EARS-form or clearly numbered requirement IDs, acceptance tests, and test traceability, as a spec-only PR that changes no code, workflow, config, or marketing.
2. VVA-5.2 UNTIL Ky actually merges the spec-only PR AND the task/action-bound authorization is intact, Codex and Cursor SHALL NOT modify any code.
3. VVA-5.3 WHEN Ky has merged the spec THEN the system SHALL assign exactly one eligible coder and a DIFFERENT reviewer per bounded implementation task, respecting `AGENTS.md`, `pnpm ai:mutation:check`, local required tests, CI/governance, and current capability/ownership.
4. VVA-5.4 The system SHALL NOT auto-merge, SHALL NOT publish unreviewed production work, and SHALL NOT merge, approve, or deploy on Ky's behalf.
5. VVA-5.5 IF `pnpm ai:mutation:check` (or any repository mutation/monetization gate) returns DENY THEN the system SHALL stop codebase work, report the DENY, and SHALL NOT edit the gate to authorize the task.

### Requirement 6: HOLD on service unavailable; fail-closed (VVA-6)

**User Story:** As Ky, I want the pipeline to fail closed when a dependency is unavailable, so that it never fakes a spec or silently bypasses a condition.

#### Acceptance Criteria

1. VVA-6.1 IF Kiro, Make, or Codex is unavailable THEN the system SHALL set state HOLD and SHALL NOT produce a fake Kiro spec, a simulated code build, or a silently bypassed condition. (Acceptance case D.)
2. VVA-6.2 WHEN the system encounters a source conflict, a stale prompt, partial pagination, an unsupported transport, a failed independent test, or an unknown side effect THEN it SHALL set state HOLD rather than proceed.
3. VVA-6.3 WHEN any hard gate cannot be evaluated THEN the system SHALL default to HOLD or RESEARCH, never PASS.

### Requirement 7: Distribution, marketing, and sales-validation DRAFT preparation only (VVA-7)

**User Story:** As Ky, I want distribution and sales-validation prepared as drafts with no automatic outbound, so that nothing is sent, posted, bought, or promised without my scoped approval.

#### Acceptance Criteria

1. VVA-7.1 WHEN a candidate reaches the distribution step THEN the system MAY prepare source-grounded DRAFTS only: ICP/competitor comparison, test plan, factual positioning, landing-page and mock sales-copy drafts, UTM/link/analytics instrumentation where safe, a manual/productized-service-versus-software comparison, and an exact opt-in/outreach proposal.
2. VVA-7.2 The system SHALL NOT make automatic contact, buy ads, post publicly, make claims, or commit pricing without scoped recipient, content, destination, and term approvals and proven rights, payment, and fulfillment.
3. VVA-7.3 The existing creator publishing workflow SHALL remain OFF until its own gates pass, and the ElevenLabs frozen-voice HOLD SHALL be preserved (no sample add, remove, trim, reset, replacement, retraining, deletion, or billing change without Ky's fresh explicit authorization).
4. VVA-7.4 WHEN preparing distribution for candidate (A) indie-game release-readiness THEN the system SHALL treat the existing Aftergrowth playability recovery/spec work (#398, PR #409, PR #414) as NOT a commercial product proof and SHALL treat PlaytestCloud as a current incumbent; IF only vendor evidence exists and no buyer-specific willingness to pay THEN the candidate SHALL stay RESEARCH ONLY with no new external product spec or build. (Acceptance case A.)
5. VVA-7.5 WHEN preparing for candidate (B) creative provenance/approval THEN the system SHALL treat U.S. Copyright Office guidance as legal context and C2PA, Autodesk Flow, and World Anvil as substitutes; IF there are no independent buyer statements and no paid need for the narrow decision-level layer THEN the candidate SHALL stay RESEARCH ONLY, and the system SHALL NOT convert internal-only #400 into a SaaS. (Acceptance case B.)

### Requirement 8: Post-test evidence measurement (VVA-8)

**User Story:** As Ky, I want post-test evidence measured against falsifiers, so that a candidate stops or revises on failure and no score decides my mission.

#### Acceptance Criteria

1. VVA-8.1 WHEN a validation test has run THEN the system SHALL measure observed replies, paid behavior, actual use, cost, churn/falsifiers, and provenance, each with an attributable source and date.
2. VVA-8.2 IF a gate or falsifier fails THEN the system SHALL stop or revise the candidate rather than advance it.
3. VVA-8.3 The system SHALL NOT let any score decide Ky's mission, venture selection, or time allocation; those remain Ky's decisions.

### Requirement 9: Idempotence and single-writer safeguards (VVA-9)

**User Story:** As Ky, I want one fingerprint per problem and single-writer safety, so that rereading the same signal creates no duplicate work and existing systems stay untouched.

#### Acceptance Criteria

1. VVA-9.1 The system SHALL maintain one fingerprint per human problem/workflow with immutable checkpoint/revision hashes, SHALL perform a fresh read before each write and a read-back after, and SHALL NOT blind-retry.
2. VVA-9.2 WHEN the same exact signal is reread THEN the system SHALL create no duplicate issue, outreach, or build, and existing Odin, story production, and W-2 job work SHALL remain untouched. (Acceptance case E.)
3. VVA-9.3 The system SHALL NOT create a new duplicate Notion tracker or a new recurring calendar block, SHALL NOT introduce another scheduled idea researcher while the existing Venture Radar scenario remains the sole research owner, and SHALL NOT point the two ODIN-ONLY Make scenarios (the Kiro scenario and the Codex scenario) at venture candidates or change them.
4. VVA-9.4 The system SHALL enforce bounded spend and rate, SHALL be capable of legitimately processing zero candidates, and SHALL deduplicate against existing issues, PRs, and Notion records (notably Aftergrowth #398 and internal cockpit #400) so it never duplicates those tasks.

### Requirement 10: Rights, canon, career, and finance gates (VVA-10)

**User Story:** As Ky, I want hard boundaries that block any external effect until the governing gate clears, so that no publish, mutation, send, or spend happens behind an unmet gate.

#### Acceptance Criteria

1. VVA-10.1 IF an existing rights lock, human canon, career, or finance gate is not cleared THEN the system SHALL NOT publish, mutate code, send externally, or spend. (Acceptance case F.)
2. VVA-10.2 The system SHALL preserve human-owned decisions and signed task/action-bound AI mutation permissions under the live Human Agency doctrine, and SHALL NOT infer that a standing delegation waives a required per-action permission.
3. VVA-10.3 WHEN a material choice, claim, or commitment arises (money, production/security/privacy change, architecture approval, destructive operation, career direction, promise, publication) THEN the system SHALL refer it to Ky and SHALL require explicit human authorization before any irreversible or externally committing action.

### Requirement 11: Standing delegation for bound low-risk preparation (VVA-11)

**User Story:** As Ky, I want evidence-validated, bounded, signed-permission preparation to flow without a second confirmation prompt, so that I stop re-approving unchanged low-risk mechanical research.

#### Acceptance Criteria

1. VVA-11.1 WHEN a candidate is actually evidence-validated AND a bounded signed permission for the exact same scope is verified intact THEN the system SHALL perform same-scope repetitive preparation without a second confirmation prompt. (Acceptance case G.)
2. VVA-11.2 WHEN a material choice, claim, or commitment arises within an otherwise-delegated flow THEN the system SHALL refer that specific decision to Ky even though the surrounding preparation is delegated.
3. VVA-11.3 IF the scope changes, the signed permission is absent or stale, or the evidence that validated the candidate no longer holds THEN the system SHALL stop and require fresh explicit authorization rather than relying on the prior delegation.

#### Known limit (VVA)

This pipeline can only grade and route the evidence it is given; it cannot prove buyer demand, revenue, or human authorship, and a green pipeline run is not evidence that either current candidate is commercially validated. Signatures and commit identities remain self-declared, so the standing delegation (VVA-11) trusts the signed permission it is shown and cannot by itself distinguish a genuine Ky authorization from a forged one; that trust boundary stays with Ky and the repository gates. The mechanism depends on non-owned connectors (Make, Notion, Kiro, Codex, Cursor, analytics), so their availability and correctness are UNKNOWN at authoring time and are handled by failing closed (VVA-6).
