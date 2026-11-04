# Kiro monthly-credit exhaustion: cloud and local continuity runbook

**Status:** Proposed, agent-drafted operating guidance for human review, 2026-10-14. **Not yet merged or activated.** Governing decision: [#219](https://github.com/KyPython/ai-governance/issues/219). Existing cloud relay correction: [#11](https://github.com/KyPython/ai-governance/issues/11). Original Kiro-only spec dispatch remains authoritative until an explicit approved change.

## Why this exists

Kiro Pro usage can exhaust before its next monthly billing reset. This is a **provider capacity failure**, not permission to bypass the spec gate, spend more, dispatch a coder or use the owner's token as if an agent were the human owner.

**Invariant:** `approved goal + relevant evidence → requirements → design → tasks → human spec approval/merge → one authorized coding task → different independent reviewer → required CI/verdict → human merge`. All branches, CI, secret-handling, author roles and human agency restrictions still apply. A non-Kiro model may make a draft, but may not create the impression it was authored by Kiro or personally implemented by Ky.

## 0. Roles and feasibility

| Operation | Kiro available | Kiro exhausted | Authority |
| --- | --- | --- | --- |
| Issue intake/source audit | Existing Kiro intake | Same issue; write **draft-only** evidence | Human-selected scope |
| Requirements/design/tasks draft | Kiro spec-only | ChatGPT/other authorized model, clearly marked AI draft, or human | Read-only draft, not merge approval |
| Spec-only PR | Kiro under existing `spec-author` role | **Ky owner override after substantive personal review**, or HOLD | `roles.yml` currently lists Kiro bot and KyPython only |
| Implementation | Only after actual spec merge + authorization | **Exactly the same rule** | One designated coder; one task per PR |
| Independent review/CI | Required | Required | Same gates, no agent self-approval |
| Merge/deploy | Human only | Human only | Never delegated or inferred |
| Payment | Existing plan | $0 automatic incremental spending | No tier change/add-on by fallback |

**Do not add Codex/Cursor as spec-author in-place.** A future provider-independent identity would require an explicit **owner-reviewed** central-role/validator change, unique authenticated bot identity, tests for coder/spec collisions and source-provenance receipts. `roles.yml` currently treats a generic agent pushing with the owner's PAT as owner, so account-level audit receipts must not be equated with proof of human authorship.

## 1. Manual state transitions (source-of-truth: original GitHub issue)

1. `KIRO_READY`: quota and session availability actually verified; existing Kiro-first routing (if independently verified running) is used.
2. `KIRO_EXHAUSTED`: a user-observed credible exhausted/limit message is recorded with source, timestamp, affected account and next billing reset. A session-limit error may not be a credit error: label `KIRO_BLOCKED_UNKNOWN` when ambiguous.
3. `SPEC_DRAFT_ONLY`: Kiro unavailable, so other assistants may **inspect** verified source and prepare marked draft requirements/design/tasks without committing into protected `specs/` or contacting upstream. Pin original issue URL and current source branch/SHA; report UNKNOWN where unavailable.
4. `HUMAN_SPEC_REVIEW`: Ky compares draft claims to sources, resolves external/maintainer contract questions, approves exact files, verifies approved PR author/provenance, checks role constraints and CI. If any gate fails, HOLD.
5. `SPEC_MERGED`: only after verifiable GitHub merge by Ky; use existing opted-in spec-merge handoff if it is **actually deployed and tested**. Avoid pretending a proposed #5 workflow is in production.
6. `CODER_AUTHORIZED`: separately authorized bounded task can go to one coder with one independent reviewer. Source and change-scope gates remain.
7. `KIRO_RECOVERED`: re-query Kiro quota and current GitHub issue/spec/PR status; compare SHA and issue IDs; never replay completed work, duplicate PRs or relaunch old tasks. Historical human-approved specs remain valid unless a new source delta requires revision.

Never use a time-based reset alone as proof an individual session/credit allotment works. Monthly Kiro credits renew at the billing cycle; the owner's screenshot says first of each month 00:00 UTC. Verify in the account and a normal read-only request before reenabling.

## 2. Cloud procedure: manual fallback, without changing the live Worker

- **Entry point:** the existing GitHub intake issue. Add one evidence section or a linked private Notion record with the source URL, exact HEAD SHA, scope authorization, Kiro outage receipt, `SPEC_DRAFT_ONLY` and assignee **human**. Do not create a second GitHub issue for the same task.
- **Drafting:** run the prompt below in a **separate already-authorized provider** using only permitted nonsecret source information. Request three artifacts in this order: `requirements.draft.md`, `design.draft.md`, `tasks.draft.md`. Their headers must include `AI DRAFT — not reviewed/approved`, model/provider, issue link, source commit, and uncertainty/approval gates. Never paste tokens, private client data, medical records, unreleased code without permission.
- **Publication:** paste or attach the draft to the **existing intake** or a private staging document; never send `/kiro` again just to cause activity. If output includes source code/test run claims, mark as **unverified** unless real execution artifacts exist.
- **Conversion to governed spec:** after Ky's substantive review, the owner chooses whether to author/submit the approved documents through his `roles.yml` owner override. If a ChatGPT agent publishes a commit using Ky's token, attribute it to the assistant in PR body and **never claim** the GitHub login proves independent Ky authoring. A protected spec-only PR/CI verdict is still required. If owner has not approved, HOLD.
- **Cloudflare/Telegram:** relay source currently lives on Grok's host and deployed Worker `kiro-telegram-relay`. **No failover switch has been deployed.** `/build` still dispatches Kiro; tell the owner to use the manual draft channel instead while exhausted. Any future source-controlled Worker change belongs to a distinct approved spec/code PR, not an ad-hoc runtime flip. Do not access, export or duplicate Telegram/GitHub secrets.

## 3. Local Mac procedure: offline Kiro-independent packet

1. Check out the target source at a known SHA and **do not let a generative tool alter the checked-out repo in draft mode**. Use a separate writable draft directory outside the repo (e.g. `~/Documents/engineering-spec-drafts/<task-slug>/`; user chooses).
2. Use the portable `spec-failover.py` scaffold distributed as a separate offline download from this conversation. It is **not installed on the user's Mac by the assistant**. Standard-library only; creates a metadata JSON and three draft Markdown files in the chosen output directory; no authentication, network, or Git writes. Review the script before running.
3. Populate drafts with an existing local assistant or manually, always noting agent vs human contributions. If provider is unavailable or would incur an unapproved charge, stop and work manually.
4. Run its read-only `verify` command for basic draft completeness, metadata consistency and required sections. This is **not** a replacement for repository validators, independently run tests, exact CI, role proof, or human approval.
5. Put the results back in the **same issue ID** and source SHA as the cloud packet. Copy artifacts by explicit human action; do not configure automatic bidirectional push/sync or upload secrets.
6. When Kiro returns, compare against current `main`/target source before resuming. Preserve prior draft revisions and no-op on duplicate work.

### Offline commands (after extracting portable kit)

```bash
python3 spec-failover.py init \
  --issue-url https://github.com/KyPython/ai-governance/issues/218 \
  --repo hotosm/field-tm \
  --source-sha <the-40-character-SHA-you-verified> \
  --slug hot-field-tm-3129 \
  --out "$HOME/Documents/engineering-spec-drafts"
python3 spec-failover.py verify \
  --dir "$HOME/Documents/engineering-spec-drafts/hot-field-tm-3129"
```

The source SHA placeholder is **intentional**: confirm a fresh SHA at the time of operation, rather than reusing the Oct 14 snapshot.

## 4. Portable prompt for the alternate spec drafter

> You are a temporary **SPEC DRAFTER ONLY**, not Kiro, not the coding implementer or approver. Read the exact issue URL and the target repository at the pinned SHA, the CONTRIBUTING/AGENTS rules, existing tests, and any relevant maintainer decisions. If inaccessible, state UNKNOWN rather than inventing facts. Prepare `requirements.draft.md`, `design.draft.md`, and `tasks.draft.md` with uniquely numbered MUST/MUST NOT acceptance requirements, alternatives/tradeoffs, requirement-to-test traceability, observed vs inferred vs blocked decisions, minimal test-first tasks, rollback and stop conditions. Never write production code, execute destructive commands, modify repo policies, claim tests passed without receipts, trigger a coder, contact maintainers, auto-merge, or deploy. Label every document **AI DRAFT — NOT HUMAN APPROVED**; record provider and exact source SHA. Include an outstanding human-owned decision list. STOP rather than calling the draft an authorized specification.

## 5. Capacity, budget and continuity policy

- Existing $20 Pro remains baseline. Zero automatic paid fallback; no new token/API bill, Kiro upgrade, add-on credit or premium Codex session until separately funded.
- On verified usage data, pre-allocate a reserve of **25% of Kiro plan credits** for rework/review and limit low-priority dispatch. This is a **proposed policy**, not a claim that a telemetry alert or rate limiter is installed. A real Kiro usage webhook/API has not been verified.
- If credits are exhausted, do not spam `/kiro` or manually restart several competing sessions. Mark each issue once, move to draft-only, and preserve its already-existing spec/PR state.
- Count completed human-approved specs, merged code/test/acceptance evidence and upstream outcomes—not agent task acknowledgments, available credits or draft count.
- Temporary outage does not justify violating HOT's no-AI-account/DCO rules, an upstream maintainer's ownership, or the user's protected noncommercial code boundaries.

## 6. Acceptance matrix and rollback

| Case | Expected |
| --- | --- |
| Kiro quota ready | existing dispatch unchanged |
| Quota exhausted | same intake ID, no new Kiro/coder messages, draft-only work allowed |
| Cloud tool blocked | retain issue and offline packet; no silent substitute premium spend |
| Local offline | generate/inspect draft without network or writing target source |
| Spec reviewer absent | no protected spec PR/merge or implementation |
| Wrong bot/agent identity | fail the governance role gate, never impersonate `kiro-agent[bot]` |
| Maintainer input missing | explicit blocked requirement, no invented design decision |
| Kiro resets while draft active | compare issue/source/PR SHA, skip duplicates; recover normal Kiro on a deliberate owner decision |
| CI failure or nonmatching evidence | HOLD, no merge/deploy |
| Relay workaround compromised | do not deploy; restore original reviewed Worker/route by human-controlled change |

**Verification state at authoring:** official Kiro billing/docs read; main repo roles and #11 reviewed; GitHub/Notion fallback intake to be checked against exact issues. No actual Mac install, cloud Worker change, validator run, full payment audit or resumed Kiro session is claimed by this document.

References: [governance #219](https://github.com/KyPython/ai-governance/issues/219) · [relay repair #11](https://github.com/KyPython/ai-governance/issues/11) · [spec handoff #5](https://github.com/KyPython/ai-governance/issues/5) · [Kiro Billing](https://kiro.dev/docs/billing/) · [Kiro add-on credits](https://kiro.dev/docs/billing/add-on-credits/).
