# Implementation Plan: JavaScript Signup Form Validation Regex Repair

## Overview

This is the FUTURE real implementation plan that runs ONLY after an actual Kiro review PASS and Ky's human merge of the new canonical 18-record spec PR to `main`. THIS Kiro session executes none of it — no code, no tests, no publication, no registration, no capture, no PASS. Each task reuses the UNCHANGED recovered unworked source (no duplicate build) and names a coder plus a DISTINCT reviewer.

## Task Dependency Graph

```mermaid
graph TD
  T1[1. Reconcile + reuse source, private source commit] --> T2[2. Confirm no offline adapter needed]
  T2 --> T3[3. Strengthened failing-then-passing tests]
  T3 --> T4[4. Smallest production repair]
  T4 --> T5[5. Separate guided worked reference]
  T4 --> T6[6. Source/Goal-bound registration + internal admission]
  T5 --> T7[7. Prepare/verify/publish Notion recording route]
  T6 --> T7
  T7 --> T8[8. Combined cloud artifacts + Shared sync]
```

```json
{ "waves": [ { "wave": 1, "tasks": ["1"] }, { "wave": 2, "tasks": ["2"] }, { "wave": 3, "tasks": ["3"] }, { "wave": 4, "tasks": ["4"] }, { "wave": 5, "tasks": ["5", "6"] }, { "wave": 6, "tasks": ["7"] }, { "wave": 7, "tasks": ["8"] } ] }
```

## Tasks

- [ ] 1. Reconcile and reuse the UNCHANGED unworked source; publish a full PRIVATE source commit
  - Coder: Codex / Reviewer: Cursor
  - Reuse `extractedRoot` starter at `starterSubdirectory` (cloud task `task_e_6ac6d5f886fc8322ae0ceab6e191f68b`, ready; `diffSha256` `89720c3ef31690572cb134fe568704153a2b9019c7981cf0ad364626c2da0e2d`; 10 files). Do NOT invent a new repo or source commit; do NOT re-create. Legacy issue #182 is historical only.
  - Traces: REQ-1, REQ-2, REQ-3.

- [ ] 2. Confirm no offline packaging adapter is required
  - Coder: Cursor / Reviewer: Codex
  - Node built-ins only; no npm install, no fake requirements file, no network pip. Record Node 20.11+ floor and `node --test` / `node server.js` entrypoints.
  - Traces: REQ-5.

- [ ] 3. Write strengthened tests that FAIL before the repair and PASS after
  - Coder: Codex / Reviewer: Cursor
  - Add decisive `node --test` rows: long-TLD + `+`-local-part valid emails; malformed phone with surrounding characters. Deterministic replay. Keep the ordinary baseline SEPARATE from any guided worked reference.
  - Traces: REQ-4, REQ-1, REQ-2, REQ-3.

- [ ] 4. Apply the smallest production repair
  - Coder: Cursor / Reviewer: Codex
  - Remove the `{2,4}` email TLD cap to the contract alphabetic >=2 rule; anchor `phonePattern` with `^...$`; preserve NO-TRIM / as-entered. Smallest change that turns the failing tests green.
  - Traces: REQ-1, REQ-2, REQ-3.

- [ ] 5. Record the separate manual browser verification + disposable guided reference
  - Coder: Codex / Reviewer: Cursor
  - Specify the `localhost:4173` manual check as distinct human evidence; keep any guided worked reference disposable and separate from the baseline.
  - Traces: REQ-6, REQ-4.

- [ ] 6. Exact source/Goal-bound registration and internal admission
  - Coder: Cursor / Reviewer: Codex
  - Bind registration to the verified Goal+LF hash and the recovered source; perform bound internal admission. Preconditions: Kiro review PASS and Ky main merge (not Fit Gate release or paid approval).
  - Traces: REQ-1..REQ-6.

- [ ] 7. Prepare, verify, and publish the exact source/Goal-bound Notion recording route
  - Coder: Codex / Reviewer: Cursor
  - PREPARE and VERIFY the exact source/Goal-bound route with observed checkpoints, recovery, and narration, then PUBLISH the route steps. The VERIFIED separate disposable worked reference (task 5) precedes finalizing these route checkpoints. The actual manual capture is FUTURE HUMAN work and PENDING; it is NEVER agent-executed. No AI during actual capture.
  - Traces: REQ-6.

- [ ] 8. Produce combined cloud artifacts and Shared sync
  - Coder: Cursor / Reviewer: Codex
  - Assemble successful combined cloud artifacts and complete Shared sync ONLY AFTER actual successful proof and sync of the preceding tasks. No final 18-doc PASS is emitted here; the independent parent final-reviews the combined 54 docs at the committed HEAD.
  - Traces: REQ-4, REQ-6.

## Notes

- Paid acceptance is UNVERIFIED (neither eligible nor ineligible). Recorded Candidate/Fit Gate HOLD preserved as facts.
- No destructive operations, deploys, merges, or approvals by any agent.
