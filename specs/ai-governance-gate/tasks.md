# Tasks: AI governance spec gate and agent roles

Implemented in KyPython/ai-governance#1 after this spec merges.

- [ ] 1. Spec gate in the `policy` job: issue link, base-branch spec reference, EARS criteria, traced tests, no spec+code PRs (GATE-1.1 to GATE-1.8).
- [ ] 2. Caller template re-runs on `edited` without cancelling same-SHA runs (GATE-2.1, GATE-2.2).
- [ ] 3. `roles.yml` role map plus role gate on spec paths, on code paths (coder/owner identity check, GATE-3.7), on `roles.yml` itself, with fail-closed on a missing owner, spec paths, spec-author identities, or `coder` list (GATE-3.4) (GATE-3.1 to GATE-3.7).
- [ ] 4. Verdict scorecard: test-output parser, policy outputs, JSON summary and artifact (GATE-4.1 to GATE-4.4).
- [ ] 5. `tests/test_policy.py` cites each criterion ID; self-test runs it.
- [ ] 6. `AGENTS.governance.md` rule 2 (fixed roles, spec first, one coder per task with cross-review), `templates/spec/`, README.
- [ ] 7. Strict-repo parity: security job and guardrail policies, including the tightened `workflow_run` deploy guardrail (upstream must be a push on the default branch of the same repository, and a `push` deploy must filter to the default or an allowed release branch) (GATE-5.1 to GATE-5.7), in KyPython/ai-governance#4.
