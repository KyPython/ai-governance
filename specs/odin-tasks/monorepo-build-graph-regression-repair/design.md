# Design — Monorepo Build-Graph Regression Repair

## Overview

This design is a Kiro spec review/enhancement in local session sess_ef9c3844-0570-409c-baa6-7cc73d898476 (executionTarget local) of a spec originally prepared under a prior owner/process. Existing design content is preserved and folded into Kiro canonical sections; provenance, pinned-dependency, evidence-boundary, failure-mode, and human-gate material is retained. No prior authorship is claimed.

A synthetic pnpm/Turborepo monorepo has a service that consumes built output from a shared workspace package. The starter build graph fails for two independent reasons: the shared dependency now needs its own build step that the pipeline does not establish, and a container/config surface references an obsolete package name. In guided recording/practice mode the human later diagnoses both root causes and applies the smallest bounded corrections, manually executing and narrating actual outcomes from the unchanged starter.

- Approved Goal SHA256 (Goal+LF): 54d506c1f74e626aa6126b9df52d0adbfd337a211606a85a1d320010f43e7160
- Approval ID: ODIN-ED6E74BA231E41F0A6386D49E67DE48F (human-owned; unchanged by this pass)

Evidence boundaries (what a reviewer MAY verify pre-recording, read-only and non-authoring):
- installability with the pinned toolchain;
- the three baseline commands produce the exit codes and substrings in the acceptance criteria;
- both approved defect classes are present and independent;
- no completed repair or answer-key note exists in recorder-visible files.

A separate, disclosed, AI-authored worked reference already exists off-screen in the TaskWorkPlan (authorized, analyzed, disposable-tested). It is distinct from the recording starter. Diagnosis, tests, and repair are NOT banned in authorized off-screen reference preparation; only the pinned recording starter must remain unworked and answer-key-free.

## Architecture

Repository shape (pinned starter layout):
- root workspace manifest and `turbo.json`/equivalent pipeline config;
- `apps/` or `services/` containing the affected synthetic service (`apps/dispatch-service`);
- `packages/` containing the shared workspace dependency (`packages/route-core`) and one small unrelated package/check (`packages/status-check`);
- build/container configuration containing the intentionally stale package identity (`@harbor/dispatch-api`);
- neutral README with install + failure reproduction only.

Dependencies and reproducibility (pinned profile):
- Dependency profile: **pnpm-workspace** — `pnpm==9.15.4`, `turbo==2.3.3`, both provided via corepack.
- Dependency roots: `node_modules`, `apps/dispatch-service/node_modules`, `packages/route-core/node_modules`, `packages/status-check/node_modules`.
- Source reuse: check out the pinned starter `https://github.com/KyPython/monorepo-build-graph@2ddf3c8f2a0e054ea2e40ab077c5a48132c34a38` and reuse it unchanged. Downstream MUST NOT rebuild or re-synthesize the starter.
- Pinned setup recipe: enable corepack with the pinned pnpm/turbo versions bound to the existing PrepareTaskWork helper per-task profile/argv/env, run `pnpm install` from the clean checkout; no additional network fetches during the baseline runs.

## Components and Interfaces

- **Affected service (`apps/dispatch-service`):** consumes generated/built output from the shared package; its build fails because build ordering is not established.
- **Shared dependency (`packages/route-core`):** requires its own deterministic build output (`packages/route-core/dist/routes.json`).
- **Unrelated check (`packages/status-check`):** remains passing so a correction can be shown as bounded.
- **Container/config surface:** names the superseded identity `@harbor/dispatch-api`.

Focused baseline commands (registry baseline, verified intent, deterministic, local):
- `pnpm check:unrelated` → exit 0, output contains `status check passed`.
- `pnpm build:service` → exit 1, output references `packages/route-core/dist/routes.json`.
- `pnpm check:container` → exit 1, output contains `container target @harbor/dispatch-api is not a workspace package`.

## Data Models

- **Workspace graph:** service → shared dependency build-output edge that the pipeline must (but does not) order correctly.
- **Build artifact:** `packages/route-core/dist/routes.json`, the generated output the service consumes.
- **Package identity record:** current workspace package name vs. the stale `@harbor/dispatch-api` reference in config.

## Correctness Properties

### Property 1: both root causes required
WHERE only one of the two independent defects is corrected, THE service build OR the separate container-target check SHALL still produce a remaining observable failure (fixing one is insufficient); only when BOTH independent corrections are present do both the service build and the container-target check pass.
**Validates: Requirements 7**

### Property 2: unrelated check stays green
WHEN the unrelated workspace check runs against the starter state, THE check SHALL exit 0 with output containing `status check passed`.
**Validates: Requirements 8**

- The two defects must be independent: correcting only one leaves a remaining observable failure.
- The unrelated check must remain meaningful and passing from the starter state.

## Error Handling

Failure modes (reject and re-pin rather than alter the baseline):
- Only one defect present, or the two are not independent → fails R7/AC5; re-pin.
- Service build passes from the starter state → fails R4/AC3; re-pin.
- Unrelated check also fails → fails R8/AC2 (correction cannot be shown as bounded).
- Any corrected config, final diff, or verification note present → fails R9/AC6.
- Baseline drifts from registry exit codes/substrings → fails AC2/AC3/AC4; do not alter the baseline to pass.

## Testing Strategy

Human-only during TaskRecorder — the pending human-owned step performed in guided recording/practice mode (NOT performed in this spec pass):
- diagnosing both root causes;
- deciding the smallest bounded corrections;
- implementing them;
- verifying the service with transitive workspace dependencies;
- writing the concise verification note.

Human-boundary scope qualifier: the current intended mode is guided recording/practice. The human manually executes edits/tests and narrates actual outcomes from the unchanged unworked starter, with no AI interaction during capture; manual typing does not by itself imply unaided execution. A separate, future unaided Transfer Test is a distinct assessment. Authorized guided practice and disclosed worked references do not substitute for that assessment or establish unaided mastery, paid eligibility, or human approval. No starter file may provide the final corrected config.

Explicit human gates:
- Human diagnosis, repair, recording, capture, and any Odin attempt/approval/pay remain human-owned and outside this spec.
- All coding and source promotion are HELD until Ky merges the specs-only PR with green required checks (repo CI + `ai-governance / verdict`).
