# Design: Read the role map while ai-governance is private

Spec ID: GRM

## Verified current state (2026-11-10)

- `gh api repos/KyPython/ai-governance` reports `private: true`. An unauthenticated `curl` of the raw `roles.yml` URL returns 404.
- `governance.yml` line 348 sets `ROLES_URL` to the raw URL. Lines 401-403 read it with `urllib.request.urlopen(roles_src, timeout=20)` and no headers. `ROLES_FILE` overrides it; `tests/test_policy.py` uses `ROLES_FILE`.
- The `policy` job has `permissions: contents: read`, and its step environment already sets `GITHUB_TOKEN: ${{ github.token }}` (line 352), used today for login resolution (line 703 on).
- `workflow_call` declares inputs only, no secrets.
- `gh api repos/KyPython/ai-governance/actions/permissions/access` returns `{"access_level":"user"}`.
- `tests/test_policy.py` line 252 asserts the raw `ROLES_URL` string is in the workflow.

## Decision

Fetch `GET https://api.github.com/repos/KyPython/ai-governance/contents/roles.yml?ref=main`
with `Accept: application/vnd.github.raw+json` and `Authorization: Bearer <token>`. The token is
`secrets.AI_GOVERNANCE_READ_TOKEN` when the caller passes it, else `github.token`.

| Option | Rejected because |
|---|---|
| Make the repository public | Ky chose to fix the gate instead (2026-11-10). |
| Publish `roles.yml` to a public location | Adds a second source of truth that can drift from `main` (GATE-3.5). |
| Embed the role map in the workflow at the caller's pinned ref | Callers pin a SHA, so role changes would stop applying everywhere at once. |
| `actions/checkout` of ai-governance | Needs the same token and checks out more than one file. |
| Fall back to unauthenticated or cached reads | Weakens GATE-3.4; forbidden by GRM-2.3. |

## Token reach

| Where the gate runs | `github.token` reads ai-governance? | Needs `AI_GOVERNANCE_READ_TOKEN`? |
|---|---|---|
| KyPython/ai-governance (self-test, #263, #264) | Expected yes: same repository, `contents: read`. INFERENCE until GRM-1.4 is shown in CI. | No |
| Other KyPython repositories | No: the token is scoped to the calling repository. | Yes |
| KyLamportLogic repositories | Not reached: `access_level: user` stops them calling the private workflow; they are also under an Actions billing lock. | Out of scope |

## Unknowns

- Whether a KyPython caller can pass a secret to this private reusable workflow without other settings changes. To be shown by task 6.
- The token type Ky prefers (fine-grained personal access token or GitHub App) and its expiry.

## Human gates

- HOLD 1: Ky merges this spec-only PR.
- HOLD 2: Ky creates a token with read-only Contents access to `KyPython/ai-governance` and stores it as the `AI_GOVERNANCE_READ_TOKEN` secret in each calling KyPython repository. Agents do not create tokens or change repository settings.
- HOLD 3: Ky decides separately how KyLamportLogic repositories get the gate (Actions access level, transfer, or another route).
