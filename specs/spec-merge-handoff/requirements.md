# Requirements: Spec-merge handoff

Spec ID: HANDOFF · Issue: #5 · Status: proposed; Ky approves by merging this spec-only PR

Provenance: Kiro drafted these sentences from Ky's issue #5 goal and done checks, reconciled with Ky's third (latest, authoritative) comment on that issue, which moves the handoff to a central scheduled runner in KyPython/ai-governance that holds the only copy of `CODEX_TRIGGER_PAT`. Ky owns the sentences, and coders implement them exactly; they do not paraphrase them to fit the code.

## Introduction

When a spec PR (one that changes only files under `specs/`) merges to `main` in a repo Ky has opted in, each task in that spec's `tasks.md` should become its own GitHub issue so a coder can pick it up. For `codex`-assigned issues, a comment `@codex implement this task per the linked spec and open a PR` must be posted as KyPython so that Codex (which ignores comments made with `GITHUB_TOKEN`) wakes up in Codex Cloud; Ky then taps "Create PR" himself.

This spec is for Ky (who runs and owns the mechanism) and for the coders who will build it in a later PR. Per Ky's latest comment, `CODEX_TRIGGER_PAT` is stored once, centrally, in KyPython/ai-governance, because personal accounts have no account-wide secrets. The handoff therefore runs **centrally** from KyPython/ai-governance on a schedule and on `workflow_dispatch`: a job enumerates opted-in repos (in the spirit of `scripts/sweep.sh`), detects spec-only merges to `main`, parses their `tasks.md`, opens one issue per task in that repo, and posts the `@codex` comment on `codex`-labeled issues with the central PAT. Opted-in repos hold no secrets of their own.

Reconciliation with done-check #1 is stated in full in `design.md` (## Overview). In short: the central scheduled/`workflow_dispatch` scanner is the authoritative mechanism; the "commit changes only `specs/**`" filter is evaluated centrally by inspecting each detected merge; per-repo "opt in" becomes membership in a central allowlist/discovery mechanism rather than per-repo secrets. Where done-check #1's reusable-workflow/per-repo-caller wording conflicts with the central model, the latest comment (central) wins.

Out of scope for this PR: writing any workflow YAML, Python, or tests; editing `README.md`, `AGENTS.md`, or any file outside `specs/spec-merge-handoff/`. This is a spec-only PR. The mechanism itself must never write to `specs/`, never push commits, and never merge or approve a PR; coders build the mechanism after Ky merges this spec.

## Requirements

### Requirement 1: Central handoff runner (HANDOFF-1)

**User Story:** As Ky, I want a single central workflow in KyPython/ai-governance to perform the handoff for all opted-in repos, so that `CODEX_TRIGGER_PAT` lives in exactly one place and no opted-in repo needs its own secret.

#### Acceptance Criteria

1. HANDOFF-1.1 The system SHALL perform the handoff from a central workflow in KyPython/ai-governance (`.github/workflows/spec-handoff.yml`), not from a per-repo workflow in each opted-in repo.
2. HANDOFF-1.2 WHEN the central workflow is triggered on its schedule (`on: schedule` cron) or by `on: workflow_dispatch` THEN the system SHALL scan the opted-in repos for spec-only merges and task lists and perform the handoff.
3. HANDOFF-1.3 WHEN scanning an opted-in repo THEN the system SHALL evaluate the "commit changes only `specs/**`" condition centrally by inspecting the changed paths of each detected merge to that repo's `main`, rather than relying on a per-repo push-triggered caller.
4. HANDOFF-1.4 The central workflow SHALL hold the only copy of `CODEX_TRIGGER_PAT`, and opted-in repos SHALL NOT be required to store any secret of their own for the handoff.

### Requirement 2: Opt-in discovery and allowlist (HANDOFF-2)

**User Story:** As Ky, I want a central allowlist/discovery mechanism to decide which repos are opted in, so that joining is a central membership decision and not a per-repo secret.

#### Acceptance Criteria

1. HANDOFF-2.1 The system SHALL determine opted-in repos from a central allowlist/discovery mechanism, in the spirit of `scripts/sweep.sh` (enumerate owned/admin repos via the GitHub REST API with `affiliation=owner,organization_member`, combined with an allowlist or skip list), rather than from per-repo secrets.
2. HANDOFF-2.2 IF a repo is not a member of the central allowlist/discovery set THEN the system SHALL skip that repo and open no issues in it.
3. HANDOFF-2.3 WHEN the allowlist/discovery set is empty or cannot be read THEN the system SHALL perform no handoff and SHALL report a clear message rather than acting on an unintended set of repos.

### Requirement 3: Spec-only merge detection (HANDOFF-3)

**User Story:** As Ky, I want the handoff to fire only for merges whose changes are entirely under `specs/`, so that ordinary code merges never trigger it.

#### Acceptance Criteria

1. HANDOFF-3.1 WHEN a detected merge to an opted-in repo's `main` changes only paths under `specs/` THEN the system SHALL treat that merge as a spec-only merge eligible for handoff.
2. HANDOFF-3.2 IF a detected merge changes any path outside `specs/` (even alongside spec paths) THEN the system SHALL NOT trigger the handoff for that merge.
3. HANDOFF-3.3 WHEN a spec-only merge touches more than one spec folder THEN the system SHALL perform the handoff for each changed spec folder's `tasks.md`.

### Requirement 4: One issue per task (HANDOFF-4)

**User Story:** As a coder, I want one issue per spec task with the spec path, the task text, and its requirement IDs, so that I can implement exactly one task per PR.

#### Acceptance Criteria

1. HANDOFF-4.1 WHEN a spec-only merge is detected for a spec at `specs/<slug>` THEN the system SHALL open exactly one issue per task listed in `specs/<slug>/tasks.md`.
2. HANDOFF-4.2 WHEN the system opens a task issue THEN the issue body SHALL contain the line `Spec: specs/<slug>`, the task text, and the task's requirement IDs.
3. HANDOFF-4.3 WHEN the system opens a task issue THEN the system SHALL label it with the task's assigned coder, or with `codex` when the task names no coder.

### Requirement 5: tasks.md parsing and coder-label default (HANDOFF-5)

**User Story:** As Ky, I want a well-defined `tasks.md` grammar with a default coder, so that parsing is deterministic and every task has an owner.

#### Acceptance Criteria

1. HANDOFF-5.1 The system SHALL parse `tasks.md` checklist lines of the form `- [ ] N. <task> (<ID>, ...)` into a task id `N`, the task text, and the list of referenced requirement IDs.
2. HANDOFF-5.2 WHEN a task line names its coder (for example `— coder: <name>`) THEN the system SHALL use that coder as the issue label.
3. HANDOFF-5.3 WHEN a task line names no coder THEN the system SHALL default the coder, and therefore the label, to `codex`.
4. HANDOFF-5.4 IF `specs/<slug>/tasks.md` is missing or cannot be parsed into at least one task THEN the system SHALL fail clearly for that repo and open no issues for that spec.

### Requirement 6: Idempotency marker (HANDOFF-6)

**User Story:** As Ky, I want re-runs to create no duplicate issues, so that a second scheduled scan, a re-run, or a manual dispatch is safe.

#### Acceptance Criteria

1. HANDOFF-6.1 WHEN the system opens a task issue THEN the issue body SHALL include a stable marker `<!-- spec-task: <slug>#<task-id> -->`.
2. HANDOFF-6.2 WHEN the system considers creating a task issue THEN it SHALL first search the target repo's existing issues for that task's marker and SHALL NOT create a new issue when the marker already exists.
3. HANDOFF-6.3 WHEN the handoff runs again for the same spec and commit (a re-run, a later scheduled scan, or a manual dispatch) THEN the system SHALL create zero additional issues.

### Requirement 7: At-most-once @codex comment (HANDOFF-7)

**User Story:** As Ky, I want the `@codex` comment posted only on `codex` issues and only once each, so that Codex is triggered exactly once per task without spam.

#### Acceptance Criteria

1. HANDOFF-7.1 WHEN a task issue is labeled `codex` THEN the system SHALL post the comment `@codex implement this task per the linked spec and open a PR` on that issue, using the central `CODEX_TRIGGER_PAT`.
2. HANDOFF-7.2 IF a task issue is not labeled `codex` THEN the system SHALL NOT post the `@codex` comment on it.
3. HANDOFF-7.3 WHEN the system considers commenting on a `codex` issue THEN it SHALL post the comment at most once per issue, detecting an existing `@codex` comment before posting again.

### Requirement 8: Secret handling (HANDOFF-8)

**User Story:** As Ky, I want `CODEX_TRIGGER_PAT` protected, so that it never leaks and never reaches an untrusted context.

#### Acceptance Criteria

1. HANDOFF-8.1 The system SHALL read `CODEX_TRIGGER_PAT` only from the central secret in KyPython/ai-governance, and opted-in repos SHALL hold no copy of it.
2. HANDOFF-8.2 The system SHALL NOT echo, log, or write `CODEX_TRIGGER_PAT` to step logs, outputs, artifacts, or the job summary.
3. HANDOFF-8.3 The system SHALL NOT expose `CODEX_TRIGGER_PAT` to `pull_request` runs triggered from forks.
4. HANDOFF-8.4 WHEN the system creates task issues THEN it SHALL use the least-privileged token that works (a token with `issues: write` for the target repo), reserving `CODEX_TRIGGER_PAT` for the `@codex` comment that must appear as KyPython to trigger Codex.
5. HANDOFF-8.5 IF `CODEX_TRIGGER_PAT` is missing THEN the system SHALL fail clearly and open no partial set of issues.

### Requirement 9: Workflow hygiene (HANDOFF-9)

**User Story:** As Ky, I want the central workflow to pass this repo's own gate, so that it meets the same security baseline as `governance.yml`.

#### Acceptance Criteria

1. HANDOFF-9.1 The central workflow SHALL pin every action to a full 40-character commit SHA and SHALL use only GitHub-owned actions.
2. HANDOFF-9.2 The central workflow SHALL declare explicit, minimal `permissions` at the workflow and job level (least privilege, defaulting to `contents: read`).
3. HANDOFF-9.3 The central workflow SHALL pass untrusted event and repository fields through `env` and SHALL NOT splice them into `run:` scripts.
4. HANDOFF-9.4 The central workflow SHALL be clean under `zizmor` and `actionlint`.

### Requirement 10: No writes, no merges (HANDOFF-10)

**User Story:** As Ky, I want the handoff to be strictly read-plus-issue-only, so that it can never alter a spec, push code, or merge a PR.

#### Acceptance Criteria

1. HANDOFF-10.1 The system SHALL NOT create, edit, or delete any file under `specs/` in any repo.
2. HANDOFF-10.2 The system SHALL NOT push commits to any repo.
3. HANDOFF-10.3 The system SHALL NOT merge or approve any pull request.
4. HANDOFF-10.4 The system SHALL have no write path to repository contents or merges, and this SHALL be provable by an automated test or a static check over the workflow's permissions and operations.

### Requirement 11: Automated tests citing requirement IDs (HANDOFF-11)

**User Story:** As Ky, I want automated tests run by this repo's quality job to cover the handoff behavior and cite requirement IDs, so that the gate proves the mechanism works.

#### Acceptance Criteria

1. HANDOFF-11.1 The system's implementation SHALL ship automated Python tests, run by this repo's quality (`pytest`) job, covering: `tasks.md` parsing, the coder-label default, the idempotency marker, at-most-once commenting, the missing-secret failure, the spec-only merge-detection filter, and cross-repo discovery/allowlist membership.
2. HANDOFF-11.2 WHEN the handoff runs a second time for the same spec and commit THEN a test SHALL prove that zero additional issues are created.
3. HANDOFF-11.3 WHEN a `codex` issue already has the `@codex` comment THEN a test SHALL prove that no second comment is posted.
4. HANDOFF-11.4 Each test SHALL cite the requirement ID(s) it verifies in its name or a comment (for example `# HANDOFF-6.2`).

### Requirement 12: README opt-in documentation (HANDOFF-12)

**User Story:** As a repo owner, I want the README to document how a repo opts in, so that joining the central handoff is clear.

#### Acceptance Criteria

1. HANDOFF-12.1 The system's implementation SHALL document in `README.md` how a repo joins the central allowlist/discovery mechanism (that opt-in is central membership, not a per-repo secret).
2. HANDOFF-12.2 The README SHALL document the labels used (notably `codex`) and the meaning of the coder label.
3. HANDOFF-12.3 The README SHALL state that each opted-in repo must have its Codex cloud environment set up for Codex to act on the `@codex` comment.

#### Known limit (HANDOFF)

Because the `@codex` comment is posted with `CODEX_TRIGGER_PAT`, its git/comment identity appears as KyPython; the mechanism cannot make the comment appear as a distinct bot identity while still triggering Codex. A scheduled central scan has detection latency compared with an on-merge trigger, so a task issue may be opened minutes after the spec merges rather than immediately. Central allowlist/discovery replaces per-repo secrets, so a newly created repo is not handled until it is a member of the central set.
