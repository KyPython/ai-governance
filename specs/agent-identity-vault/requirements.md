# Requirements: Agent Identity & Vault Credentials

Spec ID: AIV · Status: proposed; Ky approves by merging this spec-only PR  
Author: Antigravity (coder/partner) & Kiro (spec author), from Ky's 2026-11-12 instruction to codify the reviewed specification.  
Coders implement these sentences; they do not edit them to fit the code.

## Introduction

Autonomous coding agents (Antigravity, Kiro, Codex, Cursor, Grok Bot, Claude Code, Copilot) currently run with ambient developer authority. They inherit the host environment's personal API keys, SSH credentials, GitHub PATs, and cloud tokens without cryptographic binding to the specific task, agent role, or run boundary.

This specification defines a local-first, zero-cost ($0) Agent Identity and Vault Credential Broker for `KyPython/ai-governance`. It establishes:
1. Immutable agent identity records bound to specific tasks and roles.
2. Short-lived ephemeral credential grants with strict TTLs (15 min default / 60 min hard maximum).
3. Immediate hard-cut revocation and strict fail-closed stray trapping.
4. Synthesis of verified patterns from Google Cloud IAM Helper (read-only diagnosis stop-lists, permission simulation, diagnostic/mutation identity separation), TestMu Agent Assurance (three-state verdicts, empirical effect checks, evidence quoting), and dev-loop (fail-safe gate defaults, resume reconciliation, separate-role checkers).
5. Seamless verification integration with `completion-gate/completion_gate.py`.

Out of scope: commercial IAM platforms, third-party auth services (Okta, Auth0), multi-tenant cloud federation, and modifying existing completion gate verdict rules.

### Evidence States

- **Verified Current Behaviour** (as of 2026-11-12):
  - `KyPython/ai-governance` has merged `completion-gate/` (PR #271), completion contract templates (PR #273), and the pilot contract (PR #276).
  - Rule 13 ("Done means a VERIFIED completion gate") is active in `AGENTS.governance.md` (PR #272).
  - Ambient credentials are unmanaged locally: any subprocess launched by an agent inherits the full ambient environment of Ky's user session.
  - No local token issuer or registry currently exists in `KyPython/ai-governance`.
- **Intended Behaviour:**
  - Every agent action running under governed tasks must present a valid, time-bound, cryptographically signed credential grant issued against a human-approved scope contract.
  - Any out-of-scope write, expired token, or unauthenticated action fails closed as a `STRAY`, triggering an immediate `FAILED` / `UNKNOWN` verdict.

---

## Requirements

### Requirement 1: Agent Registry & Pilot Agent Pair (AIV-1)

**User Story:** As Ky, I want an immutable local registry of authorized agent identities and their permitted roles, so that agents cannot self-attest or invent arbitrary identities.

#### Acceptance Criteria

1. AIV-1.1 WHEN the registry is initialized THEN it SHALL reside in `KyPython/ai-governance` at `registry/agents.json`, version-controlled via Git and matching `registry/agents.schema.json`.
2. AIV-1.2 WHEN the registry is created THEN it SHALL define the initial pilot agent pair:
   - `antigravity`: role `author`, permitted capabilities `[repo:read, repo:write, subprocess:exec]`.
   - `kiro`: role `reviewer`, permitted capabilities `[repo:read, spec:read, spec:write, subprocess:exec]`.
3. AIV-1.3 WHEN an agent requests credential activation THEN the Vault Broker SHALL verify that the declared `agent_id` exists in `registry/agents.json` and that the requested capability set is a subset of the agent's registered capabilities.
4. AIV-1.4 IF the declared `agent_id` is unrecognized or the capability set exceeds registered permissions THEN the Vault Broker SHALL reject the request with a fail-closed `DENY` and log an authorization failure.

---

### Requirement 2: Ephemeral Credential Grants & Lifetime Bounding (AIV-2)

**User Story:** As Ky, I want task credentials to be strictly time-bound and least-privilege, so that credentials cannot be reused across tasks or linger after a task concludes.

#### Acceptance Criteria

1. AIV-2.1 WHEN a credential grant is issued THEN the Vault Broker SHALL assign a default Time-To-Live (TTL) of 15 minutes.
2. AIV-2.2 IF a credential request specifies a TTL greater than 60 minutes THEN the Vault Broker SHALL clamp the TTL to a maximum of 60 minutes or reject the request.
3. AIV-2.3 WHEN a credential grant is issued THEN the Vault Broker SHALL output an Ed25519-signed structured token containing `agent_id`, `role`, `task_id`, `scopes_hash`, `issued_at`, `expires_at`, and a unique `jti`.
4. AIV-2.4 The Vault Broker SHALL enforce that `approver != requester`; an agent SHALL NOT authorize its own credential grant or scope elevation.
5. AIV-2.5 The Vault Broker SHALL treat human-curated declarative scope contracts (`scopes.json` or `completion-contract.json`) as the exclusive Source of Truth for permitted execution scopes.

---

### Requirement 3: Revocation, Stray Trapping & Fail-Closed Defaults (AIV-3)

**User Story:** As Ky, I want immediate hard revocation and strict stray trapping, so that compromised, looping, or out-of-scope agent actions are terminated instantly.

#### Acceptance Criteria

1. AIV-3.1 WHEN a task completes, fails, or is cancelled THEN the Vault Broker SHALL immediately revoke the associated `jti` and invalidate any active process grants.
2. AIV-3.2 IF an agent executes an action using an expired, revoked, or out-of-scope credential THEN the gate/broker SHALL record a `STRAY_ACTION` in the audit log and return exit code non-zero (`UNKNOWN`/`FAILED`).
3. AIV-3.3 The system SHALL write all credential requests, grants, rejections, revocations, and stray detections to an append-only JSONL audit log (`logs/vault-audit.jsonl`).
4. AIV-3.4 IF any configuration parameter, setting, or environment flag is missing or unparseable THEN the Vault Broker SHALL default to the strictest security check and fail closed.

---

### Requirement 4: Read-Only Diagnosis & Permission Simulation (AIV-4)

**User Story:** As Ky, I want agents diagnosing failures to run read-only with explicit stop conditions and permission simulation, so that agents do not probe policies or escalate privileges.

#### Acceptance Criteria

1. AIV-4.1 WHILE an agent is diagnosing permissions or investigating a failure, the agent SHALL operate under a read-only diagnostic identity without mutation authority.
2. AIV-4.2 WHEN diagnosing an access issue, the agent SHALL evaluate an explicit stop-list and halt immediately if:
   - Access is already `GRANTED` (indicating an application-level, non-IAM failure).
   - Identity or group membership state is `UNKNOWN` (reporting the visibility gap rather than escalating).
   - A diagnostic call returns `403` / `PERMISSION_DENIED` (halting instead of probing alternate endpoints).
3. AIV-4.3 BEFORE applying any scope modification, the system SHALL simulate the access change, producing a deterministic diff (`access_before` vs `access_after`).
4. AIV-4.4 IF the permission simulation produces an ambiguous, unsupported, or unverified result THEN the scope modification SHALL fail closed and be rejected.

---

### Requirement 5: TestMu & dev-loop Verification Assurances (AIV-5)

**User Story:** As Ky, I want empirical side-effect verification and multi-agent separation of concerns, so that pass rates reflect genuine verified work.

#### Acceptance Criteria

1. AIV-5.1 The system SHALL report verdicts using three-state resolution (`VERIFIED`, `FAILED`, `UNKNOWN`), excluding `UNKNOWN` from the pass denominator and reporting test coverage as `verified / total`.
2. AIV-5.2 The verification harness SHALL verify task completion against an empirical effect-check checklist (tool calls, file diffs, database records, subprocess exit codes) and SHALL NOT accept an agent's self-generated text summary as proof.
3. AIV-5.3 Each recorded verdict in `evidence.json` SHALL quote its deterministic evidence identifiers (e.g. `tool_call_id`, `git_commit_sha`, `record_id`).
4. AIV-5.4 WHEN starting a task session THEN the system SHALL reconcile unmerged branches, worktrees, and open PRs before initiating new work.
5. AIV-5.5 The system SHALL enforce that the Author agent of a change SHALL NOT act as the Reviewer or Checker for that change.
6. AIV-5.6 IF an unresolved finding or security warning exists on a PR THEN the gate SHALL prevent merge clearance.

---

### Requirement 6: Owner Console CLI (AIV-6)

**User Story:** As Ky, I want a local command-line interface to inspect, approve, and revoke agent credentials, so that I maintain real-time operational control without web UI overhead.

#### Acceptance Criteria

1. AIV-6.1 The system SHALL provide a local CLI tool (`govctl` / `vault-ctl`) requiring $0 external infrastructure.
2. AIV-6.2 WHEN `govctl grants list` is executed THEN the CLI SHALL display all active grants, their bound `agent_id`, `task_id`, scopes, and remaining TTL.
3. AIV-6.3 WHEN `govctl revoke --all` or `govctl revoke <grant_id>` is executed THEN the CLI SHALL immediately invalidate the designated grants in the local broker.

---

### Requirement 7: Completion Gate Integration (AIV-7)

**User Story:** As Ky, I want the completion gate to cryptographically inspect agent credentials declared in task contracts, so that gate clearance proves attributed execution.

#### Acceptance Criteria

1. AIV-7.1 WHEN a task declares `agent_identity` and `credential_grant` in its `completion-contract.json` THEN `completion_gate.py` SHALL record those fields into `evidence.json`.
2. AIV-7.2 IF a contract check requires cryptographic verification of an agent grant and the token signature or grant validity cannot be verified THEN `completion_gate.py` SHALL evaluate that check to `UNKNOWN` and exit with non-zero.
