# Requirements: AI governance spec gate

Spec ID: GATE · Issue: #2 · Status: draft, awaiting Ky's approval
Author: requirements drafted by an AI agent from Ky's 2026-10-03 instruction. Ky owns these sentences; agents must not paraphrase them to fit the code.

## Introduction

No AI-agent code merges without a spec guiding it. The `policy` job of the shared `ai-governance / verdict` gate enforces three things on every pull request that changes code:

- an issue link;
- a spec folder with numbered acceptance criteria;
- tests that trace back to those criteria.

The format follows Kiro's spec layout (`requirements.md`, `design.md`, `tasks.md`) and the requirement-ID traceability Ky already uses: the LamportLogic `AUTH-REQ-001` requirement-to-test matrix, the ZeroAPI `EO-1` trace labels, and the bootcamp `GOLDEN_SPEC.md` `[R-SPEC-F1]` IDs.

## Requirements

### Requirement 1: Spec gate for code changes (GATE-1)

**User Story:** As Ky, I want every AI-authored code change to be guided by written requirements, so that agents implement agreed behavior instead of inventing it.

#### Acceptance Criteria

1. GATE-1.1 WHEN a pull request changes a code path THEN the system SHALL fail the policy job unless the PR body links an issue (`Closes #N`, `Relates to #N`, or an issue URL).
2. GATE-1.2 WHEN a pull request changes a code path AND neither adds or changes a file under a spec folder nor references one with `Spec: <dir>/<slug>` THEN the system SHALL fail the policy job.
3. GATE-1.3 WHEN the referenced or changed spec folder has no `requirements.md`, or its `requirements.md` contains no numbered EARS acceptance criterion (`<PREFIX>-<n>.<m> ... SHALL ...`) THEN the system SHALL fail the policy job.
4. GATE-1.4 WHEN a pull request changes a code path AND no added or changed test file cites an acceptance-criterion ID or its requirement ID from the spec THEN the system SHALL fail the policy job.
5. GATE-1.5 WHEN every changed path matches the explicit exemption rule THEN the system SHALL pass the spec gate without a spec. The rule covers docs, spec and contract files, non-executable config, GitHub workflow and template files, lockfiles, `requirements*.txt`, and `package.json` changes limited to dependency keys.
6. GATE-1.6 WHEN deciding whether a pull request is exempt THEN the system SHALL ignore labels, branch names, and PR authors.

### Requirement 2: Gate re-runs on PR metadata edits (GATE-2)

**User Story:** As Ky, I want the verdict to reflect the PR's current title and body, so that removing an issue link after a green run cannot slip through.

#### Acceptance Criteria

1. GATE-2.1 WHEN a pull request's title or body is edited THEN the caller template SHALL re-run the gate (`pull_request` types include `edited`).
2. GATE-2.2 WHEN a re-run is triggered on the same commit THEN the caller template SHALL NOT cancel the in-flight run.
