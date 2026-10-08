# Implementation Plan: Async Side-Effect Idempotency Hardening

## Overview

This is an actionable FUTURE implementation plan. It begins ONLY after real Kiro final review and @KyPython merge of this spec to `ai-governance/main`. Nothing runs in this spec-only session; baselineExecuted is false. No code or tests are written here; no task is marked done; nothing is executed. **HOLD (every task):** coding/source promotion does not begin until the canonical spec PR is merged by **@KyPython** into `ai-governance/main` with green required checks. The Odin state is **Awaiting approval / PASS / pay 0** and is preserved; this plan does not grant approval or change pay. Authorship provenance is author session `sess_6ccf95b7-8bbe-4225-8682-6f74410eb9cd`; the final combined 54-file reviewed-HEAD Kiro merge receipt comes from the ORIGINAL final-review session `sess_ef9c3844-0570-409c-baa6-7cc73d898476`, not the author session alone. The exact repair/test/narration/recovery reference lives separately off-screen and is NOT in these public docs.

## Tasks

- [ ] 1. Reuse the exact recovered unworked `starters/async-side-effect-idempotency-hardening` (diffSha256 `6e81335d…`) in a disposable copy; confirm digests match; reuse reviewed offline editable-package packaging (IDEM-3, IDEM-4) — coder: codex — reviewer: cursor — HOLD until merge
- [ ] 2. Run meaningful ordinary baseline `python -m unittest discover -s tests -v`; then process `fixtures/replayed_deliveries.jsonl` and record that duplicate job_id yields multiple outbox notifications (RED) (IDEM-1, IDEM-5) — coder: codex — reviewer: cursor — HOLD until merge
- [ ] 3. Write RED duplicate + concurrent-identical regression tests (via `asyncio.gather`) asserting one effect per job_id, plus a failure-policy test: a controlled failed/uncertain send keeps the reservation, propagates the original exception, and performs no second attempt for that job_id; stronger before/after/replay checks than baseline; failing before the fix (IDEM-1, IDEM-2, IDEM-5, IDEM-7) — coder: cursor — reviewer: codex — HOLD until merge
- [ ] 4. Apply the bounded process-local reservation fix: check-and-reserve job_id before the awaited send; apply the explicit AI-proposed failure policy (on a failed/uncertain send keep the reservation, propagate the exception, suppress later same-job retry — bounded at-most-once ATTEMPT, no durable/exactly-once promise); preserve single/distinct behavior and outbox record format; process-local scope only; the reservation and failure policy are proposals for Ky's PR review (IDEM-1, IDEM-2, IDEM-3, IDEM-4, IDEM-6, IDEM-7) — coder: codex — reviewer: cursor — HOLD until merge
- [ ] 5. Confirm GREEN + duplicate replay in the disposable copy: `python -m unittest discover -s tests -v` and the duplicate replay; record observed-vs-expected showing exactly one effect per job_id and ordinary cases intact; state out-of-scope limits; no PASS claimed before this runs; approval/pay unchanged (IDEM-1, IDEM-3, IDEM-5, IDEM-8, IDEM-9) — coder: codex — reviewer: cursor — HOLD until merge
- [ ] 6. Post-merge: publish the private Ky-owned unworked starter and confirm its full 40-character commit SHA plus per-file byte and mode verification against the inventory BEFORE internal admission/registration; no SHA invented; approval/pay unchanged (IDEM-9) — coder: codex — reviewer: cursor — HOLD until merge
- [ ] 7. Author the off-screen guided record reference (separate from these public docs): literal paths, edits, Save All, commands, observed-vs-expected results, rollback, recovery, capture start/stop bound to the actual reviewed source; include internal-preparation admission/registration, exact Notion route (row `3f08621e0a7a81e3b4efcfea472d9930`), private full starter pin verified after merge, paired cloud artifact, and Shared sync via EXISTING Morning/owner; no paid/unaided/recording-ready claim; external Odin approval remains a separate pending decision (IDEM-7, IDEM-8, IDEM-9) — coder: cursor — reviewer: codex — HOLD until merge

## Task Dependency Graph

```json
{"waves":[["1"],["2"],["3"],["4"],["5"],["6"],["7"]]}
```

## Notes

- Honesty constraints: no PASS and no batch PASS is claimed; no SHA or PR number is invented; baselineExecuted is false. Nothing in this spec-only session is executed.
- Preserved paid-state: Odin **Awaiting Odin approval / PASS / Approved Pay 0** is preserved verbatim; this plan does not grant approval or change pay. The preserved paid state is NOT a prerequisite for internal off-screen code/testing/private source publishing; the future technical-prep gates are real Kiro final review, a @KyPython merged-to-main spec, and the bound internal admission. Human/Recorder/paid gates (including the external Odin approval) are separate and remain pending.
- Failure policy (explicit, AI-proposed GUIDEDREFERENCE for Ky's PR review; the README defines none): reserve before send; on a failed/uncertain send keep the reservation for this process, propagate the original exception, and suppress a later same-job retry in this worker — a bounded at-most-once ATTEMPT, not confirmed delivery; no durable/restart/multi-process/exactly-once promise. A failed/ambiguous send does not prove an effect occurred. Ky may choose another consistent explicit policy at review. This is not a human judgment or approval claim.
- Remaining HOLDs: no private starter commit SHA exists yet; it is confirmed only post-merge (full 40-char SHA + byte/mode verification) before internal admission/registration.
- Each task has coder ≠ reviewer; off-screen disposable repairs are permitted only after merge; captured starters/attempts remain preserved. No current paid/unaided/recording-ready claim.
