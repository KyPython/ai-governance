# Requirements: Agent role cards and role enforcement

Spec ID: ROLES · Issue: #9 · Status: proposed; Ky approves by merging this spec-only PR

Provenance: Kiro drafted these sentences from Ky's issue #9 goal and done checks. Ky owns the sentences, and coders implement them exactly; they do not paraphrase them to fit the code. The drafting agent (Kiro) does not build the mechanism; coders do, in a later PR, after Ky merges this spec.

## Introduction

Agents keep stepping outside their roles. On PR #8, Codex picked up a `/kiro` fix request that was meant for Kiro and started rewriting a spec file. Only Kiro writes specs. The fix is two-sided: tell every agent its role in the place where that agent actually reads instructions, and make the shared governance check stop any agent that steps outside its role, with a message that names the broken role so Ky can read it from his phone.

The roles are fixed by Ky and do not change in this spec:

- **Kiro** writes specs: `requirements.md` with numbered acceptance criteria, `design.md`, and `tasks.md`, as spec-only PRs that merge before code. Kiro also fixes its own spec PRs. Kiro does not build product code unless a merged spec assigns a task to Kiro's builders (`kiro-agent[bot]`).
- **Codex** builds only tasks that a merged spec assigns to it. Codex never creates or edits spec files. Codex ignores requests addressed to Kiro (`/kiro`) and acts only when a handoff explicitly assigns it a task.
- **Cursor / Grok Bot** builds or reviews only tasks that a merged spec assigns to it. It never writes or edits specs. It opens plain-language `kiro` issues and routes work.
- **Reviewer** is a different coder than the one who built the task. A PR whose reviewer is the same coder that built it is flagged.
- **Ky** reviews and merges by hand. No agent merges, approves, or deploys its own work.
- **CI and governance checks** judge every PR; the `ai-governance / verdict` check is the required gate on `main`.

This spec **extends**, and does not redefine, the substrate already proposed in spec #3 (`KyPython/ai-governance#2`, the AI governance spec gate):

- the role map `roles.yml` (roles `spec-author`, `coder`, `approver`; `spec_paths`; `owner: KyPython`);
- the spec-path role gate **GATE-3** (only the `spec-author` role may change files under `spec_paths`, read from `roles.yml` on `KyPython/ai-governance@main`);
- the code-must-link-a-merged-spec gate **GATE-1**.

It also relates to the spec-merge handoff spec #5 (`HANDOFF`), which turns merged-spec tasks into one issue per task and routes `codex` work. This spec treats `roles.yml` and GATE-3 as prerequisites: the role cards here describe the same role map that `roles.yml` encodes, and the enforcement here reuses GATE-3's commit-identity matching rather than inventing a second one. Where #3 already states a rule (GATE-1.6 ignoring labels and branch names, GATE-3.1 commit-identity match, GATE-3.2 web-flow committer exception, GATE-3.4 fail-closed `roles.yml`, GATE-3.6 Kiro's builders are coders too), this spec cites it instead of restating it as new behavior.

## Requirements

### Requirement 1: Role cards where each agent reads (ROLES-1)

**User Story:** As Ky, I want each agent told its role in the file that agent actually reads, so that no agent has to guess its role and none can claim it did not know.

#### Acceptance Criteria

1. ROLES-1.1 The system SHALL state the fixed roles (Kiro writes specs and fixes its own spec PRs; Codex builds only assigned merged-spec tasks and never edits specs; Cursor / Grok Bot builds or reviews only assigned merged-spec tasks and never writes specs; reviewer differs from builder; Ky reviews and merges by hand; no agent merges) in plain words in an `AGENTS.md` role card, which is the file Codex and other coding agents read.
2. ROLES-1.2 The system SHALL state the same fixed roles in plain words in a Kiro steering file under `.kiro/steering/` (for example `.kiro/steering/roles.md`), which is the file Kiro reads.
3. ROLES-1.3 WHEN the role card text is authored THEN the `AGENTS.md` role card SHALL live inside the canonical shareable `AI-GOVERNANCE:v1` section of `AGENTS.governance.md`, so that it propagates to every repo through the same section every repo already copies, rather than as repo-local prose that can drift.
4. ROLES-1.4 The Kiro steering card SHALL be shipped as a shareable template in `KyPython/ai-governance` (for example `templates/kiro-steering/roles.md`) so that every repo receives the same card rather than writing its own.
5. ROLES-1.5 The role cards (both the `AGENTS.md` section text and the Kiro steering card) SHALL name the same roles and the same identities as `roles.yml`, so that the words an agent reads and the identities the gate enforces cannot disagree.

### Requirement 2: Shareable distribution to every repo (ROLES-2)

**User Story:** As Ky, I want the role cards to reach every KyPython and KyLamportLogic repo through the opt-in and caller setup I already use, so that one place defines the cards and every repo picks them up.

#### Acceptance Criteria

1. ROLES-2.1 WHEN `scripts/optin.sh` opts a repo in THEN the system SHALL write or update that repo's `AGENTS.md` governance section (the `AI-GOVERNANCE:v1` section from `AGENTS.governance.md`, now carrying the role card) in the same step it already writes that section.
2. ROLES-2.2 WHEN `scripts/optin.sh` opts a repo in THEN the system SHALL drop the Kiro steering card (`.kiro/steering/roles.md`) from the shared template into that repo.
3. ROLES-2.3 WHEN the role card text in `AGENTS.governance.md` or the steering template changes on `KyPython/ai-governance@main` AND a repo bumps its pinned governance SHA in a PR THEN that repo SHALL pick up the changed cards, matching the existing "callers pin a SHA; a change here affects nobody until each repo bumps it" model.
4. ROLES-2.4 The distribution SHALL NOT require any repo to store a secret of its own, matching the existing opt-in (the cards are text copied by `optin.sh`, not a credential).

### Requirement 3: Spec-authorship enforcement (ROLES-3)

**User Story:** As Ky, I want a PR that adds, changes, or deletes a spec file to fail unless its commits come from Kiro, so that only Kiro writes specs and the PR #8 case cannot repeat.

#### Acceptance Criteria

1. ROLES-3.1 WHEN a pull request adds, changes, or deletes a file under `spec_paths` (`specs/`, `.kiro/specs/`) THEN the system SHALL fail the `policy` job unless the author and committer of every commit in the PR match an identity of the `spec-author` role in `roles.yml`, reusing GATE-3.1 rather than defining a second rule.
2. ROLES-3.2 WHEN the system decides whether a commit's identity matches `spec-author` THEN it SHALL compare the GitHub login (the login inside a `users.noreply.github.com` commit email, for example `kiro-agent[bot]` from `244629292+kiro-agent@users.noreply.github.com`), the commit email, and the author or committer name against the `spec-author` identities in `roles.yml` (notably `kiro-agent[bot]`, `244629292+kiro-agent@users.noreply.github.com`, `Kiro Agent`, with `KyPython` as the owner override), case-insensitively.
3. ROLES-3.3 WHEN a commit's committer is GitHub's web-flow identity (`noreply@github.com`) THEN the system SHALL check only that commit's author, reusing GATE-3.2.
4. ROLES-3.4 WHEN deciding whether a spec PR passes ROLES-3 THEN the system SHALL rely on the git author and committer identity of the commits and SHALL NOT rely on the PR author, a PR label, or the branch name, because PRs are pushed with Ky's token and so the PR-level author shows as `KyPython` while the commit identity is the reliable signal (reusing GATE-1.6, which already ignores labels, branch names, and PR authors for exemption).
5. ROLES-3.5 WHEN an agent other than Kiro (for example Codex, whose commits are authored as `chatgpt-codex-connector[bot]` or `codex`, or Cursor / Grok Bot as `cursor` / `cursoragent` / `grok-bot`) adds, changes, or deletes a file under `spec_paths` THEN the `policy` job SHALL fail and the `ai-governance / verdict` check (the required status check on `main`) SHALL be red, so the PR cannot merge. This is the PR #8 case: Codex picked up a `/kiro` fix request and edited a spec file; its commit identity is a `coder`, not `spec-author`, so the required check goes red and names the role.
6. ROLES-3.6 WHEN a request is addressed to Kiro with `/kiro` THEN Codex and the other coders SHALL ignore it (they act only on tasks a merged spec assigns to them), and the gate SHALL still block any spec-file change whose commits are not Kiro's, so routing by convention is backed by the enforced commit-identity rule rather than trusted on its own.
7. ROLES-3.7 IF `roles.yml` cannot be read, or lacks an owner, `spec_paths`, or `spec-author` identities THEN the system SHALL fail the `policy` job closed, reusing GATE-3.4.

### Requirement 4: Product code must link an assigned merged-spec task (ROLES-4)

**User Story:** As Ky, I want a product-code PR to fail unless it links a merged spec task that is assigned to the coder who built it, so that an agent only builds work that was assigned to it.

#### Acceptance Criteria

1. ROLES-4.1 WHEN a pull request changes product code THEN the system SHALL fail the `policy` job unless the PR body references, with a `Spec: <spec-path>/<slug>` line, a spec folder that already exists on the base branch, reusing GATE-1.2.
2. ROLES-4.2 WHEN a product-code PR links a spec folder THEN the system SHALL resolve the referenced task in that spec's `tasks.md` on the base branch and SHALL fail unless the task's assigned coder matches the author and committer identity of the PR's commits, using the same identity-matching rule as ROLES-3.2.
3. ROLES-4.3 WHEN the committing identity is not the coder named on the linked task THEN the system SHALL fail the `policy` job and name both the task's assigned coder and the committing identity, so that a coder building another coder's task is caught.
4. ROLES-4.4 WHEN `kiro-agent[bot]` opens or commits to a product-code PR THEN the system SHALL apply the same code rules as for every other coder, including the assigned-task rule and the no-spec-change-in-a-code-PR rule, reusing GATE-3.6 and GATE-1.7.

### Requirement 5: Same-coder-reviewer flag (ROLES-5)

**User Story:** As Ky, I want a PR whose reviewer is the same coder that built it to be flagged, so that cross-review by a different agent is visible and self-review stands out.

#### Acceptance Criteria

1. ROLES-5.1 WHEN a pull request's reviewer (the identity that submitted the review, or the identity named in the PR body as the reviewer) is the same coder as the author and committer of the PR's commits THEN the system SHALL flag it with a clear notice that names the shared coder identity.
2. ROLES-5.2 The same-coder-reviewer signal SHALL be a warning in the `policy` job (a notice in the job summary) rather than a hard failure, because the no-self-merge gate already lives with Ky (every agent PR appears as `KyPython`, so required approvals cannot enforce reviewer identity; see GATE-3's `approver` note), and the flag exists so Ky can see at a glance that cross-review was skipped before he merges.
3. ROLES-5.3 WHEN the reviewer differs from the builder THEN the system SHALL record a PASS line, so the scorecard shows cross-review happened.

### Requirement 6: Clear role-naming failure messages (ROLES-6)

**User Story:** As Ky, I want every enforcement failure to name the role that was broken in plain words, so that I can tell what happened from my phone without opening the diff.

#### Acceptance Criteria

1. ROLES-6.1 WHEN the spec-authorship check (ROLES-3) fails THEN the message SHALL name the acting agent, its role, and that only Kiro writes specs, for example: `Codex is a coder and may not change spec files; only Kiro (spec-author) writes specs. This PR changes specs/<path> with commits authored by codex.`
2. ROLES-6.2 WHEN the product-code-link check (ROLES-4) fails THEN the message SHALL name the committing coder, the linked task, and the task's assigned coder, for example: `This code PR is built by codex but task <id> in specs/<slug>/tasks.md is assigned to cursor; a coder may build only tasks assigned to it in a merged spec.`
3. ROLES-6.3 WHEN the same-coder-reviewer flag (ROLES-5) fires THEN the message SHALL name the shared coder and state that the reviewer must be a different coder, for example: `Reviewer and builder are both codex; a task must be reviewed by a different coder.`
4. ROLES-6.4 Every enforcement message SHALL be emitted so it appears in the `policy` job summary (the lines Ky reads on his phone), and SHALL name the role in words, not only an identity string, matching the existing `::error::` / `::warning::` style of the `policy` job.

#### Known limit (ROLES)

Git author and committer fields are self-declared, so an agent that pushes with Ky's own token and stamps `KyPython` as the author and committer cannot be told apart from Ky himself; the gate then treats those commits as the owner override and lets them through. This matches the limit already recorded in `roles.yml` and in GATE-3's `#### Known limit`. The spec-authorship and assigned-task checks therefore prove only the identities that the commits declare. The robust fix is to give each agent its own GitHub App or bot identity with write-but-not-admin access (the Cursor / Codex GitHub apps, or a dedicated Kiro App), as the README's Limits section describes; until that identity exists, the check trusts the declared commit identity and this spec reuses `kiro-agent[bot]` as the Kiro identity rather than a provisioned App.
