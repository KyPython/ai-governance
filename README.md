# ai-governance

Ky's AI governance, tests, and CI rules live here and apply to every repo AI agents work in (Kiro, Codex, Cursor, Grok Bot, Claude Code, Copilot). The rules come from `KyLamportLogic/LamportLogic`.

**The gate:** agent code cannot merge to `main` (and so cannot deploy) unless the repo's own CI and the `ai-governance / verdict` check pass. Checks are the gate, and only Ky merges.

## What's here

| Path | Purpose |
| --- | --- |
| `.github/workflows/governance.yml` | Reusable workflow (`on: workflow_call`) that runs the gate in any repo |
| `AGENTS.governance.md` | Canonical `AI-GOVERNANCE:v1` section every repo's `AGENTS.md` must contain |
| `templates/ai-governance.yml` | Caller workflow that goes in each repo |
| `scripts/optin.sh` | One command to opt a repo in, plus `--protect` to apply the protection model |
| `scripts/sweep.sh` | Finds every owned/admin repo without the gate; report-only by default, `--apply` opens opt-in PRs and protects repos whose verdict has passed. Optional `scripts/sweep.skip` (`owner/repo reason` per line, kept out of git) lists exclusions |
| `.github/workflows/self-test.yml` | This repo dogfoods its own gate and runs `tests/` (behavioral tests of the policy script) |
| `roles.yml` | The agent role map (spec-author / coder / approver) and spec paths; read by every gate run from `main` |
| `templates/spec/` | Spec templates: `requirements.md`, `design.md`, `tasks.md` |
| `specs/ai-governance-gate/` | The gate's own spec (the requirements the tests in `tests/` trace to) |

## What the gate checks

All jobs run on `pull_request` and on `push` to `main`.

| Job | Checks | LamportLogic source |
| --- | --- | --- |
| `quality` | Detects pnpm / yarn / npm (via corepack) or Python. Runs install (frozen lockfile), then `lint`, `type-check`/`typecheck`, `test`, `build` if those scripts exist; Python uses ruff, mypy, and pytest when configured. Missing tests fail unless `require-tests: false`. Optional `extra-command` runs repo-specific gates, e.g. `pnpm validate:all`. | `ci.yml`, `.claude/hooks/verify-before-stop.mjs` |
| `policy` | `AGENTS.md` contains the `AI-GOVERNANCE:v1` section. CODEOWNERS has a global `*` owner. Every workflow has a `permissions:` block and SHA-pinned `uses:`. On PRs: the title follows Conventional Commits, and the body references an issue. A missing reference is a warning by default and an error for code PRs or when `require-issue-reference: true`. The **spec gate** (below) runs on every PR. Structural changes need a valid `SYSTEMS_THINKING_CONTRACT` covering every structural path (`auto` = enforced when `.systems-thinking/contracts/` exists). If governance files change, a notice flags that code-owner review is needed. | `AGENTS.md`, `CLAUDE.md`, `CODEOWNERS`, `.husky/commit-msg`, PR template, `validate-security-baseline.js`, `.systems-thinking/` |
| `security` | zizmor (workflow static analysis), shellcheck on changed scripts, osv-scanner dependency review of newly introduced vulnerabilities; all pinned by hash/checksum. | `security-lint.yml`, `ci.yml`, `dependency-review.yml` |
| `secret-scan` | gitleaks 8.30.1 binary, pinned by checksum, over the **whole PR commit range** (not just the tip). Uses the repo's `.gitleaks.toml` if it has one. Fails closed. | `secret-scan.yml`, `.gitleaks.toml` |
| `verdict` | A single aggregate check that fails closed. **Make this the one required status check.** It also publishes the scorecard (see below). | n/a |

The gate uses only GitHub-owned actions pinned to commit SHAs, so it also passes in repos that set "allowed actions: selected" and "require SHA pinning".

### Roles and the spec gate (no spec, no code)

`roles.yml` is the single role map. Ky owns it (CODEOWNERS) and only Ky merges it. The `policy` job reads it from `KyPython/ai-governance@main` on every run, in every repo, and fails closed if it can't. Callers have no input to change roles or spec paths.

| Role | Who | May |
| --- | --- | --- |
| `spec-author` | Kiro (`kiro-agent[bot]`); KyPython as owner override | write specs and requirements in spec-only PRs |
| `coder` | Kiro's builders (`kiro-agent[bot]`), Codex (`chatgpt-codex-connector[bot]`, `codex`), Cursor (`cursor[bot]`), Copilot, Claude, Grok Bot, … | implement specs that already exist on `main`; a code PR never touches spec paths, even when Kiro writes it |
| `approver` | KyPython | review and merge (enforced by branch protection: agents can't merge) |

Every PR that changes a **code path** fails `policy` (and therefore `verdict`) unless all of these hold:

1. **It links an issue** in the body: `Closes #N`, `Relates to #N`, or an issue URL.
2. **It references an existing spec.** The body has a `Spec: specs/<slug>` (or `.kiro/specs/<slug>`) line, and that spec **already exists on the base branch**. Its `requirements.md` contains at least one numbered EARS acceptance criterion: a stable ID `<PREFIX>-<n>.<m>` on a line containing `SHALL`, e.g. `1. GOV-1.1 WHEN … THEN the system SHALL …`.
3. **It does not touch spec paths.** Specs come first, in their own spec-only PR.
4. **It traces tests to the spec.** It adds or changes a test file (`*.test.*`, `*.spec.*`, `test_*.py`, `*_test.*`, `tests/`, `__tests__/`) whose path or content cites one of those criterion IDs (`GOV-1.1`, or `GOV_1_1` in identifiers) or requirement IDs (`GOV-1`).

Every PR that **touches spec paths** (`spec_paths` in roles.yml) fails unless the PR opener **and the author and committer of every commit** match a `spec-author` identity. The committer check is skipped for GitHub's own web-flow committer (`noreply@github.com`). In `KyPython/ai-governance`, a change to `roles.yml` additionally needs every identity to be the owner.

**What the role gate can and cannot prove.**
- The PR opener's login comes from GitHub, so it is reliable.
- Commit author and committer names and emails are self-declared git metadata. Anyone can write any name.
- Many agents push with Ky's token, so their commits and PRs appear as **KyPython**. The owner override then accepts them.
- So the gate reliably blocks spec changes that show a coder or unknown identity anywhere: a `cursor[bot]` commit, a Codex-opened PR, or a `box@…` committer. It **cannot** tell an agent using Ky's token from Ky himself.
- Closing that gap needs each agent to have its own GitHub identity (app or bot account), with no shared token. Signed-commit verification would be a further step.
- Ky's merge remains the real approval for any spec.

**Exempt by path only.** A PR is exempt from the code rules when *every* changed path is one of these:

- docs (`*.md`, `docs/`, images, `.cursorrules`, `.cursor/rules/`);
- spec and contract files (spec paths are still subject to the role gate);
- repo metadata (`.gitignore`, `.gitattributes`, `.editorconfig`, prettier config, `.npmrc`, `.nvmrc`/`.node-version`/`.python-version`, `CODEOWNERS`, `LICENSE`, `.github/workflows/*.yml`, issue/PR templates, `dependabot.yml`). Other config such as `tsconfig.json` or `eslint.config.*` changes behavior, so it counts as code;
- lockfiles and `requirements*.txt`;
- `package.json` where only dependency keys changed (`dependencies`, `devDependencies`, `peerDependencies`, `optionalDependencies`, `packageManager`, `overrides`, `resolutions`, `pnpm`).

Labels, branch names (including `dependabot/*`), and authors never exempt a PR, so a dependabot lockfile/manifest bump passes by path while a dependabot PR touching code does not. The rules live in `governance.yml` (policy sections 0, 8, 9) and are covered by `tests/test_policy.py`.

**Format and where it came from.** Specs follow Kiro's layout: `requirements.md` (Spec ID, issue, user stories, numbered EARS criteria), optional `design.md` and `tasks.md`; see `templates/spec/`. The ID-to-test traceability copies what Ky already does:

- LamportLogic `packages/auth/src/requirement-to-test.ts`: the `AUTH-REQ-001` → test-case matrix;
- ZeroAPI `docs/specs/EMAIL_OUTCOME_REQUIREMENTS.md`: `EO-1..EO-4` with a tests section;
- park-city-studios `REQUIREMENTS_TRACEABILITY.md`;
- human-rebuild-bootcamp `GOLDEN_SPEC.md`: `[R-SPEC-F1]` requirement IDs plus acceptance oracles;
- ky-cloud-control-plane's Kiro-first spec gate: Kiro drafts requirements, Ky approves the exact sentences.

### Strict-repo parity (gap analysis)

`KyLamportLogic/LamportLogic`, `human-rebuild-bootcamp` and `ky-cloud-control-plane` are the strictest repos and the source of truth. Every control they enforce is listed below with its ai-governance status.

- **had**: the gate already did this.
- **added**: the `security` job and policy sections 10–13 (requirements GATE-5).
- **repo-specific**: not generic. It stays in that repo's own required CI, which the gate runs *alongside* and never replaces.

| Control | Source | ai-governance |
| --- | --- | --- |
| Install, lint, type-check, test, build | LamportLogic `ci.yml` (verify); bootcamp `ci.yml` (`npm run ci:github`); control-plane `pnpm build`/`pnpm test` | had (`quality`) |
| Gitleaks over the PR commit range | LamportLogic `secret-scan.yml` | had (`secret-scan`) |
| Workflow SHA pinning and `permissions:` | LamportLogic `validate-security-baseline.js` | had (`policy`; `workflow-baseline: all` matches LamportLogic's full-repo scope) |
| Workflow static analysis | LamportLogic `security-lint.yml` (zizmor) | **added**: zizmor 1.30.1, hash-pinned, `--min-severity medium` on in-scope workflows |
| Shellcheck on changed scripts | LamportLogic `ci.yml` | **added**: `shellcheck --severity=error` |
| Dependency review | LamportLogic RAG `dependency-review.yml`; `validate-dependency-floor.js` | **added**: osv-scanner 2.6.0 (checksum-pinned). Fails on vulnerabilities the PR *introduces* (head vs. base), so no paid GitHub Advanced Security is needed |
| No hand-rolled auth, no direct DB client | LamportLogic `validate-constitution.sh` (pre-commit) | **added**: fails when added lines use `jwt.sign`/`jwt.verify`/`jsonwebtoken` or `new PrismaClient` outside `packages/auth|security|database/` |
| No destructive commands | LamportLogic `.claude/hooks/pre-tool-use.mjs` | **added**: force-push, `reset --hard`, `git clean -fdx`, DB reset/drop, `terraform destroy` and `rm -rf /` fail when added to scripts, workflows, Dockerfiles, Makefiles, `.husky/` or `package.json` |
| Deploy only after CI | LamportLogic `deploy-all.yml` (`workflow_run` + success); AGENTS rule | **added**: changed deploy/release/publish workflows fail if they deploy on PR events, use `workflow_run` without a success check, or deploy on push to any branch |
| Container hardening | LamportLogic `validate-container-hardening.js` | **added** (subset): changed Dockerfiles need a versioned, non-`latest` base and a non-root final `USER`. The full rules (digest pin, HEALTHCHECK, ports, volumes) stay in LamportLogic |
| CODEOWNERS | all three | had (global owner required) |
| PR template | LamportLogic, bootcamp `PULL_REQUEST_TEMPLATE.md` | **added** (warning) |
| Dependabot | LamportLogic `dependabot.yml` | **added** (warning) |
| Conventional Commits | LamportLogic `.husky/commit-msg` | had (PR title) |
| Systems-thinking contract | LamportLogic, bootcamp `.systems-thinking/` | had |
| Requirements before code; Kiro authors specs | control-plane `KIRO_SPEC_AND_MONETIZATION_GATE.md`; LamportLogic AGENTS | had (spec gate + role gate) |
| AI monetization / mutation gate | LamportLogic `validate-ai-monetization-gate.js`, `ai:mutation:check` | repo-specific (the generic analog is the spec + role gates) |
| `validate:all` suite (env vars, RLS, auth coverage, provider SDK, workspace sync, path integrity) | LamportLogic | repo-specific |
| Snyk code, open-source and IaC scans | LamportLogic `snyk-security.yml` | repo-specific (needs a Snyk account token). osv-scanner and zizmor cover the free part |
| PCS Godot tests, model-verification plane, mutation testing | LamportLogic | repo-specific |
| OPA policy tests, TLA+ model check, `cdk synth --strict` with cdk-nag | control-plane | repo-specific. The gate's `quality` job runs its `pnpm build` and `pnpm test`, which include the OPA and TLA+ suites |
| Bootcamp grading parity (`ci:github`) | bootcamp | repo-specific |
| Scheduled full-history gitleaks | LamportLogic `secret-scan.yml` (schedule) | not added; the strict repos keep their own |

### Workflow: one coder per task, cross-reviewed

1. **Kiro writes the spec** (`requirements.md`, `design.md`, `tasks.md`) in a spec-only PR. Ky merges it.
2. **Each task in `tasks.md` goes to one coder**, in its own PR that cites `Spec: specs/<slug>` and the task's criterion IDs.
3. **A different agent reviews that PR**: for example, Codex reviews Cursor's PR and Cursor reviews Codex's. The gate checks the code; the reviewer checks intent against the requirement sentences.
4. **Ky merges** once `verdict` and the repo's CI are green and review threads are resolved.

Coders cooperate rather than compete. Sometimes the same task is built head-to-head by two coders, purely for learning; the scorecard below makes that comparison cheap.

### Scorecard (machine-readable verdict summary)

Every run's `verdict` job publishes the same JSON (schema `ai-governance-summary/v1`) in three places:

- the run's **job summary**, as a one-row table plus the JSON;
- a **`ai-governance-summary` artifact** (`ai-governance-summary.json`, kept 90 days);
- the reusable workflow's **`summary` output**, also printed as a log line starting `AI_GOVERNANCE_SUMMARY `.

```json
{
  "schema": "ai-governance-summary/v1",
  "repo": "KyPython/effectproof", "pr": 21, "pr_author": "cursor[bot]", "head_sha": "…",
  "verdict": "pass", "jobs": {"quality": "success", "policy": "success", "secret-scan": "success"},
  "failed_checks": 0, "failed_check_names": [], "policy_errors": 0,
  "tests": {"passed": 46, "failed": 0, "total": 46},
  "spec": ["specs/ai-governance-gate"], "requirement_ids": ["GOV-1.1", "GOV-1.2", "GOV-1.3", "GOV-2.1", "GOV-3.1"],
  "changed_lines": {"added": 50, "deleted": 0, "total": 50}, "files_changed": 2,
  "run_url": "https://github.com/…/actions/runs/…"
}
```

What each field means:

- **`tests`** is parsed from the test output of the quality job and the `extra-command`. Supported runners: Jest, Vitest, pytest, unittest, node:test and Mocha; counts are summed across monorepo packages. The values are `null` when the runner's output isn't recognized, or when tests didn't run (for example, lint failed first).
- **`requirement_ids`** are the spec IDs cited by the PR's changed tests.
- **`failed_checks`** counts the gate jobs that didn't succeed, and `policy_errors` counts policy findings.
- **`changed_lines`** counts the PR diff against the merge-base, excluding lockfiles.

The scorecard only reports; the pass/fail decision never reads it. Use it to see at a glance what a PR covered, to check a reviewer's claims, or to compare an occasional head-to-head. Example: `gh run download <run-id> -n ai-governance-summary`.

### Inputs

`node-version` ("22"), `python-version` ("3.12"), `working-directory` ("."), `run-quality` (true; set false only when the repo's own required CI already runs install/lint/test/build on every PR), `workflow-baseline` ("changed" = only workflows touched by the PR/push must be pinned and permissioned; "all"; "off"), `require-tests` (true), `extra-command` (""), `require-issue-reference` (false; code PRs always need it), `enforce-conventional-title` (true), `systems-thinking-contract` ("auto" | "required" | "off").

## Opt a repo in

```bash
# 1. Open the opt-in PR. It adds the caller workflow, the AGENTS.md section,
#    CODEOWNERS if missing, and a systems-thinking contract if the repo uses them.
GITHUB_TOKEN=<pat with repo+workflow> ./scripts/optin.sh <repo-name>

# 2. Wait until the PR shows the "ai-governance / verdict" check, then require it on main:
./scripts/optin.sh --protect <repo-name>

# 3. Ky reviews and merges the opt-in PR.
```

To do it by hand: copy `templates/ai-governance.yml` to `.github/workflows/ai-governance.yml`, replace `__AI_GOVERNANCE_SHA__` with the current `main` SHA of this repo, paste `AGENTS.governance.md` near the top of `AGENTS.md`, and add `* @KyPython` to `.github/CODEOWNERS`. Then add the branch protection on `main` (the "checks are the gate" model):

- require a PR, with 0 required approvals (no code-owner review, no last-push approval)
- required checks: the repo's own CI that runs on every PR, plus `ai-governance / verdict`
- strict (branch must be up to date)
- conversation resolution required
- linear history
- no force pushes, no deletions
- enforced on admins

**Access:** this repo is public, so any repo can call the gate: KyPython repos, `KyLamportLogic` org repos, private or public. A private reusable workflow can only be shared with repos owned by the same account. The repo holds no secrets; that was checked with gitleaks before publishing.

**Updating the gate:** callers pin a commit SHA, so a change here affects nobody until each repo bumps its SHA in a PR that Ky approves. That stops an agent from weakening the gate for every repo in one edit.

## Deploys

Gate deploys on governance. Deploy only from `main` (which only advances through governed PRs), or chain off the gate the way LamportLogic's `deploy-all.yml` does:

```yaml
on:
  workflow_run:
    workflows: ["AI Governance"]
    types: [completed]
    branches: [main]
jobs:
  deploy:
    if: github.event.workflow_run.conclusion == 'success' && github.event.workflow_run.event == 'push' && github.event.workflow_run.head_repository.full_name == github.repository
```

For hosted deploys (Vercel, Cloudflare, etc.), restrict production deploys to the `main` branch.

## Limits (be honest)

- The protection model has no approval requirement on purpose: agents push with Ky's account, and GitHub never lets authors approve their own PRs. The checks are the gate. Branch protection cannot stop a holder of Ky's admin token from merging their own PR once checks pass. That rule lives in AGENTS.md, so keep agents' tokens scoped where possible.
- (Historical) GitHub enforces "Ky approves" only when the PR author is **not** Ky's own account, because GitHub never lets authors approve their own PRs. If agents push and open PRs with Ky's personal token, the PR is authored by `KyPython`. With `enforce_admins` on, it can then never collect the required approval. With admin bypass on, anything holding Ky's admin token, agents included, can bypass. The robust fix is to give agents their own identity (a GitHub App / bot account, or the Cursor/Codex GitHub apps) with write access but not admin, so Ky's review is the real gate.
- Branch protection and rulesets on **private** repos need a paid plan. The KyPython account is on Pro, so its private repos work. The `KyLamportLogic` org is on Free, so its private repos return `403 Upgrade to GitHub Pro or make this repository public`; fixing that needs GitHub Team, $4/user/month. Org-wide rulesets also need Team, and "require workflows" rulesets need Enterprise.
- **The role gate proves declared identities only.** See "What the role gate can and cannot prove" above. While agents push with Ky's token, the gate cannot tell an agent from Ky. Giving each agent its own GitHub identity is what makes `roles.yml` fully enforceable.
- **Cross-review by a different agent is a workflow rule, not a gate check.** The gate does not verify who reviewed a PR.
- **The scorecard is best-effort.** Test counts depend on recognizing the runner's output; anything else reports `null`. It never affects the verdict.
- **`roles.yml` is read from `main` at run time**, unlike the SHA-pinned workflow. A role change by Ky applies everywhere at once. If raw.githubusercontent.com is unreachable, verdicts fail closed.
