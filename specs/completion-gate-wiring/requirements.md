# Requirements: Wire the Completion Gate into every agent, in CI and locally

Spec ID: CGW · Issue: #269 · Status: proposed; Ky approves by merging this spec-only PR
Author: Kiro (spec author), from Ky's 2026-11-11 instruction "Now wire it into all agents in the cloud and locally".
Coders implement these sentences; they do not edit them to fit the code.

## Introduction

The Completion Gate runs a human-approved contract of checks when an agent says a task is done and returns
VERIFIED, FAILED or UNKNOWN, with UNKNOWN never reported as VERIFIED. Its spec and code were built and judged
outside this repo (Google Drive, `Spec Briefs & Evals/Completion Gate Spec/`: requirements, design, tasks,
amendment A1, frozen acceptance suite, bake-off result).

This spec makes every coding agent (Kiro, Codex, Cursor, Antigravity/Gemini, Claude Code, Copilot, Grok Bot)
run that gate before claiming completion, and makes the governance verdict check it in CI.

Out of scope: changing the gate's verdict rules (they live in the gate's own spec and A1), the vault/agent
identity spec (draft, Ky's Nov 17 review), deploys, and any repo outside the opt-in model.

### Evidence states

- **Verified current behaviour** (read or run 2026-11-11):
  - The gate exists only in Google Drive, not in any git repo, so CI and cloud agents cannot run it.
  - On that copy, the frozen neutral suite passes 124 of 125 with 0 hard-gate violations. The one failure is a
    superseded 60-line test. Its own tests pass 18 of 18.
  - `ai-governance / verdict` (`.github/workflows/governance.yml`) runs install/lint/type-check/test/build,
    policy checks including the spec gate, and gitleaks. It runs no completion contract.
  - `AGENTS.governance.md` rule 3 ("Prove it green before you stop") is self-attested: nothing checks it.
  - User-level agent rule files exist at `~/.codex/AGENTS.md`, `~/.gemini/GEMINI.md` and `~/.cursor/rules/`.
    Kiro has `~/.kiro/hooks/`. There is no `~/.claude/CLAUDE.md`. None of them mention a completion gate.
- **Intended existing behaviour:** spec paths are writable only by the spec-author role, and a code PR may not
  touch them (`roles.yml`, rule 2). This spec relies on that to keep contracts out of coders' reach.
- **Unknowns requiring confirmation before the matching task:**
  - which file Antigravity reads its user rules from (`~/.gemini/GEMINI.md` is likely, not confirmed);
  - where Kiro's global steering lives on this machine (no `~/.kiro/steering/` directory exists);
  - whether Codex Cloud, Cursor background agents and Copilot read anything beyond the repo's `AGENTS.md`.

## Requirements

### Requirement 1: Versioned gate home (CGW-1)

**User Story:** As Ky, I want the gate's code in this repo at a pinned revision, so that CI and every agent run
the same reviewed code.

#### Acceptance Criteria

1. CGW-1.1 WHEN the import lands THEN the repo SHALL contain `completion-gate/` with `completion_gate.py`,
   `contract_validator.py`, `completion_aggregator.py`, `schemas/`, `tests/`, the frozen acceptance suite and a
   README.
2. CGW-1.2 WHEN the import lands THEN each imported file SHALL be byte-identical to the Drive `code/` and
   `bakeoff/acceptance/` copies, and the PR SHALL list each file's SHA-256. Any difference SHALL be listed and
   justified in the PR body.
3. CGW-1.3 WHEN the import is merged THEN `completion-gate/` on `main` SHALL be the canonical code, and the Drive
   copy SHALL be recorded as historical in `Completion Gate Spec/SOURCE-OF-TRUTH.md`.
4. CGW-1.4 The repo's own test run SHALL include `completion-gate/tests` and the acceptance suite, with the
   superseded `test_A1_D1_line_budget_le_60` replaced by a 120-counted-line check citing A1-D1.

### Requirement 2: Contracts live with the spec (CGW-2)

**User Story:** As Ky, I want each task's completion contract approved with its spec, so that the agent doing
the work can never write or loosen its own definition of done.

#### Acceptance Criteria

1. CGW-2.1 The contract for a spec SHALL live at `specs/<slug>/completion-contract.json` (or
   `.kiro/specs/<slug>/completion-contract.json`) and SHALL be valid under the gate's contract schema.
2. CGW-2.2 WHEN a contract is added or changed THEN that change SHALL arrive in a spec-only PR. The existing
   spec-path rule then limits it to the spec-author role and Ky.
3. CGW-2.3 `templates/spec/` SHALL include a `completion-contract.json` template with every required key and a
   comment-free placeholder for each.
4. CGW-2.4 IF a contract check needs to run a task-specific test THEN the command SHALL name that test, and the
   test name SHALL cite the requirement ID it verifies.

### Requirement 3: CI enforcement in the governance verdict (CGW-3)

**User Story:** As Ky, I want the verdict to run the contract on every code PR that has one, so that a done
claim made in the cloud is checked by something other than the agent.

#### Acceptance Criteria

1. CGW-3.1 WHEN a code PR's spec has a base-branch contract THEN the verdict SHALL run that contract against the
   PR's head revision. "Has a base-branch contract" means the PR's `Spec: specs/<slug>` line names a spec whose
   folder on the base branch holds `completion-contract.json`.
2. CGW-3.2 The verdict SHALL read the contract from the **base branch** and run `completion_gate.py` from the
   `ai-governance` revision pinned by the caller, never from the PR's own tree.
3. CGW-3.3 The step SHALL upload the evidence file as a workflow artifact and write the verdict, the reasons and
   the contract hash to the job summary.
4. CGW-3.4 The caller input `completion-gate` SHALL accept `off`, `advisory` or `required`, defaulting to
   `advisory`. WHILE `advisory` THEN a FAILED or UNKNOWN result SHALL be reported but SHALL NOT fail the
   verdict. WHILE `required` THEN anything other than VERIFIED SHALL fail the verdict.
5. CGW-3.5 IF a code PR references a spec that has no contract THEN the verdict SHALL report "no completion
   contract" and SHALL NOT report VERIFIED for completion.
6. CGW-3.6 The step SHALL run with `permissions: contents: read`, receive no repository secrets, and pass no
   `--audit` file. Audit flags in CI arrive only through a later spec.
7. CGW-3.7 Changing the default from `advisory` to `required` SHALL be a separate PR that Ky merges.

### Requirement 4: One completion-claim rule for every agent (CGW-4)

**User Story:** As Ky, I want every agent told the same thing about claiming "done", so that no agent claims
completion without gate evidence.

#### Acceptance Criteria

1. CGW-4.1 `AGENTS.governance.md` SHALL gain a rule titled "Done means a VERIFIED completion gate", which says:
   - when the task's spec has a completion contract, the agent SHALL run
     `python3 completion-gate/completion_gate.py <contract> --evidence <file>` before claiming completion;
   - the agent SHALL quote the verdict line, the evidence path and the contract hash in its completion message;
   - FAILED or UNKNOWN means the task is not done, and the agent SHALL say so in those words;
   - when no contract exists, the agent SHALL say "no completion contract; not gate-verified";
   - the agent SHALL NOT write, edit or delete a contract, pass an `--audit` file it authored, or edit the gate.
2. CGW-4.2 WHEN the rule lands THEN `optin.sh` SHALL deliver it to opted-in repos through the existing canonical
   AGENTS.md section, unchanged in wording.
3. CGW-4.3 The same rule text SHALL be installed in each user-level agent rule file that exists on Ky's
   machine (Codex `~/.codex/AGENTS.md`, Antigravity/Gemini `~/.gemini/GEMINI.md`, Cursor `~/.cursor/rules/`,
   Kiro's global steering), inside a marked block `<!-- BEGIN COMPLETION GATE RULE --> ... <!-- END ... -->`
   so it can be found and removed. Any other content in those files SHALL be left unchanged.
4. CGW-4.4 IF a target rule file's location is unconfirmed (see Unknowns) THEN the installer SHALL skip it and
   report it as skipped. It SHALL NOT create a guessed file.

### Requirement 5: Local enforcement where the agent supports it (CGW-5)

**User Story:** As Ky, I want local runs checked by a hook where the agent allows one, so that the local rule is
more than an instruction where enforcement is possible.

#### Acceptance Criteria

1. CGW-5.1 WHERE an agent supports a session-end or stop hook (Kiro: `Stop`) the hook SHALL run the gate when a
   completion contract is resolvable for the current task, and SHALL show the verdict and evidence path.
2. CGW-5.2 IF the hook cannot resolve a contract, find the gate, or run it THEN it SHALL report "not
   gate-verified" with the reason. It SHALL never report VERIFIED.
3. CGW-5.3 The hook SHALL NOT block or alter the agent's other tools, and SHALL NOT write anywhere except its
   evidence file.
4. CGW-5.4 Agents without hook support SHALL be listed in the README as rule-only. CI (CGW-3) is their
   enforcement.

### Requirement 6: Honest limits (CGW-6)

**User Story:** As Ky, I want the limits stated, so that wiring is not mistaken for proof.

#### Acceptance Criteria

1. CGW-6.1 The README SHALL state that:
   - the local rule is advisory for rule-only agents;
   - commands in a contract run with the runner's permissions and are not sandboxed;
   - git identities are self-declared (`roles.yml` limit);
   - VERIFIED means the declared checks passed, not that the work is correct for users.
2. CGW-6.2 No task under this spec SHALL change `roles.yml`, branch protection, CODEOWNERS or another repo's
   pinned SHA. Rollout to repos happens by Ky bumping each caller's pin.
