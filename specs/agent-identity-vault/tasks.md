# Tasks: Agent Identity & Vault Credentials (AIV)

Each task is implemented by one coder in its own PR, reviewed by a different agent. Ky merges. Order is dependency order.  
No code is written for these tasks until Ky merges this spec-only PR.

- [ ] **T1. Agent Registry Schema & Pilot Pair** (AIV-1.1, AIV-1.2, AIV-5.5). Spec/schema PR adding `registry/agents.schema.json` and `registry/agents.json` defining the pilot pair (`antigravity` and `kiro`), with schema validation tests in `tests/test_agent_registry.py`. Depends on: spec merge.
- [ ] **T2. Cryptographic Token Engine** (AIV-2.3, AIV-7.2). Code PR implementing zero-dependency Ed25519 token signing, parsing, and offline signature validation in `agent_vault/token.py` with tests in `tests/test_token_verifier.py`. Depends on: T1.
- [ ] **T3. Vault Broker Core & TTL Bounding** (AIV-1.3, AIV-1.4, AIV-2.1, AIV-2.2, AIV-2.4, AIV-2.5). Code PR implementing the grant request handler, 15-minute default TTL, 60-minute hard cap, and human scope contract binding in `agent_vault/broker.py` with tests in `tests/test_vault_broker.py`. Depends on: T2.
- [ ] **T4. Revocation, Stray Trapping & Audit Logging** (AIV-3.1–3.4). Code PR implementing hard-cut revocation, append-only JSONL audit logging (`logs/vault-audit.jsonl`), and strict stray trapping in `agent_vault/audit.py` and `agent_vault/stray.py` with tests in `tests/test_stray_trapping.py` and `tests/test_vault_audit.py`. Depends on: T3.
- [ ] **T5. Read-Only Diagnosis Stop-List & Permission Simulator** (AIV-4.1–4.4). Code PR implementing the read-only diagnostic wrapper, stop-list evaluation (`GRANTED`, `UNKNOWN`, `403`), and pre-scope simulation diff in `agent_vault/simulator.py` with tests in `tests/test_permission_simulation.py`. Depends on: T3.
- [ ] **T6. Owner Console CLI (`govctl`)** (AIV-6.1–6.3). Code PR implementing the terminal CLI for grant inspection, active grant listing, and emergency revocation in `agent_vault/cli.py` (entry point `govctl`) with tests in `tests/test_govctl_cli.py`. Depends on: T4.
- [ ] **T7. Completion Gate Integration & Evidence Extension** (AIV-5.1–5.4, AIV-7.1, AIV-7.2). Code PR wiring token attestation and credential grant inspection into `completion-gate/completion_gate.py` and updating the contract template in `templates/spec/completion-contract.json` with integration tests in `tests/test_gate_integration.py`. Depends on: T2, T4.

| Requirement | Tasks |
|---|---|
| AIV-1 | T1, T3 |
| AIV-2 | T2, T3 |
| AIV-3 | T4 |
| AIV-4 | T5 |
| AIV-5 | T1, T7 |
| AIV-6 | T6 |
| AIV-7 | T2, T7 |
