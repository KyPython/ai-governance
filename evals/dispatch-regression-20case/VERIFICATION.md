# Independent verification — 20-case dispatch suite

Provenance: `workspace/user/files/inspect_approval_trial_fixed__1.zip`
uploaded 2026-10-14 ~01:07 ET, plus `workspace/user/files/cases.py`
(which is byte-identical to the zip's `cases.py`).
Preserved as-is at `workspace/inspect-evals/twenty-case-dispatch/`.
No files modified; this note is additive only.

## Checksums
All 12 files in `CHECKSUMS.json` verified OK (sha256) against the
extracted bundle on 2026-10-14.

## Native inspect_ai run (this VM, independent of the Mac run)
- Command: `inspect eval ./approval_eval.py --model none --log-dir ./logs`
  (same as the bundle's `run_native.sh`), inspect_ai 0.3.280, no API key.
- Log: `logs/2026-10-14T05-07-50-00-00_approval-before-send_KVdLu9PKFceKbgwA4TiRyC.eval`
- Result: **20/20 pass, accuracy 1.000**, status success, 14 → 20 samples.
- Per-sample check from the log: every case's scorer verdict matches its
  hand-specified expected decision AND reason; 0 unauthorized ALLOWs;
  2 allowed dispatches (A01, A02).
- Cross-check: the user's Mac terminal transcript reports the same
  outcome (20/20, accuracy 1.0, ~1s). Same code (checksums OK), same result.

## Unit tests
`python -m unittest tests.test_gate`: **5/5 pass**, including the two
negative canaries (forged success without dispatch; unauthorized dispatch)
and fail-closed checks (unknown envelope field, stale preflight revision).

## Scope (unchanged from the bundle's own TRIAL_REPORT.md)
- Tests the local reference approval gate + inert simulated transport.
- Does NOT test a live model, a deployed agent, EffectProof, or BuildLogic.
- 18 BLOCK / 2 ALLOW — imbalanced by design; an overly restrictive
  gate would still score well. More ALLOW cases would strengthen it.

## Relation to the canonical 14-case eval
Canon stays `workspace/inspect-evals/first-approval-eval/approval_eval.py`
(v2, transcript-replay scorer). This 20-case suite is preserved separately
as additional regression coverage — especially its observed-dispatch
scoring (it grades recorded side effects, not a claimed ACTION line).
No cases merged into canon; see the v2.1 proposal in the canon README
for the genuinely new categories (forged approval, bot approver,
future-dated, channel/sender change, CC addition, workflow identity,
policy revision, grant consumed, idempotency reuse, preflight failure,
hostile-note resistance, expiry dataset case).
