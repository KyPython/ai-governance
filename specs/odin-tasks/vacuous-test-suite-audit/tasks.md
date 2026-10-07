# Tasks — Vacuous Test Suite Audit

> Spec-only. These tasks are a dependency-ordered plan for a later bounded
> handoff and for KyJahn's human-owned work. No implementation is performed in
> this spec. Each implementation task names an **assigned coder** and a
> **different reviewer** (coder ≠ reviewer). Tasks stop at the human-owned gates.

## Provenance

- Approved goal (verbatim) and Kiro contract govern scope.
- Odin row `3f08621e-0a7a-81ed-a36b-dd125c60221c`; Approval ID
  `ODIN-5959D60FB16547A0A846BB836D8D0C3F`; GitHub issue #13 (Relates to #12).

## Ownership legend

- **[AI-BUILDABLE]** — Codex/Cursor may build this; synthetic starter
  environment only (fixtures, setup, failing/oracle tests, deterministic
  verification, scaffolding).
- **[HUMAN-OWNED — KyJahn]** — substantive diagnosis, final patch, final
  verification, and acceptance. AI MUST NOT perform or pre-fill these. No
  generative-AI interaction during TaskRecorder.

> Names below (`coder` / `reviewer`) are role placeholders to be assigned to two
> distinct people/agents at handoff; the coder and reviewer MUST NOT be the same
> person for any task. KyJahn is the human owner for all `[HUMAN-OWNED]` tasks
> and the final merge/acceptance authority throughout.

---

## TASK-1 — Create the synthetic Python module + documented behavior
- **Traces to:** REQ-1.
- **Ownership:** [AI-BUILDABLE]
- **Assigned coder:** Coder A
- **Reviewer (distinct):** Reviewer B
- **Depends on:** none.
- **Done when:** one deterministic, self-contained synthetic module exists with a
  prose documented-behavior statement; no real product/metric/personal fact
  (REQ-1.1–1.4). Reviewer B confirms the behavior is specific enough to assert
  against. Resolve UNKNOWN-1 here and record the choice.

## TASK-2 — Seed exactly one defect + write the withheld answer artifact
- **Traces to:** REQ-2.
- **Ownership:** [AI-BUILDABLE]
- **Assigned coder:** Coder B
- **Reviewer (distinct):** Reviewer A
- **Depends on:** TASK-1.
- **Done when:** the defective build violates ≥1 documented-behavior clause via
  the public interface, is not a crash/import/syntax error, and the defect is
  captured in a withheld answer artifact that is kept out of the diagnosis path
  (REQ-2.1–2.4, REQ-8.3). Reviewer A confirms the defect is detectable by a
  meaningful oracle and that the answer artifact is not leaked. Resolve
  UNKNOWN-2 here.

## TASK-3 — Build the vacuous pytest suite (passes on defective build)
- **Traces to:** REQ-3.
- **Ownership:** [AI-BUILDABLE]
- **Assigned coder:** Coder A
- **Reviewer (distinct):** Reviewer C
- **Depends on:** TASK-1, TASK-2.
- **Done when:** a pytest suite of real (non-commented) vacuous assertions exits
  **0** on the defective build, within single-module scope (REQ-3.1–3.4).
  Reviewer C confirms the assertions are genuinely vacuous and enumerable by
  file/line. Resolve UNKNOWN-4 here.

## TASK-4 — Implement deterministic dual builds (defective / corrected selector)
- **Traces to:** REQ-4.
- **Ownership:** [AI-BUILDABLE] for the mechanism + defective build. The final
  corrected patch content is produced under TASK-7 (human-owned).
- **Assigned coder:** Coder B
- **Reviewer (distinct):** Reviewer B
- **Depends on:** TASK-2.
- **Done when:** a deterministic, explicit, reproducible selector switches builds;
  the two builds differ only by the defect and its minimal correction point
  (REQ-4.1–4.4). Reviewer B confirms determinism and that no other differences
  exist. Resolve UNKNOWN-3 here. (Note: the corrected build's actual fix is
  authored in TASK-7.)

## TASK-5 — Build the deterministic verification harness (reports exit codes only)
- **Traces to:** REQ-7.3 (harness), supports REQ-7.1–7.2.
- **Ownership:** [AI-BUILDABLE] — harness only; it MUST NOT embed or reveal the
  answer artifact and MUST NOT run the final acceptance.
- **Assigned coder:** Coder C
- **Reviewer (distinct):** Reviewer A
- **Depends on:** TASK-3, TASK-4.
- **Done when:** a deterministic, repeatable harness runs a given suite against a
  selected build and reports its exit code reproducibly (REQ-7.3). Reviewer A
  confirms repeatability (same inputs → same exit codes) and that no answer
  leaks. Resolve UNKNOWN-5 here.

## TASK-6 — [HUMAN-OWNED — KyJahn] Diagnose the vacuous assertions
- **Traces to:** REQ-5.
- **Ownership:** [HUMAN-OWNED — KyJahn] — AI MUST NOT perform or pre-fill. No
  generative-AI interaction during TaskRecorder.
- **Depends on:** TASK-3 (and the confirmed starter signal from TASK-5).
- **Done when:** KyJahn produces a human-authored list of each vacuous assertion
  by file/line with the reason it is vacuous, recorded under the no-AI
  TaskRecorder constraint (REQ-5.1–5.3). **AI handoff stops before this task.**

## TASK-7 — [HUMAN-OWNED — KyJahn] Rewrite into meaningful checks + author corrected build
- **Traces to:** REQ-6 (and completes the corrected build for REQ-4.3).
- **Ownership:** [HUMAN-OWNED — KyJahn] — AI MUST NOT author the final
  assertions or the fix. No generative-AI interaction during TaskRecorder.
- **Depends on:** TASK-6.
- **Done when:** KyJahn's strengthened suite asserts documented observable
  behavior, is traceable assertion-by-assertion to the vacuous originals, is not
  weakened/skipped/deleted to force green, and the corrected build satisfies the
  documented behavior (REQ-6.1–6.4, REQ-4.3).

## TASK-8 — [HUMAN-OWNED — KyJahn] Verify before/after signal + accept
- **Traces to:** REQ-7, REQ-8.
- **Ownership:** [HUMAN-OWNED — KyJahn] — AI MUST NOT self-attest the result or
  accept the deliverable. No merge/deploy/publish by any agent.
- **Depends on:** TASK-5, TASK-7.
- **Done when:** using the TASK-5 harness, KyJahn confirms the strengthened suite
  exits **non-zero** on the defective build and **zero** on the corrected build,
  deterministically; KyJahn records the exit codes and accepts the deliverable
  (REQ-7.1–7.4). Acceptance, merge, and any release remain KyJahn's.

---

## Dependency order summary

```
TASK-1 → TASK-2 → TASK-3 ┐
                 TASK-2 → TASK-4 ┐
                 TASK-3, TASK-4 → TASK-5
--- AI handoff stops here (synthetic starter environment complete) ---
TASK-3 → TASK-6 (human)
TASK-6 → TASK-7 (human)
TASK-5, TASK-7 → TASK-8 (human: verify + accept)
```

## Guardrail recap (applies to every task)
- AI builds only the synthetic starter environment (TASK-1 … TASK-5); it stops
  before TASK-6 (REQ-8.1–8.2).
- The seeded-defect answer artifact is never exposed to the diagnosis path or any
  AI step (REQ-8.3).
- No generative-AI interaction during TaskRecorder (REQ-8.4).
- No agent merges, deploys, publishes, or submits on KyJahn's behalf
  (REQ-8.5; AGENTS.governance rules 1, 10).
- This spec change touches only the three files under
  `specs/odin-tasks/vacuous-test-suite-audit/` (REQ-9).
