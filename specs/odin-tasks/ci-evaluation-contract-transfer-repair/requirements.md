# Requirements — CI Evaluation Contract Transfer Repair

## Scope
Prepare a synthetic grading repository in which written evaluation requirements are not fully enforced before grading. The environment must expose a real enforcement gap without pre-implementing the final fail-closed validation or final negative fixture.

## Functional requirements
1. **R1 — Synthetic-only repository.** Use fabricated requirements, fixtures, package names, data, and CI configuration.
2. **R2 — Written evaluation contract.** A recorder-visible document shall define at least one mandatory pre-grading requirement in clear, testable language.
3. **R3 — Incomplete enforcement boundary.** The starter CI/grading flow shall omit enforcement of at least one written mandatory requirement, allowing one defective case to progress farther than the contract permits.
4. **R4 — Valid case preserved.** Include at least one valid fixture/workflow that passes the starter pipeline.
5. **R5 — Reproducible defective case.** Include starter data/scaffolding sufficient for the engineer to construct or expose the unenforced case during the recording, but do not ship the final negative fixture required by the approved deliverable.
6. **R6 — Fail-closed target is discoverable, not solved.** The code structure shall contain a bounded transfer/validation boundary where a human can add one enforcement check, but no recorder-visible file may identify the exact final patch.
7. **R7 — Deterministic local CI simulation.** Provide a local command that runs the same validation/grading sequence deterministically.
8. **R8 — No weakening.** Existing unrelated checks in the starter shall remain meaningful so the recorded engineer can demonstrate that the eventual correction preserves them.
9. **R9 — No answer key.** Do not include a completed validator, final negative fixture, diagnosis note, expected patch diff, or hidden solution file.
10. **R10 — Handoff integrity.** Before recording, a reviewer can verify the valid case passes, the enforcement gap exists, and the final task remains undone.

## Acceptance criteria
- AC1: Local pipeline command succeeds for the valid fixture.
- AC2: Inspection shows at least one written mandatory requirement is not enforced at the transfer/CI boundary.
- AC3: The repository contains no completed fail-closed check or final negative fixture.
- AC4: Unrelated checks are runnable and meaningful.
