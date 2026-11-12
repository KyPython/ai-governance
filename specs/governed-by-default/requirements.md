# Requirements: Every repo governed by default, before it can be created

Spec ID: GBD · Issue: #282 · Status: proposed; Ky approves by merging this spec-only PR
Author: Kiro (spec author), from Ky's 2026-11-11 instruction: "I need all repos governed the same way… it must
happen by default before a repo is even allowed to be created and any repo in my account."
Coders implement these sentences; they do not edit them to fit the code.

## Introduction

Today a repo is governed only if someone opted it in, and nothing keeps it governed. This spec makes governance
the default for every repo Ky owns: new repos can only be created governed, existing repos are swept onto the
gate and kept current, and anything outside the gate is reported, never silently skipped.

Out of scope: changing the gate's checks (`governance.yml`, `AGENTS.governance.md`), and changing any repo's
application code.

### Evidence states

- **Verified current behaviour (2026-11-11):**
  - The daily `sweep.yml` has failed on every run checked (2026-11-09, -10 and -11) with "SWEEP_TOKEN secret is
    missing", so it has opted in, protected and reported nothing.
  - `sweep.sh` reports a stale pin but never bumps it. When a repo allows only selected Actions, it adds only the
    workflow pattern, not `KyPython/ai-governance/.github/actions/system-quality`, which the current workflow
    uses. That made `KyLamportLogic/buildlogic-governance#28` fail to start.
  - `scripts/ky-new-repo` (#244) creates a governed repo from `KyPython/repo-starter` (a template repo) and
    defaults to the `KyLamportLogic` org, but nothing makes it the only way to create a repo.
  - `KyLamportLogic` is on the GitHub Team plan, and its members can create repos.
  - On 2026-11-11, 11 repos called the shared workflow, at pins 29 and 44 commits behind `main`. Three had no
    gate at all: `KyLamportLogic/LamportLogic` runs its own governance check, and `KyPython/name-that-llm` and
    `KyPython/ple-verified-harness` have no workflows.
  - `KyPython/odin-tasks` has a ruleset targeting `~ALL` branches that requires a PR for every change, so no PR
    branch can receive a commit.
- **Verified platform limits (GitHub documentation):**
  - Org rulesets apply to many repos in an org on the Team plan, and can require status checks.
  - A personal account has no account-wide rules, and nothing can stop a repo being created in it.
- **Unknown, to confirm before the matching task:**
  - Whether the `governance-mandatory` org ruleset that `ky-new-repo` refers to exists, and what it enforces.
    The available token lacks `admin:org`.
  - Whether "Require workflows to pass before merging" (a ruleset rule that runs a workflow with no file in the
    repo) is available on the Team plan. It launched for Enterprise Cloud.

### Decisions for Ky (recorded on merge)

- **D1. Where repos live.** A personal account cannot block creation, so "before a repo is allowed to be
  created" is only achievable in the org. Choose: (a) every governed repo lives in `KyLamportLogic`, and
  personal repos are moved there (each move is Ky's); or (b) personal repos stay, covered within a day of
  creation by the sweep (Requirement 3), which is detection, not prevention.
- **D2. Ruleset bypass.** Choose whether the org ruleset lets Ky bypass it (no bypass is stricter; a bypass is
  the escape hatch if the gate breaks).

## Requirements

### Requirement 1: The org refuses ungoverned repos (GBD-1)

**User Story:** As Ky, I want every repo in my org to be unable to merge anything until it is governed, so that
a new or forgotten repo can never drift outside the gate.

#### Acceptance Criteria

1. GBD-1.1 The `KyLamportLogic` org SHALL have one active org ruleset that targets all repositories, including
   repositories created later, and their default branch.
2. GBD-1.2 That ruleset SHALL require a pull request, block force-pushes and deletion of the default branch, and
   require the `ai-governance / verdict` status check.
3. GBD-1.3 WHERE "Require workflows to pass before merging" is available on the org's plan, the ruleset SHALL
   also require `KyPython/ai-governance/.github/workflows/governance.yml` at a pinned SHA, so a repo without the
   caller file is still gated.
4. GBD-1.4 The ruleset's bypass list SHALL be exactly what Ky chose in D2, and nothing else.
5. GBD-1.5 No ruleset SHALL target `~ALL` branches with a pull-request requirement, because that leaves no branch
   a PR can come from.

### Requirement 2: Repos can only be created governed (GBD-2)

**User Story:** As Ky, I want new repos to start governed, so that governance never depends on remembering an
opt-in.

#### Acceptance Criteria

1. GBD-2.1 In `KyLamportLogic`, repository creation SHALL be restricted to org owners.
2. GBD-2.2 `scripts/ky-new-repo` SHALL be the documented way to create a repo. WHEN it creates one THEN the repo
   SHALL already contain the governance caller pinned to `ai-governance` `main`, the canonical `AGENTS.md`
   section, and `CODEOWNERS`.
3. GBD-2.3 `KyPython/repo-starter` SHALL stay a template whose caller pins a SHA no older than the sweep accepts
   (GBD-3.3).
4. GBD-2.4 WHEN `ky-new-repo` targets an org THEN it SHALL confirm, before creating the repo, that the org has an
   active ruleset requiring `ai-governance / verdict` on the default branch of all repositories. IF it cannot
   confirm that (ruleset missing or inactive, the check not required, or the token lacks `admin:org`) THEN it
   SHALL create nothing, exit non-zero, and print the reason and the fix.
5. GBD-2.5 WHEN `ky-new-repo` targets a personal account THEN it SHALL refuse unless `--allow-personal` is given,
   and SHALL print that a personal repo cannot be blocked at creation and is only covered by the daily sweep.

### Requirement 3: Every existing repo is swept onto the gate and kept current (GBD-3)

**User Story:** As Ky, I want a daily sweep that covers every repo I own, personal and org, so that any repo in
my account is governed within a day.

#### Acceptance Criteria

1. GBD-3.1 The daily sweep SHALL run successfully. IF its token is missing or expired THEN the run SHALL fail and
   SHALL open or update one issue in `KyPython/ai-governance` saying so.
2. GBD-3.2 The sweep SHALL cover every non-archived, non-fork repo owned by `KyPython` and by every org where Ky
   is an admin, except those in `sweep.skip`, each with a stated reason.
3. GBD-3.3 WHEN a governed repo pins a `governance.yml` SHA other than `ai-governance` `main` THEN the sweep SHALL
   open, or keep open, one bump PR to `main`'s SHA.
4. GBD-3.4 WHEN a repo allows only selected Actions THEN the sweep SHALL allow every `KyPython/ai-governance`
   path the pinned workflow uses (`.github/workflows/governance.yml@*` and `.github/actions/*@*`).
5. GBD-3.5 The sweep SHALL never merge, change visibility, delete a repo, or change a ruleset.

### Requirement 4: Nothing is silently ungoverned (GBD-4)

**User Story:** As Ky, I want a standing list of every repo that is not fully governed and why, so that a gap is
visible the day it appears.

#### Acceptance Criteria

1. GBD-4.1 Each sweep run SHALL write a report listing every repo with one status, for example: governed and
   current, bump PR open, opt-in PR open, blocked (with the blocking reason), or skipped (with the reason).
2. GBD-4.2 The sweep SHALL keep one pinned issue in `KyPython/ai-governance` up to date with every repo that is
   not "governed and current".
3. GBD-4.3 IF a repo cannot receive a PR (for example a ruleset like GBD-1.5's) THEN the report SHALL say exactly
   which setting blocks it and what Ky must change.

### Requirement 5: Settings stay human (GBD-5)

**User Story:** As Ky, I want org settings, rulesets, tokens and repo transfers left to me, so that the agent
never holds the keys to its own gate.

#### Acceptance Criteria

1. GBD-5.1 Agents SHALL NOT create or change org rulesets, org creation settings, tokens or secrets, and SHALL
   NOT transfer repos. Each of those is a task assigned to Ky, with exact steps in `tasks.md`.
2. GBD-5.2 The sweep's token SHALL be a fine-grained or classic token that Ky creates. Its scopes SHALL be listed
   in the README, and it SHALL be stored only as the `SWEEP_TOKEN` secret.
