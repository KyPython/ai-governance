# Requirements: Read the role map while ai-governance is private

Spec ID: GRM · Issue: none (goal selected by Ky in chat on 2026-11-10; found on #264) · Status: proposed; Ky approves by merging this spec-only PR

Provenance: drafted by Kiro on 2026-11-10 from Ky's chat choice "1a": fix the gate properly, spec first, rather than make the repository public. Ky owns the sentences; coders must not paraphrase them to fit the code.

## Introduction

`KyPython/ai-governance` is now private. The `policy` job in `.github/workflows/governance.yml`
reads the role map with an unauthenticated `urllib.request.urlopen` of
`https://raw.githubusercontent.com/KyPython/ai-governance/main/roles.yml`, which now returns
HTTP 404. GATE-3.4 makes the job fail closed, so every gated pull request fails
`ai-governance / policy`. Observed on KyPython/ai-governance#263 and #264 and on
KyPython/ple-verified-harness#3 (run started 2026-11-10T16:11:53Z), each with:
`Role map could not be loaded from https://raw.githubusercontent.com/KyPython/ai-governance/main/roles.yml (HTTP Error 404: Not Found). The gate fails closed without it.`

This spec changes only how the policy job fetches `roles.yml`. GATE-3.4 (fail closed when the
role map cannot be read) and GATE-3.5 (read only from `roles.yml` on `main`, no caller input
changes roles or spec paths) stay in force unchanged.

Out of scope: the repository's Actions sharing level (`access_level: user`, which keeps
KyLamportLogic organization repositories from calling this private reusable workflow at all),
the KyLamportLogic Actions billing lock, and the `acp.helpers` failure (spec `inspect-acp-pin`).

## Requirements

### Requirement 1: Authenticated fetch from main (GRM-1)

**User Story:** As Ky, I want the gate to read the role map from the private repository, so that
gated pull requests are judged on their content instead of failing on a 404.

#### Acceptance Criteria

1. GRM-1.1 WHEN the policy job loads the role map without `ROLES_FILE` THEN the system SHALL request `roles.yml` at ref `main` of `KyPython/ai-governance` through the GitHub REST contents API with an `Authorization: Bearer` token.
2. GRM-1.2 The system SHALL take the repository, path, and ref of that request from constants in `governance.yml`, and SHALL NOT accept a caller input that changes any of them.
3. GRM-1.3 WHERE the caller supplies the secret `AI_GOVERNANCE_READ_TOKEN` THEN the system SHALL use it for the request; otherwise the system SHALL use the job's `github.token`.
4. GRM-1.4 WHEN the gate runs in `KyPython/ai-governance` itself THEN the role map request SHALL succeed with the job's `github.token` and no added secret.

### Requirement 2: Fail closed (GRM-2)

**User Story:** As Ky, I want a missing or wrong token to block the gate with a message that says
how to fix it, so that the gate never passes without the real role map.

#### Acceptance Criteria

1. GRM-2.1 IF the role map request returns a non-200 status or times out THEN the system SHALL fail the policy job, as GATE-3.4 requires.
2. GRM-2.2 IF the role map request returns 401, 403, or 404 THEN the failure message SHALL name the `AI_GOVERNANCE_READ_TOKEN` secret and state that it needs read access to the contents of `KyPython/ai-governance`.
3. GRM-2.3 The system SHALL NOT fall back to an unauthenticated request, a cached copy, a caller-supplied file, or a built-in default role map.
4. GRM-2.4 The system SHALL NOT write the token, or any `Authorization` header value, to logs, job outputs, or the step summary.

### Requirement 3: Callers (GRM-3)

**User Story:** As Ky, I want every calling repository wired the same way, so that one secret
setup fixes the gate everywhere it is allowed to run.

#### Acceptance Criteria

1. GRM-3.1 The reusable workflow SHALL declare `AI_GOVERNANCE_READ_TOKEN` as an optional `workflow_call` secret.
2. GRM-3.2 WHEN `scripts/sweep.sh` reports on a repository that calls the gate THEN its report SHALL state whether the caller workflow passes `AI_GOVERNANCE_READ_TOKEN`.
3. GRM-3.3 The caller template `templates/ai-governance.yml`, which `scripts/optin.sh` installs, SHALL pass `AI_GOVERNANCE_READ_TOKEN` to the reusable workflow.

### Requirement 4: Tests (GRM-4)

**User Story:** As a reviewer, I want the new fetch covered by tests, so that a regression shows
up in the self-test instead of in every repository at once.

#### Acceptance Criteria

1. GRM-4.1 The tests in `tests/` SHALL cover: a 200 response that loads the role map; a 404 and a 401 that fail with the GRM-2.2 message; a timeout that fails; and a run whose captured output does not contain the token value.
2. GRM-4.2 The existing assertion in `tests/test_policy.py` that the workflow contains the raw `ROLES_URL` SHALL be replaced by assertions for the GRM-1.1 repository, path, and ref constants.
