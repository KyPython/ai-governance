<!-- CODEX-AUTHORED SPEC PROPOSAL — HUMAN ADOPTION/MERGE PENDING. RUNTIME ACCEPTANCE NOT RUN.
Publication through KyPython owner override explicitly authorized by Ky in this conversation.
Issue: https://github.com/KyPython/ai-governance/issues/219
Source: KyPython/ai-governance@efd0e11dde73a70d4867293e4ac2308d28be057e
Additional source: draft PR #220 at 06e4442f8074c2b04e77edb3004d21ce3be855b6
Provider/author: OpenAI Codex agent in this conversation; exact underlying model ID not exposed.
Human contribution: selected goal and explicit fallback-author approval; document prose drafted by Codex.
-->

# Tasks — review first, implementation later

Status: proposed; no coder has been dispatched. These tasks support existing issue #219 and do not close #219, change PR #220's runbook-only scope or trigger existing Kiro issues.

## Completed drafting evidence

- [x] Verify canonical main SHA against the inspected checkout: `efd0e11dde73a70d4867293e4ac2308d28be057e`.
- [x] Read current role/agent rules, existing issue #219 and draft PR #220.
- [x] Preserve the supplied kit; four existing tests passed and extracted bytes match the archive.
- [x] Use the existing kit to scaffold this external packet for #219; untouched template verification blocked as expected.
- [x] Record the user's Codex fallback-author decision; draft requirements/design/tasks with truthful author attribution.
- [x] Recover actual deployed relay source/settings using existing Cloudflare authentication and GET-only reads; preserve a private source backup. No Worker code changed.

These checks do not establish provider capacity, runtime failover, human spec approval, CI for a new implementation or cloud cutover.

## Ordered work requiring human review/admission

| Task | Scope and prerequisite | Requirement IDs | Acceptance evidence / state |
| --- | --- | --- | --- |
| T1 | Human reviews exact requirement/design/task bytes and adopts or changes them. Resolve only the deployment facts needed for the next chosen phase. | CONT-01–12 | Exact-file decision receipt; PENDING HUMAN REVIEW. |
| T2 | Publish through the now-authorized KyPython owner override with Codex authorship disclosed; run actual required CI and wait for Ky review/merge before implementation. Preserve #220 runbook and accepted accessibility sentences. | CONT-01,04,05,12 | Spec-only publication authorized; exact submission/CI evidence tracked by this PR; human review/merge PENDING. |
| T3 | After T2 and separate bounded code admission, implement the minimum local draft adapter in the approved existing location with inert-provider tests before any model dispatch. Recheck cancellation/current authority before dispatch and draft admission; durably retain attempts and reconcile uncertain consequential effects before retry. | CONT-02–07,09,11,12 | Eligible draft succeeds; missing auth/extra billing/protected effects fail; no source mutation. Revocation blocks continuation, crashes preserve receipts and uncertain effects stay held. Coder/reviewer/location UNASSIGNED. |
| T4 | Before automatic local/cloud handoff, integrate an approved existing durable owner/capacity store and enforce current fencing/authority at write boundaries. | CONT-03,04,07–11 | Concurrent claims, stale tokens, crash boundaries, unknown effects and revocation controls pass. Store/configuration UNSET; NOT IMPLEMENTED. |
| T5 | Version the now-recovered actual relay #11 source, verify its owners/credential boundaries and select the authorized draft environment. Propose a narrowly conditional author-policy change only if protected-spec automation is required. | CONT-01,02,05–08,11 | Source/configuration/actor evidence and independent policy tests; DEPLOYED SOURCE RECOVERED; VERSIONED SOURCE/ADMISSION PENDING. |
| T6 | After T4/T5 and exact cloud implementation admission, test the existing relay integration with inert transports, stable issue IDs, duplicate requests and controlled quota/recovery events. | CONT-02–12 | One owner, zero unauthorized/duplicate effects, successful eligible resume and truthful receipts; NOT IMPLEMENTED/NOT RUN. |
| T7 | Human reviews all required evidence and separately approves any live rollout; perform only that authorized bounded verification and preserve rollback receipts. | CONT-01–12 | Local and cloud readiness reported separately; NOT AUTHORIZED/NOT DEPLOYED. |

T3–T6 are candidate implementation tasks, not automatic issue creation or coder labels. Each admitted implementation uses one task/PR and a different reviewer. Tasks with unresolved source, budget, authority or runtime admission stay held; manual drafting remains available.

## Required future behavioral vectors

| Vector | Expected observed result | Requirements |
| --- | --- | --- |
| Eligible Kiro-ready task | Existing authorized path succeeds with its original gates. | 01,06,12 |
| Approved Codex outage continuation | Same issue/revision and immutable accepted inputs; actual Codex draft succeeds. | 02,04–06 |
| Exhaustion vs throttle/session limit | Correct evidence-based classification; no exhaustion retry storm or interface escape. | 02,03 |
| Forged/wrong-account/unknown capacity | No unauthorized provider switch; clear hold or authorized manual drafting. | 02,03,07 |
| No fallback or additional API cost | Work queued, zero new purchases/unauthorized calls. | 06,07,12 |
| Tampered source/spec/artifact | Detect drift before publication; preserve prior verified work. | 04,05 |
| Unapproved spec or self-attested approval | Zero implementation dispatch/publication. | 01,05,12 |
| Concurrent local/cloud claims and late worker | One current owner; stale publications rejected. | 08 |
| Crash or timeout after possible effect | Authoritative reconciliation before retry; unresolved stays held. | 09 |
| Unknown reset, competing or failed probe | No guessed recovery/polling storm; at most one current probe. | 03,10 |
| Recovery during active fallback | Preserve owner and finished work; no duplicate task/PR. | 04,08,10 |
| Human cancellation/revocation | No subsequent dispatch or publication. | 11 |
| Exit zero/queue drained/structure PASS | Do not call incomplete task or unapproved spec complete. | 12 |

Negative controls: an always-blocking adapter fails the eligible positive case; deliberate exhaustion retries, stale writes, uncertain-effect redispatch, altered spec hashes, billed substitutions and fabricated completion each fail their relevant oracle. All these runtime vectors are NOT RUN.

## Stop and rollback conditions

Stop affected work on missing scope/source identity, revoked authority, unapproved spend, unknown effects, invalid ownership or failed required checks. Preserve artifacts and attempts. Revert to manual neutral drafts without changing gates, erasing evidence, launching duplicate work, touching upstream HOT projects or modifying the adopted accessibility requirements. Only human-reviewed deployment changes can restore a cloud route.
