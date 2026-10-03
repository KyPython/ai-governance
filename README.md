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
| `.github/workflows/self-test.yml` | This repo dogfoods its own gate |

## What the gate checks

All jobs run on `pull_request` and on `push` to `main`.

| Job | Checks | LamportLogic source |
| --- | --- | --- |
| `quality` | Detects pnpm / yarn / npm (via corepack) or Python. Runs install (frozen lockfile), then `lint`, `type-check`/`typecheck`, `test`, `build` if those scripts exist; Python uses ruff, mypy, and pytest when configured. Missing tests fail unless `require-tests: false`. Optional `extra-command` runs repo-specific gates, e.g. `pnpm validate:all`. | `ci.yml`, `.claude/hooks/verify-before-stop.mjs` |
| `policy` | `AGENTS.md` contains the `AI-GOVERNANCE:v1` section. CODEOWNERS has a global `*` owner. Every workflow has a `permissions:` block and SHA-pinned `uses:`. On PRs: the title follows Conventional Commits, and the body references an issue (warning only by default). Structural changes need a valid `SYSTEMS_THINKING_CONTRACT` covering every structural path (`auto` = enforced when `.systems-thinking/contracts/` exists). If governance files change, a notice flags that code-owner review is needed. | `AGENTS.md`, `CLAUDE.md`, `CODEOWNERS`, `.husky/commit-msg`, PR template, `validate-security-baseline.js`, `.systems-thinking/` |
| `secret-scan` | gitleaks 8.30.1 binary, pinned by checksum, over the **whole PR commit range** (not just the tip). Uses the repo's `.gitleaks.toml` if it has one. Fails closed. | `secret-scan.yml`, `.gitleaks.toml` |
| `verdict` | A single aggregate check that fails closed. **Make this the one required status check.** | n/a |

The gate uses only GitHub-owned actions pinned to commit SHAs, so it also passes in repos that set "allowed actions: selected" and "require SHA pinning".

### Inputs

`node-version` ("22"), `python-version` ("3.12"), `working-directory` ("."), `run-quality` (true; set false only when the repo's own required CI already runs install/lint/test/build on every PR), `workflow-baseline` ("changed" = only workflows touched by the PR/push must be pinned and permissioned; "all"; "off"), `require-tests` (true), `extra-command` (""), `require-issue-reference` (false), `enforce-conventional-title` (true), `systems-thinking-contract` ("auto" | "required" | "off").

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
