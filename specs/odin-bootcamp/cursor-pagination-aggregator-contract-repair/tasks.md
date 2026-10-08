# Implementation Plan: Cursor-Pagination Aggregator Contract Repair

## Overview

This plan is a Kiro spec review/enhancement in local session sess_ef9c3844-0570-409c-baa6-7cc73d898476 of a spec originally prepared under a prior owner/process. The pinned starter already exists at commit `9c829c6ec7f85cf382f97e286bf8acce20a96fe7`; construction verbs below are HISTORICAL and already satisfied at that pin. They are relabeled as verification-only and MUST NOT rebuild or reseed the pin. Each task has a coder and a different reviewer and traces to requirement IDs. Governing invariant INV-1 is preserved. No prior authorship is claimed.

## Tasks

1. **Verify (historical, already satisfied at pin): synthetic starter, fixtures, and contract doc** (R1, R2)
   - Assigned coder: **Codex**
   - Reviewer: **Cursor**
   - Confirm (read-only) that the pinned commit holds synthetic client code, the ordinary/edge fixtures, and a neutral aggregation-contract description. Do NOT rebuild or reseed; the pin is authoritative.

2. **Confirm the diagnostic-level aggregation defect is present** (R3, R5; INV-1)
   - Assigned coder: **Codex**
   - Reviewer: **Cursor**
   - Confirm the aggregator collects in response order but does not guard against repeated cursors, empty pages, or duplicate records. Describe only at the diagnostic level; do not write or hint the fix.

3. **Verify (historical, already satisfied at pin): deterministic green baseline and preserved ordinary case locally** (R4, R6, R7)
   - Assigned coder: **Codex**
   - Reviewer: **Cursor**
   - Confirm `{python} -m unittest discover -s tests -v` with `PYTHONPATH=src` exits 0 and output contains `Ran 4 tests`, and that existing checks remain meaningful.

4. **Perform no-solution-leak review** (R8, R9)
   - Assigned coder: **Cursor**
   - Reviewer: **Codex**
   - Confirm there is no completed edge-case aggregation, final edge-case tests tied to the contract, diagnosis note, or expected patch diff.

5. **Technical SOURCE verification only: candidate starter is in the defective starting state** (R5, R9)
   - Assigned coder: **Codex**
   - Reviewer: **Cursor**
   - Confirm (read-only) the candidate starter is in the defective, baseline-green starting state with the human-execution work (edge-case handling + verification) still undone. This is technical SOURCE verification only against the pinned commit; human capture admission is SEPARATELY PENDING. A spec/source PASS implies NO Odin paid approval, NO completed capture/pre-record gate checks, and NO unaided mastery.

6. **Binding validation (no duplication)** (provenance; AC1, AC2)
   - Assigned coder: **Cursor**
   - Reviewer: **Codex**
   - Downstream registration/scripts MUST bind the exact Source SHA (`9c829c6ec7f85cf382f97e286bf8acce20a96fe7`), the verbatim Goal, these requirements, INV-1, and the verified baseline output substring (`Ran 4 tests`). Reuse the existing prep registry/helper/publisher/learning-map/paired GHA artifacts and the existing Notion row (`3f28621e0a7a81418d6edfb9a5b43054`). Never duplicate trackers or jobs.

7. **HOLD — human merge gate (final)**
   - All coding and source promotion are HELD until Ky merges the eventual specs-only PR with green required checks (repo CI + `ai-governance / verdict`). Agents never merge, approve, deploy, or promote source. Human diagnosis, repair, recording, attempt, approval, and pay remain human-owned and are not implied by this spec.

## Task Dependency Graph

```mermaid
graph TD
  T1[1. Verify starter + fixtures + contract doc] --> T2[2. Confirm aggregation defect]
  T2 --> T3[3. Verify green baseline + ordinary case]
  T3 --> T4[4. No-solution-leak review]
  T4 --> T5[5. SOURCE verification of candidate starting state]
  T5 --> T6[6. Binding validation]
  T6 --> T7[7. HOLD — human merge gate]
```

```json
{
  "waves": [
    ["1"],
    ["2"],
    ["3"],
    ["4"],
    ["5"],
    ["6"],
    ["7"]
  ]
}
```

## Notes

- Construction verbs in historical tasks (1, 3) are verification-only against the existing pin; never rebuild or reseed.
- Coder/reviewer are always distinct: Codex codes and Cursor reviews on construction/verification tasks; Cursor codes and Codex reviews on review and binding-validation tasks.
- SOURCE PASS at this stage is technical only; it does not establish Odin paid approval, completed capture, or human mastery. The current intended mode is guided recording/practice; a separate future unaided Transfer Test is a distinct assessment, not part of this spec or guided world prep.
