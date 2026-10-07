# Requirements: Exact-match grader normalization false-positive repair

Spec ID: EMGN · Issue: #20 · Odin row: 3f08621e-0a7a-811a-a81d-c7a39ac80b91 · Status: proposed; Ky approves by merging this spec-only PR

Provenance: Kiro drafted these sentences from only two inputs available in the authoring environment: the issue #20 title/slug ("Exact-Match Grader Normalization False-Positive Repair") and the generic Project Odin contract text quoted in the task instruction. At authoring time the issue's "Exact approved Goal" field was empty, its "Approval ID" was empty, and its "Spec path" was empty. The authoritative goal lives in a Notion row (ODIN_ROW_ID `3f08621e-0a7a-811a-a81d-c7a39ac80b91`) that was NOT readable from the authoring environment. KyJahn owns the goal; this spec MUST be reconciled against that Notion row before it is relied on. Nothing here is a verified claim about a real grader: no grader source exists in this repo (confirmed by search), so the grader's existence, location, design, root cause, normalization rules, and final diagnosis/fix are treated as UNKNOWN, not asserted. Where a requirement is general-purpose it is written as a proposed implementation constraint; where it depends on KyJahn's goal it is marked UNKNOWN.

## Introduction

An "exact-match grader" compares a produced answer against an expected answer and reports pass/fail. Such graders normalize both sides first (for example trimming, case-folding, or whitespace collapsing) so that trivially different strings still compare equal. A **false positive** is a grade of PASS when the two answers are in fact semantically distinct: normalization has erased a difference that should have mattered, so a wrong answer is scored correct.

This spec frames a repair of that class of defect. It is written spec-first and is spec-only: it creates exactly three markdown files under `specs/exact-match-grader-normalization/` and no product code, workflow YAML, or tests. Per the Project Odin contract, the eventual Codex/Cursor handoff may build ONLY the synthetic starter environment (fixtures, setup, failing tests/oracles, deterministic verification, scaffolding) and MUST stop before the human diagnosis, the final patch, the completed deliverable, or any hidden answer. The recorded substantive diagnosis, implementation, professional decisions, tests, and final verification remain KyJahn's human work, and no generative-AI interaction is permitted during TaskRecorder.

The spec keeps these evidence states distinct, as the spec-first steering requires:

- **Verified current behavior:** none observed. No grader source is present in this repo, so no current behavior has been seen.
- **Intended existing behavior:** an exact-match grader is intended to grade PASS only when the produced answer matches the expected answer after an agreed normalization, and FAIL otherwise.
- **Verified failures:** none reproduced here. The false positive is reported by the task title; it has not been reproduced in the authoring environment.
- **Unknowns requiring reproduction:** the specific grader, its normalization pipeline, the exact inputs that produce the false positive, and the expected grades. See EMGN-0.
- **Proposed implementation constraints:** the MUST / MUST NOT language in the requirements below, which constrains any repair without inventing the goal.

### UNKNOWN — requires KyJahn's Notion goal (EMGN-0)

The following cannot be specified without the authoritative Notion goal (ODIN_ROW_ID `3f08621e-0a7a-811a-a81d-c7a39ac80b91`). They are UNKNOWN, not guesses, and MUST be filled in by KyJahn (or from a repo he names) before any implementation task starts:

- **EMGN-0.1 (UNKNOWN) — the exact grader under repair.** Which grader, in which repository and file path, is the subject of this repair. No grader source exists in this repo.
- **EMGN-0.2 (UNKNOWN) — the precise normalization behavior that produces the false positive.** The current normalization steps (for example case-folding, whitespace handling, Unicode normalization, punctuation stripping, numeric or ordering tolerance) and which step collapses a distinction that should remain.
- **EMGN-0.3 (UNKNOWN) — concrete example inputs and expected outputs.** At least one produced answer and expected answer that currently grade PASS but should grade FAIL, with the grade each should receive.
- **EMGN-0.4 (UNKNOWN) — the acceptance oracle values.** The exact expected grades (and any tolerance) the deterministic oracle must assert, so a reproducing fixture can encode a failing case precisely.
- **EMGN-0.5 (UNKNOWN) — the substantive diagnosis and the final patch.** The root cause and the corrective change remain KyJahn's human work and are explicitly out of scope for the AI handoff.

Until EMGN-0.1 through EMGN-0.5 are resolved from the Notion goal, the requirements below constrain only what is general-purpose and verifiable for an exact-match grader normalization false-positive repair.

## Requirements

### Requirement 1: Reproduction-first repair (EMGN-1)

**User Story:** As KyJahn, I want any repair to be driven by a reproducing fixture that I supply or confirm, so that the work targets a real, demonstrated false positive and not an invented one.

#### Acceptance Criteria

1. EMGN-1.1 The repair MUST be driven by at least one reproducing fixture that KyJahn supplies or explicitly confirms, encoding a produced answer and expected answer that currently grade PASS but should grade FAIL.
2. EMGN-1.2 WHEN no KyJahn-supplied or KyJahn-confirmed reproducing fixture exists THEN the implementation handoff MUST NOT begin, and the task MUST remain blocked on EMGN-0.3.
3. EMGN-1.3 The implementation MUST NOT invent example inputs, expected outputs, root cause, or normalization rules; where these are not supplied they SHALL remain marked UNKNOWN per EMGN-0.
4. EMGN-1.4 The reproducing fixture MUST identify, by stable reference, the exact grader and normalization step it exercises (resolving EMGN-0.1 and EMGN-0.2), so the fixture is traceable to the grader under repair.

### Requirement 2: Normalization MUST NOT collapse distinct answers (EMGN-2)

**User Story:** As a consumer of grades, I want normalization to preserve meaningful distinctions, so that two semantically different answers never compare equal.

#### Acceptance Criteria

1. EMGN-2.1 Normalization MUST NOT cause two semantically distinct answers to compare equal; WHEN a produced answer differs from the expected answer in a way the grading contract treats as significant THEN the grader SHALL return FAIL.
2. EMGN-2.2 The grader MUST return PASS only when the produced answer and the expected answer are equal under the agreed normalization; IF they are not equal under that normalization THEN it MUST NOT return PASS.
3. EMGN-2.3 The agreed normalization (which distinctions are significant versus ignorable) MUST come from KyJahn's goal (EMGN-0.2) and MUST NOT be inferred by the implementation.
4. EMGN-2.4 A repair MUST NOT introduce a new false negative: WHEN a produced answer is in fact correct under the agreed normalization THEN the grader SHALL still return PASS. (This criterion depends on EMGN-0.2/EMGN-0.4 for its concrete oracle values.)

### Requirement 3: Failing oracle test in the synthetic starter environment (EMGN-3)

**User Story:** As KyJahn, I want the synthetic starter environment to contain a failing oracle test that encodes the false-positive case, so that the defect is demonstrable before any human diagnosis begins.

#### Acceptance Criteria

1. EMGN-3.1 The synthetic starter environment MUST include at least one failing oracle test that encodes the false-positive case from the reproducing fixture (EMGN-1.1): the current grader returns PASS while the oracle asserts FAIL.
2. EMGN-3.2 The failing oracle test MUST assert the expected grade from the acceptance oracle values (EMGN-0.4) and MUST fail against the unrepaired grader, so the failure demonstrates the defect rather than a test-authoring error.
3. EMGN-3.3 The synthetic starter environment MUST NOT contain the diagnosis, the corrective patch, the completed deliverable, or any hidden answer; it MUST stop at fixtures, setup, failing tests/oracles, deterministic verification, and scaffolding.
4. EMGN-3.4 Each oracle test MUST cite the requirement ID(s) it verifies (for example `# EMGN-2.1`) in its name or a comment.

### Requirement 4: Deterministic verification (EMGN-4)

**User Story:** As KyJahn, I want verification to be deterministic, so that the same inputs always produce the same grade and the oracle result is reproducible.

#### Acceptance Criteria

1. EMGN-4.1 The verification harness MUST be deterministic: WHEN run repeatedly on the same inputs THEN it SHALL produce the same grade and the same pass/fail oracle result every time.
2. EMGN-4.2 The verification harness MUST NOT depend on network access, wall-clock time, locale defaults, random seeds, or any generative-AI call; all inputs SHALL be fixed fixtures.
3. EMGN-4.3 The verification harness MUST report, for each fixture, the produced answer, the expected answer, the normalization applied, and the resulting grade, so a human can inspect why a grade was reached.

### Requirement 5: Human diagnosis and patch stay human; no generative AI in TaskRecorder (EMGN-5)

**User Story:** As KyJahn, I want the substantive diagnosis and final fix to remain my human work with no generative-AI interaction during recording, so that authorship and the Project Odin contract are preserved.

#### Acceptance Criteria

1. EMGN-5.1 The AI handoff MUST stop before the human diagnosis, the final patch, the completed deliverable, and any hidden answer; it SHALL build only the synthetic starter environment (fixtures, setup, failing tests/oracles, deterministic verification, scaffolding).
2. EMGN-5.2 The recorded substantive diagnosis, implementation, professional decisions, tests, and final verification MUST remain KyJahn's human work.
3. EMGN-5.3 No generative-AI interaction is permitted during TaskRecorder; WHEN recording is active THEN the process MUST NOT make a generative-AI call.
4. EMGN-5.4 The scaffolding MUST NOT include or encode a candidate root cause or a candidate fix, so that it cannot leak the answer the human is expected to produce.

### Requirement 6: Spec and handoff hygiene (EMGN-6)

**User Story:** As KyJahn, I want this spec and its handoff to be deterministically discoverable and strictly spec-only, so that the automation can find it and nothing is implemented prematurely.

#### Acceptance Criteria

1. EMGN-6.1 This change MUST be spec-only: it SHALL create exactly `specs/exact-match-grader-normalization/requirements.md`, `design.md`, and `tasks.md`, and SHALL NOT add or edit any file outside that directory.
2. EMGN-6.2 The spec PR body MUST include both `ODIN_ROW_ID:3f08621e-0a7a-811a-a81d-c7a39ac80b91` and `Relates to #20`, so the automation can discover the spec PR deterministically.
3. EMGN-6.3 Every implementation task in `tasks.md` MUST name an assigned coder AND a different reviewer (reviewer name MUST NOT equal the coder name on that task).
4. EMGN-6.4 Tasks MUST trace to requirement IDs and MUST be dependency-ordered.
5. EMGN-6.5 This spec MUST be reconciled against the authoritative Notion goal (ODIN_ROW_ID `3f08621e-0a7a-811a-a81d-c7a39ac80b91`) before any implementation task begins; WHEN the Notion goal and this spec conflict THEN the Notion goal (the current human-authored source of truth) wins.

#### Known limit (EMGN)

This spec was authored without the authoritative goal: the issue's "Exact approved Goal", "Approval ID", and "Spec path" were empty, and the Notion row was not readable from the authoring environment. The requirements therefore cover only what is general-purpose and verifiable for an exact-match grader normalization false-positive repair; the exact grader, its normalization pipeline, the concrete reproducing inputs/outputs, and the acceptance oracle values remain UNKNOWN (EMGN-0) until KyJahn supplies them or names the repo that holds the grader. Nothing here asserts a verified root cause or a verified fix. Because the diagnosis and patch are reserved as KyJahn's human work with no generative-AI interaction during TaskRecorder, the AI handoff is bounded to the synthetic starter environment and intentionally stops short of solving the defect.
