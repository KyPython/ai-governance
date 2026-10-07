# Requirements — Vacuous Test Suite Audit

> Spec-only deliverable. No product/implementation code, test code, fixtures, or
> scaffolding is included or authorized by this document. This file defines
> requirements for a later, bounded Codex/Cursor handoff and for KyJahn's
> human-owned diagnosis and fix.

## Provenance and authority

- **Approved goal (verbatim, authoritative):** "As a QA engineer, audit a
  synthetic Python module whose pytest suite passes even though a seeded defect
  breaks the documented behavior, identify the vacuous assertions that let it
  pass, rewrite them into meaningful checks, and verify that the strengthened
  suite fails on the defective build and passes on the corrected build."
- **Odin Notion row:** https://app.notion.com/p/3f08621e0a7a81eda36bdd125c60221c
- **ODIN_ROW_ID:** `3f08621e-0a7a-81ed-a36b-dd125c60221c`
- **Approval ID:** `ODIN-5959D60FB16547A0A846BB836D8D0C3F`
- **GitHub issue:** #13 in KyPython/ai-governance — "[Odin Spec] Vacuous Test
  Suite Audit — Tests Pass While the Claim Is False" (Relates to #12).

The approved goal is the sole authority for scope. This spec serves exactly that
goal and nothing broader. Where this spec and the goal appear to conflict, the
goal wins.

## Evidence-state legend

Each requirement is tagged with the honest evidence state of what it describes.
Because the target environment is **synthetic and does not yet exist**, almost
nothing here is a verified current observation of a running system.

- **VERIFIED CURRENT OBSERVATION** — observed directly in this repo/session.
- **INTENDED / TO-BE-CREATED** — behavior to be built; not yet observed.
- **VERIFIED FAILURE** — a failure state to be reproduced on purpose (the
  vacuity); it does not exist until the environment is built.
- **UNKNOWN (needs reproduction)** — a genuine open question for environment
  construction.
- **PROPOSED CONSTRAINT** — a constraint this spec places on the build.

## Scope boundary

- IN SCOPE: a single synthetic Python module, its documented behavior, a seeded
  defect, a vacuous pytest suite, dual (defective / corrected) builds, the
  strengthened suite, and deterministic verification of the before/after signal.
- OUT OF SCOPE: real products, product direction, metrics, broader test-infra
  tooling, CI changes, governance changes, and any claim about KyJahn's
  conclusions. Do not invent any of these.

---

## REQ-1 — Synthetic Python module with documented behavior

**Subject:** the system under audit.
**Evidence state:** INTENDED / TO-BE-CREATED.

1.1. The deliverable MUST include exactly one synthetic Python module that is
     purpose-built for this audit and represents no real product.
1.2. The module MUST have documented behavior stated in prose (docstring and/or
     a short spec note) that is specific enough to be checked by assertions.
1.3. The module's domain MUST be simple, self-contained, and deterministic (no
     network, clock, randomness, or external I/O in the behavior under audit).
1.4. The module MUST NOT reference or embed any real KyJahn product name, metric,
     or personal fact.

**Rationale/source:** approved goal ("a synthetic Python module … documented
behavior"); Kiro contract (synthetic starter environment only).
**Acceptance evidence:** the module exists at a fixed path with a documented
behavior statement; a reviewer can read the doc and name the behavior being
promised. The specific domain is an environment-construction decision (see
`design.md`, UNKNOWN-1); it MUST NOT be fabricated here as settled.
**Dependency:** none (root requirement).

## REQ-2 — Seeded defect that breaks the documented behavior

**Subject:** the intentional defect.
**Evidence state:** INTENDED / TO-BE-CREATED.

2.1. The defective build MUST contain exactly one seeded defect that causes the
     module to violate at least one clause of its REQ-1 documented behavior.
2.2. The defect MUST be observable through the module's public interface (i.e.,
     a correct, meaningful test could detect it).
2.3. The defect MUST be recorded in a hidden/answer artifact that is NOT required
     for, and MUST NOT be surfaced during, KyJahn's diagnosis (see REQ-8).
2.4. The defect MUST NOT be a syntax error, import error, or crash — the module
     MUST import and run so the vacuous suite can still pass.

**Rationale/source:** approved goal ("a seeded defect breaks the documented
behavior"); Kiro contract (the hidden answer is withheld).
**Acceptance evidence:** with the defect present and a meaningful oracle applied,
the documented behavior is demonstrably violated; the defect is captured in the
answer artifact. The exact defect is an environment-construction decision
(UNKNOWN-2) and MUST NOT be asserted as settled here.
**Dependency:** REQ-1.

## REQ-3 — Vacuous pytest suite that passes anyway

**Subject:** the starting (weak) test suite.
**Evidence state:** INTENDED / TO-BE-CREATED (its green result is a planned
VERIFIED FAILURE of test quality once built).

3.1. The starter deliverable MUST include a pytest suite whose assertions are
     *vacuous* — e.g., asserting on nothing meaningful, asserting a tautology,
     asserting only that no exception was raised, over-mocking the behavior under
     test, or asserting against a value the test itself produced.
3.2. The vacuous suite MUST exit **zero (pass)** when run against the defective
     build of REQ-2.
3.3. The suite MUST contain enough vacuous patterns to make the audit non-trivial
     but MUST stay within the single-module scope (no sprawling suite).
3.4. Each vacuous assertion MUST be real pytest code (not commented-out), so the
     auditor can point to the exact lines that let the defect pass.

**Rationale/source:** approved goal ("whose pytest suite passes even though a
seeded defect breaks the documented behavior … the vacuous assertions that let
it pass").
**Acceptance evidence:** `pytest` exits 0 on the defective build; the vacuous
assertions are present and enumerable.
**Dependency:** REQ-1, REQ-2.

## REQ-4 — Dual builds: defective and corrected

**Subject:** the two deterministic build states.
**Evidence state:** INTENDED / TO-BE-CREATED.

4.1. The deliverable MUST provide a deterministic way to select between a
     **defective build** (defect present) and a **corrected build** (defect
     absent, documented behavior satisfied).
4.2. Build selection MUST be reproducible and explicit (e.g., a flag, env var, or
     separate build target) and MUST NOT depend on nondeterministic state.
4.3. The corrected build MUST satisfy every clause of the REQ-1 documented
     behavior.
4.4. The two builds MUST differ only by the seeded defect and whatever minimal
     change corrects it — nothing else.

**Rationale/source:** approved goal ("fails on the defective build and passes on
the corrected build"); Kiro contract (deterministic verification).
**Acceptance evidence:** a reviewer can switch builds deterministically and
confirm the corrected build meets the documented behavior while the defective one
does not.
**Dependency:** REQ-1, REQ-2.

## REQ-5 — Audit identifies the vacuous assertions (human-owned)

**Subject:** the diagnosis of why the suite is vacuous.
**Evidence state:** INTENDED / human-owned work product.

5.1. The audit SHALL identify, by file and line, each vacuous assertion that
     allowed the defect to pass, with a stated reason it is vacuous.
5.2. The identification SHALL be KyJahn's substantive human work; AI MUST NOT
     perform or pre-fill the diagnosis.
5.3. The audit record SHALL be captured during TaskRecorder with **no
     generative-AI interaction** (Kiro contract).

**Rationale/source:** approved goal ("identify the vacuous assertions that let it
pass"); Kiro contract (diagnosis is KyJahn's human work; no generative AI during
TaskRecorder).
**Acceptance evidence:** a human-authored list of vacuous assertions with
locations and reasons, recorded under the no-AI TaskRecorder constraint.
**Dependency:** REQ-3 (the vacuous suite must exist to be audited).

## REQ-6 — Rewrite into meaningful checks (human-owned)

**Subject:** the strengthened test suite.
**Evidence state:** INTENDED / human-owned work product.

6.1. The strengthened suite SHALL replace each vacuous assertion with a check
     that asserts the module's documented observable behavior (per
     AGENTS.governance rule 3: observable behavior / stable contracts, not source
     snippets).
6.2. The strengthened suite SHALL NOT be weakened, skipped, or deleted to force a
     green result.
6.3. The rewrite SHALL be KyJahn's substantive human work; AI MUST NOT author the
     final meaningful assertions.
6.4. The strengthened checks MUST stay within the single-module scope.

**Rationale/source:** approved goal ("rewrite them into meaningful checks");
AGENTS.governance rule 3; Kiro contract (implementation/decisions are human).
**Acceptance evidence:** the strengthened suite asserts documented behavior and
is traceable, assertion-by-assertion, to the vacuous ones it replaces.
**Dependency:** REQ-5.

## REQ-7 — Verification: fail on defective, pass on corrected

**Subject:** the before/after signal that proves the fix.
**Evidence state:** INTENDED / to be verified by KyJahn.

7.1. The strengthened suite MUST exit **non-zero (fail)** when run against the
     defective build.
7.2. The strengthened suite MUST exit **zero (pass)** when run against the
     corrected build.
7.3. The verification MUST be deterministic and repeatable (same inputs → same
     exit codes).
7.4. The final verification run and its acceptance SHALL be KyJahn's human
     decision; AI MUST NOT self-attest the result.

**Rationale/source:** approved goal ("verify that the strengthened suite fails on
the defective build and passes on the corrected build"); AGENTS.governance rule 2
(never claim tests pass without running them); Kiro contract (final verification
is human-owned).
**Acceptance evidence:** recorded exit codes — strengthened suite non-zero on
defective build, zero on corrected build — produced deterministically and
accepted by KyJahn.
**Dependency:** REQ-4, REQ-6.

## REQ-8 — Human/AI ownership and TaskRecorder boundary

**Subject:** the authorship and tooling boundary.
**Evidence state:** PROPOSED CONSTRAINT (binding on the build).

8.1. AI (Codex/Cursor) MAY build ONLY the synthetic starter environment:
     fixtures, setup, the failing/oracle tests, deterministic verification
     harness, and scaffolding.
8.2. AI MUST stop before the human diagnosis (REQ-5), the final patch/correction,
     the completed deliverable, and the final verification/acceptance (REQ-7).
8.3. The seeded-defect answer artifact (REQ-2.3) MUST NOT be exposed to the
     diagnosis workflow or to any AI step that could leak it.
8.4. During TaskRecorder, there MUST be **no generative-AI interaction**.
8.5. No step authorized by this spec may merge, deploy, publish, or submit on
     KyJahn's behalf.

**Rationale/source:** Kiro contract (verbatim); AGENTS.governance rules 1, 2, 10;
Human Agency Runtime steering.
**Acceptance evidence:** the handoff builds only the starter environment; the
diagnosis, patch, and verification are human-authored and recorded with no
generative-AI involvement; no merge/deploy/publish occurs.
**Dependency:** applies across REQ-1 … REQ-7.

## REQ-9 — Spec-only, no-scope-creep, no-governance-touch

**Subject:** this deliverable's own boundaries.
**Evidence state:** VERIFIED CURRENT OBSERVATION (of this spec package).

9.1. This change MUST consist of exactly three Markdown files under
     `specs/odin-tasks/vacuous-test-suite-audit/` (`requirements.md`,
     `design.md`, `tasks.md`).
9.2. This change MUST NOT add product/implementation code, test code, fixtures,
     or scaffolding.
9.3. This change MUST NOT create or modify governance files (`AGENTS.md`,
     `AGENTS.governance.md`, `.github/`, `CODEOWNERS`, workflows, `templates/`,
     `scripts/`) or any other file in the repo.
9.4. The eventual implementation MUST remain within the approved goal and MUST
     NOT invent product direction, metrics, or KyJahn's conclusions.

**Rationale/source:** Kiro contract; Kiro-First Cloud Delivery steering;
AGENTS.governance rule 6.
**Acceptance evidence:** the diff contains only the three named spec files; no
governance or other files are touched.
**Dependency:** none.
