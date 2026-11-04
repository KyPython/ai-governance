# Requirements: governance rollout to all repos

Spec ID: ROLLOUT · Status: proposed; Ky approves by merging this spec-only PR

Provenance: drafted 2026-11-04 from the discovery inventory (152 local checkouts,
`sweep.sh` report-only over 34 GitHub repos) and the existing gate docs
(`AGENTS.governance.md`, `README.md`). It records what the rollout changes and the
order it changes it in.

## Introduction

After this rollout every repo Ky owns calls the shared `ai-governance / verdict`
gate, carries the `AI-GOVERNANCE:v1` agent rules, and protects its default branch
with the checks-are-the-gate model. New repos get an opt-in PR within 24 hours of
creation from a scheduled sweep, and a starter template gives them the gate files
from the first commit. Two private org repos stay blocked until Ky resolves the
failed Team payment (ROLLOUT-2.4).

The rollout opens PRs and applies branch protection. It never merges, deletes, or
changes visibility. Only Ky merges, per the governance rule that checks are the
gate and only Ky merges.

## Scope

Canonical set (from `sweep.sh` report-only, 2026-11-04):

- Needs opt-in PR (14): ci-evaluation-contract, claim-checker, claim-checker-local,
  cursor-pagination-aggregator, flaky-clock-injection, monorepo-build-graph,
  oauth-callback-state, odin-recording-preparation, oss-integration-checks,
  python-exception-propagation, repair-bench, skills-hello-github-actions,
  threshold-evaluation, vacuous-test-suite-audit (all under KyPython).
- Needs `--protect` only (1): KyPython/effectproof.
- Verify only, already protected (5): KyPython/ai-governance, KyPython/KyPython,
  KyPython/visit-taniti, KyLamportLogic/aws-career-sandbox,
  KyLamportLogic/buildlogic-governance.
- Best effort, protection API blocked (2): KyLamportLogic/LamportLogic,
  KyLamportLogic/ky-cloud-control-plane (private repos on a Free org, see
  ROLLOUT-2.4).
- Local files only, no remote yet (2): second-brain, study-engine.

Excluded: 11 forks (upstream rules forbid AI edits), WGU GitLab repos (academic
upstreams; a `.gitlab-ci.yml` port is a separate decision), vendor and cache
checkouts (marketplaces, `.gemini/history`, `.nvm`, `.verdent`,
`evaluation-lab`, `zindi-audit`, `oss/*` mirrors), legacy local-only checkouts
(IdeaProjects, Desktop, Documents), and the `human-rebuild-bootcamp` checkout
whose remote returns 404.

## Requirements

### Requirement 1: Opt-in caller in every in-scope repo (ROLLOUT-1)

**User Story:** As Ky, I want every owned repo to call the shared gate, so that
agent code cannot merge anywhere without the same checks.

#### Acceptance Criteria

1. ROLLOUT-1.1 WHEN a repo is in the canonical set THEN the repo SHALL contain
   `.github/workflows/ai-governance.yml` calling
   `KyPython/ai-governance/.github/workflows/governance.yml` at a pinned commit
   SHA that includes the ROLLOUT-4 fixes.
2. ROLLOUT-1.2 WHEN a repo is in the canonical set THEN its `AGENTS.md` SHALL
   contain the `AI-GOVERNANCE:v1` section from `AGENTS.governance.md`.
3. ROLLOUT-1.3 WHEN a repo is in the canonical set THEN its `CODEOWNERS` SHALL
   declare a global `*` owner.
4. ROLLOUT-1.4 WHEN a repo is in the canonical set THEN every `uses:` line in
   its workflows SHALL pin a full commit SHA and every workflow SHALL declare
   a least-privilege `permissions:` block.
5. ROLLOUT-1.5 The rollout SHALL NOT open opt-in PRs in forks, WGU GitLab repos,
   vendor checkouts, or repos outside the canonical set.

### Requirement 2: Branch protection on every gated repo (ROLLOUT-2)

**User Story:** As Ky, I want the default branch of every gated repo to require
the gate, so that green checks are what allow a merge.

#### Acceptance Criteria

1. ROLLOUT-2.1 WHEN `ai-governance / verdict` has passed on a repo THEN the
   rollout SHALL protect the default branch with: PR required, 0 required
   approvals, required checks (the repo CI that ran on a PR plus the verdict),
   strict up-to-date, conversation resolution, no force-push, no deletion,
   enforced on admins.
2. ROLLOUT-2.2 WHEN the repo allows squash or rebase merges THEN the protection
   SHALL also require linear history.
3. ROLLOUT-2.3 The rollout SHALL apply protection only through `optin.sh
   --protect` after the verdict has passed, and SHALL never merge, delete, or
   change visibility.
4. ROLLOUT-2.4 IF branch protection returns 403 (private repo; the org holds
   a Team subscription whose payment authorization failed, so plan features
   are suspended until Ky resolves billing with the bank) THEN the rollout
   SHALL record the repo as blocked with the billing reason and SHALL NOT
   change its visibility. Blocked repos: KyLamportLogic/LamportLogic,
   KyLamportLogic/ky-cloud-control-plane.

### Requirement 3: Tests before protection (ROLLOUT-3)

**User Story:** As Ky, I want repos without tests to get tests before the gate
locks in, so that protection never certifies untested code.

#### Acceptance Criteria

1. ROLLOUT-3.1 WHEN a repo has no test command THEN the gate SHALL fail closed
   (`require-tests: true`) until tests land.
2. ROLLOUT-3.2 IF Ky explicitly allows a repo without tests THEN the rollout
   SHALL record the `require-tests: false` exception in the rollout log with
   the reason.

### Requirement 4: Gate fixes land before callers pin (ROLLOUT-4)

**User Story:** As Ky, I want callers to pin a gate that fails closed, so that
the rollout does not stamp a leaky verdict across all repos.

#### Acceptance Criteria

1. ROLLOUT-4.1 Callers SHALL pin a SHA that includes the PR #233 verdict
   fail-closed fix and the Python quality failure-propagation fix (ruff, mypy,
   pytest as separate steps so `set -e` applies).
2. ROLLOUT-4.2 The accessibility caller in every repo, including ai-governance
   itself, SHALL pin `buildlogic-governance` at a full commit SHA, never a
   branch name.
3. ROLLOUT-4.3 `self-test.yml` SHALL keep a regression job that exercises the
   Python quality failure propagation (`tests/test_quality_step.py`).

### Requirement 5: New repos cannot exist without governance (ROLLOUT-5)

**User Story:** As Ky, I want every new repo governed from the start, so that
the rollout never goes stale.

#### Acceptance Criteria

1. ROLLOUT-5.1 WHEN a new repo appears under KyPython or KyLamportLogic THEN a
   scheduled sweep in ai-governance SHALL open an opt-in PR on it within 24
   hours.
2. ROLLOUT-5.2 A starter template repo marked `isTemplate` SHALL exist with the
   caller workflow, `AGENTS.md` section, `CODEOWNERS`, and minimal tests and CI.
3. ROLLOUT-5.3 IF the org plan permits THEN org rulesets SHALL require the
   `ai-governance / verdict` check. While the org is on Free, ROLLOUT-5.1 and
   ROLLOUT-5.2 are the enforcement path.
