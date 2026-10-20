# Delegation-Judgment Eval — v1

**Question:** can an orchestrator agent correctly decide *when* to delegate
to subagents — so a human doesn't have to manage the fan-out by hand?

**Motivation:** [Vals AI's Vibe Code Bench study](https://www.vals.ai/blogs/multi-agent-vibe-code-bench)
compared single agents and teams on 50 full-stack web apps. Teams cost
1.8–5.1 times as much, and only one of four model/effort comparisons had a
statistically significant score gain. Those benchmark-specific cost results
do not establish a general token multiplier or outcomes for other work.
This eval tests delegation decisions against an explicit policy.

## Rule under test

> Delegate to subagents ONLY for genuinely independent parallel work.
> Otherwise work solo.

## Dataset

12 cases, balanced 6 DELEGATE / 6 SOLO (over-delegation is penalized —
unlike the approval eval, which is intentionally imbalanced).

**DELEGATE** (independent parallel strands): three independent bug fixes
in disjoint files · three unrelated API research summaries · unit tests
for three independent modules · three unrelated PR reviews · one metric
from three independent sources · three independent utility refactors.

**SOLO** (delegation would hurt or waste): single linear fix with exact
stack trace · one-fact config lookup · dependent chain (migration →
code → tests, order matters) · coherent single-voice essay · two edits
to the same file (parallel writes clobber) · explore-first bug with
unknown location.

Each case: `task`, `should_delegate`, `category`, `rationale`, `expected`.
The labels express this policy; they are not experimental proof that each
choice improves task quality, speed, or cost.

## Setup and run

From the repository root, using Python 3.10 or newer:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install 'inspect_ai==0.3.280' pytest
.venv/bin/python -m pytest evals/delegation-judgment/test_scorer.py
.venv/bin/inspect eval evals/delegation-judgment/delegation_eval.py --model mockllm/model
.venv/bin/inspect eval evals/delegation-judgment/delegation_eval.py --model mockllm/model -T agent=always_delegate
.venv/bin/inspect eval evals/delegation-judgment/delegation_eval.py --model mockllm/model -T agent=never_delegate
```

Mock runs need no API key. Inspect writes eval logs to `logs/` by default.

## Scorer

`delegation_scorer()` grades the decision, not the work product:

- **Mock solvers** must emit `DECISION: DELEGATE|SOLO`. An ordinary summary
  without that line is unparseable and scores INCORRECT.
- **Completed live runs** are graded from tool behavior: any
  `spawn_subagent` call means DELEGATE; none means SOLO. Declared decision
  lines cannot override the observed behavior.
- **Incomplete live runs** score INCORRECT. The solver records normal
  return with a final model response; cancelled, timed-out, truncated, and
  filtered runs cannot earn credit merely by avoiding a delegation call.
  Inspect's `TaskState.completed` alone is insufficient because Inspect
  also sets it before scoring interrupted samples.

The explanation distinguishes correct, over-delegation, under-delegation,
and incomplete/unparseable runs, and includes the case rationale.

## Mock controls (inspect_ai 0.3.280, mockllm)

| Solver | Expected accuracy | Meaning |
|---|---|---|
| `oracle` | 12/12 (1.000) | Replays each hand label |
| `always_delegate` | 6/12 (0.500) | Fails every SOLO case |
| `never_delegate` | 6/12 (0.500) | Fails every DELEGATE case |

`test_scorer.py` covers decision extraction, actual TaskState scoring,
behavior overriding declarations, interruption handling, dataset balance,
and over/under-delegation verdicts.

## Optional live decision run

With provider credentials configured and a supported model identifier:

```sh
.venv/bin/inspect eval evals/delegation-judgment/delegation_eval.py --model <provider/model> -T agent=live
```

The orchestrator calls a **simulated** `spawn_subagent` worker. That worker
returns a canned result and does not perform the requested coding or
research. No live-model performance results are reported. A live run can
measure routing decisions under this policy, but cannot establish actual
subagent quality, speedup, or total multi-agent cost. Wiring a real worker
harness and measuring those outcomes is future work.
