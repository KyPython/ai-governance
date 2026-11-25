# Design: trusted exact-SHA external validation evidence (SECFC-7)

Spec ID: SECFC · Issue: #245 · Status: proposed; Ky approves by merging this spec-only PR

Proposed implementation constraints. Nothing here changes code until Ky merges it.

## Mechanism (default; Ky may replace it)

Chosen: the verdict queries the check-runs API. Alternative: a caller-passed
attested artifact. The API route needs no new secret and no artifact format.

| Option | Needs | Weakness |
|---|---|---|
| Check-runs API (chosen) | `checks: read` on the verdict job and on the caller | Caller picks the check name (residual limit in SECFC-7) |
| Attested artifact | Attestation tooling, a verification step, a format | More moving parts; same caller-chosen producer |

## Verdict step flow (SECFC-7.1 to 7.7)

1. Resolve `HEAD_SHA`: `github.event.pull_request.head.sha` on `pull_request`,
   `github.sha` on `push`. Empty means fail.
2. If `RUN_QUALITY` is `true`: keep today's logic (SECFC-1.2), skip the API.
3. If `RUN_QUALITY` is `false`:
   1. `PREREQUISITE_RESULT` must equal `success` (SECFC-1.1 stays).
   2. `PREREQUISITE_CHECK` must be non-empty and not `ai-governance / verdict`.
   3. `gh api --paginate repos/$REPO/commits/$HEAD_SHA/check-runs` with the
      workflow token. Any non-zero exit means fail.
   4. Keep runs where `name == PREREQUISITE_CHECK` and `head_sha == HEAD_SHA`.
      Pick the one with the greatest `completed_at`; a tie means fail (U2).
   5. Require `status == completed`, `conclusion == success`,
      `app.slug == github-actions`.
4. `prerequisite_ok=true` only if every step above held. The final AND with
   quality, policy, security, secret-scan and completion stays as on `main`.

The step must parse JSON with `python3` (already on the runner), not `jq` text
tricks, and must print which condition failed.

## Permissions

`verdict` gets `permissions: {checks: read}`. A reusable workflow cannot exceed
the caller's grant, and GitHub checks the grant when the run starts. So every
caller grants `checks: read` on the calling job, not only callers that set
`run-quality: false` (corrected after F2; the first version of this design said
only those callers). Callers that set `run-quality: false` also pass
`prerequisite-check`.

Caller job shape (self-test.yml and the template):

```yaml
  ai-governance:
    permissions:
      contents: read
      checks: read
    uses: ./.github/workflows/governance.yml   # or KyPython/ai-governance/...@<sha>
```

Granting it on the calling job keeps the workflow-level default at
`contents: read`. Other jobs in the reusable workflow keep their own narrower
`permissions`. README and `docs/quality/system-evidence.md` document the grant
(this changes the hash, SECFC-7.11).

Rollout order (F3): each external caller adds the grant while still on its
current pin (a no-op there), then Ky moves the pin. Moving the pin first fails
that repo at startup. Rollback: revert the verdict change; the extra grant is
harmless on older pins.

## Test design (SECFC-7.10)

Extend `tests/test_completion_step.py` and `tests/test_workflow_shell_syntax.py`
style: extract the `v` step, run it with a controlled environment, and put a
stub `gh` first on `PATH` that serves canned check-runs JSON.

| Case | Stub returns | Expected |
|---|---|---|
| Hardcoded success, validation skipped | no matching run | fail |
| Native `needs.validate.result` skipped | `PREREQUISITE_RESULT=skipped` | fail |
| Stale SHA | run with other `head_sha` | fail |
| False evidence | `conclusion: failure` | fail |
| Missing evidence | `[]` | fail |
| `neutral`, `in_progress`, other app | as named | fail |
| API error | `gh` exits 1 | fail |
| Failed security | `SECURITY=failure`, good evidence | fail |
| Bad shell syntax | mutated script | `bash -n` fails |
| Good case | matching `success` run, all needs success | pass |

## Rollback

Revert the implementation PR. Callers with `run-quality: false` keep working on
the SECFC-1 behavior.
