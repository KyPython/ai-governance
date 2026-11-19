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
