# Implementation Plan: SSRF URL Allowlist Validator Bypass Fix

## Overview

This is an actionable FUTURE implementation plan. It begins ONLY after real Kiro final review and @KyPython merge of this spec to `ai-governance/main`. Nothing runs in this spec-only session; baselineExecuted is false. No code or tests are written here; no task is marked done; nothing is executed. **HOLD (every task):** coding/source promotion does not begin until the canonical spec PR is merged by **@KyPython** into `ai-governance/main` with green required checks. Authorship provenance is author session `sess_6ccf95b7-8bbe-4225-8682-6f74410eb9cd`; the final combined 54-file reviewed-HEAD Kiro merge receipt comes from the ORIGINAL final-review session `sess_ef9c3844-0570-409c-baa6-7cc73d898476`, not the author session alone. The exact repair/test/narration/recovery reference lives separately off-screen and is NOT in these public docs.

## Tasks

- [ ] 1. Reuse the exact recovered unworked `specs/odin-tasks/ssrf-url-allowlist-validator/starter` (diffSha256 `df0f9fbb…`) in a disposable copy; confirm digests match; reuse reviewed offline packaging (pytest 8.3.5 / setuptools 75.8.0) (SSRF-6) — coder: codex — reviewer: cursor — HOLD until merge
- [ ] 2. Run meaningful ordinary baseline `python -m pytest -q` and demonstrate (offline) that suffix-extension and userinfo bypasses pass the prefix matcher; record observed-vs-expected RED (SSRF-1, SSRF-8) — coder: codex — reviewer: cursor — HOLD until merge
- [ ] 3. Write the table-driven RED test suite: one row per bypass class (synthetic `.example.test`, raw-IP, private/loopback) plus legitimate rows; failing before the fix (SSRF-2, SSRF-3, SSRF-4, SSRF-5, SSRF-7) — coder: cursor — reviewer: codex — HOLD until merge
- [ ] 4. Apply the bounded parsed-URL + IP-range fix with the single normalization policy; preserve the GET-plan contract; no network/DNS/sockets; AI-proposed rules are proposals for Ky's PR review (SSRF-1, SSRF-2, SSRF-3, SSRF-4, SSRF-5, SSRF-6, SSRF-8) — coder: codex — reviewer: cursor — HOLD until merge
- [ ] 5. Confirm GREEN in the disposable copy: `python -m pytest -q`; every bypass row rejected, every legitimate row allowed; record observed-vs-expected; state out-of-scope limits; no PASS claimed before this runs (SSRF-6, SSRF-7, SSRF-9) — coder: codex — reviewer: cursor — HOLD until merge
- [ ] 6. Post-merge: publish the private Ky-owned unworked starter and confirm its full 40-character commit SHA plus per-file byte and mode verification against the inventory BEFORE internal admission/registration; no SHA invented (SSRF-9) — coder: codex — reviewer: cursor — HOLD until merge
- [ ] 7. Author the off-screen guided record reference (separate from these public docs): literal paths, edits, Save All, commands, observed-vs-expected results, rollback, recovery, capture start/stop bound to the actual reviewed source; include internal-preparation admission/registration, exact Notion route (row `3f08621e0a7a81f5b437e25bc0e45e8d`), private full starter pin verified after merge, paired cloud artifact, and Shared sync via EXISTING Morning/owner; no paid/unaided/recording-ready claim (SSRF-9) — coder: cursor — reviewer: codex — HOLD until merge

## Task Dependency Graph

```json
{"waves":[["1"],["2"],["3"],["4"],["5"],["6"],["7"]]}
```

## Notes

- Honesty constraints: no PASS and no batch PASS is claimed; no SHA or PR number is invented; baselineExecuted is false. Nothing in this spec-only session is executed.
- Preserved paid-state: Odin **Candidate / HOLD / empty paid-approval** is preserved verbatim and is NOT a prerequisite for internal off-screen code/testing/private source publishing; the future technical-prep gates are real Kiro final review, a @KyPython merged-to-main spec, and the bound internal admission. Human/Recorder/paid gates are separate and remain pending.
- One consistent proposed normalization policy governs case/default-port handling (case-insensitive scheme/host, default-port filling, non-default port rejected unless allowlisted) — it does not reject case-only while also normalizing. This policy is an AI-proposed GUIDEDREFERENCE for Ky's PR review, not a decided rule.
- Remaining HOLDs: no private starter commit SHA exists yet; it is confirmed only post-merge (full 40-char SHA + byte/mode verification) before internal admission/registration.
- Each task has coder ≠ reviewer; off-screen disposable repairs are permitted only after merge; captured starters/attempts remain preserved. No current paid/unaided/recording-ready claim.
