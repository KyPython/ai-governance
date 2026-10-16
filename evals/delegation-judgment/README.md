# Delegation-Judgment Eval — v1

**Question:** can an orchestrator agent correctly decide *when* to delegate
to subagents — so a human doesn't have to manage the fan-out by hand?

**Motivation:** Vals AI (Oct 2026) found multi-agent teams burn 1.8–5.1x
the tokens of a single agent for ~zero quality gain on most coding tasks.
The waste isn't AI coding — it's *unjudged delegation*. Current
orchestrators (Claude Code, Cursor, Kiro-class) decide mostly by vibes:
the model matches the task against subagent `description` fields, and
without explicit routing rules it "guesses — and often guesses wrong."
This eval turns delegation judgment into a measurable skill.

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

## Scorer

`delegation_scorer()` grades the *decision*, not the work product:

1. **Behavioral signal first:** any `spawn_subagent` tool call in the
   transcript counts as DELEGATE (what it did beats what it said).
2. **Declared signal:** `DECISION: DELEGATE|SOLO` line (mock solvers).
3. No signal → INCORRECT (unparseable).
4. Correct / over-delegation / under-delegation verdicts with the case
   rationale in the explanation.

## Verified results (inspect_ai 0.3.280, mockllm, no API key)

| Solver | Accuracy | Meaning |
|---|---|---|
| `oracle` | 12/12 (1.000) | Scorer reaches the ceiling; agreement 12/12 |
| `always_delegate` | 6/12 (0.500) | Fails every SOLO case — over-delegation penalized |
| `never_delegate` | 6/12 (0.500) | Fails every DELEGATE case — under-delegation penalized |

Unit tests: `test_scorer.py` — 14/14 pass (decision extraction,
tool-call precedence, over/under-delegation verdicts, dataset balance).

## The improvement loop (why this eval exists)

1. Run `-T agent=live` with a real model; read *where* it over/under-delegates.
2. Tighten the delegation policy: the `spawn_subagent` tool description,
   the orchestrator prompt, cost thresholds (the "delegation ladder").
3. Re-run. Delegation reasoning improves by measurement, not by hoping
   the system prompt is wise enough.

## Friday live-run plan (Oct 16, 2:30–3:30 PM ET slot)

The slot is already reserved for the sandboxed real-agent
dispatch-boundary test (approval *enforcement*). The delegation eval's
live solver (`-T agent=live`) is stubbed and ready: a `react()`
orchestrator with a real `spawn_subagent` tool. It needs a real model:

```
inspect eval delegation_eval.py --model <model> -T agent=live
```

v1's `spawn_subagent` worker is simulated (the *decision* is what's
scored); wiring it to a real subagent harness is the defined next step
after the approval-boundary test lands. Token usage per decision is
recorded in the eval log for the cost side of delegation ROI.
