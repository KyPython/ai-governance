# Requirements — Vacuous Test Suite Audit

## Scope
Prepare a synthetic Python/pytest starter repository for the approved Odin task. This specification governs only the pre-recording starter environment. It must not contain the human diagnosis, strengthened final assertions, defect repair, completed deliverable, or an answer key.

## Functional requirements
1. **R1 — Synthetic project only.** The repository shall contain only fabricated code, documentation, test data, names, and values. No private source, credentials, Mercor/Odin admin content, or personal data may appear.
2. **R2 — Documented behavior.** The starter shall include a concise product/module behavior contract that a reviewer can use to determine the intended behavior without being told the defect.
3. **R3 — Seeded behavioral defect.** The implementation shall violate at least one documented behavior in a bounded, reproducible way.
4. **R4 — Vacuous passing suite.** The initial pytest suite shall pass on the defective implementation because one or more assertions fail to prove the documented behavior. The weak assertions must look superficially plausible rather than being obvious placeholders.
5. **R5 — Independent reproduction.** A single documented command shall reproduce the initial passing suite from a clean checkout.
6. **R6 — Human-discoverable evidence.** The repository shall provide enough observable behavior and documentation for a software/QA engineer to discover that the suite is insufficient through inspection and execution during TaskRecorder.
7. **R7 — No solution leakage.** Recorder-visible files shall not identify which assertions are vacuous, describe the corrective implementation patch, contain a strengthened hidden test suite, or state the expected human diagnosis.
8. **R8 — Deterministic tooling.** Setup and baseline test commands shall be deterministic and local; avoid network-dependent runtime behavior after dependencies are installed.
9. **R9 — Packaging.** The starter shall include a neutral README with setup/run instructions only, plus a script or documented command for the baseline test run.
10. **R10 — Pre-recording integrity.** A reviewer shall be able to verify that the defective code and weak suite are present and that no completed solution exists before recording.

## Acceptance criteria
- AC1: Clean setup completes using the declared Python/pytest toolchain.
- AC2: Baseline pytest exits successfully.
- AC3: Manual comparison of the behavior contract and implementation demonstrates that a real documented behavior can be false while the weak suite remains green.
- AC4: No file states the final correction or provides ready-to-paste strengthened assertions.
- AC5: All recorder-visible names are neutral and synthetic.
## Recording envelope
- The baseline command should complete quickly enough to support diagnosis and at least two verification runs inside a 15:00–45:59 recording without long idle waits.
