<!-- KIRO-AUTHORED SPEC (spec-author subagent) — HUMAN ADOPTION/MERGE PENDING. Not an owner approval. Drafted 2026-11-28; model ID not exposed. Issue: #238. Source: KyPython/ai-governance@90bcd70. -->
<!-- Completion: no completion contract; not gate-verified. -->

# Requirements: Owner-signed stage approval (B1 channel)

Spec ID: OSA · Issue: #238 (existing; no new issue) · Status: proposed; Ky adopts it only by reviewing and merging the spec-only PR
Implements the B1 exit criteria in `specs/engineering-stage-enforcement/design.md` (section "B1 criteria for leaving `UNVERIFIABLE_APPROVER`"). Relates to ESE-2.2, ESE-6, ESE-17.3, SAD-4.3.
Coders implement these sentences. They do not paraphrase, reword or weaken them to fit code.

Duplicate check (one writer, no duplicates): no existing B1 or owner-signature spec was found under `specs/` on `origin/main` @ `90bcd70`. The owner's Notion page "Agent Conduct Rules — One Write, No Duplicates" could not be loaded; this packet applies its stated gist as passed by the parent: no duplicate sources of truth, one writer.

## Introduction

### Problem
`UNVERIFIABLE_APPROVER` (B1) means no owner approval channel exists that an agent cannot forge. `roles.yml` states the limit: "git author/committer fields are self-declared, and agents that push with Ky's token show up as KyPython." ESE-2.2 requires BLOCKED with reason `UNVERIFIABLE_APPROVER` until a non-agent-forgeable channel exists. ESE-17.3 and SAD-4.3 keep that wording until the channel is "demonstrated by observed execution evidence".

### Proposal in one paragraph
Ky signs a small approval record on a device agents do not control, using an OpenSSH-format signature (`ssh-keygen -Y sign`). The policy and pre-dispatch boundary verifies the signature with `ssh-keygen -Y verify` against a public key pinned in an owner-only file on `main`. B1 ends only after the four ESE criteria are observed in real CI runs (OSA-8).

### Evidence states

| State | Statement | Source |
| --- | --- | --- |
| VERIFIED GOVERNING RULE | Until a non-agent-forgeable channel exists, report BLOCKED with `UNVERIFIABLE_APPROVER`; a comment is no fallback. | `specs/engineering-stage-enforcement/requirements.md` ESE-2.2 |
| VERIFIED GOVERNING RULE | A GitHub comment, PR author, label, commit signature, bot JSON, `@approved` tag, YAML checkbox or CI metadata is not approval by itself. A verified commit signature authenticates a key, not human authorship. | ESE-2.1, ESE-2.5 |
| VERIFIED GOVERNING RULE | `UNVERIFIABLE_APPROVER` stays until an independent owner-only signing channel with trusted verification is demonstrated by observed execution evidence. | ESE-17.3 |
| VERIFIED GOVERNING RULE | Four B1 criteria: owner-only signing on a device agents do not control; a verifier whose trust root an agent cannot change checks the exact subject; forged, agent-issued, replayed, expired and revoked approvals each fail for the correct reason; an outage leaves HOLD. | `specs/engineering-stage-enforcement/design.md`, section "B1 criteria for leaving `UNVERIFIABLE_APPROVER`" |
| VERIFIED GOVERNING RULE | A delegation is described as "recorded on the base branch by an owner-identity merge" and not as owner-authenticated while B1 is open. | `specs/spec-author-delegation-check/requirements.md` SAD-4.3 |
| VERIFIED GOVERNING RULE | Receipts bind stage, paths, operations, policy revision, content digests and expiry/revocation; fail closed; recheck at dispatch and before publish. | ESE-6.1 to ESE-6.6, ESE-17.1 |
| VERIFIED GOVERNING RULE | Agents do not edit `roles.yml`, workflows, `CODEOWNERS` or `AGENTS*.md`; such a change is a proposed task needing Ky's exact request and Ky's merge. Agents never use Ky's identity to pass a role gate. | `AGENTS.governance.md` rules 2, 7, 11; ESE-13.4 |
| VERIFIED CURRENT OBSERVATION | Owner-only files read from `main` already exist as a pattern: `roles.yml` (GATE-3.3, GATE-3.5) and `delegations.yml` (SAD-2.1, SAD-2.4; no records yet, `delegations: {}`). | `specs/ai-governance-gate/requirements.md`; `delegations.yml` |
| VERIFIED CURRENT OBSERVATION | `agent_vault/token.py` contains a stdlib-only RFC 8032 `ed25519_verify(public_key, message, signature)`. `verify_token` is specific to vault grants: it requires `iss == "ai-governance-local-vault"` and the AIV payload fields. | `agent_vault/token.py` |
| STATED BY PARENT, UNVERIFIED | iPhone Secure Enclave keys are P-256 only, not Ed25519. | INFERENCE; verify on device (T1) |
| STATED BY PARENT, UNVERIFIED | OpenSSH is on GitHub-hosted runners. | INFERENCE; the OpenSSH version must be recorded in the demonstration (OSA-8.3) |
| UNKNOWN | Which iPhone app can create a key and produce an OpenSSH signature (`-Y sign`, SSHSIG format) over a file with a chosen namespace; whether the key is Secure-Enclave-backed; whether use requires biometrics. | T1 (Ky) |
| UNKNOWN | Whether Ky's device can produce Ed25519 signatures at all (candidate B). | T1 (Ky) |
| UNKNOWN | Whether `ssh-keygen -Y verify -r <revocation_file>` behaves as needed on the runner's OpenSSH version. | T2 test run |

### Bootstrap limit (stated plainly)
The pinned public key is enrolled by a merge to `main`. While B1 is open, that first merge is an owner-identity merge and carries the known limit: an agent holding Ky's token appears as `KyPython`. The trust root is therefore only as strong as the first owner merge. Later key changes are covered by OSA-3.5. The signature channel proves possession of the private key. It does not prove the human identity of whoever holds the device (OSA-7.1).

### Out of scope
- Any change to the ESE-2 approval bar. This channel is one way to satisfy ESE-2.2. It adds no approval path and removes none.
- Editing any protected path (OSA-9.1).
- Running a model, creating an issue, spending money, adding a paid service (OSA-9.2).
- Deciding which stages need a signed record. ESE-1 owns the stages. This spec owns only the channel.

---

## Requirements

### Requirement 1: Signed approval record (OSA-1)

**User Story:** As Ky, I want my signature to cover one exact subject, so that an approval for one thing cannot be stretched to another.

Source: ESE-6.1, ESE-6.2, ESE-17.1, ESE-1.9.

#### Acceptance Criteria
1. OSA-1.1 The signed record SHALL contain these fields, and a record missing or mistyping any of them SHALL be invalid: `purpose` (constant `stage-approval`), `version`, `repository` (`owner/name`), `issue` (number), `spec_sha`, `stage` (G0 to G6), `decision` (`APPROVE` only), `permitted` (list of path globs and operations), `issued_at`, `expires_at`, and `nonce`.
2. OSA-1.2 The record SHALL be serialized as canonical JSON (sorted keys, compact separators, UTF-8), and the signature SHALL cover exactly those bytes. The verifier SHALL verify the signature over the bytes as received and SHALL parse them only after the signature verifies.
3. OSA-1.3 WHEN a record has no `expires_at`, or an `expires_at` later than the owner-adopted maximum lifetime THEN the system SHALL treat it as invalid. WHILE no maximum is adopted, the system SHALL still require `expires_at` and SHALL NOT supply a default. (Maximum is UNKNOWN; decision D2.)
4. OSA-1.4 One record SHALL authorize one stage, for one repository, issue and `spec_sha`, within the listed paths and operations, and SHALL NOT confer a later stage, a merge, a deployment or spend. (Source: ESE-1.9, ESE-6.7.)
5. OSA-1.5 `spec_sha` SHALL identify the exact spec content the owner reviewed. The git object it names (commit or tree of the spec folder) is an owner decision (D3).

**Evidence/test method:** schema tests for each missing/mistyped field; byte-exact signing test. Deferred to implementation.
**Dependencies:** ESE-6.1, ESE-17.1.

---

### Requirement 2: Namespace and purpose separation (OSA-2)

**User Story:** As Ky, I want a signature made for stage approval to be useless for anything else, and the reverse.

Source: OpenSSH signature namespaces (`ssh-keygen -Y sign -n`); `agent_vault/token.py` (separate token format).

#### Acceptance Criteria
1. OSA-2.1 The system SHALL use one fixed namespace string for stage approval (proposed: `ai-governance-stage-approval@v1`), and SHALL pass it to `ssh-keygen -Y verify -n`.
2. OSA-2.2 The pinned key file SHALL restrict the enrolled key to that namespace (the `namespaces="..."` option in `allowed_signers`), so that a signature in another namespace fails even if the key matches.
3. OSA-2.3 WHEN the record's `purpose` is not `stage-approval` THEN the system SHALL treat the record as invalid.
4. OSA-2.4 The system SHALL NOT accept an AIV vault grant token, a commit signature, a signature in any other namespace, or a signature made for the spike (T1 namespace) as a stage approval. A stage-approval signature SHALL NOT be accepted by any other verifier.
5. OSA-2.5 Any new purpose (delegation, deployment) SHALL use its own namespace string and its own spec. This spec does not authorize it.

**Evidence/test method:** wrong-namespace and cross-purpose scenarios (A12). Deferred to implementation.
**Dependencies:** OSA-1.

---

### Requirement 3: Trust root and key pinning (OSA-3)

**User Story:** As Ky, I want the key the verifier trusts to be one only I can change, so that an agent cannot swap in its own key.

Source: GATE-3.3, GATE-3.5, SAD-2.1, SAD-2.4, SAD-2.5.

#### Acceptance Criteria
1. OSA-3.1 The system SHALL read the pinned public key file only from `KyPython/ai-governance` `main`, and SHALL NOT read it from a pull request head, a caller input, a comment, a label or a PR body.
2. OSA-3.2 WHEN the pinned key file is missing, unreadable, malformed, or has no entry for the owner identity and namespace THEN the system SHALL fail with `KEY_UNPINNED`.
3. OSA-3.3 WHEN a pull request changes the pinned key file THEN the system SHALL fail the policy job unless the PR opener and every commit identity match the owner, using the same rule that protects `roles.yml` (GATE-3.3), and SHALL flag the change for owner review.
4. OSA-3.4 The system SHALL state, in the design, the delivery report and the demonstration evidence, that the first enrollment is an owner-identity merge and that the trust root is no stronger than that merge (bootstrap limit).
5. OSA-3.5 WHEN the enrolled key changes after bootstrap THEN the change SHALL either carry a stage-approval-style record signed by the currently pinned key naming the new key, or come from an owner merge that the system flags for review. A change by neither route SHALL fail.
6. OSA-3.6 WHEN one pull request both changes the pinned key file and presents an approval THEN the system SHALL verify that approval against the key on `main` only (never the changed file), so a signature by the newly added key fails.
7. OSA-3.7 The pinned file SHALL contain public keys only. The file name and location are an owner decision (D4).

**Evidence/test method:** A9, A10, A17. Deferred to implementation.
**Dependencies:** GATE-3.3, OSA-1, OSA-2.

---

### Requirement 4: Verification boundary and fail-closed reasons (OSA-4)

**User Story:** As Ky, I want a failure to name its cause on my phone, and an outage to stop work and not approve it.

Source: ESE-6.3, ESE-6.6, ESE-7.1, GATE-3.4, SAD-3.

#### Acceptance Criteria
1. OSA-4.1 The system SHALL verify the approval in the policy job and in the pre-dispatch broker (ESE-7.1), against the pinned key on `main`, and SHALL verify again immediately before publication.
2. OSA-4.2 The system SHALL take the record and signature only from committed files in the repository at a named commit (location is decision D5). It SHALL NOT take them from a PR body, PR or issue comment, label, title, or commit message.
3. OSA-4.3 The system SHALL report exactly one of these reasons for a failure: `OWNER_SIGNATURE_MISSING`, `OWNER_SIGNATURE_INVALID`, `OWNER_SIGNATURE_EXPIRED`, `OWNER_SIGNATURE_REPLAYED`, `OWNER_SIGNATURE_REVOKED`, `OWNER_SIGNATURE_WRONG_SUBJECT`, `KEY_UNPINNED`, or `VERIFIER_UNAVAILABLE`. The message SHALL name the repository, issue, stage and record id.
4. OSA-4.4 The system SHALL evaluate in this order and stop at the first failure: key pinned (`KEY_UNPINNED`); signature present (`OWNER_SIGNATURE_MISSING`); signature and namespace valid (`OWNER_SIGNATURE_INVALID`); record schema and purpose; subject match for repository, issue, `spec_sha`, stage and permitted paths and operations (`OWNER_SIGNATURE_WRONG_SUBJECT`); not expired (`OWNER_SIGNATURE_EXPIRED`); not revoked (`OWNER_SIGNATURE_REVOKED`); not replayed (`OWNER_SIGNATURE_REPLAYED`).
5. OSA-4.5 WHEN `ssh-keygen` is unavailable, `main` cannot be read, or the verifier errors for any reason other than a verification failure THEN the system SHALL report HOLD with `VERIFIER_UNAVAILABLE`, SHALL NOT default to approve, and SHALL NOT fall back to a comment or self-declared override. (Source: ESE-6.6.)
6. OSA-4.6 A skipped or stale verification SHALL be reported as not passed.
7. OSA-4.7 A verified approval SHALL satisfy only the owner-decision requirement of ESE-2.2 for the named stage and subject. All other ESE requirements SHALL still apply.

**Evidence/test method:** one real CI run per reason, quoted. Deferred to implementation.
**Dependencies:** OSA-1 to OSA-3, ESE-7.

---

### Requirement 5: Revocation and replay (OSA-5)

**User Story:** As Ky, I want to withdraw an approval or a key, and I want one approval to be used once.

Source: ESE-6.3, ESE-13.1, ESE-17.4.

#### Acceptance Criteria
1. OSA-5.1 The system SHALL read an owner-only revocation list of record ids and nonces from `main`, and a record on that list SHALL fail with `OWNER_SIGNATURE_REVOKED`. The same change rule as OSA-3.3 SHALL apply to that list.
2. OSA-5.2 WHEN the enrolled key is revoked (removed from the pinned file or listed in a key revocation file passed to `ssh-keygen -Y verify -r`) THEN every approval signed by it SHALL fail, and the system SHALL NOT accept approvals signed before the revocation unless Ky re-signs them.
3. OSA-5.3 A record's `nonce` SHALL be consumed once. A second presentation of a consumed nonce, for any subject, SHALL fail with `OWNER_SIGNATURE_REPLAYED`. The consumption mechanism is decision D6. Recommended option: a nonce already present in a record on `main` counts as consumed.
4. OSA-5.4 WHEN two pull requests present the same nonce concurrently THEN the system SHALL re-check at merge or publication time, so that the second to land fails (time-of-check to time-of-use). (Source: ESE-13.2.)
5. OSA-5.5 Revocation and expiry SHALL be re-read from current `main` at each check, never cached from an earlier run.

**Evidence/test method:** A3, A5. Deferred to implementation.
**Dependencies:** OSA-3, OSA-4.

---

### Requirement 6: Private key custody (OSA-6)

**User Story:** As Ky, I want the private key to stay on my device, so that nothing an agent can reach holds it.

Source: ESE-2.3; `AGENTS.governance.md` rules 8 and 11.

#### Acceptance Criteria
1. OSA-6.1 The private key SHALL NOT be stored in any repository, any CI secret or variable, any agent environment, any agent-reachable file, or any session with an agent. This spec, its tests and its evidence SHALL contain no private key material.
2. OSA-6.2 An agent MAY prepare an unsigned record (a template with the subject fields filled from observed facts) and MAY verify a signature. An agent SHALL NOT sign, SHALL NOT hold a signing key for the pinned identity, and SHALL NOT ask Ky to paste a private key.
3. OSA-6.3 An unsigned record SHALL be reported `OWNER_SIGNATURE_MISSING`, and no agent output SHALL describe it as an approval.
4. OSA-6.4 Tests MAY generate throwaway keys in a temporary directory. A throwaway key SHALL NOT be enrolled in the pinned file on `main`, and tests SHALL label it a test key.
5. OSA-6.5 The repository SHALL NOT add a signing helper that reads a private key from the repository, an environment variable or a CI secret.

**Evidence/test method:** repository scan for key material in the demonstration PR; A2 (agent-signed with another key). Deferred to implementation.
**Dependencies:** none.

---

### Requirement 7: Honest claims (OSA-7)

**User Story:** As Ky, I want a green check never to claim more than it proves.

Source: SAD-4.1 to SAD-4.3; ESE-2.1, ESE-2.5; `AGENTS.governance.md` rule 11.

#### Acceptance Criteria
1. OSA-7.1 The system SHALL describe a passing verification as "signature verified against the key pinned on main", and SHALL NOT claim it proves who held the device, that Ky was present, or that Ky exercised judgment.
2. OSA-7.2 WHILE the OSA-8 demonstration is not complete, and after it until Ky records the disposition (OSA-8.6), the system SHALL NOT describe an approval as "owner-authenticated" or "verified human approval".
3. OSA-7.3 The system SHALL NOT accept a chat message, GitHub comment, label, PR body text, commit signature or agent statement as a stage approval or as evidence of one.
4. OSA-7.4 WHEN the device or key is lost or suspected compromised THEN Ky revokes by OSA-5 and the system SHALL report all approvals from that key as untrusted until re-signed.

**Evidence/test method:** wording checks on real job output (A11, A15). Deferred to implementation.
**Dependencies:** SAD-4, ESE-2.

---

### Requirement 8: B1 exit only by observed demonstration (OSA-8)

**User Story:** As Ky, I want B1 closed by something I can reproduce, not by a document.

Source: `specs/engineering-stage-enforcement/design.md` "B1 criteria"; ESE-17.3; ESE-9 to ESE-14 method (real boundary, quoted results).

#### Acceptance Criteria
1. OSA-8.1 The demonstration SHALL show all four ESE criteria by real CI runs on real commits: (1) an owner-only signing step on a device agents do not control; (2) a verifier with an agent-unchangeable trust root checking the exact subject; (3) a forged, an agent-produced, a replayed, an expired and a revoked approval each failing for the correct reason; (4) a verifier or issuer outage leaving HOLD.
2. OSA-8.2 The demonstration SHALL run every scenario in `scenarios.md` and SHALL read each result from the real job, not from a mock whose return value the test sets. An always-pass verifier SHALL fail the adverse scenarios, and an always-deny verifier SHALL fail P1.
3. OSA-8.3 The evidence SHALL record, per run: workflow run id and URL, commit SHA, record id and digest, key fingerprint (public), OpenSSH version, the quoted verdict line and reason, and the device-and-app description supplied by Ky. It SHALL contain no private key material.
4. OSA-8.4 The genuine signature in P1 SHALL be produced by Ky on his device. A reviewer who is not the evidence author SHALL be able to reproduce each verdict from the recorded inputs.
5. OSA-8.5 UNTIL OSA-8.1 to OSA-8.4 are satisfied, ESE-17.3 SHALL remain in force: every stage needing an owner decision reports BLOCKED with `UNVERIFIABLE_APPROVER`. A passing unit test, a spike, a merged spec, or this verifier existing in the repository SHALL NOT end that state.
6. OSA-8.6 Only Ky records the disposition that B1 is closed, by an owner comment on #238 or an owner merge. No agent declares B1 closed.
7. OSA-8.7 The demonstration SHALL NOT change the ESE-2 approval bar, and SHALL NOT be reported as ending any other blocker (B2 to B5).

**Evidence/test method:** the demonstration run and evidence file (T5). Deferred.
**Dependencies:** OSA-1 to OSA-7.

---

### Requirement 9: Scope, candidates and constraints (OSA-9)

**User Story:** As Ky, I want no protected file touched and no money spent by accident.

Source: ESE-13.4; `AGENTS.governance.md` rule 7; the 00-human-agency and infra-guardrails rules.

#### Acceptance Criteria
1. OSA-9.1 Any change to a workflow, `roles.yml`, `CODEOWNERS`, `AGENTS*.md`, a pinned caller SHA, or the new pinned key file's owner-only rule SHALL be a proposed future task requiring Ky's exact request and Ky's own merge. This spec SHALL NOT be read as that request.
2. OSA-9.2 The channel SHALL cost $0 and SHALL NOT add a paid service, a hosted signing service or an always-on component.
3. OSA-9.3 The system SHALL evaluate candidate A (OpenSSH signatures) first. WHERE the T1 spike shows the device or app cannot produce an OpenSSH signature but can produce Ed25519 signatures, the system MAY use candidate B (Ed25519 over the record, verified with `ed25519_verify` from `agent_vault/token.py`, with its own domain-separation prefix). Candidate B SHALL NOT reuse `verify_token`, the vault issuer or the vault payload.
4. OSA-9.4 WHERE the T1 spike shows neither candidate works, the system SHALL record `NO_CHANNEL`, B1 SHALL stay open, and a new spec revision SHALL be required before any code.
5. OSA-9.5 No implementation code SHALL be written before T1 reports. (Source: device facts are UNKNOWN.)
6. OSA-9.6 This spec SHALL NOT change GATE-1 to GATE-5, ESE-1 to ESE-17 or SAD-1 to SAD-6.

**Evidence/test method:** diff of the implementing PRs shows no unrequested protected-path edit; T1 report on file before T2 starts. Deferred.
**Dependencies:** T1.

---

## Traceability

| Requirement | Scenarios in `scenarios.md` | Tasks in `tasks.md` |
| --- | --- | --- |
| OSA-1 | P1, A4, A6, A7, A8, A14 | T2 |
| OSA-2 | A12 | T1, T2 |
| OSA-3 | A9, A10, A17 | T2, T3 |
| OSA-4 | all | T2, T4 |
| OSA-5 | A3, A5 | T2, T3, T4 |
| OSA-6 | A2, A18 | T1, T2, T5 |
| OSA-7 | A11, A15 | T4, T6 |
| OSA-8 | all | T5, T6 |
| OSA-9 | none | T1, T3, T4 |
