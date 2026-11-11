# Design: Completion Gate wiring (CGW)

Complements `requirements.md`. Status: proposed with the spec-only PR.

## Shape

```
specs/<slug>/completion-contract.json   (spec author writes; Ky merges; coders cannot touch)
            │
            ├── CI:    governance.yml "completion" step ── base-branch contract + pinned gate ──> evidence artifact + summary
            │                                               mode: off | advisory (default) | required
            │
            └── local: agent rule (AGENTS.governance.md + user-level files) ──> agent runs gate, quotes verdict
                        Kiro Stop hook ──> runs gate, shows verdict (CGW-5)
```

## Decisions

1. **Gate code moves into this repo** (`completion-gate/`) because CI and cloud agents cannot reach Drive
   (CGW-1). Git becomes canonical for code after merge; Drive keeps the decision history.
2. **Contracts live in spec folders.** The existing spec-path role rule already stops coders from editing them,
   so contract immutability (gate spec E-1, design §1.2) needs no new mechanism (CGW-2).
3. **CI reads the contract from the base branch and the gate from the pinned SHA.** A PR then cannot loosen its
   contract or swap the runner (CGW-3.2). The PR's code still runs, as it already does in the quality job.
4. **Advisory first.** The first rollout reports without blocking, so the step can be watched on real PRs
   before Ky makes it required (CGW-3.4, 3.7).
5. **One rule text everywhere**, in marked blocks so it can be removed. Kiro gets a hook. Other agents are
   rule-only locally and enforced in CI (CGW-4, CGW-5).

## CI step sketch (illustrative; the task PR owns the exact YAML)

- Resolve the spec slug the policy job already parses from the PR body.
- Run `git show <base>:specs/<slug>/completion-contract.json`; if it is absent, report "no completion contract".
- Check out `KyPython/ai-governance` at the caller-pinned SHA into `.ai-governance/` and run
  `python3 .ai-governance/completion-gate/completion_gate.py contract.json --evidence completion-evidence.json`
  in the PR workspace.
- Upload `completion-evidence.json`. Write the verdict, reasons and contract hash to `$GITHUB_STEP_SUMMARY`.
- Apply the mode: under `required`, a non-zero exit fails the verdict.

## Risks

- **A contract that is too strict** makes advisory mode noisy. Advisory mode exists to find that out before it
  blocks anything.
- **Contract commands are not sandboxed** in CI. They come only from merged specs, which only Ky merges.
- **Agents may ignore a rule-only instruction.** CI catches that for PR work. Local-only work by rule-only
  agents stays self-reported, and the README says so (CGW-6).
