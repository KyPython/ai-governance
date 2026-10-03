# ai-governance — agent rules

This repository *is* the governance source for all of Ky's repos. Changes here change the gate for every opted-in repo (once they bump their pinned SHA), so only Ky merges PRs here.
<!-- AI-GOVERNANCE:v1 | canonical source: KyPython/ai-governance/AGENTS.governance.md | do not weaken locally; change it upstream via a PR Ky approves -->
## AI Governance (mandatory for every AI agent)

Applies to every AI coding agent working in this repo: Kiro, Codex, Cursor, Grok Bot, Claude Code, Copilot, and any sub-agent they spawn. Sub-agents inherit these rules and may not weaken, relabel, bypass, or self-attest them. Repo-specific rules below this section may tighten these rules but never loosen them. Derived from `KyLamportLogic/LamportLogic` (AGENTS.md, CODEOWNERS, PR template, `.husky/`, `.claude/`, CI and secret-scan workflows).

**Merge and deploy gate.** Nothing reaches `main` or production unless both of these are true:
1. The required checks are green: the repo's own CI plus `ai-governance / verdict`. The verdict runs install plus whichever of lint, type-check, test, and build the repo defines as scripts, then policy checks (including the spec gate) and a gitleaks secret scan, all through the reusable workflow in `KyPython/ai-governance`.
2. Ky (@KyPython) merges the PR. Checks are the gate; only Ky merges.

Agents never merge, approve, or deploy their own work.

### Rules
1. **Branch + PR only.** Never push to `main`. Work on a branch such as `feat/*`, `fix/*`, `chore/*`, `docs/*`, `ci/*`, `refactor/*`, or `governance/*`, then open a PR. Do not merge it, approve it, enable auto-merge, or trigger a deploy. Ky merges.
2. **Spec first: no spec, no code.** Before writing or changing code, read the spec for the change. If none exists, write the requirements first and stop until they exist. Kiro (or Ky) writes specs; coding agents (Codex, Cursor, Claude Code, Grok Bot, Copilot) implement them.
   - **Format.** A spec lives in `specs/<slug>/` or `.kiro/specs/<slug>/`. It holds `requirements.md` (required) plus optional `design.md` and `tasks.md`; templates are in `KyPython/ai-governance/templates/spec/`.
   - **Criteria.** `requirements.md` gives a Spec ID and the issue, then user stories, then numbered EARS acceptance criteria with stable IDs, e.g. `GOV-1.1 WHEN <trigger> THEN the system SHALL <response>`.
   - **Requirement sentences are the requirement.** Coders do not paraphrase, reword, or weaken them to fit the code. If a requirement is wrong, stop and ask Ky, or route the change back through the spec author.
   - **What the gate enforces.** Every PR that changes code fails `ai-governance / verdict` unless it does all three of these:
     1. links an issue (`Closes #<n>` / `Relates to #<n>`);
     2. adds or changes a spec folder, or references one with a `Spec: specs/<slug>` line in the PR body;
     3. adds or changes tests whose names or comments cite the criterion IDs they verify, e.g. `it("GOV-1.1 ...")` or `# GOV-1.1`.
   - **Exemptions** apply only by an explicit path rule in the gate: docs, spec and contract files, non-executable config and workflow/template files, lockfiles, and dependency-only manifest changes. Labels, branch names, and authors never exempt a PR.
3. **Prove it green before you stop.** Run the repo's install, lint, type-check, test, and build commands locally (whichever exist). If any of them fails, fix it or report the blocker. Never say "tests pass" without running them.
4. **Tests ship with behavior changes.** Tests check observable behavior or stable contracts, not snippets of source code. Never delete, skip, or loosen a test just to get green.
5. **PR hygiene.**
   - The PR title follows Conventional Commits: `<type>(<scope>): <description>`, where type is one of feat, fix, docs, test, refactor, style, chore, ci, perf, build, or revert.
   - The body references the issue (`Closes #<n>` / `Relates to #<n>`). The gate always requires the reference for code PRs (rule 2). It also requires it for every PR when the repo's caller sets `require-issue-reference: true`.
   - The body says what changed, why it works, how it could fail, and how it was tested.
6. **Structural changes need a contract.** Structural paths include `packages/`, workflows/validators, AGENTS/CLAUDE/.cursorrules, `docs/quality|architecture`, and SPEC/empire-spec files. If the repo has `.systems-thinking/contracts/`, add a `SYSTEMS_THINKING_CONTRACT` JSON file there. Its `scope` must cover every structural path, and it fills in event → pattern → structure → archetype → intervention → leading_indicators → transfer. No placeholders.
7. **Do not touch the governance itself.** Agents do not edit, weaken, disable, or route around these:
   - `.github/workflows/ai-governance.yml` and its pinned SHA
   - other CI workflows
   - `CODEOWNERS`
   - this section
   - `.husky/`, `.claude/`, `.cursor/rules/`
   - branch protection or rulesets

   A change to any of them needs Ky's explicit request, and Ky merges it. Never edit a gate to make it pass.
8. **Secrets.** Never commit secrets, tokens, or `.env` values, and never print credentials. If a secret leaks: rotate it at the provider first, then rewrite it out of branch history. Deleting it in a later commit is not enough.
9. **No destructive commands without explicit human authorization.** This covers `git push --force`, `git reset --hard`, `git clean -fd`, `prisma migrate reset`, `supabase db reset`, `drop database`, `terraform destroy`, and `rm -rf /`.
10. **Supply chain.** Pin third-party GitHub Actions to a full commit SHA. Every workflow declares a least-privilege `permissions:` block. Untrusted event data (PR title, body, branch name) goes through `env:` and is never spliced into `run:` scripts.
11. **Human judgment stays human.** Do not invent users, traction, metrics, or personal facts. Stop and hand formative, consequential (irreversible), and authorship decisions to Ky.
12. **Deploys follow governance.** Deploy jobs run only from `main` after CI/governance passed: `workflow_run` on success, same-repo `push` events only, never fork PR code with secrets.
