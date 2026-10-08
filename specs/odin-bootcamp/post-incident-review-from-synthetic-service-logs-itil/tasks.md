# Implementation Plan: Post-Incident Review from Synthetic Service Logs (ITIL)

## Overview

This is an actionable FUTURE implementation plan. It begins ONLY after real Kiro final review and @KyPython merge of this spec to `ai-governance/main`. Nothing runs in this spec-only session; baselineExecuted is false. No code or tests are written here; no task is marked done; nothing is executed. **HOLD (every task):** coding/source promotion does not begin until the canonical spec PR is merged by **@KyPython** into `ai-governance/main` with green required checks. Authorship provenance is author session `sess_6ccf95b7-8bbe-4225-8682-6f74410eb9cd`; the final combined 54-file reviewed-HEAD Kiro merge receipt comes from the ORIGINAL final-review session `sess_ef9c3844-0570-409c-baa6-7cc73d898476`, not the author session alone. The exact repair/test/narration/recovery reference lives separately off-screen and is NOT in these public docs.

## Tasks

- [ ] 1. Reuse the exact recovered unworked `bootcamp/incident-review` starter (diffSha256 `0034e1c0…`) in a disposable copy; confirm digests match the inventory; reuse reviewed offline packaging; do not modify fixtures or `summarize_logs.py` (PIR-1, PIR-6, PIR-8) — coder: codex — reviewer: cursor — HOLD until merge
- [ ] 2. Run meaningful ordinary baseline: `python -m unittest discover -s tests -v` and `python scripts/summarize_logs.py fixtures/lb-access.log`; record observed-vs-expected neutral aggregates; proves parsing only, not any PIR claim (PIR-6) — coder: codex — reviewer: cursor — HOLD until merge
- [ ] 3. Write RED-confirming claim-verification tests that fail while timeline entries and impact figures are unverified, computing in UTC (PIR-3, PIR-4, PIR-5) — coder: cursor — reviewer: codex — HOLD until merge
- [ ] 4. Author the separate claim-verification script (not `summarize_logs.py`) AND a clearly labeled, SEPARATE AI-proposed guided-reference PIR DRAFT (disclosed reference only, not the adopted PIR); keep trigger, root cause, and contributing factors separated with uncertainty preserved. The HUMAN analyst completes and adopts the FINAL PIR and owns the final trigger / root-cause / contributing-factor / corrective-action judgments; this task does NOT complete the PIR for the human (PIR-2, PIR-3, PIR-4, PIR-5, PIR-7) — coder: codex (claim-verification script + labeled AI-proposed PIR draft only) — final PIR owner: human analyst — reviewer: cursor — HOLD until merge
- [ ] 5. Confirm GREEN in the disposable copy: verifier exits 0 only when every timeline entry is log-citable and every impact figure reconciles; record observed-vs-expected; no PASS claimed before this runs (PIR-3, PIR-4, PIR-5) — coder: codex — reviewer: cursor — HOLD until merge
- [ ] 6. Post-merge: publish the private Ky-owned unworked starter and confirm its full 40-character commit SHA plus per-file byte and mode verification against the inventory BEFORE internal admission/registration; no SHA invented (PIR-8, PIR-9) — coder: codex — reviewer: cursor — HOLD until merge
- [ ] 7. Author the off-screen guided record reference (separate from these public docs): literal paths, edits, Save All, commands, observed-vs-expected results, rollback, recovery, capture start/stop bound to the actual reviewed source; include internal-preparation admission/registration, exact Notion route (row `3f08621e0a7a817bb25efaa3bfc84919`), paired cloud artifact, and Shared sync via EXISTING Morning/owner; no paid/unaided/recording-ready claim (PIR-7, PIR-8, PIR-9) — coder: cursor — reviewer: codex — HOLD until merge

## Task Dependency Graph

```json
{"waves":[["1"],["2"],["3"],["4"],["5"],["6"],["7"]]}
```

## Notes

- Honesty constraints: no PASS and no batch PASS is claimed; no SHA or PR number is invented; no root cause is stated as settled fact; baselineExecuted is false. Nothing in this spec-only session is executed.
- Preserved paid-state: Odin **Candidate / HOLD / empty paid-approval** is preserved verbatim and is NOT a prerequisite for internal off-screen code/testing/private source publishing; the future technical-prep gates are real Kiro final review, a @KyPython merged-to-main spec, and the bound internal admission. Human/Recorder/paid gates are separate and remain pending.
- No-answer-key scope: the public spec and the UNWORKED starter contain no answer key (no diagnosis, final window, impact total, settled root cause, corrective decision, or completed verification). The separate private disclosed guided reference / Notion cues may contain an AI-proposed causal/PIR/owner reference; final human judgment remains distinct from any such reference.
- Remaining HOLDs: no private starter commit SHA exists yet; it is confirmed only post-merge (full 40-char SHA + byte/mode verification) before internal admission/registration. Unresolved causation is marked HOLD in the PIR rather than asserted.
- Each task has coder ≠ reviewer; off-screen disposable repairs are permitted only after merge; captured starters/attempts remain preserved. No current paid/unaided/recording-ready claim.
