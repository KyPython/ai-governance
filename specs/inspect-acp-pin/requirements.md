# Requirements: Stop agent-client-protocol 1.0.0 from breaking the eval tests

Spec ID: ACP · Issue: none (goal selected by Ky in chat on 2026-11-10; found on #264) · Status: proposed; Ky approves by merging this spec-only PR

Provenance: drafted by Kiro on 2026-11-10 from Ky's chat choice "2a". Ky owns the sentences; coders must not paraphrase them to fit the code.

## Introduction

Root `requirements.txt` pins `inspect-ai==0.3.287`, whose metadata requires
`agent-client-protocol>=0.12.0` with no upper bound. `agent-client-protocol` 1.0.0 was published
on 2026-11-09, and CI now installs it. With it, two tests in
`evals/delegation-judgment/test_scorer.py`
(`test_live_solver_runs_in_inspect_with_scripted_model[False]` and `[True]`) fail with
`ModuleNotFoundError: No module named 'acp.helpers'`, which fails `ai-governance / quality` and
`system-quality` on every pull request in this repository (seen on #263 and #264).

Out of scope: `evals/dispatch-regression-20case/requirements.txt` (`inspect-ai>=0.3.0`, not used
by CI), the role-map 404 (spec `gate-private-role-map`), and
`tests/test_policy.py::SpecGate::test_GATE_1_2_kiro_spec_dir_on_base_passes`, which fails locally
on clean `main` `8da4ed4` but not in CI's quality job; its cause is unknown.

## Requirements

### Requirement 1: Reproducible dependency set (ACP-1)

**User Story:** As Ky, I want CI to install a dependency set the eval tests pass with, so that a
third-party release does not fail every pull request overnight.

#### Acceptance Criteria

1. ACP-1.1 WHEN CI runs `python3 -m pip install -r requirements.txt` on a fresh runner THEN the installed `inspect-ai` and `agent-client-protocol` versions SHALL be ones listed in `requirements.txt` with `==`.
2. ACP-1.2 WHEN the tests run against that install THEN `python3 -m pytest -q` in `evals/delegation-judgment` SHALL report 33 passed and 0 failed.
3. ACP-1.3 WHEN the change lands THEN `ai-governance / quality` and `system-quality` SHALL no longer fail on `ModuleNotFoundError: No module named 'acp.helpers'`.
4. ACP-1.4 The change SHALL NOT edit, skip, or delete any test to make it pass.

### Requirement 2: Change size (ACP-2)

**User Story:** As a reviewer, I want the smallest change that restores a tested set, so that the
fix carries no unrelated upgrade risk.

#### Acceptance Criteria

1. ACP-2.1 The change SHALL modify only `requirements.txt`.
2. ACP-2.2 WHEN the change lands THEN the full suite `python3 -m pytest -q` at the repository root SHALL have no failure that does not also occur on `8da4ed4` with `agent-client-protocol==0.12.1` installed.
