# Tasks: Declare each PR's file manifest in its body, not in a committed `.pr-scope`

Spec ID: PRS

One coder, one PR per task, reviewed by a different agent. No task edits `.github/workflows/`, `roles.yml`, rulesets, or any completion contract (PRS-4.2). Tasks are dependency-ordered. Status as of 2026-11-25.

- [ ] 1. Ky merges this spec-only PR (#312). Open. No admin bypass is expected now that `.pr-scope` is gone (V6); whether `diff-hygiene / hygiene` passes is recorded on the PR. Prerequisite for task 7.
- [x] 2. Add `tests/test_no_committed_pr_scope.py` (PRS-2.1, PRS-2.2). Done by #311, but its test is named `test_GATE_1_5_pr_scope_is_not_tracked_in_repo_root` and cites GATE-1.5, so PRS-2.3 is not met until task 7.
- [x] 3. Delete `.pr-scope` from the repository root (PRS-1.1). Done by #311 (`87e3415`). The U3 question is resolved by code reading (see requirements.md).
- [x] 4. Put `## Files touched` listing every changed path in a PR body (PRS-1.2, PRS-3.1). Done for this PR (body lists the three spec paths). The negative check (a missing path makes hygiene report `files outside declared manifest`, PRS-3.2) is open and unverified.
- [x] 5. Confirm the changed-file list of #311 contains none of the PRS-4.2 paths and that `ai-governance / verdict` passed (PRS-4.2). Done by #311 merging under the required checks; not independently re-verified here.
- [ ] 6. Ky decides U4 (allow or forbid a `.pr-scope` on PR branches) and records it as a requirement change in a new spec-only PR if it changes PRS-2.1 or PRS-4.1. Open. Ky only.
- [ ] 7. Follow-up: update `tests/test_no_committed_pr_scope.py` so its test name or a comment cites `PRS-1.1`, and its failure message names `.pr-scope` and cites PRS-1.1 (PRS-2.3, PRS-2.1). Keep the GATE-1.5 reference if wanted. The `Spec:` line of that PR is `Spec: specs/pr-scope-manifest`. Depends on 1.

Completion contract: this spec has none. Ky decides whether it needs one; the author does not write `completion-contract.json`. Until then the completion message says "no completion contract; not gate-verified".
