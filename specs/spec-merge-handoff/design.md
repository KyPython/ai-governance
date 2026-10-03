# Design: Spec-merge handoff

Spec ID: HANDOFF

## Overview

The authoritative design is Ky's third (latest) comment on issue #5: the handoff runs **centrally** from KyPython/ai-governance, which holds the only copy of `CODEX_TRIGGER_PAT` (personal accounts have no account-wide secrets). On a schedule and on `workflow_dispatch`, a central job enumerates opted-in repos, detects spec-only merges to `main`, parses each merged spec's `tasks.md`, opens one issue per task in the target repo, and posts the `@codex` comment on `codex`-labeled issues using the central PAT. Opted-in repos hold no secrets of their own. This mirrors `scripts/sweep.sh`: a single central token, cross-repo discovery via the GitHub REST API, read/scan then create-issue/comment, and never merge or delete.

**Reconciliation with done-check #1.** Done-check #1 literally describes a reusable `on: workflow_call` workflow (like `governance.yml`) plus a per-repo caller that runs on `push` to `main` filtered to `specs/**`. The central model supersedes that wording:

- The central scheduled/`workflow_dispatch` scanner in KyPython/ai-governance is the **primary and authoritative** mechanism.
- The "commit changes only `specs/**`" filter is still enforced, but it is evaluated **centrally** by inspecting the changed paths of each detected merge, instead of by a per-repo push-triggered caller.
- Per-repo "opt in" becomes **membership in a central allowlist/discovery mechanism** (like `sweep.sh`'s repo enumeration plus a skip/allowlist file) rather than a per-repo secret or a per-repo caller workflow.
- Where done-check #1's per-repo-caller wording conflicts with the central model, the latest comment (central) **wins**. All other done checks (2–10) are kept and are expressed against the central scanner.

The result is a central scanner that still satisfies the spec-only filter, one-issue-per-task, idempotency, at-most-once commenting, secret safety, workflow hygiene, and the no-write/no-merge guarantees, with opt-in handled as central membership.

## Architecture / components

The central workflow is `.github/workflows/spec-handoff.yml` in KyPython/ai-governance. It mirrors `governance.yml` hygiene: explicit minimal `permissions`, GitHub-owned actions pinned to full SHAs only, untrusted fields passed through `env` and never spliced into `run:`, and fail-closed behavior. Its triggers are `on: schedule` (a cron) and `on: workflow_dispatch`. It calls a small Python package (built later) with these components:

- **Discovery (`handoff_discovery`).** Enumerates opted-in repos in the spirit of `sweep.sh`: list the central user's owned and admin repos via `/user/repos?affiliation=owner,organization_member`, then intersect with a central allowlist and subtract a skip list. Repos not in the set are skipped. (HANDOFF-1.1, HANDOFF-1.2, HANDOFF-2.1, HANDOFF-2.2, HANDOFF-2.3)
- **Spec-only merge detector (`handoff_merge`).** For each opted-in repo, finds recent merges to `main` and, for each, inspects the changed paths. A merge qualifies only when every changed path is under `specs/`; a merge that also touches any non-spec path is ignored. When a qualifying merge touches multiple spec folders, each folder is handed off. (HANDOFF-1.3, HANDOFF-3.1, HANDOFF-3.2, HANDOFF-3.3)
- **tasks.md parser (`handoff_parser`).** Reads `specs/<slug>/tasks.md` at the merged commit and parses checklist lines `- [ ] N. <task> (<ID>, ...) [— coder: <name>]` into `(task_id, text, requirement_ids, coder)`. The coder comes from the optional `— coder: <name>` tail; absent that, it defaults to `codex`. An empty or unparsable `tasks.md` is a hard error for that spec. (HANDOFF-5.1, HANDOFF-5.2, HANDOFF-5.3, HANDOFF-5.4)
- **Issue builder (`handoff_issue`).** For each parsed task, builds an issue whose body contains `Spec: specs/<slug>`, the task text, the task's requirement IDs, and the marker `<!-- spec-task: <slug>#<task-id> -->`. The label is the task's coder, or `codex` when none is set. (HANDOFF-4.1, HANDOFF-4.2, HANDOFF-4.3, HANDOFF-6.1)
- **Idempotency check (`handoff_idempotency`).** Before creating an issue, searches the target repo's existing issues for the task's marker; if present, nothing is created. Guarantees zero duplicates across re-runs, later scans, and manual dispatch. (HANDOFF-6.2, HANDOFF-6.3)
- **@codex comment (`handoff_comment`).** For `codex`-labeled issues only, posts `@codex implement this task per the linked spec and open a PR` using `CODEX_TRIGGER_PAT`, at most once per issue (it checks for an existing `@codex` comment first). Non-`codex` issues get no comment. (HANDOFF-7.1, HANDOFF-7.2, HANDOFF-7.3)
- **Static no-write guarantee.** The workflow declares no `contents: write`, no push step, and no merge/approve API call. A static check over the workflow permissions and the code's API surface proves there is no write path to `specs/` contents and no merge capability. (HANDOFF-10.1, HANDOFF-10.2, HANDOFF-10.3, HANDOFF-10.4)

## Data and interfaces

- **Central secret `CODEX_TRIGGER_PAT`.** The single copy lives in KyPython/ai-governance repository/environment secrets. It is used only for the `@codex` comment so that comment appears as KyPython and triggers Codex. It is never echoed, logged, written to outputs/artifacts, or exposed to fork `pull_request` runs. (HANDOFF-1.4, HANDOFF-8.1, HANDOFF-8.2, HANDOFF-8.3)
- **Least-privileged token.** Issue creation uses the least-privileged token that works (a token scoped to `issues: write` on the target repo). The PAT is reserved for the comment, not for issue creation. If the PAT is missing, the job fails fast before opening any issues. (HANDOFF-8.4, HANDOFF-8.5)
- **Allowlist/discovery data.** Opt-in is central membership: the owned/admin enumeration plus an allowlist and a skip list (modeled on `scripts/sweep.sh`'s `sweep.skip`). A repo "joins" by being added to the central set, not by storing a secret. (HANDOFF-2.1, HANDOFF-2.2, HANDOFF-2.3)
- **Marker format.** `<!-- spec-task: <slug>#<task-id> -->`, one per task issue, used as the idempotency key. (HANDOFF-6.1, HANDOFF-6.2)
- **Issue body schema.** `Spec: specs/<slug>` line, the task text, the requirement IDs, and the marker comment. (HANDOFF-4.2)
- **Label semantics.** The label equals the task's assigned coder; absent a coder it is `codex`, which is also the trigger for the `@codex` comment. (HANDOFF-4.3, HANDOFF-5.3, HANDOFF-7.1)

## Error handling and failure modes

- **Missing `CODEX_TRIGGER_PAT`.** Fail fast with a clear message; open no partial set of issues. (HANDOFF-8.5)
- **Unparsable or missing `tasks.md`.** Fail clearly for that repo/spec and open no issues for it; other repos in the scan are unaffected. (HANDOFF-5.4)
- **Fork `pull_request` isolation.** The PAT is never made available to `pull_request` runs from forks; the handoff runs only from the trusted central schedule/dispatch context. (HANDOFF-8.3)
- **Repo not in the allowlist.** Skipped with no issues created. (HANDOFF-2.2)
- **Empty/unreadable allowlist.** No handoff performed; a clear message is reported instead of acting on an unintended repo set. (HANDOFF-2.3)
- **Non-spec-only merge.** Ignored; no handoff. (HANDOFF-3.2)
- **Marker already present.** No duplicate issue; no second `@codex` comment. (HANDOFF-6.2, HANDOFF-6.3, HANDOFF-7.3)

## Testing strategy (criterion ID -> test file)

Automated Python tests run by this repo's quality (`pytest`) job. Each test cites the requirement ID(s) it verifies in its name or a comment. The files below are intended; they are NOT created by this spec PR.

| Criterion | Test |
| --- | --- |
| HANDOFF-1.1 | `tests/test_spec_handoff.py` |
| HANDOFF-1.2 | `tests/test_spec_handoff.py` |
| HANDOFF-1.3 | `tests/test_handoff_merge.py` |
| HANDOFF-1.4 | `tests/test_spec_handoff.py` |
| HANDOFF-2.1 | `tests/test_handoff_discovery.py` |
| HANDOFF-2.2 | `tests/test_handoff_discovery.py` |
| HANDOFF-2.3 | `tests/test_handoff_discovery.py` |
| HANDOFF-3.1 | `tests/test_handoff_merge.py` |
| HANDOFF-3.2 | `tests/test_handoff_merge.py` |
| HANDOFF-3.3 | `tests/test_handoff_merge.py` |
| HANDOFF-4.1 | `tests/test_handoff_issue.py` |
| HANDOFF-4.2 | `tests/test_handoff_issue.py` |
| HANDOFF-4.3 | `tests/test_handoff_issue.py` |
| HANDOFF-5.1 | `tests/test_handoff_parser.py` |
| HANDOFF-5.2 | `tests/test_handoff_parser.py` |
| HANDOFF-5.3 | `tests/test_handoff_parser.py` |
| HANDOFF-5.4 | `tests/test_handoff_parser.py` |
| HANDOFF-6.1 | `tests/test_handoff_idempotency.py` |
| HANDOFF-6.2 | `tests/test_handoff_idempotency.py` |
| HANDOFF-6.3 | `tests/test_handoff_idempotency.py` |
| HANDOFF-7.1 | `tests/test_handoff_comment.py` |
| HANDOFF-7.2 | `tests/test_handoff_comment.py` |
| HANDOFF-7.3 | `tests/test_handoff_comment.py` |
| HANDOFF-8.1 | `tests/test_handoff_secret.py` |
| HANDOFF-8.2 | `tests/test_handoff_secret.py` |
| HANDOFF-8.3 | `tests/test_handoff_secret.py` |
| HANDOFF-8.4 | `tests/test_handoff_secret.py` |
| HANDOFF-8.5 | `tests/test_handoff_secret.py` |
| HANDOFF-9.1 | `tests/test_handoff_workflow_hygiene.py` |
| HANDOFF-9.2 | `tests/test_handoff_workflow_hygiene.py` |
| HANDOFF-9.3 | `tests/test_handoff_workflow_hygiene.py` |
| HANDOFF-9.4 | `tests/test_handoff_workflow_hygiene.py` |
| HANDOFF-10.1 | `tests/test_handoff_no_write.py` |
| HANDOFF-10.2 | `tests/test_handoff_no_write.py` |
| HANDOFF-10.3 | `tests/test_handoff_no_write.py` |
| HANDOFF-10.4 | `tests/test_handoff_no_write.py` |
| HANDOFF-11.1 | `tests/test_handoff_suite.py` |
| HANDOFF-11.2 | `tests/test_handoff_idempotency.py` |
| HANDOFF-11.3 | `tests/test_handoff_comment.py` |
| HANDOFF-11.4 | `tests/test_handoff_suite.py` |
| HANDOFF-12.1 | `tests/test_handoff_readme.py` |
| HANDOFF-12.2 | `tests/test_handoff_readme.py` |
| HANDOFF-12.3 | `tests/test_handoff_readme.py` |
