# Requirements — Lambda Handler API Gateway Event-Shape Regression (Local Tests)

<!-- ODIN_ROW_ID:3f08621e-0a7a-8155-9019-c1739de4151c -->
Relates to #12.
Relates to #18.

> **Spec-only.** This document and its sibling `design.md` / `tasks.md` are the entire
> deliverable of this change. No handler code, fixtures, tests, or configuration are
> created here. A later Codex/Cursor handoff may build **only** the synthetic starter
> environment defined below and MUST stop at the boundary in R-700.

## 1. Source authority and evidence states

Authority order for this spec (highest first):
1. Explicit current instruction from KyJahn.
2. GitHub issue #18 body (the "Kiro contract" block) — the governing source quoted below.
3. Repo governance (`AGENTS.md` / `AGENTS.governance.md`, `.github/workflows/governance.yml`, `.github/CODEOWNERS`).
4. This spec.

Evidence legend used throughout:
- **[VERIFIED GOVERNING RULE]** — stated verbatim in issue #18 or in repo governance files read at authoring time.
- **[VERIFIED CURRENT OBSERVATION]** — observed directly in the repo at authoring time.
- **[INFERENCE]** — reasoned from the above; not independently confirmed.
- **[UNKNOWN]** — not determinable from available sources; requires KyJahn or the Notion row.

### 1.1 Governing contract (verbatim excerpt, issue #18)

> Write a spec-only PR at `/` containing requirements.md, design.md, and tasks.md.
> Requirements must use numbered, testable criteria. Every implementation task must
> name an assigned coder and a different reviewer.
>
> The PR body must include both ODIN_ROW_ID:3f08621e-0a7a-8155-9019-c1739de4151c and
> Relates to #<this issue number> so the automation can discover the spec PR
> deterministically.
>
> Do NOT implement the solution in the spec PR. The eventual Codex/Cursor handoff may
> build only the synthetic starter environment: fixtures, setup, failing tests/oracles,
> deterministic verification, and scaffolding. It must stop before the human diagnosis,
> final patch, completed deliverable, or hidden answer.
>
> The recorded substantive diagnosis, implementation, professional decisions, tests,
> and final verification remain KyJahn's human work. No generative-AI interaction is
> permitted during TaskRecorder.

## 2. Blocking unknowns (MUST be resolved by KyJahn before any implementation)

These are recorded as explicit unknowns, not guesses. The "Exact approved Goal" field
in issue #18 is blank and the linked Notion row is not reachable from this environment.
**[VERIFIED GOVERNING RULE]** (issue #18: "Exact approved Goal (blank)").

- **U-1 — The exact approved Goal.** [UNKNOWN] Issue #18's Goal field is blank.
  The one-sentence goal that scopes the task MUST come from KyJahn or the Notion row
  (`3f08621e0a7a81559019c1739de4151c`). This spec MUST NOT invent it.
- **U-2 — The specific regression.** [UNKNOWN] Which API Gateway event-shape change
  the Lambda handler regresses on (e.g. REST `v1` vs HTTP API `v2.0` payload format,
  a field rename, a presence/absence change, encoding, or multi-value headers) is not
  stated in issue #18. The title names the *symptom class* ("event-shape regression,
  local tests"); the concrete shape delta is KyJahn's diagnosis.
- **U-3 — Root cause and final patch.** [UNKNOWN / RESERVED] The diagnosis and the fix
  are explicitly reserved to KyJahn. **[VERIFIED GOVERNING RULE]** ("substantive
  diagnosis, implementation ... remain KyJahn's human work").
- **U-4 — Target runtime, language, and layout.** [UNKNOWN] The handler language
  (Node/Python/other), the AWS SDK/runtime version, the test runner, and where the
  handler lives are not stated in issue #18 and are not present in this repo
  (**[VERIFIED CURRENT OBSERVATION]**: this repo is a governance repo with no Lambda
  handler). These MUST be confirmed with KyJahn before scaffolding paths are chosen.
- **U-5 — "TaskRecorder" definition.** [UNKNOWN] Issue #18 forbids generative-AI
  interaction "during TaskRecorder" but does not define the tool/session here. Treated
  as a named human-recording session owned by KyJahn; see R-620.

> No requirement below depends on resolving U-1..U-5 by guessing. Each instead names
> the resolution as a prerequisite.

## 3. Scope

**In scope (what a later handoff MAY build):** the *synthetic starter environment* — a
self-contained, deterministic, locally runnable harness that **reproduces a failing
state** for an API Gateway event-shape regression and gives KyJahn a clean bench to
diagnose and fix by hand.

**Out of scope (reserved to KyJahn):** the diagnosis, the handler fix/patch, the
completed deliverable, any "answer key", and the final verification/sign-off.

## 4. Functional requirements

Each requirement is numbered, has MUST/MUST NOT language, a rationale/source, and
acceptance evidence. "The environment" = the synthetic starter environment.

### R-100 — Deterministic, offline reproduction
- **R-100.1** The environment MUST reproduce the failing state locally with no network
  calls and no live AWS resources. **Rationale:** issue #18 ("Local Tests"; "deterministic
  verification"). **Acceptance:** running the documented setup + verify command on a clean
  checkout, twice, produces identical pass/fail results with no outbound network access.
- **R-100.2** The environment MUST be deterministic: fixed inputs, no reliance on wall
  clock, random seeds, locale, or ordering of a hash map. **Acceptance:** two consecutive
  runs produce byte-identical oracle output (R-300).
- **R-100.3** The environment MUST run from a single documented entrypoint command.
  **Acceptance:** the command is named in `design.md` §Setup and succeeds on a clean clone.

### R-200 — API Gateway event fixtures
- **R-200.1** The environment MUST include checked-in fixture(s) representing the API
  Gateway event shape(s) relevant to the regression. **Rationale:** issue #18 ("fixtures").
  **Acceptance:** fixture files exist under the handoff's fixtures directory and are valid
  JSON that parse without error.
- **R-200.2** Fixtures MUST be clearly labeled by event shape (for example, the payload
  format version and whether the field under test is present), so the *contrast* between a
  passing and a failing shape is visible without reading handler code. **Acceptance:** each
  fixture carries a comment/sidecar or filename naming its shape; a reviewer can state which
  fixture is expected to pass and which to fail from the labels alone.
- **R-200.3** Fixtures MUST be synthetic/sanitized and MUST NOT contain real credentials,
  account IDs, tokens, or personal data. **Rationale:** `AGENTS.governance.md` Rule 7
  (**[VERIFIED GOVERNING RULE]**) and the gate's gitleaks scan. **Acceptance:** `secret-scan`
  job passes; no real ARNs/account numbers in fixtures.
- **R-200.4** The *specific* shape delta encoded by the fixtures depends on U-2 and MUST be
  confirmed by KyJahn before the fixtures are authored. The handoff MUST NOT invent the delta.

### R-300 — Failing tests / oracles
- **R-300.1** The environment MUST include at least one automated test/oracle that **fails**
  against the regressed behavior and would **pass** once the handler correctly handles the
  event shape. **Rationale:** issue #18 ("failing tests/oracles"). **Acceptance:** on the
  unpatched starter environment the oracle exits non-zero and names the failing expectation.
- **R-300.2** The oracle MUST assert **observable handler behavior / stable contract**
  (the handler's response or effect for a given event), MUST NOT assert on source-code
  snippets, and MUST NOT be skipped or loosened to go green. **Rationale:**
  `AGENTS.governance.md` Rule 3 (**[VERIFIED GOVERNING RULE]**). **Acceptance:** the test
  reads inputs → runs the handler → asserts output; no string match on handler source.
- **R-300.3** The failing oracle MUST NOT embed the correct fix, the expected diff, or any
  "answer" to the diagnosis. It asserts the *desired observable outcome*, not *how* to reach
  it. **Rationale:** issue #18 ("stop before ... hidden answer"). **Acceptance:** see R-700
  boundary check.
- **R-300.4** The oracle's failure message MUST be legible: it states the input shape, the
  expected observable result, and the actual result. **Acceptance:** failure output contains
  all three.

### R-400 — Verification harness
- **R-400.1** The environment MUST provide a deterministic verification command that reports
  a clear pass/fail verdict and exit code. **Rationale:** issue #18 ("deterministic
  verification"). **Acceptance:** command exits non-zero while unpatched, zero once a correct
  human fix is applied, with no other change.
- **R-400.2** The verification harness MUST be the mechanism that later proves KyJahn's fix,
  but MUST NOT itself contain the fix. **Acceptance:** R-700 boundary check passes.

### R-500 — Scaffolding only
- **R-500.1** The handler module the environment exercises MUST be a **starter stub**: enough
  structure to run the oracle and exhibit the failing state, with the substantive logic left
  for KyJahn. **Rationale:** issue #18 ("scaffolding"; "stop before the ... final patch").
  **Acceptance:** the stub's handler body is a clearly marked TODO/placeholder that produces
  the failing behavior, not a working implementation.
- **R-500.2** Setup files (manifest, lockfile, test config, README for running it) MUST be
  present so the environment is reproducible. **Rationale:** issue #18 ("setup"). **Acceptance:**
  a clean clone runs setup → verify without manual edits.

### R-600 — Governance alignment
- **R-600.1** The spec-only change (this directory) MUST be delivered on a non-`main` branch
  via PR and MUST NOT be merged, approved, auto-merged, or deployed by any agent; KyJahn
  merges. **Rationale:** `AGENTS.governance.md` Rules 1 and the merge gate
  (**[VERIFIED GOVERNING RULE]**).
- **R-600.2** The spec PR body MUST contain both `ODIN_ROW_ID:3f08621e-0a7a-8155-9019-c1739de4151c`
  and `Relates to #18` (plus `Relates to #12`) so Odin automation can discover it
  deterministically. **Rationale:** issue #18 (**[VERIFIED GOVERNING RULE]**). **Acceptance:**
  the strings appear in the PR body. *(The orchestrator opens the PR; this requirement records
  the obligation.)*
- **R-600.3** The PR title MUST follow Conventional Commits and the body MUST reference the
  issue, to satisfy the `policy` job. **Rationale:** `governance.yml` policy checks
  (**[VERIFIED CURRENT OBSERVATION]**). **Acceptance:** `ai-governance / verdict` passes.
- **R-600.4** No governance file (`.github/**`, `AGENTS*.md`, `CODEOWNERS`, `.husky/`,
  `.claude/`, `.cursor/`) may be edited by this change or the later handoff to make a gate
  pass. **Rationale:** `AGENTS.governance.md` Rule 6 (**[VERIFIED GOVERNING RULE]**).
- **R-600.5** No destructive commands, no deploys, and no spend by any agent at any stage.
  **Rationale:** `AGENTS.governance.md` Rules 8, 11; infra guardrails (**[VERIFIED GOVERNING RULE]**).

### R-620 — Human-authorship and no-AI-during-recording boundary
- **R-620.1** The diagnosis, implementation/final patch, professional decisions, tests of the
  fix, and final verification/sign-off MUST remain KyJahn's human work. **Rationale:** issue
  #18 (**[VERIFIED GOVERNING RULE]**). **Acceptance:** the handoff deliverable contains no such
  content (R-700).
- **R-620.2** No generative-AI interaction is permitted during the TaskRecorder session.
  **Rationale:** issue #18 (**[VERIFIED GOVERNING RULE]**). **Acceptance:** recorded as a hard
  constraint in `design.md`; the environment does not require or invoke a generative-AI call to
  run. (U-5: exact TaskRecorder tooling confirmed by KyJahn.)

### R-700 — The STOP line (explicit, testable boundary)
This is the single most important acceptance boundary. The synthetic starter environment is
**complete** only when all of R-700 hold.
- **R-700.1** The handoff MUST NOT include a working/correct handler implementation of the
  regression fix. **Acceptance:** running the verification harness on the delivered environment
  (unmodified) FAILS (non-zero). If it passes out of the box, the fix leaked — reject.
- **R-700.2** The handoff MUST NOT include an answer key, a "solution"/"fix"/"patch" file, a
  reference diff, or commented-out correct logic. **Acceptance:** no file or comment in the
  handoff states the root cause or the corrective change; a reviewer scan finds none.
- **R-700.3** The handoff MUST NOT record or assert KyJahn's diagnosis, decisions, or final
  verification result. **Acceptance:** reviewer confirms absence.
- **R-700.4** The boundary MUST be stated in the handoff's README so the human picks up exactly
  at diagnosis. **Acceptance:** README contains a "STOP HERE — human diagnosis begins" section
  mapping to R-700.

## 5. Non-functional requirements
- **NFR-1** Reproducibility: pinned dependency versions / lockfile committed (supports R-100).
- **NFR-2** Portability: runs on a standard dev machine and in CI without AWS credentials.
- **NFR-3** Legibility: a reviewer unfamiliar with the task can run setup → verify and see the
  failing oracle within minutes using only the README.

## 6. Traceability summary
| Req | Source | Reserved to KyJahn? |
|---|---|---|
| R-100–R-500 | issue #18 "synthetic starter environment" list | No (handoff may build) |
| R-600 | repo governance / issue #18 PR-discovery rule | No |
| R-620, R-700 | issue #18 human-work + stop-line clauses | Yes (boundary) |
| U-1–U-5 | issue #18 blank Goal + absent context | Yes (must resolve first) |
