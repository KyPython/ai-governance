# Requirements: Engineering-stage enforcement (G0–G6), universal governed admission, and V1–V6 adversarial verification

Spec ID: ESE · Issue: #238 · Status: draft
Author: Kiro (spec-author role, `kiro-agent[bot]`). These sentences are authored by Kiro the spec-author. This spec does **not** claim owner approval, does **not** impersonate Ky/`KyPython`, and is **not** an owner-signed stage receipt. Ky approves this spec only by reviewing and merging the spec-only PR; coders implement these sentences and must not paraphrase, reword, or weaken them to fit code.

<!--
SOURCE MAP (quote/cite, do not fabricate):
 - ISSUE #238 body ("Intent and authorship", "Exact scope", "Required Kiro specification ... NOT YET SATISFIED"), KyPython/ai-governance, OPEN, label `kiro`, created 2026-10-29, read 2026-11-01 via GitHub REST API.
 - ISSUE #238 comment 2026-10-29 06:04 (updated 2026-11-01 05:16) — "Owner directive 2026-10-29: explicit approvals at every BDD -> SDD -> TDD -> implementation transition" defining G0–G6 and the security-critical acceptance conditions. [C-G]
 - ISSUE #238 comment, same thread, "2026-11-01 — security and executable-pilot addendum (GPT-6; AI DRAFT / NOT APPROVED)" defining P0 authority boundary, execution isolation, stage-receipt contract, test-adequacy semantics, and V1–V6. [C-V]
 - ISSUE #238 comment 2026-11-01 05:27 — "WITHDRAWN / DO NOT EXECUTE ... Kiro is back" restoring the normal Kiro spec-author route. [C-W]
 - MERGED DOC docs/operations/cucumber-bdd-rollout.md (PR #239 merge 0b137992a45873beaf6e68764649237d2bb31fd0; PR #240 merge 7213b3abef535700bea04680d2a4da8ede8e9d76), sections "Universal project admission — owner directive, 2026-11-01; NOT YET ENFORCED", "Execution-location neutrality", "Proposed governance upgrade: separate human approvals at every transition", "Additional falsification and positive acceptance for Kiro". [DOC]
 - roles.yml @ main 7213b3a (spec_paths, roles, the self-declared-identity limit). [ROLES]
 - AGENTS.md @ main 7213b3a (merge/deploy gate, fixed roles, protected-governance rule 7, supply chain rule 10). [AGENTS]
 - Existing spec specs/ai-governance-gate/requirements.md (GATE-1..GATE-5; the current syntactic spec+trace+role gate and its stated GATE-3 known limit). [GATE]
 - LamportLogic (read-only reference): packages/ai-governance gateSideEffect/gateAiSideEffect, scripts/check-ai-monetization-gate.js, AI_MONETIZATION_GATE, Human Skill Retention. [LL]
All requirement sentences below are Kiro's normative formalization of those sources; where a source only proposes/relays, that is stated.
-->

## Introduction

### Problem
Issue #238 and the merged `docs/operations/cucumber-bdd-rollout.md` request a staged engineering-governance upgrade: explicit owner approval at **every** BDD → SDD → TDD → implementation handoff (G0–G6), mandatory-by-default governance admission for every new venture/project/repository/material code change (local or cloud), and adversarial verification (V1–V6) that proves an actor who authors/tests/codes cannot also manufacture the owner approval that lets that work advance. The merged doc states these are **proposed requirements, not functioning GitHub status checks**: "G0–G6 are proposed requirements, not functioning GitHub status checks" [DOC], and universal admission is "NOT YET ENFORCED" [DOC]. The canonical issue states the "Required Kiro specification" is "NOT YET SATISFIED" [#238 body].

This document is exactly that specification-only formalization. **It does not by itself claim enforcement, deployment, or coverage.** It defines observable behavior that a later, separately-authorized implementation (one coder per task, different reviewer, owner merge) must satisfy.

### Who it is for
Ky (owner/approver), Kiro (spec-author), and the coder/verifier agents who may only implement after Ky reviews, merges this spec, and issues a separate task/path authorization.

### Reconciliation of the Cucumber→mandatory directive (issue step 3)
- ORIGINAL framing (issue #238 title and body): "Cross-repo Cucumber/Gherkin BDD rollout — spec-first, opt-in, verify"; "Opt-in at **actual executable behavior boundaries** only" [#238 body].
- LATER owner directive (2026-11-01, [DOC] "Universal project admission — owner directive"): "For **every new venture, project, repository, and material code change** ... **governance enrollment is mandatory by default, not opt-in**. Local or cloud execution is not an escape route."
- RECONCILED RULE encoded here: **governance process is mandatory everywhere; the choice of an individual testing tool/runner (Cucumber / pytest-bdd / behave / existing suites) stays a per-boundary `FULL / LIMITED / NOT_APPLICABLE` applicability decision selected when appropriate.** Per [DOC]: "**Only the Cucumber runner is selectively optional; the governance process isn't.**" Installing Cucumber everywhere is explicitly **not** required [DOC].

### Out of scope / preserved (not changed by this spec)
- This spec changes **no** protected enforcement mechanism. Per [AGENTS] rule 7, agents do not edit `roles.yml`, `.github/workflows/` (including `ai-governance.yml`/`governance.yml`), `CODEOWNERS`, `AGENTS.md`/`AGENTS.governance.md`, `.husky/`, `.claude/`, `.cursor/rules/`, branch protection, or any pinned caller SHA. Any such change is written below only as a PROPOSED future task requiring Ky's explicit request (see ESE-13).
- The existing `ai-governance / verdict` required checks, the existing syntactic spec/role gate (GATE-1..GATE-5 [GATE]), owner-only merge, owner-only deploy, and full-SHA supply-chain pinning ([AGENTS] rule 10) all stay in force and are additional to everything here.
- No code, no tests, no dependencies, no runner installs, no new infrastructure, no new issue/PR/tracker are created by this spec. [#238 body; DOC; C-V handoff rules]

### Evidence-state legend (used throughout)
VERIFIED CURRENT OBSERVATION · VERIFIED GOVERNING RULE · HISTORICAL EVIDENCE · INFERENCE · UNKNOWN. The design doc carries the full reconciliation; requirements cite their source inline.

---

## Requirements

### Requirement 1: Owner-approval stage model G0–G6 (ESE-1)

**User Story:** As Ky, I want a named owner decision at every engineering handoff, so that no agent can advance work past a stage I did not explicitly authorize for that exact subject.

Source: [C-G] enumerates G0–G6; [DOC] "State transitions and minimum approvable evidence" table; [#238 body] correct order.

#### Acceptance Criteria
1. ESE-1.1 WHEN an engineering task begins THEN the system SHALL require a G0 owner authorization that scopes BDD discovery (source-backed issue, repo/scope, actors, problem, permitted research/fixtures, no-go boundaries) before any discovery outside that approved scope. (Source [C-G] G0; [DOC] G0 row.)
2. ESE-1.2 WHEN discovery output exists AND no G1 owner acceptance of the sourced outcomes/rules/edge-cases/counterexamples/unknowns is present THEN the system SHALL NOT permit authoritative spec authoring to proceed. (Source [C-G] G1.)
3. ESE-1.3 IF a requirements/design/tasks spec has not been approved and **merged** by Ky (G2) THEN the system SHALL reject scenario formulation and any code or step-definition change for that work. (Source [C-G] G2; [DOC] G2 row.)
4. ESE-1.4 WHEN mapped Gherkin/equivalent acceptance scenarios are proposed AND no G3 owner approval of those scenarios (mapped to requirement IDs) is present THEN the system SHALL NOT authorize executable acceptance/TDD test authoring. (Source [C-G] G3.)
5. ESE-1.5 WHEN production implementation is requested AND Ky has not examined genuine test-only RED evidence at G4 (see ESE-8) THEN the system SHALL NOT authorize production implementation. (Source [C-G] G4.)
6. ESE-1.6 WHEN implementation (GREEN) is complete AND Ky has not accepted the bounded implementation/GREEN evidence at G5 THEN the system SHALL NOT dispatch independent verification as owner-authorized. (Source [C-G] G5.)
7. ESE-1.7 WHEN independent changed verification tied to the exact revision is complete AND Ky has not accepted it at G6 THEN the system SHALL NOT treat the work as more than **"eligible for owner review only"**, and SHALL NOT merge. (Source [C-G] G6; [C-V] V6.)
8. ESE-1.8 WHILE any stage decision is absent, ambiguous, expired/stale, revoked, or unmatched to the recorded repo/issue/spec/revision/scope the system SHALL hold at **HOLD/PENDING** and SHALL NOT infer approval. (Source [DOC] "absence, ambiguity, expired/stale decision or missing evidence means HOLD".)
9. ESE-1.9 The system SHALL treat approval of one stage as authorizing only the single next specified phase, within the recorded repo/issue/spec/revision/scope, and SHALL NOT let it confer later phases or any cost-bearing/deploy action. (Source [DOC] "An approval authorizes the *next* specified phase only"; [C-G] "deploy remains separately authorized".)

**Evidence/test method:** V1 out-of-order control (ESE-9), plus per-gate positive control within V6 (ESE-14). Deferred to implementation; this spec asserts the required observable behavior only.
**Dependencies:** ESE-2 (genuine authorization), ESE-7 (receipt contract), ESE-8 (RED semantics).

---

### Requirement 2: Genuine, non-agent-forgeable human authorization (ESE-2)

**User Story:** As Ky, I want stage approval to depend on an authentication channel an agent cannot forge, so that an agent pushing with my token cannot approve its own work.

Source: [ROLES] "agents that push with Ky's token show up as KyPython. The gate cannot tell those commits apart from Ky's own." [C-G] "a GitHub comment, PR author, label, commit signature or machine-generated metadata is *not* evidence of trusted human approval." [C-V] "If owner-authenticated, non-agent-forgeable approval is unavailable, status = BLOCKED, not a comment-based owner override."

#### Acceptance Criteria
1. ESE-2.1 The system SHALL NOT accept a GitHub comment, PR author, label, commit author/committer field, commit signature, bot-supplied JSON, Gherkin `@approved` tag, YAML checkbox, or machine/CI metadata as, by itself, evidence of a trusted human stage approval. (Source [C-G]; [C-V] "identity theater".)
2. ESE-2.2 WHEN a stage requires an owner decision AND no authenticated, non-agent-forgeable owner authorization artifact is available THEN the system SHALL report status **BLOCKED** (reason `UNVERIFIABLE_APPROVER`) and SHALL NOT fall back to a comment-based or self-declared owner override. (Source [C-G]; [DOC] security requirement 1 "or the gate must block with `UNVERIFIABLE_APPROVER`".)
3. ESE-2.3 The system SHALL NOT issue, store, or honor an owner-approval receipt that was produced by an agent, by Ky's shared PAT acting as an agent, or by any principal in the `coder` or `spec-author` role acting on its own behalf. (Source [C-V] P0 invariant "an untrusted agent ... cannot self-issue the owner's approval".)
4. ESE-2.4 WHEN a commit's committer is GitHub's web-flow identity or any token-based `KyPython` appearance is observed THEN the system SHALL NOT infer that Ky the human authored or approved the content from that appearance alone. (Source [ROLES] limit; [C-V] "Git author/committer are self-declared ... does not authenticate the author".)
5. ESE-2.5 A verified commit signature SHALL be treated as authenticating the signing key only, and GitHub Actions OIDC SHALL be treated as identifying a workflow execution only; neither SHALL be treated as proof of claimed human authorship or as granting path-scoped approval authority. (Source [C-V] "A verified commit signature authenticates the signing key, **not** the claimed human authorship ... OIDC ... does not inherently authenticate the author".)

**Evidence/test method:** V2 role/path forgery and the "forged owner approval" / "shared-credential collision" adversarial cases (ESE-10, ESE-14). Deferred to implementation.
**Dependencies:** ESE-7, ESE-13 (any trusted-issuer channel that touches protected files is a PROPOSED future task needing Ky's explicit request).

---

### Requirement 3: Mandatory-by-default governed admission for new ventures/projects/repos/material changes (ESE-3)

**User Story:** As Ky, I want every new venture, project, repository, and material code change enrolled in governance by default, so that creation is the normal governed path and nothing starts code outside it.

Source: [DOC] "Universal project admission — owner directive"; "Required project creation and inherited coverage contract"; [#238 body] inventory.

#### Acceptance Criteria
1. ESE-3.1 WHEN a new venture, project, repository, or material code change is initiated under Ky's governed engineering workflow THEN the system SHALL require governance enrollment by default and SHALL NOT treat enrollment as opt-in. (Source [DOC] "governance enrollment is mandatory by default, not opt-in".)
2. ESE-3.2 The system SHALL bind the approved "New Project / New Venture / New Repository" entry point to an existing canonical intake record, owner decision, repo/account, classification, budgets, selected policy revision, and authorized creator before it is usable as the normal creation path. (Source [DOC] "One-click governed intake".)
3. ESE-3.3 WHEN a trusted bootstrapper creates a new repository THEN the system SHALL create it as **unready/quarantined**, install only the permitted governance scaffold (caller pinned by an immutable full SHA, agent instructions, protected policy paths, owner branch/check rules, provenance controls), and SHALL NOT grant any production implementation agent write/push credentials while unready. (Source [DOC] "A trusted bootstrapper can create an unready/quarantined repository ... No production implementation agent receives write/push credentials while unready".)
4. ESE-3.4 WHEN a project is a candidate for `GOVERNED_READY` THEN the system SHALL set that status only after independent readback and actual negative **and** positive admission checks, and SHALL NOT set it from documentation or self-attestation. (Source [DOC] "only after independent readback and actual negative/positive admission checks".)
5. ESE-3.5 IF an agent self-labels a task as no-risk, docs-only, emergency, or exempt THEN the system SHALL NOT bypass admission on that basis. (Source [DOC] "No agent may self-label a task as no-risk, docs-only, emergency, or exempt to bypass admission".)
6. ESE-3.6 The system SHALL classify every owned, reachable repository as one of `GOVERNED / QUARANTINED / NOT_APPLICABLE_BY_AUTHORIZED_SCOPE / BLOCKED_UNAVAILABLE` with source evidence and owner review, with no silent skip for private, empty, default-branch-absent, archived, coursework/learner, external, or forked repos. (Source [DOC] "Retrospective default coverage".)
7. ESE-3.7 WHEN a repository is not owned by Ky (external/fork) THEN the system SHALL classify it `NOT_APPLICABLE_BY_AUTHORIZED_SCOPE` as an ownership constraint and SHALL NOT use that classification to override that repository's own controls. (Source [DOC] "Not applicable to an unowned external repository is an ownership constraint, never a license to override that repo's controls".)
8. ESE-3.8 WHEN the applicability of a testing tool/runner is decided THEN the system SHALL record an authenticated owner-approved `FULL / LIMITED / NOT_APPLICABLE` decision that sets which artifacts/tests are needed, and SHALL NOT allow that decision to bypass the governance process or be issued by an agent. (Source [DOC] "An authenticated owner-approved FULL/LIMITED/NOT_APPLICABLE applicability decision ... without allowing a human or agent to silently bypass the governance process"; "Installing Cucumber in every repository is not required".)
9. ESE-3.9 The system SHALL NOT require installing Cucumber (or any single runner) in every repository to satisfy admission; a documented `EXISTING TESTS SUFFICIENT` / `NOT_APPLICABLE` tool decision SHALL be a valid admission outcome. (Source [DOC] "selecting its runner stays opt-in"; "A documented EXISTING TESTS SUFFICIENT is a valid successful triage result".)

**Evidence/test method:** [DOC] falsification cases 1–6 mapped to V-controls (ESE-9..ESE-14); positive control = unready→readback→`GOVERNED_READY`→eligible-for-review (ESE-14). Deferred to implementation.
**Dependencies:** ESE-2, ESE-4, ESE-5, ESE-6, ESE-13.

---

### Requirement 4: Local/cloud parity — location is never a waiver (ESE-4)

**User Story:** As Ky, I want identical governance decisions whether an agent runs on my Mac, in a container/VM, or in a cloud workspace, so that local execution is not an escape route.

Source: [DOC] "Execution-location neutrality" invariants 1–6; "Local or cloud execution is not an escape route".

#### Acceptance Criteria
1. ESE-4.1 WHEN two requests present the same canonical policy/version, owner authorization, stage, role, accepted inputs and content digests, target path scope, and revocation state THEN the system SHALL return the same admission decision and reason for a local request and a cloud request. (Source [DOC] invariant 1 "Common decision contract".)
2. ESE-4.2 WHERE a provider-specific adapter exists THEN it SHALL change only how isolation is enforced, and SHALL NOT change what actions are authorized. (Source [DOC] invariant 1.)
3. ESE-4.3 WHEN pre-dispatch stage/scope/isolation/owner-receipt checks fail THEN both local and cloud launchers SHALL refuse to hand out a write-capable workspace. (Source [DOC] "Control admission at both ends".)
4. ESE-4.4 The system SHALL NOT give an untrusted code agent an owner PAT or raw publish privilege in any location. (Source [DOC] "untrusted code agents must not get an owner PAT or raw publish privilege".)
5. ESE-4.5 WHEN code is pushed to an unprotected branch before verification THEN the system SHALL treat it as untrusted and unmergeable and SHALL NOT treat it as equivalent to pre-write prevention. (Source [DOC] "Code pushed to an unprotected branch before verification is not equivalent to pre-write prevention".)
6. ESE-4.6 WHEN remote approval, required-check status, live provider isolation, or authentication is unavailable THEN the system SHALL permit offline research/neutral drafts/diff inspection/deterministic tests but SHALL NOT self-authorize progression to mutation or publication, preserving `PASS / FAIL / BLOCKED / UNKNOWN / NOT_RUN` at the actual observed scope. (Source [DOC] invariant 4 "Offline safe operation".)
7. ESE-4.7 WHERE a provider cannot meet the same isolation and proof bar THEN the system SHALL leave that provider's implementation lane **BLOCKED** rather than apply weaker rules. (Source [DOC] invariant 6; "leave its implementation lane BLOCKED".)
8. ESE-4.8 The system SHALL classify unmanaged/out-of-band local authoring that no GitHub ruleset or repo file can prevent as **OUTSIDE ENFORCED BOUNDARY / NOT PROVEN**, and SHALL NOT assert that absolute local-authoring prevention is installed. (Source [DOC] "Unavoidable host boundary"; "Do not tell Ky that absolute prevention is installed".)

**Evidence/test method:** V1–V6 reproduced "separately in at least one representative isolated local and one provider-managed cloud environment" [DOC]; distinguish offline policy simulation from real provider rejection (ESE-9..ESE-14). Deferred to implementation.
**Dependencies:** ESE-2, ESE-6, ESE-7.

---

### Requirement 5: Execution isolation, read-only inputs, trusted publisher (ESE-5)

**User Story:** As Ky, I want each stage to run in a disposable sandbox with genuinely read-only inputs and a separate trusted publisher, so that a coder cannot alter specs/tests or publish its own output.

Source: [C-V] "Execution isolation" and "Separate boundaries"; [DOC] invariant 2 "Two independent barriers".

#### Acceptance Criteria
1. ESE-5.1 WHEN a stage job runs THEN it SHALL run in a fresh unprivileged disposable container/VM/workspace with upstream inputs mounted genuinely read-only, a scoped writable output, no host Docker daemon/socket, no owner credentials or broad secrets, minimal capabilities, and explicit network egress. (Source [C-V] isolation paragraph.)
2. ESE-5.2 The system SHALL ensure a `coder` principal cannot change `features/`, `specs/`, or `tests/`; those input artifacts SHALL remain immutable to the coder. (Source [C-V] "a coder must not be able to change features/, specs/ or tests/".)
3. ESE-5.3 The system SHALL NOT treat `chmod 444` (or any file-mode flag alone) as a security boundary against an elevated process. (Source [C-V] "chmod 444 alone is not a security boundary".)
4. ESE-5.4 WHEN output is proposed for publication THEN a separate trusted publisher SHALL validate the output tree and write permissions **before** pushing, and the system SHALL NOT treat post-PR CI alone as sufficient. (Source [C-V] "Trusted publishing must validate the output tree ... before pushing; post-PR CI alone is insufficient".)
5. ESE-5.5 The system SHALL keep the four boundaries separate — (1) trusted receipt issuance/pre-write authorization, (2) fresh stage execution environment, (3) independent verification + controlled publisher, (4) GitHub status/branch admission + human merge/deploy — and SHALL NOT give any single orchestrator all agent credentials with unilateral signing authority. (Source [C-V] "Separate boundaries"; "Never give the orchestrator all agent credentials".)
6. ESE-5.6 The system SHALL NOT claim that third-party agent environments (e.g. cloud IDE) already provide these per-stage mounts; such isolation SHALL be independently verified before relied upon. (Source [C-V] "Do not assume Codex Cloud/IDE or third-party agents already provide these per-stage mounts; verify independently".)

**Evidence/test method:** V2 forgery at the sandbox/publisher boundary (ESE-10); isolation negative controls in V-suite (ESE-14). Deferred to implementation.
**Dependencies:** ESE-2, ESE-7.

---

### Requirement 6: Stage-receipt contract, lineage, replay/revocation invariants (ESE-6)

**User Story:** As Ky, I want every stage approval bound to exact subject and content with revocation and lineage, so that stale, replayed, scope-expanded, or drifted receipts cannot advance work.

Source: [C-V] "Stage receipt contract and state transitions"; [DOC] security requirement 2 "Bind to exact immutable inputs".

#### Acceptance Criteria
1. ESE-6.1 Each stage receipt SHALL identify: stage; feature/task ID; exact authorized paths and operations; authenticated issuer/principal; role; policy revision; predecessor receipt IDs/digests; canonical relevant-input content digests; candidate output digest; expiry/revocation/freshness; and the required owner decision. (Source [C-V] receipt contract.)
2. ESE-6.2 The system SHALL bind each approval to the exact subject and content and SHALL reject stale-SHA replay or scope expansion. (Source [C-V]; [DOC] "no stale SHA replay or scope expansion".)
3. ESE-6.3 The system SHALL recheck receipts at dispatch **and** before publish, and SHALL reject missing, malformed, reused, expired, revoked, or drifted receipts. (Source [C-V] "Recheck at dispatch and before publish; reject missing/malformed/reused/expired/revoked or drifted receipts".)
4. ESE-6.4 WHEN a material upstream change occurs (changed behavior/spec/input, or a revoked/expired receipt) THEN the system SHALL invalidate only the affected downstream descendants, and SHALL NOT invalidate unrelated lineage. (Source [C-V] "invalidate only affected downstream descendants".)
5. ESE-6.5 The system SHALL NOT inherit receipts across repositories or unrelated issues. (Source [DOC] security requirement 2 "No inheritance across repositories or unrelated issues".)
6. ESE-6.6 WHEN a receipt's required stage is missing, malformed, untrusted, revoked, stale, or inconsistent THEN the system SHALL HOLD, and an unavailable approval service SHALL NOT default to approve; the system SHALL report `PENDING / BLOCKED / REJECTED / SUPERSEDED / VERIFIED` accurately. (Source [DOC] security requirement 3 "Fail closed and distinguish statuses".)
7. ESE-6.7 The system SHALL keep deployment approval separate from merge approval. (Source [C-V] "Keep deployment approval separate from merge"; [AGENTS] rule 12.)

**Evidence/test method:** V5 replay/revocation and "concurrent changed inputs" adversarial case (ESE-13, ESE-14). Deferred to implementation.
**Dependencies:** ESE-2.

---

### Requirement 7: Pre-dispatch admission broker — enforcement before implementation begins (ESE-7)

**User Story:** As Ky, I want enforcement at task dispatch and writable-workspace handoff, not only at final CI, so that an agent cannot start unauthorized code and rely on a late check.

Source: [DOC] security requirement 4 "Enforcement must work before implementation begins"; [C-V] "Recheck at dispatch and before publish".

#### Acceptance Criteria
1. ESE-7.1 WHEN an agent task is dispatched or a writable workspace is handed off THEN the system SHALL evaluate stage/role/path/receipt authority as a blocking pre-mutation guard and SHALL NOT rely on a final PR check alone to prevent unauthorized phase work. (Source [DOC] req 4.)
2. ESE-7.2 WHEN unauthorized phase artifacts or PR merges are attempted THEN the final CI verdict SHALL also block them (defense in depth alongside ESE-7.1). (Source [DOC] req 4 "plus blocking final CI for unauthorized phase artifacts and PR merges".)
3. ESE-7.3 WHERE a stronger repo gate exists (e.g. LamportLogic per-path mutation authority) THEN the system SHALL require explicit per-file mutation authority and SHALL NOT relax protection. (Source [DOC] req 4; [LL] `pnpm ai:mutation:check`.)
4. ESE-7.4 WHERE enforcement is technically impossible at a given surface THEN the system SHALL describe that surface as unenforceable rather than claim full prevention. (Source [DOC] req 4 "describe any surfaces where enforcement is impossible rather than claiming full prevention".)

**Evidence/test method:** V1 (pre-write rejection) and V2 at the dispatch boundary (ESE-9, ESE-10). Deferred to implementation.
**Dependencies:** ESE-2, ESE-5, ESE-6.

---

### Requirement 8: Test-adequacy semantics — genuine RED, GREEN, no vacuous trace (ESE-8)

**User Story:** As Ky, I want RED and adequacy judged by behavior, not by exit codes or cited IDs, so that a false RED or an `assert True` trace cannot authorize advancement.

Source: [C-V] "Test adequacy semantics"; [DOC] security requirement 3 "G4 RED means ...".

#### Acceptance Criteria
1. ESE-8.1 WHEN RED evidence is evaluated for G4 THEN the system SHALL require a structured expected assertion failure on the intended behavior with a healthy fixture/import/harness and passing unrelated invariant/regression tests, and SHALL NOT accept a nonzero exit code alone, import/syntax errors, collection failures, skips, or a universal stub exception as genuine RED. (Source [C-V]; [DOC] "G4 RED means expected assertion failure ... not a generally failing CI job".)
2. ESE-8.2 The system SHALL treat a requirement↔scenario↔test marker (an ID cited in a name or comment) as a trace-intent check only, and SHALL NOT treat it as behavioral coverage. (Source [C-V] "Never treat a marker in a comment as behavioral coverage"; [GATE] GATE-1.4 is explicitly "syntactic".)
3. ESE-8.3 WHEN all requirement IDs are cited but assertions are vacuous (e.g. `assert True`) THEN the system SHALL NOT grant adequacy authorization on regex/ID-match alone. (Source [C-V] V4; [DOC] "assert True and a single matching ID may satisfy" the current syntactic check — this requirement closes that gap.)
4. ESE-8.4 WHEN GREEN evidence is evaluated for G5 THEN the system SHALL require the corresponding tests GREEN, preserved existing tests, and independently selected negative/contrast oracles. (Source [C-V] "After implementation, require ... GREEN, preserved existing tests and independently selected negative/contrast oracles".)
5. ESE-8.5 WHERE mutation testing is used THEN it SHALL run on real implemented production code where meaningful; the system SHALL NOT mandate an arbitrary global mutation threshold (e.g. 80–85%) and SHALL NOT run mutation before code exists. (Source [C-V] "Do not mandate an arbitrary global 80–85% mutation threshold or run mutation before code exists".)
6. ESE-8.6 WHEN mutation survivors exist, no valid mutants are generated, jobs are skipped, the baseline/stub is weak, or implementations are equivalent THEN the system SHALL record an honest `UNKNOWN`/`FAIL` disposition and SHALL NOT invent a percentage. (Source [C-V].)
7. ESE-8.7 The system SHALL keep the method contract (what RED/adequacy mean) over any specific vendor tool (Stryker/Mutmut/Schemathesis/Specmatic are options, not mandatory). (Source [C-V] "options, not mandatory products"; "Keep the method contract over vendor tooling".)

**Evidence/test method:** V3 (false RED) and V4 (vacuous trace) controls (ESE-11, ESE-12). Deferred to implementation.
**Dependencies:** ESE-1, ESE-6.

---

### Requirement 9: V1 — out-of-order rejection (ESE-9)

**User Story:** As Ky, I want a spec write attempted without a G1 receipt to be rejected before any authorized write/publish, so that stage order is enforced at the boundary, not after the fact.

Source: [C-V] "V1 OUT OF ORDER"; [DOC] invariant 5.

#### Acceptance Criteria
1. ESE-9.1 WHEN a spec write (or any stage artifact) is attempted without the required predecessor stage receipt THEN the system SHALL reject it **before** the authorized write/publish point and SHALL record the correct reason (out-of-order) at the correct boundary. (Source [C-V] V1.)
2. ESE-9.2 The system SHALL demonstrate ESE-9.1 at a real boundary (not only as isolated logic) in at least one isolated local and one provider-managed cloud environment, and SHALL distinguish offline policy simulation from real provider rejection. (Source [DOC] invariant 5.)

**Evidence/test method:** V1 negative control execution producing evidence of pre-write rejection. Deferred to implementation.
**Dependencies:** ESE-1, ESE-6, ESE-7.

---

### Requirement 10: V2 — role/path forgery rejection (ESE-10)

**User Story:** As Ky, I want a coder's attempt to modify tests/specs or spoof a human git author to be rejected by the read-only sandbox/publisher, so that identity strings and signatures cannot substitute for authority.

Source: [C-V] "V2 ROLE/PATH FORGERY".

#### Acceptance Criteria
1. ESE-10.1 WHEN a coder principal attempts to modify `tests/`, `specs/`, or `features/` THEN the read-only sandbox/publisher SHALL reject the change. (Source [C-V] V2; ESE-5.2.)
2. ESE-10.2 WHEN a commit presents a spoofed human git author/committer or a signed commit asserting owner authorship THEN the system SHALL NOT allow it to silently substitute for authenticated owner authority. (Source [C-V] V2; ESE-2.1, ESE-2.5.)
3. ESE-10.3 The "forged owner approval" and "shared-credential collision" adversarial cases SHALL be exercised and SHALL fail closed for the correct reason. (Source [C-V] "Add adversarial cases for forged owner approval, shared-credential collision".)

**Evidence/test method:** V2 negative controls at the filesystem/credential/publisher boundary. Deferred to implementation.
**Dependencies:** ESE-2, ESE-5, ESE-7.

---

### Requirement 11: V3 — false RED rejection (ESE-11)

**User Story:** As Ky, I want a harness/syntax/import failure rejected as RED while a genuine behavioral assertion failure with a healthy harness is eligible, so that broken environments cannot masquerade as desired failures.

Source: [C-V] "V3 FALSE RED"; [C-G] G4 "distinguishing desired failure from environment failure".

#### Acceptance Criteria
1. ESE-11.1 WHEN RED is claimed but caused by syntax/import/collection/harness failure THEN the system SHALL reject RED authorization. (Source [C-V] V3; ESE-8.1.)
2. ESE-11.2 WHEN RED is a designated behavioral assertion failure on the intended behavior with a healthy harness and passing unrelated invariants THEN the system SHALL treat it as RED-eligible. (Source [C-V] V3.)
3. ESE-11.3 The "fake/synthetic RED reports" adversarial case SHALL be exercised and SHALL fail closed. (Source [C-V] "fake/synthetic RED reports".)

**Evidence/test method:** V3 negative + eligibility controls. Deferred to implementation.
**Dependencies:** ESE-8.

---

### Requirement 12: V4 — vacuous-trace rejection and post-code adequacy (ESE-12)

**User Story:** As Ky, I want a suite that cites every ID with empty assertions to earn no adequacy authorization, so that trace alone cannot pass for correctness.

Source: [C-V] "V4 VACUOUS TRACE".

#### Acceptance Criteria
1. ESE-12.1 WHEN all requirement IDs are cited but assertions are vacuous (`assert True`) THEN the system SHALL grant no adequacy authorization. (Source [C-V] V4; ESE-8.3.)
2. ESE-12.2 The system SHALL substantiate adequacy with post-code mutation/contrast checks on real implemented code, not regex/ID-match alone. (Source [C-V] V4; ESE-8.5.)
3. ESE-12.3 The "blanket N/A exemptions" adversarial case SHALL be exercised: an agent-issued or forged `NOT_APPLICABLE` SHALL be denied while a correct human-scoped `FULL/LIMITED/NOT_APPLICABLE` preserves required baseline checks. (Source [C-V] "blanket N/A exemptions"; [DOC] falsification case 5.)

**Evidence/test method:** V4 negative controls plus a positive applicability control. Deferred to implementation.
**Dependencies:** ESE-3, ESE-8.

---

### Requirement 13: V5 — replay/revocation/concurrent-change rejection; pinned-SHA drift (ESE-13)

**User Story:** As Ky, I want changed upstream inputs or an expired/revoked receipt to reject downstream authorization by content lineage, and I want SHA-pin drift surfaced without replacing immutable pins, so that replay and silent drift cannot advance work.

Source: [C-V] "V5 REPLAY" and P0 drift paragraph; [DOC] falsification case 4.

#### Acceptance Criteria
1. ESE-13.1 WHEN upstream behavior/spec/input changes, or a receipt is expired/revoked THEN the system SHALL reject downstream authorization by content lineage. (Source [C-V] V5; ESE-6.4.)
2. ESE-13.2 WHEN concurrent creator/publisher or concurrent changed inputs are detected THEN the system SHALL reject incorrectly accepted work without duplicating a project or deadlocking legitimate setup. (Source [C-V] "concurrent changed inputs"; [DOC] falsification case 4.)
3. ESE-13.3 The system SHALL add independently reviewed drift detection and an SHA-promotion process for shared callers only after the appropriate spec approval, and SHALL keep full immutable SHA pinning; it SHALL NOT replace immutable SHAs with mutable release tags or auto-merge. (Source [C-V] P0 `buildlogic-governance` drift paragraph; [AGENTS] rule 10.)
4. ESE-13.4 Any change to a protected enforcement file, pinned caller SHA, role map, or workflow that would be needed to realize ESE-1..ESE-13 SHALL be a PROPOSED future task requiring Ky's explicit request and Ky's own merge, and SHALL NOT be made by an agent or by this spec. (Source [AGENTS] rule 7; [C-V] handoff rule 4; [DOC] "Do not edit a ruleset/role map/workflow ... by treating this documentation change as implementation authorization".)

**Evidence/test method:** V5 replay/revocation controls; drift-detection design verification. Deferred to implementation.
**Dependencies:** ESE-6.

---

### Requirement 14: V6 — positive control reaching owner-review eligibility only (ESE-14)

**User Story:** As Ky, I want one properly authenticated end-to-end pipeline to produce valid RED and GREEN, pass adequacy and independent verification, and stop at "eligible for owner review only", so that the happy path is proven without any auto-merge or deploy.

Source: [C-V] "V6 POSITIVE"; [DOC] falsification case 6 positive control; invariant 5.

#### Acceptance Criteria
1. ESE-14.1 WHEN a properly authenticated, scoped pipeline runs on one existing, scoped, safely isolated synthetic feature THEN the system SHALL create valid RED and GREEN evidence, pass justified adequacy and independent verification by a reviewer distinct from the coder, and reach status **"eligible for owner review only"**. (Source [C-V] V6; [DOC] case 6.)
2. ESE-14.2 The positive control SHALL NOT auto-merge or deploy and SHALL NOT require cloud spend. (Source [C-V] V6 "never auto-merge/deploy"; [DOC] case 6 "no auto-merge/deploy and no cloud spend required".)
3. ESE-14.3 The positive control SHALL record test fixture, policy version, actor, inputs, precondition, and observed evidence from actual execution, and SHALL be reproduced separately in at least one isolated local and one provider-managed cloud environment. (Source [C-V] "Record ... from actual execution"; [DOC] invariant 5.)
4. ESE-14.4 A new-governed-creation positive control SHALL show an approved new venture registered once, creating a bounded unready repository, proving initialized governance/identity/checks, and only then accepting legitimate stage-specific code proposals through real RED/GREEN and independent verification to become eligible for Ky's merge. (Source [DOC] falsification case 6; "Positive control".)

**Evidence/test method:** V6 positive control execution with recorded evidence; owner-review-eligibility status asserted, no merge/deploy. Deferred to implementation.
**Dependencies:** ESE-1 through ESE-13.

---

## Global definition of done (from [DOC])
An independently reproduced per-account, per-repository, per-provider, and local/cloud coverage report shows every owned writable scope either genuinely enforced or explicitly quarantined and unable to publish; new governed creation has a successful positive control; and bypass attempts fail for the right reason. If some GitHub/OS/admin surface cannot be controlled at the current plan or privilege level, the correct report is **GLOBAL INVARIANT NOT ENFORCED**, never a false 100% coverage claim. Kiro owns the specification; only owner-approved merged policy changes and independent verification can advance operational status. (Source [DOC] "Definition of DONE (global)".)

## Status note (truthfulness)
This spec is `draft`. It asserts required behavior only. It does **not** claim G0–G6 or universal admission are enforced; the merged doc records them as "NOT YET ENFORCED" / "proposed requirements, not functioning GitHub status checks" [DOC]. No enforcement may be reported on documentation (including this spec) alone.
