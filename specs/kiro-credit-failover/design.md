<!-- CODEX-AUTHORED SPEC PROPOSAL — HUMAN ADOPTION/MERGE PENDING. RUNTIME ACCEPTANCE NOT RUN.
Publication through KyPython owner override explicitly authorized by Ky in this conversation.
Issue: https://github.com/KyPython/ai-governance/issues/219
Source: KyPython/ai-governance@efd0e11dde73a70d4867293e4ac2308d28be057e
Additional source: draft PR #220 at 06e4442f8074c2b04e77edb3004d21ce3be855b6
Provider/author: OpenAI Codex agent in this conversation; exact underlying model ID not exposed.
Human contribution: selected goal and explicit fallback-author approval; document prose drafted by Codex.
-->

# Design — one process, bounded provider continuity

Status: proposed; supports the same issue #219/runbook #220. No production implementation, role change or cloud activation is part of this draft.

## Immediate path using existing tools

Use the already extracted offline kit to prepare an external packet with the original issue and independently verified source commit. Codex drafts the three artifacts in a separate session with actual author attribution. The human reviews exact files, then personally selects an authorized publishing path and merges a spec-only PR after required CI. Existing code/review/merge rules follow unchanged. This path needs no new App, paid API, scheduler or role-map edit. The current packet demonstrates only scaffolding and drafting.

Local and cloud drafting use the same explicit packet, not an assumption that hidden session memory is portable. Source snapshots and accepted artifact hashes are verified before continuation; every new revision is retained. Approved requirements are immutable inputs until the human approves an actual change.

## Proposed later local adapter

Extend the existing continuity mechanism only after exact-spec review/merge and a bounded implementation task. A launcher supplies vetted source evidence to Codex and captures returned artifacts in private staging. Start with draft-only capabilities: no Git write credential, no outbound messaging tool and no repository mutation path. Run provider commands through argument arrays/stdin rather than shell interpolation. Recheck current task authority and cancellation before dispatch and accepting returned drafts. Validate output and durably retain each attempt, error and uncertain effect before considering the draft produced; reconcile consequential outcomes before retry.

The installed CLI has `exec`, stdin input, JSON events, read-only sandbox mode, output file/schema, ephemeral mode and an option to ignore user configuration while retaining account authentication. These are useful adapter primitives, not proof of containment: the current account configuration includes connectors/plugins, and inherited credentials, hooks and tools require explicit capability review. A read-only filesystem sandbox alone does not prove absence of network effects. Do not use a bypass flag, remove repository instructions or assume cloud inherits local flags. The host adapter can write the returned draft outside Git; generated shell commands have no authorized side-effect channel.

Do not bind a new model identifier, numerical retry/probe cap or API credential merely to make an adapter run. Existing subscription auth and actual capacity are separate observations. Each missing required deployment value leaves that path held.

## State and durable evidence

Provider capacity and task lifecycle are separate records. Provider states are READY, UNAVAILABLE_CONFIRMED, UNKNOWN and RECOVERY_PENDING. Task states are QUEUED, DRAFTING, DRAFT_READY, HUMAN_REVIEW, SPEC_MERGED, CODER_AUTHORIZED, HELD_UNKNOWN_EFFECT and CANCELED. These proposed state names do not claim existing deployed enums. A draft can be ready while its spec remains unapproved; a recovered provider does not complete or reopen a task.

A handoff envelope carries the existing issue/task identity; target/revision; human scope evidence; accepted spec/artifact hashes; verified completed steps; remaining steps; provider/author/attempt; capacity cause and evidence provenance; pending effects; cancellation; and test/review receipts. Secrets are references to existing approved stores, never packet values. Metadata fields are descriptive evidence, not self-authenticating approval.

For automation, use one shared durable owner record with an atomic compare-and-claim operation and a monotonic fencing token. Every write or publication boundary checks that token and current task authority. A process-local lock, expiring lease without write-boundary checks or two independent local/cloud state files is insufficient. If an existing service cannot prove those semantics, retain manual ownership and do not enable parallel automatic dispatch. No storage service has been selected or provisioned.

Crash handling distinguishes checkpoint persisted, owner acquired, provider request issued, effect accepted, and authoritative receipt recorded. Resume only verified remaining work. Reconcile an uncertain consequential effect against authoritative receiver state or durable receiver-enforced idempotency bound to the same action, payload and key before retrying it. A local planned-request record cannot prove an effect or justify retry under a fresh key; an adapter timeout does not prove the receiver did nothing.

## Cloud integration and conditional authorship

Keep the immediate cloud path manual: transfer the same reviewed nonsecret source packet through an already authorized provider environment. A new cloud task is not part of this drafting run. Published environment/configuration, access, provider capacity and permitted capabilities must be independently known. Ordinary CI can continue separately from model availability.

The actual deployed relay from existing repair #11 is now recovered privately and hashes to `c923021ea0617698c874d8acb1061f8f221337c3f8e4c0e4349fcc1c83c58707`. It defaults to `KyPython/effectproof`, authenticates webhook/owner, and creates Kiro-labeled issues with combined spec/build instructions. It has no Codex routing or replay state. Version those recovered bytes through the governed source path before an automatic switch; original Git history and deployed GitHub credential actor/scopes are not recovered. Preserve its owner checks, secret boundaries and stable intake IDs; test untrusted input and duplicate requests against inert adapters. Do not patch a different AWS controller as a shortcut: it has separate signed Kiro admission and isolation requirements that remain authoritative.

Automatic protected-spec publishing, if later desired, needs an observed authenticated actor and a centrally reviewed condition: Codex fallback is eligible only for the approved scope during recorded Kiro unavailability, with the same spec-only and human-review rules. Do not add Codex unconditionally to all spec authors. Git author fields and an agent using Ky's token cannot prove human authorship. Current governance comments do not establish that this conditional policy is enforced at runtime.

The existing HANDOFF proposal concerns code tasks after a merged spec. It is not a deployed draft failover runner; its requirement sentences, triggers and credentials are not changed by this design. Future amendments must be reconciled in its existing intake.

## Exhaustion and recovery

Classify a verified cause rather than HTTP status alone: 429 may mean transient throttling or credit exhaustion. Share capacity pauses across surfaces that use the same account pool. Prompt text or another account's health claim cannot change account state. Unknown account/reset information remains unknown.

Recovery uses trusted account evidence plus a separately approved bounded probe policy. One fenced probe can update shared provider health. A failed/ambiguous probe leaves the provider paused. Confirmed recovery makes Kiro eligible for subsequent work without stealing the active Codex draft or recreating canceled authority. Exact numeric limits and reset dates are intentionally unconfigured.

## Acceptance, rollback and alternatives

Use inert providers, controlled clocks and observable attempted calls, ownership changes, artifact hashes and effects in the existing applicable test infrastructure. Include a legitimate authorized draft/resume, alongside exhaustion, all-providers-unavailable, forged evidence, stale source, changed requirement bytes, concurrent ownership, stale-token writes, uncertain effects, recovery and cancellation controls. Zero unauthorized effects alone is insufficient if legitimate work is always blocked.

If any acceptance invariant fails, stop new automated claims, preserve receipts and uncertain effects, revoke stale ownership, and return to the existing manual draft mode. Never rollback by replaying a possibly completed request or clearing prior evidence. Human owners control any deployed route rollback.

Alternatives: manual kit continuation works now with human transfer and no extra service; a reviewed automatic adapter reduces handoff work but requires actual state/capability enforcement; repeating Kiro dispatch or changing Kiro interfaces cannot solve shared monthly exhaustion. This draft selects the existing manual path now and proposes automation only after its prerequisites.

---

<!-- KIRO-AUTHORED DESIGN AMENDMENT (R1) — HUMAN ADOPTION/MERGE PENDING. RUNTIME ACCEPTANCE NOT RUN.
Issue: https://github.com/KyPython/ai-governance/issues/219 · Source: KyPython/ai-governance@53462a0 · Author: Kiro (spec-author), local session 2026-11-25; model ID not exposed. -->

# Design — Revision R1: fixed gates, dynamic providers

Status: proposed; supports requirements CONT-02-R1 to CONT-15 in `requirements.md`. No production implementation, role change, registry edit or cloud activation is part of this amendment.

## Five separate concepts

Keep these apart in every record and report. A name in one layer never stands in for evidence in another.

| Layer | Meaning | Where it lives |
| --- | --- | --- |
| Stage | G0 intake and BDD discovery, G1 sourced outcomes, G2 requirements/design/tasks and owner spec-only merge, G3 acceptance scenarios, G4 tests-first RED, G5 bounded implementation, G6 independent verification. Fixed. | ESE spec (ESE-1) |
| Capability class | The kind of work: evidence research, BDD discovery, spec design, scenario authoring, test synthesis, coding and debugging, independent verification and security review. | Capability registry |
| Candidate | Provider, model identifier or family and version, harness, permitted environment. A named IDE or agent is an interface, not proof of competence. | Capability registry |
| Authenticated principal | The identity that actually acts, verifiable by the enforcing boundary. Not a Git author, a Ky-token appearance, a free-text model name or an issue comment. | AIV registry and token engine |
| One-time authorization | Ky's grant for exact repo, issue, spec SHA, stage, principal, paths, operations, expiry, revocation and budget. | Owner channel (B1, not yet demonstrated) |

The selector is a deterministic function of the registry, the evaluation evidence, the availability evidence and the grant. It reads those inputs and returns an eligible set. It writes nothing, approves nothing, and cannot change its inputs.

## Proposed constraint: extend one identity authority

The AIV registry (`registry/agents.json`, merged) already records agent identities, per-agent capabilities and public keys, and AIV-2.4 already requires `approver != requester`. The capability registry SHOULD be an extension of that record, keyed so one agent identity has one authority. A second parallel identity store would let the two disagree about who an agent is. Where the AIV `role` field and a capability entry disagree, the validator reports `ROLE_CONFLICT` and rewrites neither (CONT-13).

The AIV pilot pair assigns `antigravity` the role `author` and `kiro` the role `reviewer`. R1 treats that pair as existing data, not as a policy. It does not edit it. Whether the pilot pair stays, is generalized, or is retired is Ky's decision under the AIV spec.

This is a proposed implementation constraint. Where the capability registry lives is UNKNOWN until Ky decides (see "R1 unresolved facts").

## Selection, then authorization

1. Build the candidate set for the stage from enrolled entries (CONT-13).
2. Keep candidates with a current, stage-specific evaluation that meets the adopted thresholds (CONT-14). With no adopted threshold, the set is empty and the result is `THRESHOLD_UNSET`, which routes the choice to Ky.
3. Keep candidates whose provider shows available by trusted evidence, or whose unavailability is unknown but not confirmed. Prompt text and self-reports count for nothing (CONT-02-R1).
4. Among what remains, order by cost and latency only (CONT-14). This order never overrides steps 1 to 3.
5. Report the set, including `SINGLE_CANDIDATE` where it has one member.
6. Ky's grant names one principal for one task and phase. Only the grant authorizes dispatch (CONT-12-R1). Selection alone does not.

If the set is empty, apply the fallback column below.

## Per-stage fallback matrix (CONT-15)

Columns read left to right. "Draft-only" means output outside Git and outside protected paths, labeled as an unapproved draft with actual attribution (CONT-05-R1).

| Stage | Primary | If the primary is unavailable | If no candidate qualifies | Never allowed |
| --- | --- | --- | --- | --- |
| G0 to G1 discovery | Eligible research candidate with a G0 grant | Next eligible candidate; reassign remaining work only | Read-only notes outside protected paths; report `UNKNOWN` | Source or code writes without a grant |
| G2 spec | Eligible spec-writing candidate whose principal the role map recognizes, with an issue-specific delegation | Next eligible candidate with the same recognition and delegation | Draft-only output for Ky to submit through the owner route; report `BLOCKED` for publication | Publishing under `specs/` from an unrecognized principal; a coder spoofing Kiro or Ky; merge |
| G3 scenarios | Eligible scenario-authoring candidate | Next eligible candidate | Draft-only; report `PENDING` | Writing executable tests in the same grant |
| G4 tests, RED | Eligible test-synthesis candidate | Next eligible candidate | HOLD | Production code under the same grant; vacuous or mock-set RED |
| G5 implementation | Eligible coding candidate on allowlisted paths | Next eligible candidate; new claim and new fencing token | HOLD | Editing the accepted spec or tests; self-review |
| G6 verification | Eligible reviewer, a distinct authenticated principal from the coder, preferably a different model family and execution context | Next distinct eligible reviewer | HOLD, or `INDEPENDENCE_LIMITED` recorded with reason and left for Ky to accept | Same principal or same session as reviewer; merge; deploy |
| Owner decisions (approval, merge, deploy, spend) | Ky | None | Wait for Ky | Any AI fallback |

A reassignment carries the original issue, revision, accepted artifact hashes, verified completed artifacts, remaining work, human decisions and attempt evidence (CONT-04). A recovered provider joins the pool for the next task and does not take the current one (CONT-10-R1).

## Evaluating candidates without launching models in this spec

CONT-14 needs stage-specific fixtures. This amendment authorizes no evaluation run, model launch or spend. It defines only what a later, separately authorized task must record:

| Stage | What the fixture must be able to tell apart |
| --- | --- |
| G0 to G1 | Source-backed rules and counterexamples from unsupported claims |
| G2 | EARS form, stable IDs, source fidelity, traceability to tasks |
| G3 | Scenarios that map to requirement IDs and include invalid-authorization cases |
| G4 | Genuine assertion failure from harness, import or collection failure; vacuous assertions |
| G5 | Bounded change on allowed paths; regression rate; no edits to spec or tests |
| G6 | Reproduced changed tests on the exact revision; adversarial and security findings; independence from the coder |

Each fixture has positive cases and counterexample cases. Public coding leaderboards may help someone shortlist candidates to evaluate. They do not count as a stage result.

## Interaction with other specs and records

- **ESE spec (#238).** Stage gates, receipts and the owner-only channel stay in ESE. R1 adds no approval semantics. The reviewer-independence, assignment-recording and principal-binding requirements are in the companion ESE amendment. This spec's CONT-15 at G6 states only the minimum (a distinct authenticated principal) so it stands alone until the ESE amendment is adopted.
- **AIV spec.** Token issue, TTL and revocation stay in AIV. R1 reads them and does not redefine them.
- **ROLES and `roles.yml`.** R1 edits neither. Role-map wording that names one spec author is a protected change that needs Ky's separate exact request. The proposed wording is prepared as text for that request and is not applied.
- **Relay #11.** The deployed relay is Kiro-only (original design, "Cloud integration and conditional authorship"). R1 does not change it and does not start a second router. An adapter over eligible providers waits for the relay source to be versioned and its owner verified.
- **#229 coordination hub.** A separate open intake about cloud-resource state. R1 neither depends on it nor implements any part of it.

## Failure modes and rollback

| Failure | Behavior |
| --- | --- |
| Registry missing, malformed or unreadable | Fail closed. No candidate is eligible. Report `UNKNOWN`. Manual owner route stays available. |
| Evaluation evidence stale, absent, or missing run ID or input SHA | The candidate is ineligible for that stage. |
| Registry and AIV record disagree | Report `ROLE_CONFLICT`. Do not dispatch the affected agent until Ky resolves it. |
| Selector and grant disagree | The grant wins for authorization. The selector result never expands it. |
| Reassignment races with a late writer | The claim store's fencing token rejects the late write (CONT-08-R1). |
| An always-deny implementation | Fails the positive controls S1 and S2. Zero unauthorized effects alone is not acceptance. |

Rollback for any later implementation: stop new automated claims, revoke stale owners, preserve receipts and uncertain effects, and return to the existing manual draft mode. Never roll back by replaying a possibly completed request or clearing evidence. Reverting the spec itself is Ky's revert of the merge.

## Alternatives considered

| Option | What it gives | Why not chosen as the default |
| --- | --- | --- |
| Static ordered list, for example Kiro, then Codex, then others | Simple, predictable | Recreates a permanent vendor ordering under a new name. Fails when the listed candidate is wrong for a stage, and nothing records why it is eligible. |
| Ky picks a performer by hand every time | Works today. No new mechanism. Keeps the owner decision explicit. | Does not scale across stages and tasks. It stays the default wherever thresholds are unset (CONT-14). |
| Capability-qualified selection with stage evidence (R1) | Per-task choice backed by evidence. Replacement needs no enforcement-code change. | Needs a registry, evaluation fixtures and adopted thresholds. Until those exist it behaves like the manual option. |
| A leaderboard-ranked choice | Cheap | A coding leaderboard does not measure scenario writing, false-RED rate or independent verification. Excluded by CONT-14. |

R1 selects the third option and keeps the second as the working default until its prerequisites exist.

## Observations that conflict, kept as found

The 2026-11-12 report says Kiro was out of credits. A Kiro session responded on 2026-11-25. This design relies on neither: the continuity contract works whether Kiro is available or not, and CONT-02-R1 keeps an unverified availability claim from moving routing state.
