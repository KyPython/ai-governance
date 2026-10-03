# Tasks: AI governance spec gate and agent roles

Implemented in KyPython/ai-governance#1 after this spec merges.

- [ ] 1. Spec gate in the `policy` job: issue link, base-branch spec reference, EARS criteria, traced tests, no spec+code PRs (GATE-1.1 to GATE-1.8).
- [ ] 2. Caller template re-runs on `edited` without cancelling same-SHA runs (GATE-2.1, GATE-2.2).
- [ ] 3. `roles.yml` role map plus role gate on spec paths and on `roles.yml` itself (GATE-3.1 to GATE-3.6).
- [ ] 4. Verdict scorecard: test-output parser, policy outputs, JSON summary and artifact (GATE-4.1 to GATE-4.4).
- [ ] 5. `tests/test_policy.py` cites each criterion ID; self-test runs it.
- [ ] 6. `AGENTS.governance.md` rule 2 (fixed roles, spec first, one coder per task with cross-review), `templates/spec/`, README.
