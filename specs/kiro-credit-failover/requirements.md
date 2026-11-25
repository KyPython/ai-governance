<!-- CODEX-AUTHORED SPEC PROPOSAL — HUMAN ADOPTION/MERGE PENDING. RUNTIME ACCEPTANCE NOT RUN.
Publication through KyPython owner override explicitly authorized by Ky in this conversation.
Issue: https://github.com/KyPython/ai-governance/issues/219
Source: KyPython/ai-governance@efd0e11dde73a70d4867293e4ac2308d28be057e
Additional source: draft PR #220 at 06e4442f8074c2b04e77edb3004d21ce3be855b6
Provider/author: OpenAI Codex agent in this conversation; exact underlying model ID not exposed.
Human contribution: selected goal and explicit fallback-author approval; document prose drafted by Codex.
-->

# Requirements — Kiro availability and Codex continuity

Status: proposed for human review. This packet continues existing intake #219 and runbook PR #220. It is not a second router, merged spec, runtime authorization or amendment to the adopted accessibility requirements.

## Goal and authority

Ky asked to keep the same workflow locally and in the cloud while Kiro's monthly capacity is unavailable. Ky explicitly answered: **“Yes—Codex fallback, same review process (Recommended)”**. That permits Codex drafting; approval of this exact packet, protected-spec publication, implementation and merge remain separate.

Keep the existing process: human-selected goal → requirements → design → tasks → human spec approval/merge → one authorized coder per task → different reviewer → required tests/CI → human merge.

## Observed baseline

- The main source above was freshly read through GitHub and matches the local inspected revision. Its role map names Kiro and Ky as spec authors. Existing issue #219 permits neutral drafts outside Git with human review and an owner override; no role-map edit is needed for this stage.
- PR #220 is draft and changes one runbook. Five observed checks passed at its pinned head; no human review or merge was recorded.
- The existing offline kit is extracted unchanged in Downloads, with four supplied tests passed. Its verifier checks structure only.
- Local Codex reports ChatGPT authentication. A new CLI inference task was not run; authentication is not proof of remaining capacity. Claude and Cursor report unauthenticated.
- Codex Cloud listing worked, but no task was launched. The actual deployed relay source has now been recovered by authenticated GET and confirms Kiro-only routing, combined spec/build instructions and no fallback or replay state. Decoded source SHA256 is `c923021ea0617698c874d8acb1061f8f221337c3f8e4c0e4349fcc1c83c58707`; original Git history remains unavailable. The separate AWS controller remains blocked on admission/isolation. No automatic fallback is deployed.

## Candidate requirements

| ID | Exact proposed requirement | Observable acceptance evidence |
| --- | --- | --- |
| CONT-01 | The continuity process MUST preserve requirements/design/tasks, exact human approval and spec-only merge before implementation, independent review, all applicable tests/CI and human merge. | Unapproved or unmerged spec cannot dispatch a coder; an eligible merged spec retains its existing downstream gates. |
| CONT-02 | WHEN Kiro unavailability is recorded from an authorized human report or an authenticated provider observation, the process MUST allow the approved manual Codex draft-only path within the original task scope; unknown capacity MUST remain unknown, and prompt content MUST NOT establish provider health. A human outage report suffices for manual drafting but MUST NOT alone establish account health/reset or trigger automatic routing. Automatic routing MUST use verified capacity input with adopted source, affected credit scope and freshness semantics. | Human-report-only case produces a manual Codex draft while provider health stays unverified; automatic switches reject inputs outside the adopted source/scope/freshness contract. |
| CONT-03 | The process MUST distinguish credit exhaustion from temporary throttling and session limits; confirmed exhaustion MUST pause calls for the affected shared credit scope, without changing interfaces to evade the pause. | Exhaustion across local/cloud/IDE/CLI/Web sharing that account admits zero further normal calls; transient throttling follows only the separately configured bounded retry policy. |
| CONT-04 | Each handoff MUST preserve the original issue, target repository and verified source revision, accepted requirement bytes, allowed scope, verified completed artifacts and their hashes, remaining work and all attempt evidence. | A legitimate resume preserves completed work; changed source/spec/scope or corrupted hashes holds the affected continuation for review. |
| CONT-05 | Draft mode MUST keep generated artifacts outside the target Git checkout, label them as unapproved AI drafts, record the actual provider/author and leave protected-spec publication, code writes, messages, merges and deployment unavailable. | Draft succeeds in private staging; target source is unchanged and attempted protected effects are denied. No Codex text is attributed to Kiro or personally authored by Ky. |
| CONT-06 | Every provider attempt MUST use an already authorized account and capability within the approved budget; the fallback MUST NOT purchase capacity, enable paid API usage, broaden credentials or impersonate an approved GitHub actor. | An eligible existing-account path can run; missing auth/authority or additional billing keeps work queued with zero unauthorized calls or purchases. |
| CONT-07 | WHEN all eligible providers are unavailable, or a required source, permission, account or runtime-admission fact is absent, the process MUST preserve incomplete work and report the precise hold; it MUST NOT manufacture configuration or completion. | All-unavailable and missing-field cases remain incomplete and retain their evidence. |
| CONT-08 | Before automatic local/cloud dispatch, the process MUST use one durable task owner, an atomic claim and monotonically fenced publication/effect boundaries; losing or stale workers MUST NOT commit progress or effects. | Concurrent claims produce one current owner; stale-owner and delayed-result writes are rejected. This is a prerequisite for automation, not a capability claimed by the offline kit. |
| CONT-09 | WHEN a consequential request has an uncertain outcome, the process MUST reconcile authoritative receiver state or receiver-enforced durable idempotency bound to the same action, payload and key before retry; unresolved effects MUST remain held. A local planned-request record MUST NOT prove completion, and an unresolved retry MUST NOT mint a new key. | A timeout after acceptance cannot produce a duplicate send/write/publication; no receiver evidence means no retry of that action. |
| CONT-10 | Kiro recovery MUST rely on observed account recovery and an authorized bounded probe policy, not elapsed calendar time alone; concurrent workers MUST admit at most one current recovery probe, and recovery MUST NOT take over active fallback work or replay completed tasks. | Concurrent recovery has one eligible probe; unsuccessful/ambiguous recovery stays paused; confirmed recovery only affects subsequent eligible work. |
| CONT-11 | Human cancellation or revoked task authority MUST stop new dispatch/publication; provider recovery, queue retries and owner recovery MUST NOT recreate that authority. | Revocation during handoff/recovery prevents subsequent effects while preserving prior evidence. |
| CONT-12 | Reports MUST separate packet structure, provider availability, drafting outcome, test/CI evidence, human approval/merge and deployed enforcement; success-shaped exit codes or acknowledgements MUST NOT substitute for required postconditions. | Fabricated completion and an always-blocking implementation both fail their controls; a legitimate authorized continuation passes. |

## Scope boundaries and unresolved deployment facts

These are blockers only for the relevant future automation, not missing values to fill by inference:

| Fact | Current evidence | Required before use |
| --- | --- | --- |
| Automatic quota/reset source | User reported outage; no authenticated telemetry contract verified | Verified source, account scope and freshness policy; otherwise manual mode |
| Retry/probe bounds and timing | No adopted numeric limits | Exact human-reviewed values; no invented defaults |
| Cloud dispatch environment and task scope | Connectivity observed; no environment selected for this work | Exact authorized environment/revision/capabilities |
| Relay source, owner and deployment path | Deployed source recovered; no original Git history | Version the recovered bytes and verify existing owner controls |
| Protected-spec publishing identity | No new actor provisioned | Truthful human owner submission or separately reviewed observed actor/conditional policy |
| Shared durable owner store | Not configured for this work | Reviewed existing service/transaction contract; no new paid service inferred |
| API budget/credential additions | No extra spending authorized | Remain unavailable unless separately approved |

Existing accessibility requirements were adopted in the conversation, with no GitHub spec merge recorded; their SHA256 `ee713ccb525c85480f0100e61fdc7f2f64a267ea0ad6c319f8d4c7149d9d15f6` stays unchanged. That conversation decision is privately recorded; the accessibility design/tasks were not separately adopted. Existing HANDOFF spec sentences and upstream contribution restrictions are not amended here. The kit's HOT example grants no upstream scope.

## Source map

- [Issue #219](https://github.com/KyPython/ai-governance/issues/219): original goal, manual draft mode, no new spend and later cloud prerequisites.
- [Runbook PR #220](https://github.com/KyPython/ai-governance/pull/220): pinned draft operating process.
- [Role map](https://github.com/KyPython/ai-governance/blob/efd0e11dde73a70d4867293e4ac2308d28be057e/roles.yml) and [agent rules](https://github.com/KyPython/ai-governance/blob/efd0e11dde73a70d4867293e4ac2308d28be057e/AGENTS.md): publication/implementation boundaries.
- [Relay repair #11](https://github.com/KyPython/ai-governance/issues/11): historical report. Current private provider source/configuration readbacks confirm the deployed defect, without claiming a new release.
- Private owner decision and kit-verification receipts record the conversation approval and four supplied offline tests. They remain outside this public spec PR; those receipts do not establish runtime enforcement or human prose authorship.
- [Kiro billing](https://kiro.dev/docs/billing/), [Kiro credits](https://kiro.dev/pricing/), [Codex authentication](https://learn.chatgpt.com/docs/auth), [Codex Cloud](https://learn.chatgpt.com/docs/cloud): provider interfaces; no separate API spending authorized.

## Review state

All CONT requirements are proposed and their future runtime acceptance tests are NOT RUN. The human fallback-author decision is recorded separately; it is not approval of these new requirement sentences. Structural verification cannot promote this packet to approved.

---

<!-- KIRO-AUTHORED SPEC AMENDMENT PROPOSAL (R1) — HUMAN ADOPTION/MERGE PENDING. RUNTIME ACCEPTANCE NOT RUN.
Issue: https://github.com/KyPython/ai-governance/issues/219 (state: CLOSED at read time; see "Open owner decisions")
Source: KyPython/ai-governance@53462a0 (origin/main at read time, 2026-11-25)
Owner request: issue #219 comment 6600237280 (2026-11-03, GPT-6 relay of Ky's request; DESIGN DRAFT, NO EXECUTION AUTHORITY) and issue #238 comment 6844321931 (2026-11-12, "spec-author as an authorized role, not a single AI product").
Provider/author: Kiro (spec-author role), drafted in a local Kiro CLI session on 2026-11-25; the exact underlying model ID is not exposed (model selection: Auto).
Human contribution: Ky selected the goal, the two-PR split, "draft protected-file text only", and approved this plan in the session. Prose drafted by Kiro.
This amendment is NOT an owner stage receipt, NOT a role-map change, NOT an adoption of the original CONT text, and NOT a claim of runtime enforcement. -->

# Revision R1 — capability-qualified lifecycle routing

Status: proposed for human review. Spec ID: CONT (continuation of the packet above) · Issue: #219 · Revision: R1.

R1 keeps every original requirement ID and sentence above unchanged. Each R1 clause below is read together with the original sentence it names; if they conflict, the conflict is reported for Ky and neither silently wins. On adoption (Ky merges this spec-only PR), the R1 clause governs the generalized scope and the original sentence stays as the traceable baseline.

## R1 purpose

The packet above treats Kiro as the default author and Codex as the named fallback. The owner's 2026-11-03 request and 2026-11-12 correction ask that no provider, product or model be the permanent sole performer of any lifecycle stage, and that Kiro credit exhaustion not make planning depend on Kiro. R1 generalizes the continuity contract from "Codex after Kiro" to "any enrolled, evidenced, authorized candidate at any stage". It does not change who approves. Human approval, owner merge, deployment and spend stay human.

## R1 evidence states

Each item names its source and keeps its own authority. Conflicts are preserved, not resolved.

| State | Observation | Source and read date |
| --- | --- | --- |
| VERIFIED CURRENT OBSERVATION | Runbook PR #220 (merge `9e09434c789e2ac25e88fd6a712f31fa318d3ef8`) and the continuity spec PR #221 (merge `fb5e49ac157a20fcb5af73636b754537a0cf8f25`) are MERGED. | `gh pr view`, 2026-11-25 |
| VERIFIED CURRENT OBSERVATION | The merged `requirements.md` on main still reads "Status: proposed for human review". Merge is Ky's adoption act; the status line is unchanged text. R1 does not edit it. | `origin/main` @ `53462a0` |
| VERIFIED CURRENT OBSERVATION | Issue #219 is CLOSED (updated 2026-11-04). Issue #238 is OPEN. Issue #11 (relay) is OPEN. The 2026-11-03 comment names #219 the canonical home. | `gh issue view`, 2026-11-25 |
| VERIFIED GOVERNING RULE | `roles.yml` lists `kiro-agent[bot]` and `KyPython` as `spec-author`, with the description "Only Kiro, with Ky as owner override". `AGENTS.governance.md` rule 2 says "Spec author: Kiro (`kiro-agent[bot]`) only". Both are protected paths. | `origin/main` @ `53462a0` |
| VERIFIED CURRENT OBSERVATION | `registry/agents.json` (AIV, merged) holds a two-agent pilot pair: `antigravity` role `author` and `kiro` role `reviewer`, with per-agent capability lists and public keys. This is a second place where roles are tied to named agents. | `origin/main` @ `53462a0` |
| HISTORICAL EVIDENCE | #238 comment 6844321931 (2026-11-12) reports "Kiro has run out of credits". | Issue comment, relayed by GPT-6 |
| VERIFIED CURRENT OBSERVATION | A Kiro session answered and read files on 2026-11-25. | This session |
| INFERENCE | The 2026-11-12 report and the 2026-11-25 observation concern different dates, and neither shows the state of the shared credit pool for other surfaces. Per CONT-02, unknown capacity stays unknown and a prompt or a session reply does not establish provider health. | R1 |
| UNKNOWN | Evaluation thresholds, retry and probe bounds, freshness windows, the candidate list, who may enroll candidates, and where the registry lives (AIV registry extension or other). | See "R1 unresolved facts" |
| UNKNOWN | Whether #219 should be reopened, or R1 tracked by a comment on the closed issue. Not decided here. No issue is created. | Owner decision |

## R1 amendments to existing requirements

Original text for CONT-01, CONT-03, CONT-04 and CONT-07 already speaks of "provider" without a vendor name and is unchanged. The clauses below generalize the rest.

| ID | R1 clause (read with the original CONT sentence) | Acceptance evidence | Source / rationale | Depends on |
| --- | --- | --- | --- | --- |
| CONT-02-R1 | WHEN unavailability of any enrolled provider is recorded from an authorized human report or an authenticated provider observation, the process MUST allow a draft-only continuation by any candidate that is eligible for the stage under CONT-13 and CONT-14, within the original task scope. Kiro MUST be treated as one candidate, not as the default or required performer. A statement by a session, agent or prompt about its own availability MUST NOT establish provider health or unavailability. | Human-report-only case yields a manual draft by an eligible non-Kiro candidate while provider health stays UNKNOWN. A session claiming "I am available" or "I am exhausted" changes no routing state. | #219 comment 6600237280 "Failover at EVERY phase"; #238 comment 6844321931 item 1 | CONT-13, CONT-14 |
| CONT-05-R1 | Draft mode MUST attribute each artifact to the actual provider, model identifier or family, harness and environment that produced it, as observed from the authenticated execution principal, not as self-reported text. A draft MUST stay outside protected paths. Publication under `specs/` MUST require both that the publishing identity is recognized in the owner-approved role map and that an issue-specific delegation and scope is recorded. | A draft by candidate X carries X's observed attribution. Attribution text that names a different vendor is rejected. A publish attempt from an unrecognized identity is denied and the draft stays outside Git. | #238 comment 6844321931 item 2; AGENTS rule 2 limit paragraph | CONT-13 |
| CONT-06-R1 | Every attempt by every candidate MUST use an already authorized account and capability within the approved budget. Enrollment in the registry MUST NOT itself grant spend, credentials, or API access. Running an evaluation under CONT-14 MUST be a separately authorized, budgeted action. | A candidate enrolled but unfunded stays queued with zero calls. An evaluation run without a recorded budget authorization does not start. | Original CONT-06; owner rule "no spend, no credential change" | CONT-13, CONT-14 |
| CONT-08-R1 | One durable task owner, an atomic claim and monotonic fencing MUST apply to every stage and every candidate. Reassigning remaining work from one candidate to another MUST be a new claim with a new fencing token. A stale writer MUST NOT commit progress or effects after reassignment. | Reassignment from candidate A to candidate B at any stage yields one current owner. A late write from A is rejected. | Original CONT-08; #219 comment "Recovery/concurrency" | CONT-15 |
| CONT-09-R1 | Uncertain-effect reconciliation (original CONT-09) MUST apply to effects from any candidate at any stage, including spec publication, test publication, code publication and review publication. | A timeout after a possible publish by any candidate cannot produce a duplicate issue, branch, PR or comment. | Original CONT-09 | CONT-15 |
| CONT-10-R1 | Recovery of any provider MUST rely on observed account recovery under an authorized bounded probe policy. A recovered provider MUST rejoin the eligible pool for subsequent work only. It MUST NOT displace an active writer or replay completed or canceled work. | Concurrent recovery of two providers admits one current probe per provider. Neither takes over active work. | Original CONT-10; #219 comment "Recovered Kiro rejoins the eligible pool" | CONT-15 |
| CONT-11-R1 | Human cancellation, revoked task authority, a withdrawn registry entry, and a revoked per-task grant MUST stop new dispatch and publication for the affected candidate and task. Provider recovery, queue retries and selector reruns MUST NOT recreate that authority. | Revoking a candidate's entry mid-task blocks its next dispatch and its pending publish. Prior evidence is preserved. | Original CONT-11 | CONT-13 |
| CONT-12-R1 | Reports MUST separate: candidate selection evidence, provider availability, authenticated principal, owner authorization, drafting outcome, test and CI evidence, human approval or merge, and deployed enforcement. A selection result MUST NOT be reported as approval, and a registry entry MUST NOT be reported as capability proof. | A report showing "selected" with no owner grant displays the stage as unauthorized. A selected candidate with no stage evaluation displays "eligibility UNKNOWN". | Original CONT-12; #219 comment "The selector is never an approver" | CONT-13, CONT-14 |

## R1 new requirements

| ID | Exact proposed requirement | Acceptance evidence | Source / rationale | Depends on |
| --- | --- | --- | --- | --- |
| CONT-13 | The process MUST choose a performer for each lifecycle stage G0 to G6 only from an owner-controlled, versioned capability registry. A registry entry MUST be keyed by provider, model identifier or family and version, agent harness, and permitted execution environment. The process MUST NOT designate any single provider, product, model, harness or IDE as the permanent sole eligible performer of any stage or role. Enrolling, retiring, or changing the permitted stages of an entry MUST require Ky's authenticated approval and merge. A selector, a candidate, or any agent MUST NOT change its own entry, its role, its permitted stages, or the admission policy. The selector MUST NOT be an approver. The process MUST NOT create a second authority for agent identity: where the existing AIV registry (`registry/agents.json`) already records an agent, the conflict between its role field and the capability registry MUST be reported, not silently overwritten. WHEN only one candidate is eligible for a stage, the process MUST report `SINGLE_CANDIDATE` for that stage. | (a) Retire one candidate and enroll an unrelated provider by a registry change alone. The same G0 to G6 contract passes with no change to enforcement code. (b) A candidate's attempt to edit its own entry is rejected at the registry publish boundary. (c) A stage with one eligible candidate reports `SINGLE_CANDIDATE`. (d) A registry entry that conflicts with the AIV record is reported as a conflict. | #219 comment 6600237280 "fixed gates, dynamic providers"; AIV spec (agent identity, `approver != requester`) | CONT-01 |
| CONT-14 | A candidate MUST be eligible for a stage only on reproducible, stage-specific evaluation evidence for that exact provider, model, harness and environment combination. The evidence MUST record run ID, input SHA, fixtures, outcomes, and capacity observed. It MUST include positive fixtures and counterexample fixtures. Provider or product names, marketing labels, public leaderboard rank, and self-reported model identity MUST NOT establish eligibility or ranking. Eligibility MUST be decided on quality and security thresholds first. Cost and latency MAY choose among candidates that are already eligible. The thresholds are UNKNOWN until Ky adopts them. While a stage has no adopted threshold, the process MUST treat no candidate as automatically eligible for that stage and MUST route the choice to Ky. | (a) A candidate with a high public rank that fails the stage's counterexample fixture is rejected. (b) A lower-ranked candidate that passes is eligible. (c) A stage with no adopted threshold selects no candidate automatically and reports `THRESHOLD_UNSET`. (d) An evaluation record missing run ID or input SHA is rejected. | #219 comment "Objective selection, not a marketing 'best' label"; owner rule "task-specific evidence, not names or leaderboards" | CONT-13 |
| CONT-15 | For each stage G0 to G6 the process MUST apply an ordered fallback: first the next eligible registry candidate holding current stage authority, then read-only or draft-only output outside protected paths where the stage allows it, then a HOLD that names the reason. WHEN a provider is exhausted or unavailable, the process MUST reassign only the remaining work of the original issue and revision, preserving accepted artifact hashes and human decisions. WHEN no qualifying candidate or required authority exists, the process MUST report `BLOCKED` or `UNKNOWN` under the same canonical issue and MUST NOT let any actor assume another actor's identity or role. Owner decisions (stage approval, merge, deployment, spend) MUST NOT fall back to an AI. At G6 the reviewer MUST be a distinct authenticated principal from the coder of the same task. | The matrix in `design.md` (R1) is exercised row by row: Kiro exhausted at G2 yields an alternate spec-only contribution that stops for owner approval. No qualifying G6 reviewer yields HOLD. A coder asked to "temporarily act as Kiro" is refused at the dispatch boundary. | #219 comment "Failover at EVERY phase"; #238 comment 6844321931 item 3 | CONT-13, CONT-14 |

## R1 unresolved facts

These stay UNKNOWN. Nothing below is filled in by inference.

| Fact | Current evidence | Required before use |
| --- | --- | --- |
| Stage evaluation thresholds | None adopted | Numbers adopted by Ky per stage |
| Retry bounds, probe bounds, freshness window | None adopted (as in the original packet) | Exact values reviewed by Ky |
| Initial candidate list and who may enroll | None enrolled | Ky's enrollment, one candidate at a time, by merged registry change |
| Registry home | The AIV registry exists; no decision to extend it | Ky's decision. Extending AIV is the proposed default so identity has one authority |
| Reopening #219 | Issue is CLOSED; the owner comment names it canonical | Ky's decision. R1 creates no issue |
| Owner-only authorization channel | iPhone signer proposed, not implemented (B1) | Observed independent owner-only signing and trusted verification (see ESE spec) |
| Which spec-author identities `roles.yml` recognizes | Kiro and KyPython | Ky's separate exact request (ESE T10). R1 edits no protected file |

## R1 traceability

| Requirement | Scenarios in `scenarios.md` | Tasks |
| --- | --- | --- |
| CONT-02-R1 | S1, A6 | T8, T10 |
| CONT-05-R1 | S1, A2, A5, A16 | T8, T10 |
| CONT-06-R1 | A8 | T8, T11 |
| CONT-08-R1 | A9 | T8, T10 |
| CONT-09-R1 | A10 | T8, T10 |
| CONT-10-R1 | S3 | T8, T10 |
| CONT-11-R1 | A7, A15 | T8, T10 |
| CONT-12-R1 | A11 | T8, T10 |
| CONT-13 | S1, S2, A1, A4 | T8, T9, T12 |
| CONT-14 | S1, A3, A12, A16 | T8, T11 |
| CONT-15 | S1, S3, A2, A11, A13, A14, A15 | T8, T10 |

## R1 review state

All R1 requirements are proposed. Their runtime acceptance tests are NOT RUN. Ky adopts R1 only by reviewing and merging this spec-only PR. No agent dispatch, role edit, new bot identity, issue, Worker mutation, paid call or approval receipt is made or authorized by this amendment.
