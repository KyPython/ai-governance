# Design — Requirements Change-Control Traceability Repair

## Overview

This design is a Kiro spec review/enhancement in local session sess_82309770-7349-46bb-ab4b-ae3a937b8c7f (executionTarget local). It documents a synthetic change-control starter that does **not yet exist** and the diagnostic-level defects it will embody once prepared. The starter is prepared downstream only after @KyPython merges this specs-only PR; this pass writes no code, prepares no package, and claims no human authorship. Existing design content is folded into Kiro canonical sections.

A synthetic change-control package reads a requirements baseline, one approved change request, acceptance criteria, and a traceability matrix, and produces a deterministic traceability report. In the prepared starter the updated requirement, its acceptance criteria, and its verification links are mutually inconsistent — an obsolete/stale acceptance path, a duplicate identifier, or a misclassified requirement remains — and the change-impact set is inconsistent with the approved change. The baseline is green. In guided recording/practice mode the recorded human later diagnoses the inconsistencies, decides the requirement classification and the smallest defensible impact set, repairs the artifacts or validator, adds the decisive negative checks, and produces a deterministic report showing the approved change is complete with no obsolete acceptance path remaining.

- Candidate Goal SHA256 (Goal+LF): UNKNOWN — pending downstream preparation (to be bound at preparation time; not invented here).
- Source pin (commit SHA + source URL): UNKNOWN — pending downstream preparation (to be bound after merge; not invented here).
- Candidate-stage bootcamp item: Approved Goal and Approval ID are empty; there is no retrospective Odin approval. Human approval, pay, and attempt fields are empty and unchanged by this pass.

### Distinctness

No existing factory fingerprint centers on requirements-change impact, requirement classification, acceptance-evidence linkage, and removal of obsolete trace paths. This task differs from CI evaluation-contract repair (there the decisive mechanism is CI enforcement; here it is the requirements lifecycle and traceability) and from documentation-drift tasks (there the artifact under test is a README; here it is a requirements/change baseline). The decisive mechanism under test is change-control traceability, not CI gating or documentation drift.

## Architecture

Synthetic reference shape at the future pinned commit (described for review only; not built, not pinned yet):
- A requirements baseline (fabricated requirement set with stable identifiers and classifications).
- One approved change request against that baseline.
- Acceptance criteria for the affected requirement(s).
- A traceability matrix linking requirement identifiers to acceptance criteria and verification links.
- Deterministic fixtures.
- Ordinary baseline checks.
- A repeatable, deterministic validation command.
- A recorder-visible behavior description (no defect labeling).

Dependencies and reproducibility (future pinned profile):
- Dependency profile: pinned local interpreter only, no third-party packages, no network at runtime after checkout. The exact interpreter and profile are to be bound downstream at preparation time.
- Offline, pinned setup recipe (to be bound to the downstream per-task preparation helper): check out the future pinned starter commit (UNKNOWN until preparation); use the pinned local interpreter; run the documented validation command offline; no third-party packages and no network install required.
- Source reuse: once prepared and pinned, reuse the starter unchanged; downstream MUST NOT rebuild or re-synthesize the starter after it is bound.

## Components and Interfaces

- **Requirements baseline:** fabricated requirements with stable identifiers and classifications (functional requirement, quality requirement, or constraint).
- **Change request:** one approved change whose updated requirement, acceptance criteria, and verification links are left mutually inconsistent in the prepared starter.
- **Acceptance criteria:** the criteria the approved change must connect to as acceptance evidence.
- **Traceability matrix:** maps requirement identifiers → acceptance criteria → verification links; the vacancy lies in a retained stale/obsolete link, a duplicate identifier, or a misclassification.
- **Validation command / validator:** produces the deterministic traceability report; the prepared starter's validator does not yet reject the stale/duplicate links or report the trace gaps the human must enforce.
- **Fixtures:** deterministic synthetic inputs used to produce byte-identical serialized reports.
- **Baseline checks:** green checks that do not yet enforce the strengthened traceability/obsolete-link property.
- **Behavior contract (recorder-visible description):** states the intended end-to-end traceability of the approved change without labeling the defects.

## Data Models

- **Requirements baseline:** requirement identifiers, classifications, and bodies.
- **Change request:** the approved delta to one or more requirements, with the intended affected work products.
- **Acceptance criteria:** criteria tied to the affected requirement(s) that serve as acceptance evidence.
- **Traceability matrix:** identifier → acceptance-criteria → verification-link edges, including the seeded stale/duplicate/misclassified edge the human must resolve.
- **Traceability report:** the deterministic, byte-identical serialized report (approved change complete, unaffected requirements preserved, stale/duplicate links rejected, unresolved trace gaps reported) — left for the human.

## Correctness Properties

### Property 1: approved change is traceable with no obsolete path (INV-1)
WHERE the approved change request applies to the baseline, THE traceability report SHALL connect the approved change to acceptance evidence, validate requirement identifiers and classifications, preserve unaffected requirements, reject stale or duplicate links, and show that no obsolete acceptance path remains.
**Validates: Requirements 3, 4, 6**

### Property 2: unresolved gaps reported and output is deterministic
WHERE a trace gap is unresolved, THE report SHALL state it explicitly rather than silently pass, and repeated runs of the validation command SHALL produce byte-identical serialized reports with the baseline exiting 0 (exit code and output substring to be bound downstream).
**Validates: Requirements 5, 7, 8**

- **INV-1 (governing invariant):** The deterministic traceability report MUST show that the approved change is complete — every requirement identifier and classification is valid, unaffected requirements are preserved, the approved change is connected to acceptance evidence, stale or duplicate links are rejected, unresolved trace gaps are reported explicitly, and repeated runs produce byte-identical serialized reports — with no obsolete acceptance path remaining. The prepared starter intentionally leaves the updated requirement, acceptance criteria, and verification links inconsistent (a stale/obsolete link, duplicate identifier, or misclassification), violating this invariant without identifying the final repair.
- Both seeded defects must be observable through the documented contract and ordinary execution.
- The baseline checks must remain meaningful while leaving both defects unsolved.

## Error Handling

Failure modes (reject and re-prepare rather than alter a worked baseline):
- Baseline not green at preparation → fails R5; re-prepare rather than edit a worked starter.
- No real inconsistency (links/classifications already consistent) → fails R3; INV-1 not demonstrably violated.
- Change-impact set already correct and complete → fails R4.
- Baseline checks weakened or non-meaningful → fails R8.
- Non-deterministic serialized report (not byte-identical across runs) → fails R7.
- Any chosen classification, decided impact set, repaired links/artifacts, decisive negative checks, completed traceability report, diagnosis note, or patch diff present → fails R9.
- Baseline drifts from the exit code/substring to be bound downstream → fails R5 AC; do not alter the baseline to pass.

## Testing Strategy

Baseline / red-green shape:
- The repeatable validation command (to be bound downstream, deterministic, local) → exit 0, with the baseline exit code and output substring bound at preparation time; the prepared starter is green.
- The recorded human later adds the decisive failing-then-passing negative checks for stale/obsolete links, duplicate identifiers, misclassification, and unresolved trace gaps alongside the repair. This spec does not add those checks and the prepared starter must not contain them.
- Outputs here are expectations to verify LATER against the future pinned starter in disposable copies. Nothing is executed in this spec; no PASS, SHA, or receipt is asserted.

Evidence boundaries a reviewer MAY verify pre-recording (read-only, non-authoring), once the starter is prepared and pinned downstream:
- the offline setup works and the validation command produces the bound exit 0 and output substring, byte-identically across repeated runs;
- the updated requirement, acceptance criteria, and verification links are mutually inconsistent — a stale/obsolete link, duplicate identifier, or misclassification remains (defect present; INV-1 violated);
- the requirement classification or impact set is inconsistent with the approved change (second defect present);
- no chosen classification, decided impact set, repaired artifacts, decisive negative checks, completed traceability report, or answer key exists in recorder-visible files.

Human-only during recording (not performed in this specification pass and absent from the future unworked recording starter; any separately disclosed TaskWorkPlan worked reference is AI-authored, analyzed, and disposable-tested off-screen), in guided recording/practice mode: inspecting the change request, baseline requirements, acceptance criteria, trace matrix, fixtures, and failing report; diagnosing which links or classifications are inconsistent; deciding whether the request changes a functional requirement, a quality requirement, or a constraint, and the smallest defensible impact set and affected work products; implementing the corrected requirements/traceability artifacts or validator; verifying unchanged requirements, changed requirements, acceptance coverage, obsolete-link removal, duplicate identifiers, and repeated deterministic output; distinguishing an intentional requirement change from stale documentation; explaining why the final trace is sufficient without adding unsupported scope; then teaching back the decisive change-control and traceability mechanism without relying on a generated explanation. The human manually executes edits/checks and narrates actual outcomes from the unchanged unworked starter, with no AI interaction during capture; manual typing does not by itself imply unaided execution. A separate, future unaided Transfer Test is a distinct assessment. The disclosed off-screen worked reference and authorized guided practice do not substitute for that assessment or establish unaided mastery, paid eligibility, or human approval.

Explicit human gates:
- Human diagnosis, repair, recording, capture, and any Odin attempt/approval/pay remain human-owned and outside this spec. This spec does not fill approval, pay, metric, or judgment fields.
- All coding and source promotion are HELD until Ky merges the specs-only PR with green required checks (repo CI + `ai-governance / verdict`). Agents never merge, approve, deploy, or promote.
