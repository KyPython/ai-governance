# Tasks — Lambda Handler API Gateway Event-Shape Regression (Local Tests)

<!-- ODIN_ROW_ID:3f08621e-0a7a-8155-9019-c1739de4151c -->
Relates to #12.
Relates to #18.

> **Spec-only.** These tasks are the plan a later Codex/Cursor handoff executes to build
> the **synthetic starter environment only**. No task implements the fix. Every
> implementation task names an **assigned coder** and a **different reviewer** (issue #18,
> verbatim governing rule). Tasks are dependency-ordered and trace to requirement IDs.

## Assignment rule (issue #18, verbatim governing rule)
> "Every implementation task must name an assigned coder and a different reviewer."

- Each implementation task below has **Coder:** and **Reviewer:** fields.
- The reviewer MUST be a different identity than the coder (enforced per task).
- **Who** fills those names is a KyJahn-owned assignment decision. Entries are
  placeholders `__CODER__` / `__REVIEWER__` until KyJahn assigns them; the handoff MUST
  NOT self-assign or invent names. (`00-human-agency`: authorship/assignment stays human.)

## Prerequisite gate (BLOCKS all implementation tasks)
- **T-000 — Resolve blocking unknowns.** KyJahn confirms U-1 (exact Goal), U-2 (the event-
  shape delta), U-4 (runtime/language/layout), and U-5 (TaskRecorder session). U-3
  (diagnosis/fix) stays reserved. *No `T-1xx+` task may start until T-000 is resolved.*
  - Owner: **KyJahn** (human decision; not an AI coder task).
  - Traces: U-1, U-2, U-4, U-5. Blocks: all tasks below.

---

## Phase 1 — Setup & scaffolding

### T-100 — Create the environment skeleton and setup
- Create the handoff subtree, manifest + committed lockfile, and a README skeleton with the
  one-command setup and the **"STOP HERE — human diagnosis begins"** section.
- Traces: R-500.2, R-700.4, NFR-1, NFR-2. Depends: T-000.
- Acceptance: clean clone runs setup with no manual edits; README contains the STOP section.
- **Coder:** `__CODER__` · **Reviewer:** `__REVIEWER__` (MUST differ from coder).

### T-110 — Add the handler starter stub
- Add a runnable handler stub with the correct signature for the confirmed runtime (U-4)
  whose body is a clearly marked TODO and which **exhibits the failing behavior**. No
  correct event-shape handling.
- Traces: R-500.1, R-700.1. Depends: T-100.
- Acceptance: stub is importable/invocable by the oracle and fails; body is a visible TODO.
- **Coder:** `__CODER__` · **Reviewer:** `__REVIEWER__` (MUST differ from coder).

## Phase 2 — Fixtures

### T-200 — Author the API Gateway event fixtures
- Add checked-in, synthetic, labeled JSON fixtures capturing the shape(s) under test per
  the confirmed delta (U-2). Include the contrasting shape so pass/fail is visible from
  labels.
- Traces: R-200.1, R-200.2, R-200.3, R-200.4. Depends: T-000, T-100.
- Acceptance: fixtures parse as valid JSON; labeled by shape; no real credentials/ARNs/PII
  (secret-scan clean).
- **Coder:** `__CODER__` · **Reviewer:** `__REVIEWER__` (MUST differ from coder).

## Phase 3 — Failing oracle & verification

### T-300 — Write the failing oracle
- Add the automated oracle that loads a fixture, invokes the stub, and asserts the
  **observable** result a correct handler would produce. It must fail against the stub,
  assert behavior (not source), and contain no fix/answer/hint.
- Traces: R-300.1, R-300.2, R-300.3, R-300.4. Depends: T-110, T-200.
- Acceptance: oracle exits non-zero on the stub with a legible message (input shape /
  expected / actual); no corrective logic present.
- **Coder:** `__CODER__` · **Reviewer:** `__REVIEWER__` (MUST differ from coder).

### T-400 — Add the deterministic verification harness
- Add one `verify.*` command that runs the oracle(s), prints a clear verdict + exit code,
  offline and credential-free, with identical results across two consecutive runs.
- Traces: R-100.1, R-100.2, R-100.3, R-400.1, R-400.2. Depends: T-300.
- Acceptance: fails (non-zero) on the delivered environment; double-run is byte-identical.
- **Coder:** `__CODER__` · **Reviewer:** `__REVIEWER__` (MUST differ from coder).

## Phase 4 — Boundary & governance checks

### T-700 — Enforce the STOP line (boundary review)
- Run the four-point boundary checklist against the whole handoff:
  1. verification harness FAILS out of the box (R-700.1);
  2. no solution/patch/answer file or commented-out correct logic, no root-cause prose
     (R-700.2);
  3. no capture of KyJahn's diagnosis/decisions/verification (R-700.3, R-620.1);
  4. README STOP-HERE section present and accurate (R-700.4).
- Also confirm no generative-AI dependency is required to run (R-620.2).
- Traces: R-700.*, R-620.*. Depends: T-100..T-400.
- Acceptance: all four points pass; any failure blocks the handoff.
- **Coder:** `__CODER__` · **Reviewer:** `__REVIEWER__` (MUST differ from coder).

### T-800 — Governance & delivery (handoff PR)
- Open the handoff on a non-`main` branch via PR; do not merge/approve/auto-merge/deploy.
  Conventional-Commit title; body references the issue; ship oracle/tests with behavior;
  pass `quality` + `policy` + `secret-scan` → `verdict`. Add a `SYSTEMS_THINKING_CONTRACT`
  only if KyJahn places the handoff under a structural path.
- Traces: R-600.1, R-600.3, R-600.4, R-600.5. Depends: T-700.
- Acceptance: `ai-governance / verdict` green; KyJahn merges.
- **Coder:** `__CODER__` · **Reviewer:** `__REVIEWER__` (MUST differ from coder).

---

## Human-reserved (NOT handoff tasks — KyJahn only)
These are listed to make the boundary explicit; the handoff MUST NOT perform them.
- **H-1** Diagnose the root cause of the event-shape regression (U-3).
- **H-2** Author the final handler fix/patch.
- **H-3** Make the professional/engineering decisions and record them.
- **H-4** Run and record the final verification (harness goes green by H-2 alone).
- **H-5** Conduct the TaskRecorder session with **no generative-AI interaction** (R-620.2).

## Delivery note for the orchestrator (this spec PR)
The spec PR body MUST include `ODIN_ROW_ID:3f08621e-0a7a-8155-9019-c1739de4151c`,
`Relates to #18`, and `Relates to #12` for deterministic discovery (R-600.2). The
orchestrator publishes; this agent does not push, open, merge, or deploy.

## Traceability
| Task | Requirement IDs | Depends on |
|---|---|---|
| T-000 | U-1,U-2,U-4,U-5 | — |
| T-100 | R-500.2,R-700.4,NFR-1,NFR-2 | T-000 |
| T-110 | R-500.1,R-700.1 | T-100 |
| T-200 | R-200.* | T-000,T-100 |
| T-300 | R-300.* | T-110,T-200 |
| T-400 | R-100.*,R-400.* | T-300 |
| T-700 | R-700.*,R-620.* | T-100–T-400 |
| T-800 | R-600.* | T-700 |
