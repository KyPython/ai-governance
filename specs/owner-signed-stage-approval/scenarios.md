<!-- KIRO-AUTHORED SPEC (spec-author subagent) — HUMAN ADOPTION/MERGE PENDING. Not an owner approval. Drafted 2026-11-28; model ID not exposed. Issue: #238. Source: KyPython/ai-governance@90bcd70. -->
<!-- Completion: no completion contract; not gate-verified. -->

# Scenarios: Owner-signed stage approval

Spec ID: OSA · Issue: #238 · AI draft; not a G3 receipt. Each scenario is read from a real CI job result (OSA-8.2). Only P1 needs Ky's device. All others use unsigned material or throwaway keys that are not in the pinned file.

Common setup: pinned file on `main` holds Ky's public key restricted to namespace `ai-governance-stage-approval@v1`; revocation list empty unless stated; record fields per OSA-1.1.

## Positive

**P1. Genuine signature passes** (OSA-1, OSA-4, OSA-8.4)
Given a record for the exact repository, issue, `spec_sha`, stage and paths, signed by Ky on his device, unexpired, unrevoked, nonce unused, committed in a PR.
When the policy job runs.
Then it passes with "signature verified against the key pinned on main", record id and key fingerprint. It does not say "owner-authenticated" (OSA-7.2).

## Adverse

| ID | Given | Then (reason) |
| --- | --- | --- |
| A1 | A record whose signature has one flipped byte, or whose record bytes changed after signing (forged) | `OWNER_SIGNATURE_INVALID` |
| A2 | A well-formed record signed by an agent with a throwaway key not in the pinned file (agent-signed) | `OWNER_SIGNATURE_INVALID` |
| A3 | P1's record presented again in a second PR after the first record is on `main` (replay) | `OWNER_SIGNATURE_REPLAYED` |
| A4 | A genuine record whose `expires_at` is in the past (expired) | `OWNER_SIGNATURE_EXPIRED` |
| A5 | A genuine record whose id is on the owner revocation list on `main` (revoked); variant: the key is removed from the pinned file | `OWNER_SIGNATURE_REVOKED`; variant: `KEY_UNPINNED` |
| A6 | A genuine record naming a different repository | `OWNER_SIGNATURE_WRONG_SUBJECT` |
| A7 | A genuine record whose `spec_sha` differs from the spec on `main` | `OWNER_SIGNATURE_WRONG_SUBJECT` |
| A8 | A genuine record for stage G2 presented for a G4 action | `OWNER_SIGNATURE_WRONG_SUBJECT` |
| A9 | The same PR changes the pinned key file to add an agent key, and presents a record signed by that new key | `OWNER_SIGNATURE_INVALID` (verified against `main`'s file); the key-file change also fails the owner-only rule (OSA-3.3) |
| A10 | The pinned file is missing, empty, malformed, or lacks the owner entry or namespace | `KEY_UNPINNED` |
| A11 | The approval text or signature appears only in the PR body, a PR comment, an issue comment, a label or a commit message; no committed record | `OWNER_SIGNATURE_MISSING` |
| A12 | A genuine key signs the record in another namespace (for example the T1 spike namespace), or an AIV vault token is presented as the approval | `OWNER_SIGNATURE_INVALID` |
| A13 | `ssh-keygen` is not found on the runner, or `main` cannot be read (simulated in an isolated test) | HOLD, `VERIFIER_UNAVAILABLE`; no approval, no override |
| A14 | A genuine record permits `specs/<slug>/**` add or modify, and the change deletes a file or touches `.github/workflows/` | `OWNER_SIGNATURE_WRONG_SUBJECT` |
| A15 | A `KyPython` comment, label or PR body says "approved" and no record exists | `OWNER_SIGNATURE_MISSING`; wording does not claim owner approval |
| A16 | A record with a missing or mistyped field (for example no `nonce`) with a valid signature | `OWNER_SIGNATURE_INVALID` |
| A17 | A verifier configured to read the pinned file from the PR head | Test fails the implementation (OSA-3.1); the shipped verifier reads `main` only |
| A18 | An agent-prepared unsigned record, correctly filled | `OWNER_SIGNATURE_MISSING`; no agent output calls it an approval (OSA-6.3) |

## Controls
- C1 An always-pass verifier fails A1 to A16 and A18. An always-deny verifier fails P1 (OSA-8.2).
- C2 Repository scan of the demonstration PRs finds no private key material (OSA-6.1, OSA-8.3).
- C3 Demonstration evidence is reproducible by a reviewer who is not its author (OSA-8.4).

## Traceability
| Scenario | Requirement |
| --- | --- |
| P1 | OSA-1, OSA-4, OSA-7.1, OSA-8.4 |
| A1, A2, A16 | OSA-1, OSA-4.4, OSA-6 |
| A3, A5 | OSA-5 |
| A4 | OSA-1.3, OSA-4.4 |
| A6, A7, A8, A14 | OSA-1.4, OSA-1.5, OSA-4.4 |
| A9, A10, A17 | OSA-3 |
| A11, A15 | OSA-4.2, OSA-7.3 |
| A12 | OSA-2 |
| A13 | OSA-4.5 |
| A18 | OSA-6.2, OSA-6.3 |

## Status
RUNTIME ACCEPTANCE NOT RUN. Until the T5 demonstration, B1 stays `UNVERIFIABLE_APPROVER` and ESE-17.3 stays BLOCKED.
