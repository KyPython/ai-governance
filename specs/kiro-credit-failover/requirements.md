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
