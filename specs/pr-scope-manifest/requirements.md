# Requirements: Declare each PR's file manifest in its body, not in a committed `.pr-scope`

Spec ID: PRS · Issue: #310 · Status: proposed; Ky approves by merging this spec-only PR. Revised 2026-11-25 after #311 merged (see Evidence states).

Provenance: drafted by Kiro on 2026-11-25 for Ky (goal: unblock `diff-hygiene / hygiene` on spec-only PRs). Ky owns the sentences; coders implement them and must not paraphrase them to fit the code.

## Introduction

The `diff-hygiene / hygiene` check (reusable workflow `KyLamportLogic/buildlogic-governance@c9edd8f567bc8c800f4a3bb92b032ffedfc52329`, script `specs/accessibility-enforcement/scripts/run-diff-hygiene.js`, REQ-K3/H6) compares a PR's changed files with a declared manifest. A committed `.pr-scope` file takes precedence over the PR body, so a `.pr-scope` left on `main` overrides every later PR's declared manifest. This spec fixes where the manifest lives and adds a guard so the stale-file state cannot return.

This spec covers: the default branch (`main`) of `KyPython/ai-governance`, one guard test, and the format of the PR-body manifest.

This spec does not cover:
- Changing the policy gate in `.github/workflows/governance.yml`, including how it classifies `.pr-scope` (it is not in the exempt patterns, so it counts as code and cannot share a PR with spec files). Changing the gate needs Ky's explicit request.
- Changing the reusable diff-hygiene workflow or its script (owned by `KyLamportLogic/buildlogic-governance`).
- Changing the rulesets or required checks on `main`.
- Per-PR `.pr-scope` files on PR branches, other than what PRS-4.1 states.
- Problem 2 of #310 (policy tests depending on global git config); that is #306.

## Evidence states

Observation date 2026-11-25. V1 to V5 and F1 to F2 were first observed at `2b480c0ce9852c92a45dd00a4184edd08449ca2f`. V6 to V8 were observed after #311 merged (`87e341541264c65abc060de229af37bd6ef842e9`).

### Verified current behavior
- V1. (Historical, true at `2b480c0`; superseded by V6.) `.pr-scope` was added to `main` by #233 (6c667f4) with 17 stale paths. After #309 it lists 5 paths: `.github/workflows/governance.yml`, `.github/workflows/sweep.yml`, `requirements.txt`, `.pr-scope`, `tests/test_workflow_shell_syntax.py`. (Observed in a fresh clone at `2b480c0`.)
- V2. The diff-hygiene script reads the manifest from a committed `.pr-scope` first (one path per line, an exact path or a prefix ending `/`). Only when that file is absent does it read a `## Files touched` section of the PR body (env `PR_BODY`). It fails with `files outside declared manifest`. (Re-read 2026-11-25 from `run-diff-hygiene.js` at the pinned SHA: `parseManifest()` uses `.pr-scope` in the working directory if it exists, otherwise the `## Files touched` section of `PR_BODY`, stripping a leading `-` or `*` marker and backticks.)
- V3. `.github/workflows/accessibility.yml` runs `diff-hygiene` as a separate workflow from `governance.yml`; `governance.yml` has no reference to hygiene. (Read in the clone.)
- V4. The policy step of `governance.yml` treats a PR whose changed files are all exempt by path rule, with at least one under `specs/` or `.kiro/specs/`, as a spec-only PR, and does not require the `Spec:` target to exist on base for that PR. `.pr-scope` matches none of the exempt patterns (`DOC_RE`, `META_RE`, `CONFIG_RE`, `LOCK_RE`, requirements files, `roles.yml`), so it counts as code. A PR with code and spec paths fails.
- V6. Ky merged #311 (`87e341541264c65abc060de229af37bd6ef842e9`) before this spec. On `main` after that merge, `.pr-scope` is no longer tracked at the repository root (the commit deletes it). This is the state PRS-1.1 requires.
- V7. #311 added `tests/test_no_committed_pr_scope.py`. Its test `test_GATE_1_5_pr_scope_is_not_tracked_in_repo_root` cites GATE-1.5 of `specs/ai-governance-gate`, not a PRS ID, because #311 merged before this spec existed. The guard therefore shipped without its own spec; the Codex review thread on #311 asked for one. This spec supplies it. Until the follow-up in tasks.md task 7 lands, the test does not cite PRS-1.1, so PRS-2.3 is not yet met.
- V8. Also merged since the first draft: #303 (inspect-ass bump to 0.3.291) and #309 (CI repair). Neither touches `.pr-scope` semantics. (Not re-read in detail here.)
- V5. Ruleset `main ruleset` (id 26571875, enforcement active, target `refs/heads/main`) requires both `ai-governance / verdict` and `diff-hygiene / hygiene`. Ruleset `main` (id 26302736) requires only `ai-governance / verdict`. Both list one bypass actor: repository role id 5 (admin), mode `always`.

### Intended existing behavior
- I1. `.pr-scope` is documented as an optional, per-PR file (#310).
- I2. Only Ky merges PRs in this repository (AGENTS.md).

### Verified failures
- F1. PRs #305, #306, #307 and #308 each failed `diff-hygiene / hygiene` with `files outside declared manifest` until the file was overridden. #304 passed only because `governance.yml` happened to be listed.
- F2. (Historical; the cause was removed by #311.) A spec-only PR cannot update `.pr-scope`, because the policy gate counts it as code (V4). So a spec-only PR that is not in the stale manifest cannot pass hygiene.

### Unknowns
- U1. Resolved 2026-11-25: `diff-hygiene / hygiene` IS a required status check on `main` (V5, ruleset 26571875). Admins can bypass.
- U2. Resolved 2026-11-25: `ai-governance / verdict` does not depend on hygiene (V3). They are separate workflows and checks.
- U3. Resolved 2026-11-25 by reading code, not by a CI observation: neither head nor base exactly. The reusable workflow `diff-hygiene.reusable.yml` at the pinned SHA runs `actions/checkout` with no `ref`, and `run-diff-hygiene.js` reads `.pr-scope` from that working directory. For a `pull_request` event, `actions/checkout` defaults to the PR merge ref (head merged into base). So the file is read from the merged tree: a PR that deletes `.pr-scope` sees it absent and falls back to the body; a PR that does not touch it sees base's copy. The checkout default is documented behavior of the action, not re-run here. Consequence: with `.pr-scope` gone from `main` (V6), hygiene reads the body manifest.
- U4. Open: whether a PR branch that carries a `.pr-scope` can pass CI, given PRS-2.1 as written (see PRS-4.1).

## Requirements

### Requirement 1: No committed manifest on the default branch (PRS-1)

**User Story:** As Ky, I want each PR judged against its own declared manifest, so that an earlier PR's file list never decides a later PR's hygiene result.

Rationale/source: V1, V2, F1, F2; #310 Problem 1.
Prerequisite: none.

#### Acceptance Criteria

1. PRS-1.1 The default branch of this repository SHALL NOT contain a tracked file named `.pr-scope` at the repository root.
2. PRS-1.2 WHEN a PR declares its file manifest THEN the PR SHALL declare it in a `## Files touched` section of the PR body.

Acceptance evidence: PRS-1.1: `git ls-files .pr-scope` prints nothing on `main` after the implementing PR merges. PRS-1.2: the PR body of the implementing PR contains the section.

### Requirement 2: Guard test (PRS-2)

**User Story:** As Ky, I want a failing test if `.pr-scope` is committed again, so that the stale-manifest state cannot return unnoticed.

Rationale/source: V2, F1; review thread on #311.
Prerequisite: PRS-1.1 (the test asserts it).

#### Acceptance Criteria

1. PRS-2.1 IF `.pr-scope` is tracked at the repository root THEN a repository test SHALL fail, and its failure message SHALL name the file and cite PRS-1.1.
2. PRS-2.2 The test SHALL decide by tracked state (`git ls-files`), not by whether a file exists in the working tree.
3. PRS-2.3 The test's name or a comment in it SHALL cite `PRS-1.1`, so the spec gate can match it to the criterion.

Acceptance evidence: `tests/test_no_committed_pr_scope.py` (introduced by #311) passes on a tree without a tracked `.pr-scope`, fails on a temporary repository where `.pr-scope` is added with `git add`, and cites `PRS-1.1`. The test is run by `python3 -m pytest -q`.

### Requirement 3: Body manifest format (PRS-3)

**User Story:** As a PR author, I want one rule for what the body manifest contains, so that hygiene does not fail on a path I forgot to list.

Rationale/source: V2, F1.
Prerequisite: PRS-1.1 (the body is read only when no `.pr-scope` file exists).

#### Acceptance Criteria

1. PRS-3.1 The `## Files touched` section SHALL list every path the PR changes, one per line, each as an exact path or as a prefix ending `/`.
2. PRS-3.2 IF a changed path is neither listed nor under a listed prefix THEN the PR SHALL be treated as not ready, and the author SHALL add the path to the body (the hygiene check reports `files outside declared manifest`).

Acceptance evidence: on a PR whose body lists every changed path and whose base has no `.pr-scope`, `diff-hygiene / hygiene` reports success. Removing one path from the body makes it report `files outside declared manifest`.

### Requirement 4: Scope boundary for file-form manifests (PRS-4)

**User Story:** As Ky, I want a clear limit on what this spec changes, so that no one edits the policy gate or the hygiene workflow to make a PR pass.

Rationale/source: V4, V5; AGENTS.md rule 7.
Prerequisite: PRS-1.1.

#### Acceptance Criteria

1. PRS-4.1 A PR that needs its manifest in a file rather than the body MUST NOT merge a `.pr-scope` into the default branch.
2. PRS-4.2 Implementation of PRS-1 to PRS-3 MUST NOT edit `.github/workflows/governance.yml`, `.github/workflows/accessibility.yml`, `roles.yml`, any ruleset, or any completion contract.

Acceptance evidence: PRS-4.1: PRS-2.1 fails any PR whose tree tracks the file, so it cannot merge with CI green. PRS-4.2: the implementing PR's changed-file list contains none of those paths.

Note on PRS-4.1: as PRS-2.1 is written, a PR branch that tracks `.pr-scope` fails the guard test on that PR. This spec therefore leaves file-form manifests on PR branches effectively unsupported while the guard exists. Whether to allow them (for example by testing only the default branch) is Ky's call; see U4.
