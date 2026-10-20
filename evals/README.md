# Agent-reliability evaluations

Bounded reliability fixtures built with [Inspect AI](https://inspect.aisi.org.uk/)
0.3.280. The approval suites exercise sending only within an approved scope;
the delegation suite grades whether to delegate or work solo.

## Reproduce the tests

From the repository root, using Python 3.12:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q
```

The root test entry point runs each suite in its own process, including the
archived v2 scorer test. The existing governance quality job discovers the root
requirements and tests without changes to its workflow.

## Suites and evidence scope

- [approval-gate](approval-gate/README.md): 28 scripted cases; replay checks scorer
  agreement against hand labels. An always-send control deliberately violates
  approval requirements. Scorer agreement is distinct from compliance and from
  live-model performance.
- [dispatch-regression-20case](dispatch-regression-20case/README.md): 20 cases
  exercising a reference approval gate and inert recording transport. The oracle
  checks recorded dispatches; this is not a deployed authorization service.
- [delegation-judgment](delegation-judgment/README.md): 12 balanced decision cases,
  an oracle and always/never-delegate controls. The worker is simulated; these
  controls do not establish multi-agent quality, speed or cost savings.
- [real-life-audit](real-life-audit/baseline-2026-10-14.md): a redacted historical,
  author-reported summary, not an executable suite or independently validated
  compliance result.

## Included artifacts

Source, regression tests, documentation and the dispatch suite's JSON receipts
are included. Raw binary `.eval` logs and local environments are excluded;
reproduce them using each suite's instructions. Historical reports are labeled
separately from current verification. No live-model benchmark is claimed by the
scripted replay, oracle or reference-gate results.
