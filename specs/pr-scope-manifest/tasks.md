# Tasks: Declare each PR's file manifest in its body, not in a committed `.pr-scope`

Spec ID: PRS

One coder, one PR per task, reviewed by a different agent. No task edits `specs/`, `.github/workflows/`, `roles.yml`, rulesets, or any completion contract (PRS-4.2). Tasks are dependency-ordered.

- [ ] 1. Ky merges this spec-only PR. It fails `diff-hygiene / hygiene` because of the stale `.pr-scope`, so it needs an admin bypass (Ky only). Prerequisite for every task below.
- [ ] 2. Add `tests/test_no_committed_pr_scope.py` per design.md: a case on the real repository and a case on a temporary repository with `.pr-scope` added; cite `PRS-1.1` in the name or a comment and in the failure message (PRS-2.1, PRS-2.2, PRS-2.3). Depends on 1.
- [ ] 3. Delete `.pr-scope` from the repository root (PRS-1.1). Same PR as task 2 so the new test passes on the PR (this is what #311 does; #311 only needs `Spec: specs/pr-scope-manifest` and `Relates to #310`). Depends on 1 and 2. Record whether `diff-hygiene / hygiene` passes on that PR, which settles U3.
- [ ] 4. In that PR's body, include `## Files touched` listing every changed path (PRS-1.2, PRS-3.1). Confirm `diff-hygiene / hygiene` reports success, and that removing a path in a scratch PR body makes it report `files outside declared manifest` (PRS-3.2). Depends on 3.
- [ ] 5. Confirm the changed-file list of the code PR contains none of the paths in PRS-4.2, and that `ai-governance / verdict` passes (PRS-4.2). Depends on 3.
- [ ] 6. Ky decides U4 (allow or forbid a `.pr-scope` on PR branches) and records it as a requirement change in a new spec-only PR if it changes PRS-2.1 or PRS-4.1. Ky only.

Completion contract: this spec has none. Ky decides whether it needs one; the author does not write `completion-contract.json`. Until then the completion message says "no completion contract; not gate-verified".
