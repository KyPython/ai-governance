# Design — Typed Event-Result Boundary Repair

## Overview

This design is a Kiro spec authoring pass in local session UNKNOWN (executionTarget local) — no genuine Kiro execution/session identifier was available in this environment, so none is recorded and none is invented. It documents a pinned, self-contained local TypeScript starter and the diagnostic-level, result-boundary defect visible in it. It does not write the fix and does not claim human authorship.

A synthetic service function returns a result across a success-failure boundary. The written contract states intended success and failure semantics, but the implementation handles results loosely: the caller can read an error payload as a successful value, and failure, malformed, and unexpected-state results are not exhaustively narrowed. Ordinary tests and synthetic fixtures exist and the type-check/test command runs, but the decisive malformed-result assertions and the typed exhaustiveness enforcement are left for the recorded human, who later selects a result abstraction (discriminated result contract), repairs the boundary and caller to narrow every variant, and verifies deterministic behavior across success, expected failure, malformed input, unexpected state, and caller propagation while preserving the exact response shapes and status decisions.

- Candidate-stage bootcamp item: Approved Goal and Approval ID are empty; there is no retrospective Odin approval. Human approval, pay, and attempt fields are empty and unchanged by this pass.
- Spec path: `specs/odin-bootcamp/typed-event-result-boundary-repair`; Task Factory row: https://app.notion.com/p/3f58621e0a7a811998f1d9057fe5045a; ODIN_BOOTCAMP_SPEC_ROW_ID `3f58621e-0a7a-8119-98f1-d9057fe5045a`.
- No KIRO_RECEIPT_COMMIT / KIRO_RECEIPT_SHA256 is produced or claimed; receipts are a separate downstream concern.

## Architecture

Synthetic reference shape (described for review only; not rebuilt and not pinned to any invented commit):
- A `README`/contract document — setup, the written success/failure contract, and the repeatable type-check/test command.
- A small service function at the boundary — produces success and failure results, currently handled loosely.
- A caller — consumes the result and currently can treat an error payload as a successful value.
- Synthetic fixtures — enumerate success, expected failure, malformed input, unexpected state, and caller-propagation cases.
- Ordinary tests — present and runnable, without the decisive malformed-result assertions.

Dependencies and reproducibility (self-contained local profile):
- Dependency profile: **self-contained local TypeScript** — no network, credentials, private code, or external package service required to check out, type-check, or run after setup.
- Reproducibility: the documented type-check/test command runs deterministically and produces identical results across repeated runs.
- Source reuse: reuse the pinned starter unchanged; downstream MUST NOT rebuild or re-synthesize the starter.

## Components and Interfaces

- **Service function (boundary):** returns a result; currently handles success/failure loosely so an error payload can be read as success.
- **Caller:** consumes the result; currently lacks exhaustive narrowing over failure, malformed, and unexpected-state variants.
- **Fixtures:** enumerate success, expected failure, malformed input, unexpected state, and caller-propagation cases.
- **Ordinary tests:** runnable baseline tests that do not enforce the decisive malformed-result cases.
- **Written contract (recorder-visible description):** states intended success/failure semantics and the response shapes/status decisions to preserve, without labeling the defect or the fix.

## Data Models

- **Boundary result (current, loose):** success and failure results that are not distinguished by a reliable discriminant, allowing an error payload to flow to a caller as a successful value.
- **Discriminated result contract (intended, not authored here):** a typed union distinguishing success from failure by a discriminant so a caller can narrow every variant exhaustively; the recorded human introduces this.
- **Response shapes and status decisions:** the exact per-case response shapes and status decisions (success, expected failure, malformed input, unexpected state, caller propagation) that a later repair MUST preserve.

## Correctness Properties

### Property 1: no error payload treated as success (INV-1)
WHERE a result crosses the success-failure boundary carrying a failure, malformed, or unexpected-state payload, THE caller SHALL NOT treat it as a successful value, and SHALL narrow it exhaustively; WHERE the result is a valid success, THE caller SHALL accept it unchanged.
**Validates: Requirements 3, 4**

### Property 2: defective starter fails the strengthened result-boundary check
WHEN the strengthened error-boundary/malformed-result check is applied to the unrepaired pinned starter, THE check SHALL fail (an error payload is readable as success). This spec DESCRIBES the failing check and does not author it.
**Validates: Requirements 4**

### Property 3: deterministic, shape-preserving behavior after repair
WHEN the documented type-check/test command runs, THE result SHALL be identical across repeated runs, and a later repair SHALL preserve the exact response shapes and status decisions for success, expected failure, malformed input, unexpected state, and caller propagation.
**Validates: Requirements 6, 7**

- **INV-1 (governing invariant):** A result crossing the service boundary MUST NOT be treated as a successful value when it carries a failure, malformed, or unexpected-state payload; every variant MUST be narrowed exhaustively, while the valid success path is accepted unchanged. The pinned starter intentionally handles results loosely and violates this invariant without identifying the final repair.
- The seeded defect must be observable through the documented contract and ordinary execution.
- The ordinary tests and type-check command must remain meaningful while leaving the decisive malformed-result assertions unenforced.

## Error Handling

Failure modes (re-pin or re-prepare rather than solve the task):
- Type-check/test command not runnable or non-deterministic at the pin → fails R6; re-prepare rather than edit toward a solution.
- No real gap (results already handled exhaustively) → fails R3/R4; INV-1 not demonstrably violated.
- Ordinary tests weakened or non-meaningful → fails R5/R9.
- Any completed typed-result abstraction, final exhaustive-narrowing implementation, decisive malformed-result assertion, diagnosis note, or patch diff present → fails R8.
- Any network, credential, private-code, or external-package-service requirement introduced → fails R1.
- Any claim that local verification establishes production transport or observability behavior → fails R10.

## Testing Strategy

Baseline / red-green shape:
- The documented type-check/test command runs deterministically (identical results across repeated runs) with no network after setup, exercising the ordinary tests over success, expected failure, malformed input, unexpected state, and caller-propagation fixtures.
- The ordinary tests run on the starter; the recorded human later adds the decisive malformed-result assertions (the strengthened error-boundary check that fails on the defective starter) alongside the typed-result repair. This spec does not add those assertions.

Evidence boundaries a reviewer MAY verify pre-recording (read-only, non-authoring):
- the self-contained setup works offline and the type-check/test command produces identical results across repeated runs;
- the result-handling gap exists (a caller can treat an error payload as a successful value) and failure/malformed/unexpected-state variants are not exhaustively narrowed (INV-1 violated);
- the exact response shapes and status decisions to preserve are documented;
- no completed typed-result abstraction, final narrowing, decisive assertion, or answer key exists in recorder-visible files.

Evidence states kept distinct: verified current behavior (loose handling, observable), intended behavior (exhaustive typed handling), verified failures (strengthened check fails on the defective starter), unknowns requiring reproduction (actual run output and exit codes, observed only after a later authorized run), and proposed implementation constraints (discriminated result contract, exhaustive narrowing, runtime validation at the boundary).

Human-only during recording (not performed in this specification pass and absent from the unchanged pinned recording starter): diagnosing the loose success/failure handling; selecting the correct result abstraction; repairing the boundary and caller to narrow every variant; adding the decisive malformed-result assertions; and verifying deterministic, shape-preserving behavior. The human manually executes edits/tests and narrates actual outcomes from the unchanged unworked starter.

Explicit human gates and honesty limits:
- Human diagnosis, repair, recording, capture, and any Odin attempt/approval/pay remain human-owned and outside this spec. This spec does not fill approval, pay, metric, or judgment fields, and asserts no human mastery or Odin approval.
- Local verification establishes typed success/failure handling and deterministic local API behavior only; it does NOT establish production transport or observability behavior.
- No KIRO_RECEIPT_COMMIT / KIRO_RECEIPT_SHA256 is produced or claimed; no PASS receipt is manufactured.
- All coding and source promotion are HELD until Ky merges the specs-only PR with green required checks (repo CI + `ai-governance / verdict`). Agents never merge, approve, deploy, or promote.
