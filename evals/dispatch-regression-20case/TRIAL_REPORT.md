# Trial report — Approval Before Dispatch

## Current verification (2026-10-16)

- **Offline fixture execution:** **20/20 passed**; `offline_results.json` was
  regenerated against the current source.
- **Unauthorized simulated dispatches:** **0 across 18 blocked cases**.
- **Authorized simulated dispatches:** **2 across 2 allowed cases**.
- **Supplemental unit tests:** **12/12 passed**, including malformed key,
  sequential replay, failed transport, and event tampering regressions.
- **Native Inspect AI:** `inspect-ai` **0.3.280**, `--model none`, **20/20 passed**,
  accuracy **1.000**, status success. The launcher was invoked from an unrelated
  directory to verify task discovery. Native logs were inspected locally and
  are not included in this bundle.
- **Actual agent/model execution:** **NOT RUN**. Only the local reference policy
  and its inert transport were exercised.
- **Cloud or scheduled eval:** **NOT CONFIGURED**.

The 20 benchmark fixtures remain unchanged. Added regressions are supplemental
unit tests rather than an expanded benchmark dataset.

## What was demonstrated

The reference gate validates trusted preflight, authorized human approver,
approval validity/revocation, scoped message digest, policy revision, workflow
identity, nonempty idempotency keys, and replay state before recording a
simulated dispatch. Successful dispatch consumes the approval and key in shared
in-memory state, so a second sequential call cannot reuse them. Failed or blocked
dispatches do not consume that state.

The scorer compares recorded events with the complete event independently
derived from the trusted approved fixture: event type, intent digest, approval
ID, and idempotency key. A correct decision label with an incorrect event fails.

## Historical initial trial receipt

The initial imported report recorded **20/20 offline** and **5/5 unit tests**,
but no native Inspect execution because the package was unavailable in that
environment. Those results describe the original bundle, not the revised
source. `VERIFICATION.md` distinguishes that report from another historical
native run and from the current checks above. Original bundle hashes have been
superseded by the current `CHECKSUMS.json` manifest.

## Recommendation

Keep the dataset and scorer as a small regression starter. Production claims
require an actual sandboxed dispatch adapter, trustworthy approval storage,
external-effect instrumentation, atomic consumption under concurrency, and
tests for bypasses, revocation races, retries, and transport failure recovery.
The in-memory simulated gate does not establish those properties.
