# Design: Agent role cards and role enforcement

Spec ID: ROLES

## Overview

Issue #9 has two halves, and both reuse machinery that already exists in this repo. The first half is **role cards**: short plain-language statements of the fixed roles, placed in the file each agent actually reads (`AGENTS.md` for Codex and other coding agents, a `.kiro/steering/` file for Kiro), and made shareable so every opted-in repo gets the same words. The second half is **enforcement** in the shared `policy` job of `governance.yml`, which already reads the PR's changed paths, the PR title and body, and (through spec #3) `roles.yml` from `KyPython/ai-governance@main`.

Enforcement here **extends** spec #3's substrate rather than redefining it:

- GATE-3 already restricts files under `spec_paths` to the `spec-author` role, matched by commit author and committer identity against `roles.yml`. ROLES-3 is GATE-3 applied to issue #9's wording, plus the explicit PR #8 narration and the role-naming message.
- GATE-1 already requires a product-code PR to link a spec that exists on the base branch and to carry traced tests. ROLES-4 adds, on top of GATE-1, that the linked task's assigned coder must match the committing identity.
- `roles.yml` already defines `owner`, `spec_paths`, `roles.spec-author.identities`, and `roles.coder.identities`. This spec adds no new roles and no new paths.

**Prerequisite.** GATE-3's `roles.yml` and the spec-path role gate are a prerequisite for ROLES-3, and GATE-1's code-links-a-merged-spec gate is a prerequisite for ROLES-4. Those land in `KyPython/ai-governance#1` (spec #3's implementation) and `#4`. The implementation of this spec should either follow #3's merge or ship the small `roles.yml` additions it depends on in the same PR; the tasks list names this ordering. This spec does not re-create `roles.yml` or GATE-3.

**Reconciliation with #3 and #8.** With #3, this spec shares the role map and the two gates and must not fork them; it cites GATE IDs instead of restating behavior. With #8 (HANDOFF), the routing side lines up: HANDOFF turns a merged spec's tasks into one labeled issue per task and posts the `@codex` trigger only on `codex` issues, which is how a coder learns which task is assigned to it; ROLES-4 then enforces at PR time that the committing coder matches that assignment. Codex ignoring `/kiro` (ROLES-3.6) is the same routing rule HANDOFF relies on.

## Architecture / components

Two artifacts carry the role cards, and four checks carry the enforcement. All of it is described here in prose; no code, YAML, or `roles.yml` edits are made by this spec PR.

**Role-card artifacts**

- **`AGENTS.governance.md` role card.** New prose inside the canonical `AI-GOVERNANCE:v1` section (today it is "Rules 1-11"). The card states the fixed roles in plain words. Because every repo's `AGENTS.md` carries this exact section (that is what the `policy` job's `AI-GOVERNANCE:v1` marker check verifies), the card reaches every repo that holds the section. (ROLES-1.1, ROLES-1.3, ROLES-1.5)
- **Kiro steering template `templates/kiro-steering/roles.md`.** A shareable steering file that states the same roles for Kiro, dropped into each repo as `.kiro/steering/roles.md`. It names the same roles and identities as `roles.yml` so the words and the enforced identities agree. (ROLES-1.2, ROLES-1.4, ROLES-1.5)

**Distribution.** `scripts/optin.sh` already fetches `AGENTS.governance.md` and the caller template from `KyPython/ai-governance` at a pinned SHA, writes/updates the `AGENTS.md` section, and commits. The implementation extends that same step to also copy `templates/kiro-steering/roles.md` to `.kiro/steering/roles.md`. Because the card lives inside the `AI-GOVERNANCE:v1` section, the section-copy already carries it; the steering file is one more copied path. A repo bumping its pinned SHA picks up any card change, exactly as it picks up any other governance change. (ROLES-2.1, ROLES-2.2, ROLES-2.3, ROLES-2.4)

**Policy-job checks** (added to the inline `shell: python3` `policy` job in `governance.yml`)

- **Spec-authorship check.** When any changed path is under `spec_paths`, read the author and committer identity of every commit in the PR range (the job already computes the PR commit range for the secret scan and the changed-file diff) and require each to match a `spec-author` identity in `roles.yml`. Apply the web-flow committer exception (GATE-3.2). On mismatch, fail and emit the role-naming message. This is where the PR #8 case is caught: Codex's commits are `coder` identities, so the check fails and the verdict goes red. (ROLES-3.1, ROLES-3.2, ROLES-3.3, ROLES-3.4, ROLES-3.5, ROLES-3.7)
- **Product-code-links-assigned-task check.** When the PR changes product code, resolve the `Spec: <path>/<slug>` reference against the base branch (GATE-1), read the linked task in that spec's `tasks.md`, extract the task's `coder:` label with the existing task-line grammar, and require it to match the committing identity. On mismatch, fail and name both coders. (ROLES-4.1, ROLES-4.2, ROLES-4.3, ROLES-4.4)
- **Same-coder-reviewer flag.** Compare the reviewer identity (a submitted review's author, or the reviewer named in the PR body) with the committing coder. If they are the same identity, warn (notice in the summary); if different, record a PASS. Never a hard failure. (ROLES-5.1, ROLES-5.2, ROLES-5.3)
- **Role-naming message formatter.** A small helper that, given the broken rule and the identities involved, produces the plain-words message that names the role, used by all three checks so the wording is consistent and phone-readable. (ROLES-6.1, ROLES-6.2, ROLES-6.3, ROLES-6.4)

## Data and interfaces

- **`roles.yml` fields relied on.** `owner` (the `KyPython` override), `spec_paths` (`specs/`, `.kiro/specs/`), `roles.spec-author.identities` (notably `kiro-agent[bot]`, `244629292+kiro-agent@users.noreply.github.com`, `Kiro Agent`, with `KyPython`), and `roles.coder.identities` (`kiro-agent[bot]`, `chatgpt-codex-connector[bot]`, `codex`, `cursor[bot]`, `cursoragent`, `Copilot`, `copilot-swe-agent[bot]`, `claude[bot]`, `grok-bot`). The file is read only from `KyPython/ai-governance@main` (GATE-3.5); no caller input changes roles or paths.
- **Commit-identity matching rule.** For every commit in the PR range, take the author and committer. From a `users.noreply.github.com` email, extract the login (the part after `+`, or the whole local part). Also compare the raw commit email and the author/committer name. A commit matches a role when any of login, email, or name equals a role identity, case-insensitively. When the committer is `noreply@github.com` (GitHub web-flow), check only the author. This is the single rule both ROLES-3 and ROLES-4 use.
- **Why commit identity, not PR author.** Agent PRs are pushed and opened with Ky's token, so the PR-level `author` is `KyPython` for every agent. But the Kiro CLI stamps its own git author and committer identity on the commits it makes (`Kiro Agent <244629292+kiro-agent@users.noreply.github.com>`, login `kiro-agent[bot]`), confirmed on the #8 handoff branch's commit history. So the commit identity distinguishes Kiro from a coder while the PR author does not. The check therefore reads commit identity and ignores the PR author, PR labels, and the branch name.
- **Candidate mechanisms evaluated** (the alternatives the README raises), and why commit author/committer identity is chosen as primary:
  - *Signed commit trailer (for example `Signed-off-by` or a custom `Agent:` trailer).* A trailer is just text any agent can write, so it is forgeable and is rejected for the same reason GATE-1.6 ignores self-declared labels.
  - *A PR label (for example `kiro`).* Labels are set by whoever opens the PR (here, Ky's token) and are mutable after a green run; GATE-1.6 already says the gate ignores labels. Rejected as primary.
  - *A branch-name convention (for example `spec/*`).* Branch names are chosen freely by the pusher and are ignored by GATE-1.6. Rejected as primary.
  - *A dedicated Kiro bot identity or GitHub App.* This is the robust long-term fix the README's Limits section names: a distinct identity with write-but-not-admin access makes the signal unforgeable. It is **not yet provisioned**, so it cannot be the mechanism today; the spec records it as the future fix and the residual limit.
  - *Commit author/committer email and login against `roles.yml` (chosen).* It is the one signal that already differs between Kiro and the coders in practice (Kiro stamps `kiro-agent[bot]`), it is what GATE-3 already matches, and it reuses the web-flow exception. Its residual weakness (an agent using Ky's token can stamp `KyPython`) is the stated Known limit, the same one `roles.yml` and GATE-3 already carry.
- **Merged-spec-task lookup.** A code PR links a task by a `Spec: specs/<slug>` line plus the task's requirement IDs (same convention as GATE-1 and HANDOFF issue bodies). The check reads `specs/<slug>/tasks.md` on the base branch, parses the `- [ ] N. <text> (<IDs>) — coder: <name>, reviewer: <name>` line, and matches the task's `coder:` to the committing identity through the commit-identity rule above.
- **Failure-message templates** (role-naming, phone-readable):
  - spec-authorship: `<AgentRole> is a coder and may not change spec files; only Kiro (spec-author) writes specs. This PR changes <spec-path> with commits authored by <identity>.`
  - product-code-link: `This code PR is built by <identity> but task <id> in <spec>/tasks.md is assigned to <coder>; a coder may build only tasks assigned to it in a merged spec.`
  - same-coder-reviewer: `Reviewer and builder are both <identity>; a task must be reviewed by a different coder.`

## Error handling and failure modes

- **Unreadable or incomplete `roles.yml`.** Fail the `policy` job closed, reusing GATE-3.4 (missing owner, spec paths, or spec-author identities is a hard fail). (ROLES-3.7)
- **Web-flow committer.** When a commit's committer is `noreply@github.com`, check only the author, so a GitHub-UI edit by Ky is not misread. (ROLES-3.3)
- **Mixed spec + code PR.** A PR that changes both a `spec_paths` file and product code fails: spec paths may be changed only by `spec-author` in a spec-only PR, and GATE-1.7 already fails a code PR that also touches spec paths. The role-naming message names the spec-authorship break.
- **Reviewer equals builder.** Warn only; never fail. The authoritative no-self-merge control is Ky merging by hand (every agent PR appears as `KyPython`, so required-approval rules cannot bind reviewer identity). The flag makes skipped cross-review visible before Ky merges. (ROLES-5.2)
- **No reviewer yet.** When no review has been submitted and the PR body names no reviewer, record a neutral note rather than a failure; the flag only fires on a positive same-identity match.
- **Ky-token override.** Commits authored and committed as `KyPython` match the owner override and pass, which is the stated Known limit, not a bug to work around.

## Testing strategy (criterion ID -> test file)

Automated Python tests run by this repo's quality (`pytest`) job, extending `tests/test_policy.py` (planned by spec #3, not yet on `main`) and adding focused files. Each test cites the ROLES-n.m ID it verifies in its name or a comment. The files below are intended; they are NOT created by this spec PR.

| Criterion | Test |
| --- | --- |
| ROLES-1.1 | `tests/test_role_cards.py` |
| ROLES-1.2 | `tests/test_role_cards.py` |
| ROLES-1.3 | `tests/test_role_cards.py` |
| ROLES-1.4 | `tests/test_role_cards.py` |
| ROLES-1.5 | `tests/test_role_cards.py` |
| ROLES-2.1 | `tests/test_optin_distribution.py` |
| ROLES-2.2 | `tests/test_optin_distribution.py` |
| ROLES-2.3 | `tests/test_optin_distribution.py` |
| ROLES-2.4 | `tests/test_optin_distribution.py` |
| ROLES-3.1 | `tests/test_policy_spec_authorship.py` |
| ROLES-3.2 | `tests/test_policy_spec_authorship.py` |
| ROLES-3.3 | `tests/test_policy_spec_authorship.py` |
| ROLES-3.4 | `tests/test_policy_spec_authorship.py` |
| ROLES-3.5 | `tests/test_policy_spec_authorship.py` |
| ROLES-3.6 | `tests/test_policy_spec_authorship.py` |
| ROLES-3.7 | `tests/test_policy_spec_authorship.py` |
| ROLES-4.1 | `tests/test_policy_assigned_task.py` |
| ROLES-4.2 | `tests/test_policy_assigned_task.py` |
| ROLES-4.3 | `tests/test_policy_assigned_task.py` |
| ROLES-4.4 | `tests/test_policy_assigned_task.py` |
| ROLES-5.1 | `tests/test_policy_reviewer_flag.py` |
| ROLES-5.2 | `tests/test_policy_reviewer_flag.py` |
| ROLES-5.3 | `tests/test_policy_reviewer_flag.py` |
| ROLES-6.1 | `tests/test_policy_messages.py` |
| ROLES-6.2 | `tests/test_policy_messages.py` |
| ROLES-6.3 | `tests/test_policy_messages.py` |
| ROLES-6.4 | `tests/test_policy_messages.py` |
