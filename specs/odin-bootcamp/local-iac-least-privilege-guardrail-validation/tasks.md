# Implementation Plan: Local IaC Least-Privilege Guardrail Validation

## Overview

This is an actionable FUTURE implementation plan. It begins ONLY after real Kiro final review and @KyPython merge of this spec to `ai-governance/main`. Nothing runs in this spec-only session; baselineExecuted is false. No code or tests are written here; no task is marked done; nothing is executed. **HOLD (every task):** coding/source promotion does not begin until the canonical spec PR is merged by **@KyPython** into `ai-governance/main` with green required checks. The Odin decision is **Rejected / REJECT** and is preserved; this internal-prep plan does not reopen it. Authorship provenance is author session `sess_6ccf95b7-8bbe-4225-8682-6f74410eb9cd`; the final combined 54-file reviewed-HEAD Kiro merge receipt comes from the ORIGINAL final-review session `sess_ef9c3844-0570-409c-baa6-7cc73d898476`, not the author session alone. The exact repair/test/narration/recovery reference lives separately off-screen and is NOT in these public docs.

## Tasks

- [ ] 1. Reuse the exact recovered unworked `specs/odin-tasks/local-iac-least-privilege-guardrail-validation/starter` (diffSha256 `01c2f012…`) in a disposable copy; confirm digests match; reuse reviewed offline stdlib packaging (IAC-4, IAC-7) — coder: codex — reviewer: cursor — HOLD until merge
- [ ] 2. Run meaningful ordinary baseline: `python -m unittest discover -s tests -v` and `python -m infra.synth --output build/template.json` then `python -m policy.validate build/template.json`; record that the role grants `s3:*` on `*` and the validator does not flag it (IAC-1, IAC-6) — coder: codex — reviewer: cursor — HOLD until merge
- [ ] 3. Extend the policy validator to flag `s3:*` on `*` (and equivalent over-broad grants); confirm it fails against the current stack before the fix (IAC-5) — coder: cursor — reviewer: codex — HOLD until merge
- [ ] 4. Apply the smallest least-privilege correction (read action(s) scoped to `incoming/*`), grounded in the workload contract; preserve S3 public-access block, S3 encryption, SQS KMS, and resource structure; AI-proposed scope is a proposal for Ky's PR review (IAC-1, IAC-2, IAC-3, IAC-4, IAC-8) — coder: codex — reviewer: cursor — HOLD until merge
- [ ] 5. Confirm GREEN before/after in the disposable copy: `python -m unittest discover -s tests -v` and the synth/validate pair before and after; record observed-vs-expected showing risk present then corrected with unrelated safeguards intact; no PASS claimed before this runs; Rejected/REJECT preserved (IAC-5, IAC-6, IAC-9) — coder: codex — reviewer: cursor — HOLD until merge
- [ ] 6. Post-merge: publish the private Ky-owned unworked starter and confirm its full 40-character commit SHA plus per-file byte and mode verification against the inventory BEFORE internal admission/registration; no SHA invented; Rejected/REJECT unchanged (IAC-9) — coder: codex — reviewer: cursor — HOLD until merge
- [ ] 7. Author the off-screen guided record reference (separate from these public docs): literal paths, edits, Save All, commands, observed-vs-expected results, rollback, recovery, capture start/stop bound to the actual reviewed source; include internal-preparation admission/registration, exact Notion route (row `3f08621e0a7a81418692ed974ac073a0`), private full starter pin verified after merge, paired cloud artifact, and Shared sync via EXISTING Morning/owner; no paid/unaided/recording-ready claim and no change to the Rejected/REJECT decision (IAC-8, IAC-9) — coder: cursor — reviewer: codex — HOLD until merge

## Task Dependency Graph

```json
{"waves":[["1"],["2"],["3"],["4"],["5"],["6"],["7"]]}
```

## Notes

- Honesty constraints: no PASS and no batch PASS is claimed; no SHA or PR number is invented; baselineExecuted is false. Nothing in this spec-only session is executed.
- Preserved paid-state: Odin **Rejected / REJECT / Approved Pay 0** is preserved verbatim; this internal-prep plan does not reopen, change, or override that decision. The preserved Rejected/REJECT/0 state is NOT a prerequisite for internal off-screen code/testing/private source publishing; the future technical-prep gates are real Kiro final review, a @KyPython merged-to-main spec, and the bound internal admission. Human/Recorder/paid gates are separate and remain pending (and for this task the Odin outcome is already Rejected).
- Commands use stdlib `unittest` (`python -m unittest discover -s tests -v`); synthesis is `python -m infra.synth --output build/template.json` then `python -m policy.validate build/template.json` — never `python infra/synth.py`. No undeclared pytest.
- AI-proposed read-action set and ARN form are GUIDEDREFERENCE proposals for Ky's PR review, grounded in `docs/workload-contract.md`, not decisions already made.
- Remaining HOLDs: no private starter commit SHA exists yet; it is confirmed only post-merge (full 40-char SHA + byte/mode verification) before internal admission/registration.
- Each task has coder ≠ reviewer; off-screen disposable repairs are permitted only after merge; captured starters/attempts remain preserved. No current paid/unaided/recording-ready claim.
