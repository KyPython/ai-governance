# Design — Vacuous Test Suite Audit

> Spec-only design. This document describes an *intended* synthetic environment
> that does not yet exist. It contains no implementation. Where a detail is a
> genuine open question, it is labeled UNKNOWN and left as an
> environment-construction decision — it is NOT fabricated here as settled.

## Provenance

- Approved goal: audit a synthetic Python module whose pytest suite passes
  despite a seeded defect; identify the vacuous assertions; rewrite them into
  meaningful checks; verify the strengthened suite fails on the defective build
  and passes on the corrected build.
- Odin row: https://app.notion.com/p/3f08621e0a7a81eda36bdd125c60221c
  (ODIN_ROW_ID `3f08621e-0a7a-81ed-a36b-dd125c60221c`).
- Approval ID: `ODIN-5959D60FB16547A0A846BB836D8D0C3F`.
- GitHub issue #13 in KyPython/ai-governance (Relates to #12).

---

## 1. Current implementation (greenfield / synthetic)

**Evidence state: VERIFIED CURRENT OBSERVATION.**

Nothing for this task exists yet. As observed in this repo at spec-authoring
time, there is no `specs/odin-tasks/vacuous-test-suite-audit/` content beyond
this package, no synthetic Python module, no pytest suite, no fixtures, and no
verification harness. Therefore there is **no current runtime behavior to
report** — this is a greenfield build. Every "behavior" below is intended and
to-be-created, not observed.

The repo itself is a governance repo (reusable CI workflow, `AGENTS.md`,
`CODEOWNERS`, templates, scripts). This spec adds documentation only and does not
interact with that machinery.

## 2. Intended design (to-be-created)

**Evidence state: INTENDED / TO-BE-CREATED.**

### 2.1 Synthetic module (REQ-1)

A single, self-contained Python module with documented, deterministic behavior.
No network, clock, randomness, or external I/O in the behavior under audit. The
module represents no real product and embeds no real metric or personal fact.

- **Documented-behavior statement:** prose in the module docstring (and/or a
  short note) stating what the function(s) promise, specific enough that a
  meaningful assertion can check it.

### 2.2 Seeded defect (REQ-2)

Exactly one intentional defect in the **defective build** that violates at least
one clause of the documented behavior, observable through the public interface,
and NOT a crash/import/syntax error (so the vacuous suite still passes). The
defect's description lives in a withheld answer artifact (see §6, Human gates).

### 2.3 Vacuous pytest suite (REQ-3)

A pytest suite whose assertions do not actually check the documented behavior.
Representative vacuity patterns (illustrative, to be chosen during construction —
not an authored test here):

- asserting a tautology (e.g., comparing a value to itself);
- asserting only that "no exception was raised";
- over-mocking so the real behavior is never exercised;
- asserting against a value the test itself computed from the same code path;
- asserting on type/shape but never on the documented value;
- a test that imports but never calls the behavior under audit.

This suite exits **0** on the defective build. That green result is the headline
failure of test quality (see §4).

### 2.4 Dual builds (REQ-4)

A deterministic selector (flag / env var / separate target — selection mechanism
is an UNKNOWN below) chooses between:

- **Defective build:** defect present; documented behavior violated.
- **Corrected build:** defect absent; documented behavior satisfied.

The two builds differ only by the defect and its minimal correction.

### 2.5 Strengthened suite (REQ-6, human-owned)

KyJahn rewrites each vacuous assertion into a meaningful check of documented
observable behavior. This is human authorship, not AI-authored.

## 3. The audit flow (end to end)

**Evidence state: INTENDED.**

1. Build the starter environment (AI-buildable): module, seeded defect, vacuous
   suite, dual builds, deterministic verification harness, withheld answer.
2. Confirm the starter signal (AI-buildable): vacuous suite exits 0 on the
   defective build.
3. **[HUMAN GATE] Diagnosis (REQ-5):** KyJahn identifies, by file/line, the
   vacuous assertions and why each is vacuous. No generative AI; recorded in
   TaskRecorder.
4. **[HUMAN GATE] Rewrite + patch (REQ-6):** KyJahn authors the meaningful
   assertions and the corrected build. No generative AI during TaskRecorder.
5. **[HUMAN GATE] Verification (REQ-7):** KyJahn runs the strengthened suite on
   both builds and confirms non-zero on defective, zero on corrected,
   deterministically.
6. **[HUMAN GATE] Acceptance (REQ-7.4, REQ-8):** KyJahn accepts the deliverable.
   No merge/deploy/publish by any agent.

## 4. Current failures (the designed-in vacuity)

**Evidence state: VERIFIED FAILURE (by design, once the environment is built).**

The defining failure is a **false-green**: the pytest suite passes while the
module's documented behavior is broken by the seeded defect. This is intentional
and is the artifact the audit exists to expose. Until the environment is built,
this failure does not yet exist; it will be a reproduced-on-purpose state.

## 5. Evidence boundary — what "green" proves here

**Evidence state: PROPOSED CONSTRAINT.**

- In the starter state, **green proves nothing** about correctness: the suite is
  vacuous, so a passing run is compatible with a broken module. (Per
  `10-source-authority` steering: green tests do not prove behavior unless the
  requirement is mechanically covered.)
- Green becomes meaningful only *after* REQ-6: once assertions check documented
  behavior, a pass on the corrected build and a fail on the defective build
  together are the signal. The pair of exit codes — not a single green — is the
  evidence (REQ-7).
- Per AGENTS.governance rule 2, no agent may claim "tests pass" without running
  them; the final run and its acceptance are KyJahn's (REQ-7.4).

## 6. Human gates and ownership boundary

**Evidence state: PROPOSED CONSTRAINT (binding).**

| Element | AI-buildable (starter env) | Human-owned (KyJahn) |
| --- | --- | --- |
| Synthetic module + documented behavior | Yes | — |
| Seeded defect + withheld answer artifact | Yes (create + withhold) | — |
| Vacuous pytest suite | Yes | — |
| Dual defective/corrected build mechanism | Yes (mechanism + defective build) | Final corrected patch |
| Deterministic verification harness | Yes (harness only) | Running + accepting the verdict |
| Diagnosis of vacuous assertions | No | Yes (REQ-5) |
| Rewrite into meaningful checks | No | Yes (REQ-6) |
| Final verification + acceptance | No | Yes (REQ-7) |

- The withheld answer artifact (seeded-defect description) MUST NOT be exposed to
  the diagnosis workflow or any AI step that could leak it (REQ-8.3).
- **No generative-AI interaction during TaskRecorder** (REQ-8.4).
- No agent may merge, deploy, publish, or submit on KyJahn's behalf (REQ-8.5;
  AGENTS.governance rules 1, 10).

## 7. Unknowns requiring reproduction / construction decisions

**Evidence state: UNKNOWN (needs reproduction) — do not fabricate.**

- **UNKNOWN-1 — module domain.** The specific domain of the synthetic module is
  not decided here. Bounded options to pick from during construction (not a
  settled choice): a small pure-function utility (e.g., a parsing/validation or
  arithmetic/rounding routine), a tiny stateful container with documented
  invariants, or a simple formatter/serializer. Constraint: deterministic,
  self-contained, no real product (REQ-1.3, REQ-1.4).
- **UNKNOWN-2 — exact seeded defect.** The precise defect is a construction
  decision, bounded by REQ-2 (one defect, observable via public interface, not a
  crash). Not fabricated here.
- **UNKNOWN-3 — build-selection mechanism.** Whether dual builds are selected via
  env var, flag, or two targets is an open design choice bounded by REQ-4.2
  (deterministic, explicit, reproducible).
- **UNKNOWN-4 — count/mix of vacuous patterns.** The number and mix of vacuous
  assertions (REQ-3.3) is a construction decision bounded by the single-module
  scope.
- **UNKNOWN-5 — verification harness form.** Whether verification is a thin
  shell script, a Makefile target, or a documented command sequence is open,
  bounded by REQ-7.3 (deterministic, repeatable). Must not add CI/governance
  changes (REQ-9.3).

Each unknown is to be resolved during environment construction and recorded
there, not pre-decided in this spec.

## 8. Proposed implementation constraints

**Evidence state: PROPOSED CONSTRAINT.**

- Python + pytest only for the synthetic environment; no extra heavy deps unless
  justified during construction.
- Single-module scope; no sprawling suite or multi-module system.
- Deterministic throughout (no randomness/clock/network in the audited behavior
  or verification).
- Starter environment only from AI; stop at the human gates (§6).
- Stay within the approved goal; invent no product direction, metrics, or
  KyJahn's conclusions (REQ-9.4).
- Touch nothing outside `specs/odin-tasks/vacuous-test-suite-audit/` for this
  spec change; the later build must not modify governance files (REQ-9.3).
- Branch + PR only; checks are the gate; only KyJahn merges (AGENTS.governance
  rules 1–2). This spec change itself is not committed/merged by the agent.
