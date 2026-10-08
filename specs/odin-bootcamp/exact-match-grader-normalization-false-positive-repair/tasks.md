# Implementation Plan: Exact-Match Grader Normalization False-Positive Repair

## Overview

This is the FUTURE real implementation plan that runs ONLY after an actual Kiro review PASS and Ky's human merge of the new canonical 18-record spec PR to `main`. THIS Kiro session executes none of it — no code, no tests, no publication, no registration, no capture, no PASS. Each task reuses the UNCHANGED recovered unworked source (no duplicate build) and names a coder plus a DISTINCT reviewer.

## Task Dependency Graph

```mermaid
graph TD
  T1[1. Reconcile + reuse source, private source commit] --> T2[2. Read-only technical internal-admission verification/preflight]
  T2 --> T4[4. Offline-prep: confirm no offline adapter needed + ordinary baseline]
  T2 --> T3[3. Create ONE disposable worked-reference copy]
  T4 --> T5[5. Strengthened failing-then-passing tests in the disposable copy]
  T3 --> T5
  T5 --> T6[6. Smallest normalization repair in the SAME disposable copy]
  T6 --> T7[7. Guided-reference proposal + separate worked reference]
  T2 --> T8[8. Later registration of the UNWORKED published pin using the already-verified admission]
  T6 --> T8
  T7 --> T9[9. Prepare/verify/publish Notion recording route]
  T8 --> T9
  T9 --> T10[10. Combined cloud artifacts + Shared sync]
```

```json
{ "waves": [ { "wave": 1, "tasks": ["1"] }, { "wave": 2, "tasks": ["2"] }, { "wave": 3, "tasks": ["4", "3"] }, { "wave": 4, "tasks": ["5"] }, { "wave": 5, "tasks": ["6"] }, { "wave": 6, "tasks": ["7", "8"] }, { "wave": 7, "tasks": ["9"] }, { "wave": 8, "tasks": ["10"] } ] }
```

## Tasks

- [ ] 1. Reconcile and reuse the UNCHANGED unworked source; publish a full PRIVATE source commit
  - Coder: Codex / Reviewer: Cursor
  - Reuse `extractedRoot` starter at `bootcamp/exact-match-grader` (cloud task `task_e_6ac6d5fc882c8322be32454df931e3e3`, ready; `diffSha256` `86e64757ef6adf3756de26567866677fcda85d753fc354a2b0f6d308316763c7`; 7 files). Do NOT invent a new repo/source commit; do NOT re-create. PR #37 and issue #183 are historical only; the sole spec-merge gate is Ky's main merge of the new canonical 18-record spec PR.
  - Traces: REQ-1, REQ-2, REQ-3, REQ-4.

- [ ] 2. Read-only technical internal-admission verification/preflight (BEFORE any world command/test/repair execution)
  - Coder: Cursor / Reviewer: Codex
  - Verify the bound internal admission read-only against the already-verified recovery/source/Goal evidence; NO world command, test, or repair runs before this preflight. Internal technical evidence only — NOT a new Fit release, Recorder/pre-record decision, paid approval, or mastery flag.
  - Traces: REQ-1, REQ-5.

- [ ] 3. Create ONE private disposable worked-reference copy (AFTER the preflight)
  - Coder: Codex / Reviewer: Cursor
  - Create a single disposable worked-reference copy from the published unchanged source AFTER the admission preflight. Keep a SEPARATE ordinary-baseline copy and preserve the published/recovered/Recorder UNWORKED inputs. Tasks 5 and 6 operate on THIS SAME copy.
  - Traces: REQ-5.

- [ ] 4. Confirm no offline packaging adapter is required (offline prep + ordinary baseline, AFTER the preflight)
  - Coder: Cursor / Reviewer: Codex
  - Python standard library only; no third-party install, no fake requirements file, no network pip. Record `grader/cli.py` report run and `tests/test_core.py`.
  - Traces: REQ-5.

- [ ] 5. Write strengthened tests that FAIL before the repair and PASS after
  - Coder: Codex / Reviewer: Cursor
  - In the SAME disposable worked-reference copy from task 3, add golden negative fixtures for sign, unit, and decimal-magnitude mismatches, plus positive equivalence fixtures. Deterministic replay. Keep the ordinary baseline SEPARATE from the guided worked reference.
  - Traces: REQ-1, REQ-2, REQ-3, REQ-4, REQ-5.

- [ ] 6. Apply the smallest normalization repair
  - Coder: Cursor / Reviewer: Codex
  - In the SAME disposable worked-reference copy, replace the digit-only `numeric_portion` collapse so sign/unit/magnitude are preserved and compared; keep whitespace/case/minus-glyph equivalence. Smallest change that turns the failing tests green.
  - Traces: REQ-1, REQ-2, REQ-3, REQ-4.

- [ ] 7. Record the guided-reference matching-policy proposal + disposable worked reference
  - Coder: Codex / Reviewer: Cursor
  - State the AI-designed matching-policy proposal for Ky's batch-PR review (preserve equivalence; reject sign/unit/decimal-magnitude; no unexplained conversions; no universal-equivalence claim). Keep any worked reference disposable and separate from the baseline. Do not claim a human decided.
  - Traces: REQ-1, REQ-2, REQ-3, REQ-4.

- [ ] 8. Later registration of the UNWORKED published pin, binding Source/Goal using the already-verified admission
  - Coder: Cursor / Reviewer: Codex
  - Bind registration to the verified Goal+LF hash and the recovered UNWORKED source, reusing the admission already verified at task 2 (no re-admission; no cyclic prerequisite on tasks 5/6). Preconditions: Kiro review PASS and Ky main merge (not Fit Gate release or paid approval).
  - Traces: REQ-1..REQ-5.

- [ ] 9. Prepare, verify, and publish the exact source/Goal-bound Notion recording route
  - Coder: Codex / Reviewer: Cursor
  - PREPARE and VERIFY the exact source/Goal-bound route with observed checkpoints, recovery, and narration, then PUBLISH the route steps. The VERIFIED separate disposable worked reference (task 7) precedes finalizing these route checkpoints. The actual manual capture is FUTURE HUMAN work and PENDING; it is NEVER agent-executed. No AI during actual capture.
  - Traces: REQ-5.

- [ ] 10. Produce combined cloud artifacts and Shared sync
  - Coder: Cursor / Reviewer: Codex
  - Assemble successful combined cloud artifacts and complete Shared sync ONLY AFTER actual successful proof and sync of the preceding tasks. No final 18-doc PASS is emitted here; the independent parent final-reviews the combined 54 docs at the committed HEAD.
  - Traces: REQ-5.

## Notes

- Paid acceptance is UNVERIFIED (neither eligible nor ineligible). Recorded Candidate/Fit Gate HOLD preserved as facts.
- PR #37 is a closed-unmerged historical reusable draft; not reopened or merged.
- No destructive operations, deploys, merges, or approvals by any agent.
