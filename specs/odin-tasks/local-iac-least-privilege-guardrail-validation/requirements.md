# Requirements — Local IaC Least-Privilege Guardrail Validation

## Scope
Prepare a synthetic infrastructure-as-code starter in which a locally synthesized cloud template contains one bounded permission/configuration problem. The starter must support inspection and deterministic policy validation without supplying the human diagnosis, least-privilege correction, decisive regression tests, or completed deliverable.

## Functional requirements
1. **R1 — Synthetic-only project.** All names, identifiers, resources, policies, and data are fabricated.
2. **R2 — Local synthesis.** Infrastructure synthesis runs locally, deterministically, and without cloud credentials or network access.
3. **R3 — Bounded unsafe state.** One inspectable identity policy in the starter template is broader than the workload contract requires.
4. **R4 — Workload contract.** Neutral documentation describes what the workload must do and the resources it uses without diagnosing the starter defect or prescribing a patch.
5. **R5 — Ordinary-path coverage.** Starter tests check stable synthesis behavior and unrelated safety properties while leaving the decisive least-privilege assertion for the human.
6. **R6 — Policy extension point.** A small local validator exposes a clear place to add further guardrails without naming or implementing the final check.
7. **R7 — Reproducible baseline.** Document short commands for synthesis, template inspection, and the passing starter suite.
8. **R8 — No final repair.** Do not narrow the seeded policy, add the decisive negative assertion, or include a ready-to-paste correction.
9. **R9 — No answer key.** Recorder-visible content must not state the concrete diagnosis, expected diff, hidden solution, or final narration.
10. **R10 — Human completion.** The human remains responsible for diagnosis, the smallest correction, decisive tests, verification, and explanation.

## Acceptance criteria
- AC1: Synthesis produces byte-for-byte stable JSON without external services.
- AC2: The starter suite passes and validates meaningful ordinary properties.
- AC3: Inspection reveals enough evidence for a human to reason from workload needs to granted permissions.
- AC4: No decisive least-privilege test or completed correction is present.
