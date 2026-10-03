# Requirements: AI governance spec gate and agent roles

Spec ID: GATE · Issue: #2 · Status: proposed; Ky approves by merging this spec-only PR

Provenance: Grok Bot (executor agent) drafted these sentences from Ky's 2026-10-03 instructions, standing in for Kiro during the bootstrap, and committed them with Ky's token. Ky owns the sentences, and coders must not paraphrase them to fit the code.

## Introduction

Every agent has a fixed role. Kiro writes specs in spec-only PRs that merge first. Coders implement specs that already exist on `main`; Kiro's builders count as coders too. Each task in `tasks.md` goes to one coder in its own PR, reviewed by a different agent. Ky approves and merges. The `policy` job of the shared `ai-governance / verdict` gate enforces this in every repo.

The spec format follows Kiro's layout (`requirements.md`, `design.md`, `tasks.md`, EARS acceptance criteria). The traceability follows the requirement-ID → test pattern Ky already uses:

- LamportLogic: the `AUTH-REQ-001` matrix;
- ZeroAPI: `EO-1` trace labels;
- human-rebuild-bootcamp: `GOLDEN_SPEC.md` `[R-SPEC-F1]` IDs.

## Requirements

### Requirement 1: Spec gate for code changes (GATE-1)

**User Story:** As Ky, I want every AI-authored code change to implement a spec that was written and merged first, so that agents build agreed behavior instead of inventing it.

#### Acceptance Criteria

1. GATE-1.1 WHEN a pull request changes a code path THEN the system SHALL fail the policy job unless the PR body links an issue (`Closes #N`, `Relates to #N`, or an issue URL).
2. GATE-1.2 WHEN a pull request changes a code path AND its body does not reference, with a `Spec: <spec-path>/<slug>` line, a spec folder that already exists on the base branch THEN the system SHALL fail the policy job.
3. GATE-1.3 WHEN the referenced spec folder on the base branch has no `requirements.md`, or its `requirements.md` contains no numbered EARS acceptance criterion (`<PREFIX>-<n>.<m> ... SHALL ...`) THEN the system SHALL fail the policy job.
4. GATE-1.4 WHEN a pull request changes a code path AND no added or changed test file cites an acceptance-criterion ID or requirement ID from the referenced spec THEN the system SHALL fail the policy job.
5. GATE-1.5 WHEN every changed path matches the explicit exemption rule THEN the system SHALL pass the spec gate without a spec. The rule covers docs, spec and contract files, repo metadata, GitHub workflow and template files, lockfiles, `requirements*.txt`, and `package.json` changes limited to dependency keys.
6. GATE-1.6 WHEN deciding whether a pull request is exempt THEN the system SHALL ignore labels, branch names, and PR authors.
7. GATE-1.7 WHEN a pull request changes a code path AND adds, changes, or deletes a file under a spec path THEN the system SHALL fail the policy job.
8. GATE-1.8 WHEN a pull request changes only spec paths and other exempt paths THEN the system SHALL pass the spec gate, subject to the role gate (GATE-3).

### Requirement 2: Gate re-runs on PR metadata edits (GATE-2)

**User Story:** As Ky, I want the verdict to reflect the PR's current title and body, so that removing an issue or spec link after a green run cannot slip through.

#### Acceptance Criteria

1. GATE-2.1 WHEN a pull request's title or body is edited THEN the caller template SHALL re-run the gate (`pull_request` types include `edited`).
2. GATE-2.2 WHEN a re-run is triggered on the same commit THEN the caller template SHALL NOT cancel the in-flight run.

### Requirement 3: Fixed agent roles (GATE-3)

**User Story:** As Ky, I want one role map that every repo's gate enforces, so that only Kiro (or I) author specs and coders only implement them.

#### Acceptance Criteria

1. GATE-3.1 WHEN a pull request adds, changes, or deletes a file under a spec path THEN the system SHALL fail the policy job unless the PR opener and the author and committer of every commit in the PR match an identity of the `spec-author` role in `roles.yml`.
2. GATE-3.2 WHEN a commit's committer is GitHub's web-flow identity (`noreply@github.com`) THEN the system SHALL check only that commit's author.
3. GATE-3.3 WHEN a pull request in KyPython/ai-governance changes `roles.yml` THEN the system SHALL fail the policy job unless the PR opener and every commit identity match the owner in `roles.yml`.
4. GATE-3.4 IF `roles.yml` cannot be read or lacks an owner, spec paths, or spec-author identities THEN the system SHALL fail the policy job.
5. GATE-3.5 The system SHALL read the role map and spec paths only from `roles.yml` on KyPython/ai-governance `main`, and SHALL NOT accept caller inputs that change roles or spec paths.
6. GATE-3.6 WHEN `kiro-agent[bot]` opens or commits to a code PR THEN the system SHALL apply the same code rules as for every other coder, including GATE-1.7.

### Requirement 4: Verdict scorecard (GATE-4)

**User Story:** As Ky, I want every verdict to publish a short machine-readable summary, so that I can see what each task PR covered, check reviewers' claims, and compare the occasional head-to-head build.

#### Acceptance Criteria

1. GATE-4.1 WHEN the gate runs THEN the verdict job SHALL publish a JSON scorecard (schema `ai-governance-summary/v1`) in the job summary, as the `ai-governance-summary` artifact, and as the reusable workflow's `summary` output.
2. GATE-4.2 The scorecard SHALL include:
   - tests passed, failed, and total;
   - the requirement IDs cited by the PR's changed tests and the referenced spec;
   - the number of failed checks and of policy errors;
   - the number of changed lines (excluding lockfiles) and changed files.
3. GATE-4.3 WHEN the test output comes from Jest, Vitest, pytest, unittest, node:test, or Mocha THEN the system SHALL parse passed, failed, and total counts from it. For any other runner, the system SHALL report them as null.
4. GATE-4.4 The system SHALL NOT let the scorecard change the verdict's pass/fail outcome.

### Requirement 5: Strict-repo parity (GATE-5)

**User Story:** As Ky, I want every repo held to the controls of LamportLogic, human-rebuild-bootcamp and ky-cloud-control-plane, so that no repo is weaker than my strictest ones.

#### Acceptance Criteria

1. GATE-5.1 WHEN a pull request adds a line using `jwt.sign`, `jwt.verify` or `jsonwebtoken` in a JavaScript/TypeScript source file outside `packages/auth/`, `packages/security/` or `packages/database/` THEN the system SHALL fail the policy job.
2. GATE-5.2 WHEN a pull request adds a line containing `new PrismaClient` in such a source file THEN the system SHALL fail the policy job.
3. GATE-5.3 WHEN a pull request adds a destructive command (force push, `git reset --hard`, destructive `git clean`, database reset or drop, `terraform destroy`, `rm -rf /`) to a script, workflow, Dockerfile, Makefile, `.husky/` hook or `package.json` THEN the system SHALL fail the policy job.
4. GATE-5.4 WHEN a pull request adds or changes a deploy, release or publish workflow that runs on pull_request events, uses `workflow_run` without checking `conclusion == 'success'`, or deploys on push without a branch filter THEN the system SHALL fail the policy job.
5. GATE-5.5 WHEN a pull request adds or changes a Dockerfile whose base image is unversioned or `:latest`, or whose final stage runs as root THEN the system SHALL fail the policy job.
6. GATE-5.6 WHEN the gate runs THEN the system SHALL run a `security` job that the verdict requires. The job SHALL run hash-pinned zizmor at medium severity on in-scope workflows and shellcheck at error severity on changed shell scripts.
7. GATE-5.7 WHEN a pull request changes a dependency manifest or lockfile AND the head introduces a known vulnerability (OSV) absent from the base THEN the system SHALL fail the security job.

#### Known limit (GATE-3)

Git author and committer fields are self-declared, and agents that push with Ky's token appear as KyPython (the owner override). GATE-3 therefore proves only the identities that commits and PRs declare. It cannot tell an agent using Ky's token from Ky himself.
