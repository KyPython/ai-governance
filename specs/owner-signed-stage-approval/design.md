<!-- KIRO-AUTHORED SPEC (spec-author subagent) — HUMAN ADOPTION/MERGE PENDING. Not an owner approval. Drafted 2026-11-28; model ID not exposed. Issue: #238. Source: KyPython/ai-governance@90bcd70. -->
<!-- Completion: no completion contract; not gate-verified. -->

# Design: Owner-signed stage approval (B1 channel)

Spec ID: OSA · Issue: #238 · Status: proposed. Design only; nothing here is built.
Evidence tags: [RULE] governing rule, [OBS] observed in this checkout, [STATED] stated by parent and unverified, [PROPOSED] design choice, [UNKNOWN].

## Overview
Ky signs a canonical JSON record on a device agents cannot reach. The verifier checks that signature with the system `ssh-keygen` against a public key pinned on `main`, then checks the record against the exact subject. Every failure maps to one named reason. The channel ends B1 only after the OSA-8 demonstration.

## Where it plugs in
| Existing piece | Fact | Use here |
| --- | --- | --- |
| `roles.yml`, `delegations.yml` | Owner-only files read from `main` by the policy job [OBS] (`roles.yml` header; `delegations.yml` header; GATE-3.3, GATE-3.5, SAD-2.1, SAD-2.4) | Pattern for the owner-only pinned key file and revocation list |
| Policy job in `.github/workflows/governance.yml` | Protected path (AGENTS rule 7) | Integration point; edit is a proposed task (T4) |
| Pre-dispatch broker | [PROPOSED] in ESE-7.1; does not exist [RULE: ESE status note] | Second verification point; integration deferred until it exists |
| `agent_vault/token.py` | `ed25519_verify` is reusable; `verify_token` is vault-specific (issuer, payload) [OBS] | Candidate B primitive only |
| ESE-2.2 / ESE-17.3 | BLOCKED `UNVERIFIABLE_APPROVER` until demonstrated [RULE] | Unchanged until OSA-8 |

## Signed record [PROPOSED]
```json
{"decision":"APPROVE","expires_at":"2026-12-05T00:00:00Z","issue":238,
 "issued_at":"2026-11-28T00:00:00Z","nonce":"<random, at least 128 bits>",
 "permitted":[{"paths":["specs/<slug>/**"],"ops":["add","modify"]}],
 "purpose":"stage-approval","repository":"KyPython/ai-governance",
 "spec_sha":"<git object id, see D3>","stage":"G2","version":1}
```
Canonical form: sorted keys, `(",", ":")` separators, UTF-8, no trailing newline. The signature covers those bytes. Fields come from OSA-1.1. The values above are illustrative and are not an approval.

## Signing and verification (candidate A) [PROPOSED]
Ky's device (app UNKNOWN) produces an SSHSIG armored signature of the record file in namespace `ai-governance-stage-approval@v1`; the desktop equivalent is `ssh-keygen -Y sign -f <key> -n ai-governance-stage-approval@v1 record.json`.

Pinned file (public keys only; name is decision D4), `allowed_signers` format:
```
ky-owner namespaces="ai-governance-stage-approval@v1" <key-type> <base64-public-key>
```
CI verification (the record is on stdin):
```
ssh-keygen -Y verify -f <allowed_signers from main> -I ky-owner \
  -n ai-governance-stage-approval@v1 -s record.json.sig [-r <revoked_keys>] < record.json
```
Exit status 0 is the only success. The OpenSSH `-Y verify` revocation option `-r` is [STATED/UNKNOWN] for the runner version and is confirmed in T2. If `-r` is unavailable, key revocation is done by removing the key from the pinned file (OSA-5.2), and record revocation by the list (OSA-5.1).

Key types: `ssh-keygen` verifies `ecdsa-sha2-nistp256` and `ssh-ed25519`. P-256 therefore needs no new code. [STATED] Secure Enclave keys are P-256 only. Whether an iPhone SSH app exposes `-Y sign` semantics (SSHSIG over a chosen namespace) is [UNKNOWN] until T1. FIDO `sk-*` keys are a different mechanism and not assumed.

## Candidate comparison
| | A: OpenSSH signature | B: Ed25519 via `agent_vault/token.py` |
| --- | --- | --- |
| New code to verify | Subprocess wrapper plus record checks | `ed25519_verify` plus own record format and domain prefix |
| Algorithm | P-256 or Ed25519, whatever the app makes | Ed25519 only [OBS: `ed25519_verify`] |
| Namespace separation | Built in (`-n`, `namespaces=`) | Manual domain-separation prefix (OSA-9.3) |
| Revocation | `-r` option, [UNKNOWN] on runner | Own list |
| Dependency | `ssh-keygen` on runner [STATED] | None beyond stdlib [OBS: stdlib only] |
| Device need | App producing SSHSIG [UNKNOWN] | A signer producing raw Ed25519 over the bytes [UNKNOWN] |
| Verdict | Evaluate first (OSA-9.3) | Fallback if T1 shows only raw Ed25519 |

If T1 yields neither, status is `NO_CHANNEL` (OSA-9.4) and a spec revision follows.

## Verification algorithm (OSA-4.4 order)
1. Read the pinned file from `main` (never PR head). Missing, unreadable, no owner entry: `KEY_UNPINNED`.
2. Record and signature present as committed files at the named commit: else `OWNER_SIGNATURE_MISSING`.
3. Run `ssh-keygen -Y verify`. Nonzero exit from a verification failure: `OWNER_SIGNATURE_INVALID`. Tool not found, `main` unreadable, crash, timeout: `VERIFIER_UNAVAILABLE` (HOLD).
4. Parse the record only now. Schema or `purpose` wrong: `OWNER_SIGNATURE_INVALID`.
5. Match repository, issue, `spec_sha`, stage, and that every changed path and operation falls within `permitted`: else `OWNER_SIGNATURE_WRONG_SUBJECT`.
6. `now >= expires_at` (and `issued_at` not in the future, `expires_at` within the adopted maximum): `OWNER_SIGNATURE_EXPIRED`.
7. Record id or nonce on the revocation list on `main`: `OWNER_SIGNATURE_REVOKED`.
8. Nonce already consumed (D6): `OWNER_SIGNATURE_REPLAYED`.
Pass: print "signature verified against the key pinned on main" with record id, key fingerprint and stage (OSA-7.1). Time comes from the runner clock, a [PROPOSED] limit: clock skew is accepted and recorded.

## Replay options (decision D6)
| Option | How consumption is known | Cost | Gap |
| --- | --- | --- | --- |
| 1 (recommended) | A nonce present in a record already on `main` is consumed | No new infrastructure | Two concurrent PRs both pass until one merges; re-check at merge and publish (OSA-5.4) |
| 2 | Owner-only consumption ledger on `main` appended at merge | Extra file and owner merge per use | More owner steps |
| 3 | External store | New service | Violates OSA-9.2; not proposed |

## Trust root and rotation
The pinned file is owner-only on `main`. Bootstrap: Ky's first enrollment is an owner-identity merge, which carries the `KyPython` token limit [RULE: `roles.yml` header]. The design does not hide this. Later change: a record signed by the current key naming the new key, or an owner merge that the policy flags for review (OSA-3.5). A PR that changes the pinned file and presents an approval is verified against `main`'s file only (OSA-3.6), so enrolling a new key in the same PR gains nothing for that PR.

## Threats and what stops them
| Threat | Control |
| --- | --- |
| Agent writes a record and signs with its own key | Key not in pinned file: `OWNER_SIGNATURE_INVALID` (A2) |
| Agent edits the pinned file in the same PR | Verified against `main`; file change needs owner identity (A9) |
| Agent uses Ky's token to merge a key change | Not stopped while B1 is open. This is the bootstrap limit, stated in OSA-3.4 |
| Signature reused for another repo/stage/SHA | Subject binding (A6, A7, A8) |
| Reuse of an approved record | Nonce consumption (A3) |
| Signature from another purpose | Namespace and `purpose` (A12) |
| Tool outage forces approval | HOLD, never approve (A13) |
| Stolen or unlocked device | Not stopped. Revocation limits damage (OSA-7.4). Whether the app requires biometrics is [UNKNOWN] |
| Approval claimed in PR body or comment | Never read (A11, A15) |

## Failure modes
All fail closed with a named reason. Outage is HOLD. Skipped verification is not a pass (OSA-4.6). Rollback is Ky's revert of the merge that introduced a component. No spend, no deploy, no model run is part of any path.

## Testing strategy
Tests ship with the verifier (T2) and cite OSA IDs. `ssh-keygen` runs against throwaway keys generated in a temp directory (OSA-6.4). Unit tests are not B1 evidence. B1 evidence is the T5 runs (OSA-8). Each scenario maps to a reason in `scenarios.md`.

## Decisions for Ky
D1 Which iPhone app/algorithm (from T1). D2 Maximum record lifetime. D3 `spec_sha` object type (commit of main, or tree of `specs/<slug>`). D4 File names and location of the pinned key file and revocation list. D5 Where the record and signature files live in the repository. D6 Replay mechanism. D7 Whether the demonstration runs in this repository or a scratch repository. Unanswered items stay UNKNOWN and are not defaulted.
