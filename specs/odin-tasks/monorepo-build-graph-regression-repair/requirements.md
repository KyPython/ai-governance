# Requirements — Monorepo Build-Graph Regression Repair

## Scope
Prepare a synthetic pnpm/Turborepo monorepo with a reproducible service build regression caused by two independently observable configuration problems described by the approved task: a shared workspace dependency now has its own build step, and one build/container configuration still references an obsolete package name. Do not include the final repairs.

## Functional requirements
1. **R1 — Synthetic monorepo only.** Use fabricated package/service names, source code, data, and configuration.
2. **R2 — Workspace graph.** Include one service package and at least one shared workspace dependency consumed by that service.
3. **R3 — Shared package build step.** The shared dependency shall require its own deterministic build output before the service can build successfully.
4. **R4 — Broken build relationship.** The starter build configuration shall fail to ensure the required transitive/shared build happens correctly for the affected service.
5. **R5 — Obsolete package reference.** A separate build/container/configuration surface shall reference an old package identity that no longer matches the current workspace package.
6. **R6 — Reproducible failure.** Provide a documented command that deterministically reproduces the build regression from a clean starter checkout after dependency installation.
7. **R7 — Two root causes remain independent.** The starter shall make it possible to demonstrate that correcting only one problem is insufficient.
8. **R8 — Unrelated workspace behavior.** Include at least one unrelated package/check that can remain passing so the recorded correction can be shown as bounded.
9. **R9 — No final repair.** Do not pre-correct the workspace build graph, the stale package reference, or provide a ready-to-paste final diff/verification note.
10. **R10 — Neutral recorder-visible docs.** README/setup instructions may explain how to install and reproduce the failure, but must not label exact files/lines as the answers.

## Acceptance criteria
- AC1: `pnpm install`/equivalent setup is reproducible.
- AC2: The designated service build fails from the starter state.
- AC3: Both approved defect classes are present.
- AC4: No completed repair or answer-key note exists.
- AC5: At least one unrelated check remains independently runnable.
