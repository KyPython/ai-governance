# Design: Venture validation automation

Spec ID: VVA

## Overview

This design describes a conditional, source-grounded orchestration contract that carries a human-recorded problem through research, five-question fact-checking, a Kiro spec-only issue, Ky's merge, an eligible-coder build under the Venture Firewall, and finally measured distribution and sales-validation learning (VVA-4). It is built around the EXISTING Make research owner and the EXISTING biweekly trigger; it introduces no new scheduled researcher and no new Notion tracker (VVA-9.3). The contract fails closed (VVA-6), preserves evidence states and conflicts (VVA-1), and keeps every consequential decision with Ky (VVA-10, VVA-11).

Evidence-state discipline runs throughout: every recorded value carries one of VERIFIED CURRENT OBSERVATION, VERIFIED GOVERNING RULE, HISTORICAL EVIDENCE, INFERENCE, or UNKNOWN (VVA-1.3), and the two current candidates (A indie-game release-readiness, B creative provenance/approval) stay RESEARCH ONLY because neither has passed buyer willingness-to-pay (VVA-7.4, VVA-7.5).

Any test files or paths named in this document are INTENDED. They are NOT created by this spec PR; coders create them in a later PR after Ky merges (VVA-5.1).

## Architecture / components

- **Make orchestrator role, existing scenarios only.** The existing Venture Radar scenario is the SOLE research owner; its October 10 corrected run is the authoritative RESEARCH-ONLY diagnosis of candidates A and B. The READ-ONLY biweekly trigger (1209600-second interval, next execution October 24, 2026; its last wrapper execution returned `RESEARCH_ONLY`, `external_effects_authorized:false`) remains the only scheduled entry point. The design adds NO new scheduled idea researcher and NO new Notion tracker (VVA-9.3). The two ODIN-ONLY Make scenarios (the Kiro scenario and the Codex scenario) are out of this pipeline and are neither pointed at venture candidates nor changed (VVA-9.3).
- **Admission and fingerprinting.** A human-recorded, human-origin problem enters with a stable fingerprint (one per problem/workflow) and immutable checkpoint/revision hashes; imagined or unknown-origin inputs HOLD (VVA-1.1, VVA-9.1). Admission dedupes against existing issues, PRs, and Notion records before anything advances (VVA-4.2, VVA-9.4).
- **Five-question verifier.** The existing fail-closed verifier inside the sole research owner answers and fact-checks the five questions and applies the three-independent-evidence-TYPES rule for venture work and the Love/Distribution/Math/Build-for-self/Sequencing rules for creative work (VVA-2). It rejects unsupported AI PASS deterministically (VVA-3) and resolves gaps to RESEARCH or HOLD, never PASS (VVA-2.3, VVA-6.3).
- **Verified-source boundaries.** Reads come from the named Notion sources (Idea Mining & Validation Prompts, Creative Industries Idea Mining, Venture & Consulting Research/Validation Firewall, Venture/B2B SaaS Runtime, Life Blueprint, Human Agency doctrine) and the corrected run. A signed real buyer response or payment counts only with attributable source, date, and verification receipt, never from generic web research, and is never manufactured (VVA-2.5). Market size and vendor pricing/marketing pages are not WTP (VVA-2.2).
- **Kiro-to-Codex/Cursor handoff, reconciled with spec-merge-handoff (HANDOFF).** On DEMAND-READY, the pipeline emits exactly one source-linked Kiro spec-only issue scoped to the admitted question (VVA-4.2); Kiro writes the three spec files as a spec-only PR (VVA-5.1). This design does NOT re-implement issue-per-task fan-out: the existing `spec-merge-handoff` spec already turns a merged spec's `tasks.md` into one issue per task and routes `codex` work. This pipeline hands off TO that mechanism and MUST NOT duplicate it; its responsibility ends at producing the merged-ready spec-only PR and (post-merge) honoring the one-coder/one-different-reviewer assignment per task (VVA-5.3). It also stays distinct from the two ODIN-only scenarios, which must not be retargeted.
- **Venture Firewall build stage.** After Ky merges and a trusted task/action-bound permission is intact, an eligible coder (codex, cursor/cursoragent/cursor[bot], claude, copilot/copilot-swe-agent[bot], grok-bot, or Kiro's builder per `roles.yml`) may build a disposable validation MVP only under zero-production infra, fake/safe data, no auth/payment/paid hosting, and one falsifiable buyer question (VVA-4.4). Codex/Cursor do nothing until Ky merges (VVA-5.2); the gate `pnpm ai:mutation:check` is run and a DENY stops work and is reported, never edited (VVA-5.5).
- **Distribution/sales-validation DRAFT stage.** Produces only drafts (ICP/competitor comparison, test plan, positioning, landing-page and mock sales-copy drafts, safe UTM/analytics instrumentation, service-vs-software comparison, exact opt-in/outreach proposal) with no automatic contact, ad buy, public post, claim, or pricing commitment (VVA-7). The creator publishing workflow stays OFF and the frozen voice stays on HOLD (VVA-7.3).
- **Non-owned connectors.** Make, Notion, Kiro, Codex, Cursor, and analytics are non-owned connectors; their availability and correctness are UNKNOWN at authoring time, so every unreachable/unsupported case fails closed to HOLD (VVA-6.1, VVA-6.2).

## Data and interfaces

- **Candidate record.** `{fingerprint, human_origin, problem_statement, state, evidence_items[], question_packet, dedupe_keys[], permission_ref, revision_hash}`. Each `evidence_item` carries `{claim, evidence_state, source, date, receipt}` where `evidence_state` is one of the five labels (VVA-1.3). Values without first-party evidence are UNKNOWN (VVA-1.2).
- **State field.** One of HUMAN-RECORDED PROBLEM, RESEARCH, QUESTION-PACKET FACT CHECK, HOLD, REJECT, RESEARCH (research-only loop), DEMAND-READY (VVA-4.1).
- **Question packet.** The five answered/fact-checked questions plus the three-evidence-TYPES matrix for venture or the creative-rules matrix (VVA-2.1, VVA-2.4).
- **Spec-only issue payload.** Source links, the exact admitted validation question, and dedupe references to existing issues/PRs/Notion (VVA-4.2). Held-candidate drafts are labeled non-production / not build-authorized (VVA-4.3).
- **Permission reference.** A task/action-bound signed permission with its exact scope; the standing-delegation path (VVA-11) reads this and verifies scope and freshness before skipping a second prompt.
- **Idempotence keys.** Fingerprint plus immutable checkpoint/revision hash; fresh read before write, read-back after, no blind retry (VVA-9.1).

## Error handling and failure modes

- **Service unavailable (Kiro/Make/Codex).** HOLD; never a fake spec, simulated build, or bypassed condition (VVA-6.1, acceptance case D).
- **Source conflict / stale prompt / partial pagination / unsupported transport / failed independent test / unknown side effect.** HOLD; conflicts preserved with the higher-authority source named, not smoothed (VVA-6.2, VVA-1.4).
- **Unevaluable hard gate.** Default to HOLD or RESEARCH, never PASS (VVA-6.3).
- **Unsupported AI PASS (single source, missing buyer, marketing-page cite).** Deterministic reject to RESEARCH/HOLD (VVA-3.2, acceptance case C).
- **Reread of the same signal.** No duplicate issue/outreach/build; Odin, story production, and W-2 work untouched (VVA-9.2, acceptance case E).
- **Unmet rights/canon/career/finance gate.** No publish, mutation, external send, or spend (VVA-10.1, acceptance case F).
- **Repository DENY.** Stop codebase work, report DENY, never edit the gate (VVA-5.5).
- **Scope drift or stale/absent permission.** Stop and require fresh explicit authorization (VVA-11.3).

## Testing strategy (criterion ID -> test file)

Intended automated tests, run by this repo's quality job, each citing the requirement ID it verifies. The files below are INTENDED and are NOT created by this spec PR.

| Criterion | Test |
| --- | --- |
| VVA-1.1 | `tests/test_vva_admission.py` |
| VVA-1.2 | `tests/test_vva_admission.py` |
| VVA-1.3 | `tests/test_vva_evidence_state.py` |
| VVA-1.4 | `tests/test_vva_evidence_state.py` |
| VVA-2.1 | `tests/test_vva_five_questions.py` |
| VVA-2.2 | `tests/test_vva_five_questions.py` |
| VVA-2.3 | `tests/test_vva_five_questions.py` |
| VVA-2.4 | `tests/test_vva_evidence_types.py` |
| VVA-2.5 | `tests/test_vva_buyer_receipt.py` |
| VVA-3.1 | `tests/test_vva_ai_pass_reject.py` |
| VVA-3.2 | `tests/test_vva_ai_pass_reject.py` |
| VVA-3.3 | `tests/test_vva_ai_pass_reject.py` |
| VVA-4.1 | `tests/test_vva_states.py` |
| VVA-4.2 | `tests/test_vva_spec_emission.py` |
| VVA-4.3 | `tests/test_vva_spec_emission.py` |
| VVA-4.4 | `tests/test_vva_firewall.py` |
| VVA-4.5 | `tests/test_vva_states.py` |
| VVA-5.1 | `tests/test_vva_spec_emission.py` |
| VVA-5.2 | `tests/test_vva_handoff.py` |
| VVA-5.3 | `tests/test_vva_handoff.py` |
| VVA-5.4 | `tests/test_vva_handoff.py` |
| VVA-5.5 | `tests/test_vva_mutation_gate.py` |
| VVA-6.1 | `tests/test_vva_fail_closed.py` |
| VVA-6.2 | `tests/test_vva_fail_closed.py` |
| VVA-6.3 | `tests/test_vva_fail_closed.py` |
| VVA-7.1 | `tests/test_vva_distribution_drafts.py` |
| VVA-7.2 | `tests/test_vva_distribution_drafts.py` |
| VVA-7.3 | `tests/test_vva_distribution_drafts.py` |
| VVA-7.4 | `tests/test_vva_candidate_a.py` |
| VVA-7.5 | `tests/test_vva_candidate_b.py` |
| VVA-8.1 | `tests/test_vva_evidence_measure.py` |
| VVA-8.2 | `tests/test_vva_evidence_measure.py` |
| VVA-8.3 | `tests/test_vva_evidence_measure.py` |
| VVA-9.1 | `tests/test_vva_idempotence.py` |
| VVA-9.2 | `tests/test_vva_idempotence.py` |
| VVA-9.3 | `tests/test_vva_single_writer.py` |
| VVA-9.4 | `tests/test_vva_single_writer.py` |
| VVA-10.1 | `tests/test_vva_hard_gates.py` |
| VVA-10.2 | `tests/test_vva_hard_gates.py` |
| VVA-10.3 | `tests/test_vva_hard_gates.py` |
| VVA-11.1 | `tests/test_vva_standing_delegation.py` |
| VVA-11.2 | `tests/test_vva_standing_delegation.py` |
| VVA-11.3 | `tests/test_vva_standing_delegation.py` |
