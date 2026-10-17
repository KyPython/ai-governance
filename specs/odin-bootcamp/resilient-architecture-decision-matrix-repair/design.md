# Design — Resilient Architecture Decision Matrix Repair

## Overview

This design is a Kiro spec-authoring pass for the Odin bootcamp item "Resilient Architecture Decision Matrix Repair." It documents a synthetic starter that downstream automation will prepare and pin, and the diagnostic-level shape of the seeded defect visible in it. It does not write the fix, does not select the correct architecture option, and does not claim human authorship.

A synthetic, deterministic scenario-matrix evaluator reads a written recovery policy (RTO/RPO, dependency, cost, and operational constraints), deterministic workload and failure scenarios, and three abstract architecture options, then emits a serialized report selecting one option with a rationale. Under the changed workload constraints the evaluator currently selects an unsuitable disaster-recovery design because of a seeded selection or boundary defect in the decision model or scenario evaluation. The ordinary baseline suite is green. In guided recording/practice mode the recorded human later diagnoses the defect, implements the smallest defensible repair, adds the decisive changed scenarios and verification, and produces identical serialized reports across repeated runs. This spec does none of that.

### Provenance

- KIRO_SPEC_EXECUTION_ID:6f62ebf4-6d71-4d73-91c5-7bdabf1ac08f — this run's actual Kiro session identifier (from the runtime `KIRO_SESSION_ID`/`SESSION_ID` environment), recorded verbatim and not fabricated or copied from another spec.
- ODIN_BOOTCAMP_SPEC_ROW_ID:3f68621e-0a7a-81c9-8b3e-d3d2e5695ea7
- Task Factory row: https://app.notion.com/p/3f68621e0a7a81c98b3ed3d2e5695ea7
- KIRO_RECEIPT_COMMIT and KIRO_RECEIPT_SHA256 remain HOLD/pending. They are produced only by the real authenticated publisher after a completed review and human (Ky) merge, and MUST NEVER be manufactured here. No PASS receipt is fabricated.
- Candidate-stage bootcamp item: Approved Goal and Approval ID are empty (internal practice only; Odin approval pending). Human approval, pay, and attempt fields are empty and unchanged by this pass.

## Architecture

Synthetic reference shape at the eventual pinned commit (described for review only; not built or rebuilt here):
- `README.md` — setup and the local repeatable report/baseline command.
- A written synthetic **recovery policy** artifact — RTO/RPO, dependency, cost, and operational constraints.
- Deterministic **workload and failure scenario** fixtures, including the changed-constraint variants.
- Three **abstract architecture option** definitions (provider-neutral; resilience behavior only).
- A deterministic **scenario-matrix evaluator** containing a seeded selection or boundary defect.
- Ordinary tests forming a green baseline.
- A repeatable report command producing a serialized report.

Dependencies and reproducibility (pinned profile):
- Offline and provider-free: no AWS account, credentials, cloud deployment, network access, or provider interaction is required after checkout.
- Source reuse: reuse the pinned starter unchanged; downstream MUST NOT rebuild or re-synthesize the starter.

## Components and Interfaces

- **Scenario-matrix evaluator:** reads the recovery policy, scenarios, and options; applies a decision rule across the matrix; emits a selected option plus rationale. Contains the seeded selection/boundary defect that yields an unsuitable choice under the changed constraints.
- **Recovery policy artifact:** the written RTO/RPO, dependency, cost, and operational constraints the selection must honor.
- **Scenario fixtures:** deterministic workload and failure scenarios, including changed-constraint variants.
- **Architecture options:** three abstract, provider-neutral designs under comparison.
- **Baseline tests:** ordinary green tests that do not yet enforce the decisive changed-scenario or recovery-boundary behavior.
- **Report command:** repeatable, deterministic entry point producing the serialized report.
- **Behavior contract (recorder-visible description):** states intended selection and tradeoff-explanation behavior and the reject-incomplete/contradictory-data requirement, without labeling the defect or naming the correct option.

## Data Models

- **Recovery policy:** structured RTO/RPO, dependency, cost, and operational constraint fields.
- **Scenario record:** a workload/failure scenario with the fields the matrix evaluates; the changed-constraint variants are where the seeded defect surfaces.
- **Architecture option:** abstract resilience-behavior descriptor (pilot light / warm standby / active-active family), with no provider identity and no "correct" flag.
- **Decision report:** the serialized selected-option-plus-rationale deliverable; the defensible selection, corrected rule, decisive scenarios, and tradeoff rationale are left for the human.

## Correctness Properties

### Property 1: defensible resilient selection under constraints (INV-1)
WHERE the written RTO/RPO, dependency, cost, and operational constraints apply, THE evaluator SHALL select the defensible resilient architecture — distinguishing pilot light / warm standby / active-active behavior — rather than the unsuitable option, consistently across the scenario matrix.
**Validates: Requirements 2, 3, 4**

### Property 2: deterministic, offline, repeatable report
WHERE the report command is run repeatedly on the pinned starter, THE evaluator SHALL emit identical serialized reports with no network access, and the ordinary baseline SHALL exit 0.
**Validates: Requirements 5, 7**

### Property 3: safe handling of bad scenario data
WHERE scenario data is incomplete or contradictory, THE repaired evaluator SHALL reject it rather than silently selecting an unsafe option.
**Validates: Requirement 11**

- **INV-1 (governing invariant):** The evaluator MUST select the defensible resilient architecture by consistently applying the written RTO/RPO, dependency, cost, and operational constraints — distinguishing pilot light / warm standby / active-active behavior — rather than the unsuitable option, without this spec stating the final repair. The pinned starter intentionally selects an unsuitable design under the changed constraints, violating this invariant.
- The seeded defect must be observable through the documented contract and ordinary execution.
- The baseline suite must remain meaningful while leaving the defect unsolved.

## Error Handling

Failure modes (reject and re-pin rather than alter the baseline or leak the solution):
- Baseline not green at the pin → fails R5; re-pin rather than edit the starter.
- No real selection gap (the evaluator already picks the defensible option under the changed constraints) → fails R3; INV-1 not demonstrably violated.
- No strengthened changed-scenario or recovery-boundary check can fail against the defective evaluator → fails R4.
- Baseline checks weakened or non-meaningful → fails R8.
- Any correct selection, corrected decision rule, decisive changed scenarios, final report answer, diagnosis note, or patch diff present → fails R9.
- Report not identical across repeated runs, or any network/cloud/provider dependence → fails R7.
- Incomplete/contradictory data silently selecting an option expressed as intended behavior incorrectly, or a real provider service named as the required answer → fails R11 / scope.

## Testing Strategy

Baseline / red-green shape:
- The documented repeatable report/baseline command is deterministic and local; the ordinary baseline is green on the starter.
- The recorded human later adds the decisive failing-then-passing changed-scenario and recovery-boundary checks alongside the repair. This spec does not add those checks and does not state the decision-rule fix.

Evidence boundaries a reviewer MAY verify pre-recording (read-only, non-authoring):
- the offline setup works and the baseline command exits 0 with no network/cloud/provider interaction;
- under the changed workload constraints the evaluator selects an unsuitable disaster-recovery design (defect present; INV-1 violated);
- repeated runs of the report command emit identical serialized output;
- no correct selection, corrected rule, decisive changed scenarios, final report answer, or answer key exists in recorder-visible files.

Human-only during recording (not performed in this specification pass and absent from the unchanged pinned recording starter; separately disclosed TaskWorkPlan worked references were AI-authored, analyzed, and disposable-tested off-screen), in guided recording/practice mode: inspecting the policy/scenarios/options/evaluator/fixtures/failing evidence; diagnosing why the current decision is wrong; implementing the smallest defensible repair to the decision model or scenario evaluation; verifying ordinary, exact-threshold, conflicting-constraint, dependency-failure, and repeated-run cases; comparing the selected option with at least one alternative; and teaching back the decisive resilience mechanism, tradeoff, and evidence boundary. The human manually executes edits/tests and narrates actual outcomes from the unchanged unworked starter, with no AI interaction during capture; manual typing does not by itself imply unaided execution. A separate, future unaided Transfer Test is a distinct assessment. The disclosed off-screen worked reference and authorized guided practice do not substitute for that assessment or establish unaided mastery, paid eligibility, or human approval.

Explicit human gates:
- Human diagnosis, repair, recording, capture, and any Odin attempt/approval/pay remain human-owned and outside this spec. This spec does not fill approval, pay, metric, or judgment fields.
- All coding and source promotion are HELD until Ky merges the specs-only PR with green required checks (repo CI + `ai-governance / verdict`). Agents never merge, approve, deploy, or promote. KIRO_RECEIPT_COMMIT / KIRO_RECEIPT_SHA256 remain HOLD/pending and are never manufactured.
