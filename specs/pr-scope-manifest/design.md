# Design: Declare each PR's file manifest in its body, not in a committed `.pr-scope`

Spec ID: PRS

## Overview

Keep the committed `.pr-scope` off `main`, keep a test that fails if it is tracked again, and document the PR-body manifest format. No workflow, gate, role, or ruleset changes. The deletion and the test already shipped in #311 (merged before this spec); this spec supplies the requirements they trace to. Evidence states and Unknowns are in `requirements.md`.

## Architecture / components

| Component | Owner | Role | Changed by this spec's implementation? |
|---|---|---|---|
| `.pr-scope` (repo root) | this repo | Committed manifest read first by hygiene (V2) | Deleted by #311 (PRS-1.1 holds on `main`) |
| `tests/test_no_committed_pr_scope.py` | this repo | Guard test | Added by #311; cites GATE-1.5, so PRS-2.3 needs the follow-up (tasks.md task 7) |
| `diff-hygiene / hygiene` | `KyLamportLogic/buildlogic-governance@c9edd8f5...` | Compares changed files to manifest | No |
| `governance.yml` policy step | this repo | Counts `.pr-scope` as code (V4) | No (PRS-4.2) |
| PR body `## Files touched` | PR author | Manifest after the file is gone | Convention (PRS-1.2, PRS-3.1) |

## Data and interfaces

Manifest in the PR body: a heading `## Files touched`, then one path per line. A leading `- ` list marker is what existing PRs (#305) use; the script's accepted line syntax at the pinned SHA is not re-verified here, so authors should copy the form of a PR that passed hygiene.

Guard test shape (behavioral, not a source-text check): run `git ls-files -- .pr-scope` in the repository root and assert the output is empty, with a message containing `PRS-1.1`. A second case builds a temporary git repository, runs `git add .pr-scope`, and asserts the same check reports a failure, so the test cannot pass vacuously.

## Error handling and failure modes

- Stale file returns: the guard test fails with a message naming `.pr-scope` and `PRS-1.1`.
- Author omits a path: hygiene fails with `files outside declared manifest` (PRS-3.2). Fix by editing the PR body with `gh api -X PATCH`.
- Historical: bootstrap deadlock (F2 plus V5). While the stale 5-path `.pr-scope` was on `main`, this spec PR and #311 touched paths absent from it, so both would fail `diff-hygiene / hygiene`, which ruleset 26571875 requires. #311 is a code PR whose `Spec:` line must name a spec already on `main`, so it could not wait for this spec.
- Historical: resolution. Ky merged #311 first (`87e3415`), which deleted `.pr-scope`. With the file gone, hygiene reads the PR body (V2, U3), so this spec PR no longer depends on the stale manifest. Whether hygiene now passes on this PR is recorded in the PR, not asserted here.
- Per-PR file on a PR branch: fails the guard test (PRS-4.1 note, U4).

## Options considered

| Option | Result | Why not chosen |
|---|---|---|
| Delete `.pr-scope`, add guard test (chosen; done by #311) | Matches #310 proposal; no gate change | Needed #311 to merge before its spec; resolved by merging in that order. |
| Exempt `.pr-scope` in the policy gate so spec PRs can edit it | Spec-only PRs could update the file | Edits the gate (AGENTS.md rule 7); out of scope. Keeps a per-PR file living on `main`. |
| Remove `diff-hygiene / hygiene` from required checks | Unblocks PRs | Changes a ruleset and weakens enforcement; Ky's decision, not this spec's. |

## Testing strategy (criterion ID -> test file)

| Criterion | Test or evidence |
|---|---|
| PRS-1.1 | `tests/test_no_committed_pr_scope.py` |
| PRS-1.2 | PR body inspection on the implementing PR (no automated test) |
| PRS-2.1, PRS-2.2, PRS-2.3 | `tests/test_no_committed_pr_scope.py` |
| PRS-3.1, PRS-3.2 | `diff-hygiene / hygiene` result on the implementing PR; no repository test |
| PRS-4.1 | PRS-2.1 test |
| PRS-4.2 | Changed-file list of the implementing PR |

## Human gates

- HOLD 1: Ky merges this spec-only PR.
- HOLD 2: Ky merges the follow-up PR that updates the guard test's citation (tasks.md task 7), after review by a different agent. #311 is already merged.
