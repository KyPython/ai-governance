<!-- KIRO-AUTHORED SPEC — HUMAN ADOPTION/MERGE PENDING. Not an owner approval. Drafted 2026-11-25; model ID not exposed.
Issue: https://github.com/KyPython/ai-governance/issues/238 (OPEN; tracked here at Ky's direction, no new issue)
Source: KyPython/ai-governance@593f62f (origin/main at read time).
Authority: Ky approved writing this spec in the session on 2026-11-25. Ky adopts it only by reviewing and merging the spec-only PR.
Completion: no completion contract; not gate-verified. -->

# Requirements: Spec-author delegation check

Spec ID: SAD · Issue: #238 · Status: proposed; Ky approves by merging this spec-only PR
Implements: ESE-15.6 in `specs/engineering-stage-enforcement/requirements.md` (Amendment R1, proposed in a separate spec-only PR). Relates to CONT-05-R1 and CONT-13 in `specs/kiro-credit-failover/requirements.md` (Revision R1).
Coders implement these sentences. They do not paraphrase, reword or weaken them to fit code.

## Introduction

### Problem

The policy job lets any identity in the `spec-author` role change files under spec paths. It checks that the PR opener and the author and committer of every commit are in that role (GATE-3.1). It does not check whether a non-owner identity was asked to author that particular spec. The owner's 2026-11-12 request on #238 says "spec-author as an authorized role, not a single AI product" and says an agent may edit `specs/` only after its publishing identity is recognized in the approved role map and an issue-specific delegation is recorded. Today the first half exists and the second half does not.

### Evidence states

| State | Observation | Source |
| --- | --- | --- |
| VERIFIED GOVERNING RULE | GATE-3.1: a PR touching spec paths fails unless the opener and every commit's author and committer match a `spec-author` identity in `roles.yml`. GATE-3.2 checks only the author for a web-flow committer. GATE-3.5: the role map and spec paths are read only from `roles.yml` on `KyPython/ai-governance` `main`, never from caller inputs. GATE-3.4: an unreadable or incomplete role map fails closed. | `specs/ai-governance-gate/requirements.md` |
| VERIFIED CURRENT OBSERVATION | The policy job loads the role map from `ROLES_URL` (`https://raw.githubusercontent.com/KyPython/ai-governance/main/roles.yml`) and fails closed if it cannot load it. The role gate message is "only the spec-author role ... may change spec paths", and the pass message says the identities are "self-declared, not verified". A separate rule lets only the owner change `roles.yml`. | `.github/workflows/governance.yml` at about lines 586, 609 to 671, 969 to 984 |
| VERIFIED CURRENT OBSERVATION | `roles.yml` lists `kiro-agent[bot]` and `KyPython` as `spec-author`, and warns that author and committer fields are self-declared and that agents pushing with Ky's token appear as `KyPython`. | `roles.yml` |
| VERIFIED GOVERNING RULE | An agent that uses Ky's identity to pass the role gate is impersonation. | `AGENTS.governance.md` rule 2, "Limit" |
| VERIFIED CURRENT OBSERVATION | No delegation record exists, and the gate reads none. | `origin/main` @ `593f62f` |
| UNKNOWN | Whether Ky wants today's standing identity `kiro-agent[bot]` to need a delegation. | Owner decision |
| UNKNOWN | The delegation lifetime limit, the file name and location, and the identities to enroll. | Owner decision |
| UNKNOWN (B1) | A non-agent-forgeable owner channel. The iPhone signer is a proposal, not demonstrated. | ESE-2.2, ESE-17.3 |

### Scope and limits

- This spec describes required observable behavior of a policy-check change. It changes no file by itself.
- The eventual change touches protected paths (`.github/workflows/`, `roles.yml` or a new owner-only file, and possibly a policy script). Each is a PROPOSED future task that needs Ky's separate, exact request and Ky's own merge (AGENTS rule 7, ESE-13.4). No agent applies it.
- A delegation record raises the bar from "recognized identity" to "recognized identity and a recorded, scoped, expiring owner choice". It does not authenticate Ky as a human. While B1 is open, a delegation record is exactly as strong as the owner-only merge that created it, and that merge carries the known limit that an agent using Ky's token appears as `KyPython`. SAD-4 states this limit as a requirement so no one reports more than it gives.
- The spec preserves GATE-1 to GATE-5, owner-only merge, owner-only deploy and `ai-governance / verdict` as the required check.

---

## Requirements

### Requirement 1: Delegation required for delegated identities (SAD-1)

**User Story:** As Ky, I want an enrolled non-owner spec author to publish only the specs I asked it to write, so that being recognized does not mean being free to write any spec.

Source: #238 comment 6844321931 item 2; ESE-15.6.

#### Acceptance Criteria
1. SAD-1.1 WHEN a pull request adds, changes or deletes a file under a spec path AND any identity on that pull request (the opener, or the author or committer of any commit) is a `spec-author` identity designated as delegation-required THEN the system SHALL fail the policy job unless a valid delegation record exists for that identity, repository, issue and spec folder (SAD-2).
2. SAD-1.2 WHERE an identity is designated standing, or is the owner, the system SHALL apply the existing GATE-3.1 behavior and SHALL NOT require a delegation. (Source: verified current behavior; changing it is an owner decision, see SAD-5.2.)
3. SAD-1.3 WHEN a pull request touches several spec folders THEN the system SHALL require a valid delegation that covers each folder it touches, and SHALL fail for any folder without one.
4. SAD-1.4 The system SHALL NOT treat any identity as delegation-required or standing by default. An identity with no designation SHALL be treated as delegation-required. (Source: fail closed, GATE-3.4.)
5. SAD-1.5 The designation of an identity SHALL change only by a change to the owner-controlled role map or delegation file that the owner merges (SAD-2.4). No agent SHALL enroll itself, designate itself, or widen its own scope.

**Evidence/test method:** policy-job result for a delegated identity with, and without, a valid delegation, read back from the actual job. Deferred to implementation.
**Dependencies:** GATE-3.1 to GATE-3.5; SAD-2.

---

### Requirement 2: The delegation record and its source of truth (SAD-2)

**User Story:** As Ky, I want a delegation to be one reviewable record I merged on the base branch, so that an agent cannot create, edit or extend its own delegation inside the PR it wants to publish.

Source: GATE-3.5 (read from `main`, not caller inputs); ESE-6.1, ESE-17.1; AGENTS rule 2 limit paragraph.

#### Acceptance Criteria
1. SAD-2.1 The system SHALL read delegation records only from the owner-controlled file on `KyPython/ai-governance` `main`, and SHALL NOT read them from the pull request head, from caller inputs, from a PR or issue comment, from a label, or from a PR body. (Source: GATE-3.5.)
2. SAD-2.2 A valid delegation record SHALL name: the delegated identity; the repository; the issue; the spec folder (or folders) it may change; an expiry; and a revocation state. A record missing any of these SHALL be invalid. (Source: ESE-6.1, ESE-17.1.)
3. SAD-2.3 WHEN a delegation record is expired, revoked, or names a different identity, repository, issue or spec folder than the pull request THEN the system SHALL treat it as not valid. (Source: ESE-17.1, ESE-17.4.)
4. SAD-2.4 WHEN a pull request changes the delegation file or the role map THEN the system SHALL fail the policy job unless the opener and every commit identity match the owner, using the same rule that already protects `roles.yml`. (Source: GATE-3.3.)
5. SAD-2.5 WHEN one pull request both changes the delegation file or role map and changes a spec path THEN the system SHALL fail the policy job. A delegation that did not exist on `main` before the pull request SHALL NOT authorize that pull request.
6. SAD-2.6 The delegation lifetime limit is UNKNOWN until the owner adopts one. WHILE no limit is adopted, the system SHALL still require an expiry on every record and SHALL NOT supply a default.

**Evidence/test method:** a delegation added in the same PR fails (SAD-2.5); a delegation that exists on `main` passes only for the exact subject. Deferred to implementation.
**Dependencies:** SAD-1.

---

### Requirement 3: Fail-closed named reasons (SAD-3)

**User Story:** As Ky, I want a failure to name the missing fact, so that I can read the cause on my phone and decide.

Source: GATE-3.4; ESE-1.8; the existing role-gate message style.

#### Acceptance Criteria
1. SAD-3.1 WHEN the delegation file cannot be read, cannot be parsed, or fails its schema THEN the system SHALL fail the policy job for any pull request that touches a spec path by a delegation-required identity, and SHALL report reason `DELEGATION_UNREADABLE`.
2. SAD-3.2 The system SHALL report one of these reasons when it fails a delegation check: `NO_DELEGATION`, `DELEGATION_EXPIRED`, `DELEGATION_REVOKED`, `DELEGATION_WRONG_IDENTITY`, `DELEGATION_WRONG_REPOSITORY`, `DELEGATION_WRONG_ISSUE`, `DELEGATION_WRONG_SPEC_FOLDER`, `DELEGATION_IN_SAME_PR`, `DELEGATION_UNREADABLE`, `UNDESIGNATED_IDENTITY`. The message SHALL name the identity and the spec folder.
3. SAD-3.3 The system SHALL NOT let a stale or missing check count as a pass. A skipped delegation check SHALL be reported as not passed.
4. SAD-3.4 The system SHALL report a pass line that says the delegation was matched on the base branch and that identities are self-declared and not verified, consistent with the existing role-gate pass message.

**Evidence/test method:** each reason produced by a real job run for a matching fixture. Deferred to implementation.
**Dependencies:** SAD-1, SAD-2.

---

### Requirement 4: Honest claims about what a delegation proves (SAD-4)

**User Story:** As Ky, I want the gate never to report more assurance than it has, so that a green check is not read as proof of my decision.

Source: AGENTS rule 2 "Limit"; ESE-2.1 to ESE-2.5; ESE-17.2, ESE-17.3; 00-human-agency rule on consequential decisions.

#### Acceptance Criteria
1. SAD-4.1 The system SHALL NOT accept a PR or issue comment, a label, a commit message, a PR body, a bot-supplied JSON, or a commit signature as, by itself, a delegation or as evidence of the owner's consent. (Source: ESE-2.1, ESE-2.5.)
2. SAD-4.2 The system SHALL NOT infer that Ky authored or approved a delegation from a `KyPython` appearance, a web-flow committer, or a token-based identity. (Source: ESE-2.4.)
3. SAD-4.3 WHILE no independent owner-only signing channel with trusted verification has been demonstrated by observed execution evidence (B1), the delegation check SHALL describe its result as "recorded on the base branch by an owner-identity merge" and SHALL NOT describe it as "owner-authenticated" or "verified human approval". (Source: ESE-17.3.)
4. SAD-4.4 The system SHALL NOT use a delegation to authorize anything other than publishing a spec-only change under the named spec folders. A delegation SHALL NOT authorize code, a merge, a deployment, spend, a role change, or a change to protected paths. (Source: ESE-1.9; AGENTS rule 7.)

**Evidence/test method:** a `KyPython` comment saying "delegated" does not pass; report wording is checked. Deferred to implementation.
**Dependencies:** ESE-2, ESE-17.

---

### Requirement 5: Preservation of existing behavior and ownership (SAD-5)

**User Story:** As Ky, I want today's working flow to keep working until I decide to change it, so that adding this check does not stop Kiro or me.

Source: verified current behavior; ESE-13.4; AGENTS rules 1, 2, 7.

#### Acceptance Criteria
1. SAD-5.1 The system SHALL leave GATE-1 to GATE-5 behavior unchanged for every pull request that does not involve a delegation-required identity, including the code-path rules, the exemption rule, the owner-only `roles.yml` rule, and the coder rules.
2. SAD-5.2 WHEN the owner has not designated `kiro-agent[bot]` as delegation-required THEN the system SHALL keep today's behavior for it. Whether Kiro should need a delegation is an owner decision and is UNKNOWN here.
3. SAD-5.3 The system SHALL keep `ai-governance / verdict` as the required check, SHALL keep owner-only merge, and SHALL NOT enable auto-merge or any automatic approval.
4. SAD-5.4 The change that implements SAD-1 to SAD-4 SHALL be a proposed future task. It SHALL NOT be made by an agent without Ky's explicit request and Ky's own merge, and an agent SHALL NOT edit a gate to make it pass. (Source: AGENTS rule 7; ESE-13.4.)
5. SAD-5.5 The system SHALL NOT introduce a wildcard identity, a pattern match on identity names, or a catch-all entry for any role. Each identity is an exact, enrolled entry.
6. SAD-5.6 Downstream repositories SHALL receive the new behavior only by the owner's existing pinned-SHA promotion, with full immutable SHA pins kept. (Source: ESE-13.3; AGENTS rule 10.)

**Evidence/test method:** the existing `tests/test_policy.py` GATE-3 cases still pass unchanged; a standing identity's spec PR passes with no delegation. Deferred to implementation.
**Dependencies:** GATE-1 to GATE-5.

---

### Requirement 6: Real-boundary positive and adverse acceptance (SAD-6)

**User Story:** As Ky, I want acceptance to come from the actual policy job and not from a mock, so that a check that always denies or always passes cannot look correct.

Source: ESE-9 to ESE-14 method; CONT-12-R1.

#### Acceptance Criteria
1. SAD-6.1 The implementation SHALL show, from a real policy-job run, a positive case: an enrolled delegation-required identity with a valid delegation on `main` for the exact repository, issue and spec folder passes a spec-only PR.
2. SAD-6.2 The implementation SHALL show each adverse case in `scenarios.md` failing at the policy job for the named reason, read back from the job result and not from a mock whose return value the test sets.
3. SAD-6.3 The implementation SHALL show that an always-deny check fails the positive case, and that an always-pass check fails the adverse cases.
4. SAD-6.4 Tests SHALL cite the SAD criterion IDs they verify, so that the existing spec gate can link tests to this spec.
5. SAD-6.5 WHEN any adverse case passes, or the positive case fails, the implementation SHALL be reported FAILED. Skipped CI SHALL NOT count as a pass.

**Evidence/test method:** policy-job runs for each scenario, with job results quoted. Deferred to implementation.
**Dependencies:** SAD-1 to SAD-5.

---

## Out of scope

- Enrolling any identity, or deciding which identities need a delegation.
- Any change to `roles.yml`, workflows, `CODEOWNERS` or `AGENTS*.md` by this spec.
- The owner-only approval channel (B1), which stays under ESE.
- The coder role. SAD covers publishing under spec paths only.
- The capability registry and stage evaluation, which stay under `specs/kiro-credit-failover`.

## Traceability

| Requirement | Scenarios in `scenarios.md` | Tasks in `tasks.md` |
| --- | --- | --- |
| SAD-1 | P1, P2, A1, A8, A9 | T1, T2, T3 |
| SAD-2 | P1, A2, A3, A4, A5, A6, A10 | T1, T2, T3, T4 |
| SAD-3 | A1 to A7, A11 | T2, T3 |
| SAD-4 | A12, A13 | T2, T3, T5 |
| SAD-5 | P2, A10, A14 | T1, T3, T6 |
| SAD-6 | all | T2, T3, T6 |
