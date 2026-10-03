# Tasks: AI governance spec gate

- [x] 1. Add the spec gate to the `policy` job in `.github/workflows/governance.yml` (GATE-1.1 to GATE-1.6).
- [x] 2. Make the issue link mandatory for code PRs and drop the branch-name exemption (GATE-1.1, GATE-1.6).
- [x] 3. Add `edited` and same-SHA no-cancel to the caller template (GATE-2.1, GATE-2.2).
- [x] 4. Add tests in `tests/test_policy.py` that cite each criterion ID.
- [x] 5. Add `templates/spec/` and the spec-first rule in `AGENTS.governance.md`.
