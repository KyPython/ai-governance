# Design: Agent Identity & Vault Credentials

Spec ID: AIV · Status: proposed

## 1. Overview

The Agent Identity and Vault Credential system provides local, cryptographic attribution and least-privilege, short-lived credential issuance for autonomous coding agents running in `KyPython/ai-governance`.

It eliminates ambient authority by ensuring that:
1. Every executing agent subprocess is bound to a registered `agent_id` and declared `task_id`.
2. Credentials expire rapidly (15-minute default TTL, 60-minute maximum ceiling).
3. Actions attempted outside declared scopes or after revocation trigger an immediate fail-closed stray exception.
4. Independent verification is performed by the completion gate (`completion_gate.py`) and CI.

---

## 2. Architecture & Components

```
                   +---------------------------+
                   |  Ky (Human Approver)     |
                   +-------------+-------------+
                                 | scopes.json / completion-contract.json
                                 v
+------------------+     +-------------------------------+     +----------------------+
|  Agent Registry  | --> |     Local Vault Broker        | <-- |  Owner Console CLI   |
| (registry/*.json)|     | (vault_broker / govctl)       |     | (govctl grants/rev)  |
+------------------+     +---------------+---------------+     +----------------------+
                                         |
                       Issues Signed     | Revocation / Heartbeat
                       Grant Token       v
                         +-------------------------------+
                         |   Subprocess Agent Runtime    |
                         |  (Antigravity / Kiro Pilot)   |
                         +---------------+---------------+
                                         |
                                         | Writes Evidence & Diff
                                         v
                         +-------------------------------+
                         |    Completion Gate Runner     |
                         |  (completion_gate.py)         |
                         +---------------+---------------+
                                         |
                                         v
                         +-------------------------------+
                         |  Verdict: VERIFIED / FAILED   |
                         |  (UNKNOWN on invalid grant)   |
                         +-------------------------------+
```

### Components:
1. **Agent Registry (`registry/agents.json`):** Version-controlled JSON store specifying registered agents, public keys, and permitted capability boundaries.
2. **Vault Broker (`agent_vault/broker.py` & `govctl`):** Local daemon/CLI that reads root secrets, receives grant requests from agents, validates them against human-curated contracts, and issues Ed25519-signed ephemeral grant tokens.
3. **Audit Logger (`agent_vault/audit.py`):** Append-only JSONL log recorder tracking all issuance, rejection, revocation, and stray events.
4. **Token Verifier (`agent_vault/verifier.py`):** Lightweight, zero-dependency Ed25519 public key validator used by the completion gate and CI to verify token integrity offline.

---

## 3. Data & Interfaces

### 3.1 Registry Schema (`registry/agents.schema.json`)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["version", "agents"],
  "properties": {
    "version": { "type": "integer", "enum": [1] },
    "agents": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["agent_id", "role", "public_key", "permitted_capabilities"],
        "properties": {
          "agent_id": { "type": "string" },
          "role": { "type": "string", "enum": ["author", "reviewer", "auditor"] },
          "public_key": { "type": "string" },
          "permitted_capabilities": {
            "type": "array",
            "items": { "type": "string" }
          }
        }
      }
    }
  }
}
```

### 3.2 Ephemeral Token Payload (Ed25519 Signed JWT/PASETO)
```json
{
  "jti": "grant-550e8400-e29b-41d4-a716-446655440000",
  "iss": "ai-governance-local-vault",
  "sub": "antigravity",
  "role": "author",
  "task_id": "AIV-PILOT-01",
  "scopes": ["repo:read", "workspace:write"],
  "scopes_hash": "sha256:8f434346648f6b96...",
  "iat": 1731388800,
  "exp": 1731389700
}
```

### 3.3 Audit Event Schema (`logs/vault-audit.jsonl`)
```json
{
  "timestamp": "2026-11-12T04:45:00.123Z",
  "event_type": "GRANT_ISSUED | GRANT_REJECTED | GRANT_REVOKED | STRAY_ACTION",
  "agent_id": "antigravity",
  "task_id": "AIV-PILOT-01",
  "jti": "grant-550e8400-...",
  "scopes": ["repo:read", "workspace:write"],
  "details": "Granted 15m TTL against contract hash c1a8e..."
}
```

---

## 4. Error Handling & Failure Modes

1. **Unrecognized Agent ID:** Evaluates to fail-closed `DENY` (exit 1).
2. **Expired Token:** Token validation fails with `EXPIRED_GRANT`, triggering `STRAY_ACTION` audit record; verifier evaluates to `FAILED`/`UNKNOWN`.
3. **Revocation Event:** `govctl revoke` writes to local active grant revocation list; any subsequent request using revoked `jti` is halted immediately.
4. **Missing / Unparseable Config:** Broker defaults to fail-closed state (`exit 2`).
5. **Simulation Failure:** Any permission diff that cannot be statically resolved rejects the scope change.

---

## 5. Testing Strategy (Criterion ID -> Test File)

| Criterion | Description | Test File |
|---|---|---|
| AIV-1.1, AIV-1.2 | Registry schema validation and pilot pair presence | `tests/test_agent_registry.py` |
| AIV-1.3, AIV-1.4 | Capability validation and unknown agent denial | `tests/test_vault_broker.py` |
| AIV-2.1, AIV-2.2 | 15-min default TTL and 60-min cap enforcement | `tests/test_vault_broker.py` |
| AIV-2.3 | Ed25519 token signing and offline verification | `tests/test_token_verifier.py` |
| AIV-2.4 | Approver != Requester enforcement | `tests/test_vault_broker.py` |
| AIV-3.1, AIV-3.2 | Hard revocation and stray action trapping | `tests/test_stray_trapping.py` |
| AIV-3.3, AIV-3.4 | Append-only audit logging and fail-safe defaults | `tests/test_vault_audit.py` |
| AIV-4.1, AIV-4.2 | Read-only diagnosis stop-list evaluation | `tests/test_permission_simulation.py` |
| AIV-4.3, AIV-4.4 | Pre-scope simulation diff and fail-closed resolution | `tests/test_permission_simulation.py` |
| AIV-5.1, AIV-5.3 | Three-state resolution and evidence quoting | `tests/test_gate_integration.py` |
| AIV-5.5 | Author != Reviewer separation | `tests/test_agent_registry.py` |
| AIV-6.1–6.3 | Owner CLI commands (list, revoke) | `tests/test_govctl_cli.py` |
| AIV-7.1, AIV-7.2 | Completion gate token verification | `tests/test_gate_integration.py` |
