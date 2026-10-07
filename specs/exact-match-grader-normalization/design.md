# Design: Exact-match grader normalization false-positive repair

Spec ID: EMGN

## Overview

This design describes how to repair a false positive in an exact-match grader without inventing the goal. An exact-match grader normalizes a produced answer and an expected answer and grades PASS when they are equal under that normalization. A false positive is a PASS where the two answers are in fact semantically distinct: a normalization step erased a difference that the grading contract treats as significant.

The authoritative goal lives in a Notion row (ODIN_ROW_ID `3f08621e-0a7a-811a-a81d-c7a39ac80b91`) that was not readable from the authoring environment, and no grader source exists in this repo (confirmed by search). The specific grader, its normalization pipeline, the reproducing inputs/outputs, and the acceptance oracle values are therefore UNKNOWN (requirements EMGN-0.1 through EMGN-0.4) and MUST be resolved from the Notion goal or from a repo KyJahn names before implementation. This design constrains only the general-purpose, verifiable surface and the shape of the synthetic starter environment.

Per the Project Odin contract, the Codex/Cursor handoff builds ONLY the synthetic starter environment: fixtures, setup, failing tests/oracles, deterministic verification, and scaffolding. It stops before the human diagnosis, the final patch, the completed deliverable, and any hidden answer (EMGN-5). The recorded substantive diagnosis, implementation, decisions, tests, and final verification remain KyJahn's human work, and no generative-AI interaction is permitted during TaskRecorder.

This is a spec-only PR: it creates the three markdown files under `specs/exact-match-grader-normalization/` and nothing else (EMGN-6.1). The files named in the testing-strategy table below are intended and are NOT created by this spec PR.

## Architecture / components

The repair is organized as a bounded synthetic starter environment plus a reserved human stage. The AI handoff builds the first group only.

- **Reproducing fixtures (`fixtures`).** Fixed data pairs — a produced answer and an expected answer — that KyJahn supplies or confirms, each currently grading PASS but which should grade FAIL. Each fixture references, by stable identifier, the exact grader and normalization step it exercises. No fixture is invented by the implementation. (EMGN-1.1, EMGN-1.3, EMGN-1.4, EMGN-3.1)
- **Grader adapter / setup (`setup`).** A thin, read-only adapter that invokes the grader under repair against a fixture and returns its grade, plus the environment setup needed to run it deterministically. The adapter does not modify the grader. The grader's identity and location come from EMGN-0.1 and are not assumed here. (EMGN-0.1, EMGN-4.2)
- **Failing oracle tests (`oracle`).** Tests that encode each false-positive fixture: the oracle asserts the correct grade (FAIL) while the unrepaired grader returns PASS, so the test fails and demonstrates the defect. Oracle values come from EMGN-0.4. The oracle also encodes the no-false-negative guard (a known-correct answer must still PASS) from EMGN-2.4. Each test cites its requirement ID(s). (EMGN-2.1, EMGN-2.4, EMGN-3.1, EMGN-3.2, EMGN-3.4)
- **Deterministic verification harness (`verify`).** Runs the adapter over the fixtures and compares against the oracle. It is deterministic (same inputs, same result), uses no network, clock, locale, random seed, or generative-AI call, and reports produced/expected answer, normalization applied, and resulting grade for each fixture. (EMGN-4.1, EMGN-4.2, EMGN-4.3)
- **Scaffolding and docs (`scaffold`).** Directory layout, a runner entrypoint, and documentation that explains how to add a KyJahn-confirmed fixture and run the harness. Scaffolding MUST NOT encode a candidate root cause or a candidate fix. (EMGN-5.1, EMGN-5.4)
- **Reserved human stage (NOT built by the handoff).** The substantive diagnosis of which normalization step collapses the distinction, the corrective patch, the completed deliverable, and the final verification. This stage is KyJahn's human work and is explicitly out of scope for the AI handoff and for TaskRecorder generative-AI calls. (EMGN-5.1, EMGN-5.2, EMGN-5.3)

## Data and interfaces

- **Fixture record.** `{ fixture_id, grader_ref, normalization_step_ref, produced_answer, expected_answer, expected_grade }`. `grader_ref` and `normalization_step_ref` resolve EMGN-0.1/EMGN-0.2; `expected_grade` is the oracle value from EMGN-0.4. All values are KyJahn-supplied or confirmed; none are invented. (EMGN-1.1, EMGN-1.4, EMGN-0.3, EMGN-0.4)
- **Grade value.** A grade is `PASS` or `FAIL` plus the normalization applied and the compared, normalized strings, so a human can inspect why a grade was reached. (EMGN-4.3)
- **Adapter interface.** `grade(produced, expected) -> Grade`, a pure, read-only call into the grader under repair. It performs no mutation of the grader and no network or generative-AI call. (EMGN-4.2)
- **Oracle assertion.** For a false-positive fixture, the oracle asserts the grade equals `expected_grade` (FAIL) and records that the unrepaired grader returns `PASS`; for the no-false-negative guard, it asserts a known-correct answer still returns `PASS`. (EMGN-2.1, EMGN-2.4, EMGN-3.2)
- **Determinism contract.** All inputs are fixed fixtures; no source of nondeterminism (network, clock, locale, random seed, generative AI) is permitted in the harness. (EMGN-4.1, EMGN-4.2)
- **Discovery markers.** The spec PR body carries `ODIN_ROW_ID:3f08621e-0a7a-811a-a81d-c7a39ac80b91` and `Relates to #20` so the automation can discover the spec PR deterministically. (EMGN-6.2)

## Error handling and failure modes

- **No KyJahn-confirmed reproducing fixture.** The handoff MUST NOT begin; the task stays blocked on EMGN-0.3 / EMGN-1.2. (EMGN-1.2)
- **Grader identity/location unknown.** EMGN-0.1 is unresolved: the adapter cannot target a grader, so implementation stays blocked rather than targeting an invented grader. (EMGN-0.1, EMGN-1.4)
- **Normalization rules unknown.** EMGN-0.2 is unresolved: the implementation MUST NOT infer which distinctions are significant; the agreed normalization must come from KyJahn. (EMGN-2.3, EMGN-1.3)
- **Oracle values unknown.** EMGN-0.4 is unresolved: the oracle cannot assert a precise grade, so the failing test cannot be authored correctly and the task stays blocked. (EMGN-0.4, EMGN-3.2)
- **Oracle passes against the unrepaired grader.** If the "failing" oracle does not fail, the fixture does not demonstrate a false positive; this is a fixture/oracle authoring error to fix before proceeding, not a reason to invent a defect. (EMGN-3.2)
- **Scaffolding leaks the answer.** If scaffolding would encode a candidate root cause or fix, that is a contract violation and MUST be removed; the diagnosis and patch are reserved for the human. (EMGN-5.4)
- **Spec/Notion conflict.** The Notion goal (current human-authored source of truth) wins; the spec is reconciled before implementation. (EMGN-6.5)

## Testing strategy (criterion ID -> test file)

The oracle and verification files below are part of the synthetic starter environment and are built later by the Codex/Cursor handoff, not by this spec PR. They are **intended** and are **NOT created by this spec PR**. Each test cites the requirement ID(s) it verifies in its name or a comment. The UNKNOWN items (EMGN-0.*) are not test rows because they are preconditions resolved from the Notion goal, not mechanically testable assertions.

| Criterion | Test (intended; not created by this spec PR) |
| --- | --- |
| EMGN-1.1 | `tests/test_emgn_fixtures.py` |
| EMGN-1.2 | `tests/test_emgn_fixtures.py` |
| EMGN-1.3 | `tests/test_emgn_fixtures.py` |
| EMGN-1.4 | `tests/test_emgn_fixtures.py` |
| EMGN-2.1 | `tests/test_emgn_oracle.py` |
| EMGN-2.2 | `tests/test_emgn_oracle.py` |
| EMGN-2.3 | `tests/test_emgn_oracle.py` |
| EMGN-2.4 | `tests/test_emgn_oracle.py` |
| EMGN-3.1 | `tests/test_emgn_oracle.py` |
| EMGN-3.2 | `tests/test_emgn_oracle.py` |
| EMGN-3.3 | `tests/test_emgn_scaffold.py` |
| EMGN-3.4 | `tests/test_emgn_oracle.py` |
| EMGN-4.1 | `tests/test_emgn_verify.py` |
| EMGN-4.2 | `tests/test_emgn_verify.py` |
| EMGN-4.3 | `tests/test_emgn_verify.py` |
| EMGN-5.1 | `tests/test_emgn_handoff_bounds.py` |
| EMGN-5.2 | `tests/test_emgn_handoff_bounds.py` |
| EMGN-5.3 | `tests/test_emgn_handoff_bounds.py` |
| EMGN-5.4 | `tests/test_emgn_handoff_bounds.py` |
| EMGN-6.1 | `tests/test_emgn_spec_hygiene.py` |
| EMGN-6.2 | `tests/test_emgn_spec_hygiene.py` |
| EMGN-6.3 | `tests/test_emgn_spec_hygiene.py` |
| EMGN-6.4 | `tests/test_emgn_spec_hygiene.py` |
| EMGN-6.5 | `tests/test_emgn_spec_hygiene.py` |
