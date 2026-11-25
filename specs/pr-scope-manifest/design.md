# Design: Declare each PR's file manifest in its body, not in a committed `.pr-scope`

Spec ID: PRS

## Overview

Remove the committed `.pr-scope` from `main`, add a test that fails if it is tracked again, and document the PR-body manifest format. No workflow, gate, role, or ruleset changes. Evidence states and Unknowns are in `requirements.md`.

## Architecture / components

| Component | Owner | Role | Changed by this spec's implementation? |
|---|---|---|---|
| `.pr-scope` (repo root) | this repo | Committed manifest read first by hygiene (V2) | Deleted (PRS-1.1) |
| `tests/test_no_committed_pr_scope.py` | this repo | Guard test | Added (PRS-2.1 to 2.3), already drafted in #311 |
| `diff-hygiene / hygiene` | `KyLamportLogic/buildlogic-governance@c9edd8f5...` | Compares changed files to manifest | No |
| `governance.yml` policy step | this repo | Counts `.pr-scope` as code (V4) | No (PRS-4.2) |
| PR body `## Files touched` | PR author | Manifest after the file is gone | Convention (PRS-1.2, PRS-3.1) |

## Data and interfaces

Manifest in the PR body: a heading `## Files touched`, then one path per line. A leading `- ` list marker is what existing PRs (#305) use; the script's accepted line syntax at the pinned SHA is not re-verified here, so authors should copy the form of a PR that passed hygiene.

Guard test shape (behavioral, not a source-text check): run `git ls-files -- .pr-scope` in the repository root and assert the output is empty, with a message containing `PRS-1.1`. A second case builds a temporary git repository, runs `git add .pr-scope`, and asserts the same check reports a failure, so the test cannot pass vacuously.

## Error handling and failure modes

- Stale file returns: the guard test fails with a message naming `.pr-scope` and `PRS-1.1`.
- Author omits a path: hygiene fails with `files outside declared manifest` (PRS-3.2). Fix by editing the PR body with `gh api -X PATCH`.
- Bootstrap deadlock (verified, F2 plus V5): this spec PR and #311 touch paths absent from the stale 5-path manifest. This spec PR therefore fails `diff-hygiene / hygiene`, which ruleset 26571875 requires. It passes `ai-governance / verdict` independently (U2). Only an admin bypass merges it. #311 is a code PR, so its `Spec:` line must name a spec already on `main`; it cannot go first.
- Order that avoids a second bypass (inference, depends on U3): merge this spec with Ky's admin bypass, then #311 cites `Spec: specs/pr-scope-manifest`. If hygiene reads `.pr-scope` from the PR head, #311 (which deletes it) passes on its own. If it reads from the base, #311 needs a bypass too.
- Per-PR file on a PR branch: fails the guard test (PRS-4.1 note, U4).

## Options considered

| Option | Result | Why not chosen |
|---|---|---|
| Delete `.pr-scope`, add guard test (chosen) | Matches #310 proposal; no gate change | Needs one admin bypass to bootstrap. |
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

- HOLD 1: Ky merges this spec-only PR (needs admin bypass of the hygiene check, see above).
- HOLD 2: Ky merges the code PR (#311 or a replacement) after review by a different agent.
