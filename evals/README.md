# Agent-reliability evals

Small, focused eval suites built with [inspect_ai](https://github.com/UKGovernmentBEIS/inspect_ai) (0.3.280, no API key required) to test whether an AI agent respects a single hard rule: **never send a message without approval**.

## Suites

- **approval-gate/** — Canon. 28 cases (8 compliant / 20 violating). Structured `validate_send()` scorer recomputes every evidence field. Replay: scorer agreement 28/28; `always_send` negative control: 4/28 (the scorer is sensitive, not pass-through). Unit tests 23/23.
- **dispatch-regression-20case/** — 20-case regression suite scoring observed dispatches (recorded side effects), preserved as-received with checksums verified. Native run 20/20, accuracy 1.0, 0 unauthorized ALLOWs.
- **delegation-judgment/** — 12 balanced cases (6 DELEGATE / 6 SOLVE) grading the *delegation decision* itself. Oracle 12/12; always/never-delegate controls 6/12 (both over- and under-delegation penalized). Unit tests 14/14.
- **real-life-audit/** — A 10-rule reliability audit of a real agent system over one week, run against its own operator (dogfooding).

## Method

Each suite ships with a negative control (a deliberately bad policy) to prove the scorer actually discriminates, plus unit tests for the scorer. Logs of native runs are included under each suite's `logs/`.

Built October 2026. Spec-first, bounded, reproducible.

Note: raw `.eval` run-log archives (binary zip format) are excluded from this repo — they are reproducible via each suite's run scripts and available on request.
