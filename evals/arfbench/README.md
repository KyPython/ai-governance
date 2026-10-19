# ARFBench as an inspect_ai task — v2 (local exploration)

Wraps Datadog's **Anomaly Reasoning Framework Benchmark** in an inspect_ai task
so a real vendor benchmark runs through your own eval harness.

- Benchmark: 750 multiple-choice QA pairs from 63 real Datadog production
  incidents, testing time-series anomaly reasoning (8 task categories,
  3 difficulty tiers).
- Source: https://github.com/DataDog/ARFBench — **Apache 2.0** (verified).
- Dataset: https://huggingface.co/datasets/Datadog/ARFBench (public, no auth
  needed). Paper: arXiv 2604.21199.

## What's here

- `arfbench_eval.py` — the task. Loads `data/arfbench-qa.csv`, renders each
  question with lettered choices via inspect_ai's `multiple_choice` solver,
  scores with the built-in `choice()` scorer against the correct letter.
- `data/arfbench-qa.csv` — the 750 QA pairs (704KB, metadata only).
- `data/ts/` — lazily cached per-query-group parquet files (downloaded from
  Hugging Face on first use; 134 of 406 query_groups have ts-data).
- `logs/` — eval logs from validation runs.

Follows the `first-approval-eval` conventions: single task file, `Sample`
dataset, `@task` params, mockllm-first validation, inspect_ai 0.3.280.

## v2: compact time-series context

Each question's `query_group` maps to
`arfbench-ts-data/<query_group>_<seconds>.parquet` on Hugging Face
(resolutions 10/60/300/1800/3600/86400s — the same mapping Datadog's own
eval code uses). Correlation questions name **two** comma-separated groups;
both are summarized.

Instead of dumping raw series (one group can hold 2,283 variates), each
question gets a compact statistical summary (~200–550 tokens):

- per-variate mean / std / min / max and point count + time range
- the largest local deviation per variate (rolling z-score) with timestamp
- top 8 variates by deviation shown; common label prefixes stripped

Deviations are reported descriptively — the summary never asserts anomaly
labels; the model does the reasoning. Groups without ts-data (272 of 406)
fall back to v1 behavior (descriptions only + explicit note).

New task param: `-T series_context=true/false` (default **true**).
`-T series_context=false` restores the v1 descriptions-only prompts for
quick/cheap runs.

## How to run

From this directory (reuses the sibling eval's venv — no new install;
v2 needs pandas+pyarrow in the venv, already installed):

```bash
# smoke test: 5 samples with series context, mockllm
../first-approval-eval/.venv/bin/inspect eval arfbench_eval.py \
    --model mockllm/model -T limit=5 -T series_context=true --log-dir ./logs

# v1 behavior (no series context)
../first-approval-eval/.venv/bin/inspect eval arfbench_eval.py \
    --model mockllm/model -T limit=5 -T series_context=false --log-dir ./logs

# Tier 1 only (111 easiest questions), 20 samples
../first-approval-eval/.venv/bin/inspect eval arfbench_eval.py \
    --model mockllm/model -T tier=1 -T limit=20 --log-dir ./logs

# full 750 (needs a real model; see below)
../first-approval-eval/.venv/bin/inspect eval arfbench_eval.py \
    --model openai/gpt-4o --log-dir ./logs
```

## Token cost of the context

Measured 2026-10-18 on mockllm runs (input tokens ÷ 5 samples):

- v1 (`series_context=false`): ~170 input tokens/question (question + choices).
- v2 single-group (`series_context=true`): ~533 input tokens/question —
  **~360 extra tokens** for the context block (5 variates).
- v2 two-group (correlation questions, ~14 variates): estimated ~700–800
  extra tokens/question from rendered prompt sizes (not yet measured
  end-to-end).

Full-750 estimate at v2: roughly **400–550K input tokens** (417 single-group
× ~360 + 333 two-group × ~750, plus base prompt). A real but modest spend
on a frontier API model. Start with `-T tier=1 -T limit=20` to calibrate.

## What a REAL scored run needs

1. **A real model.** mockllm always scores 0 — it outputs canned text with no
   answer letter. Options:
   - API key for a frontier model: `--model openai/gpt-4o`,
     `--model anthropic/claude-...` (inspect_ai reads keys from env).
   - Local model via vLLM if you have the GPU for it.
2. **Expect cost.** 750 questions × prompts with series context on a frontier
   API model is a real (if modest) spend — see token estimates above.
   Start with `-T tier=1 -T limit=20`.

## What's stubbed or simplified in v2

- Summaries are descriptive statistics, not the raw series or the plots
  Datadog's own evals use. Scores are closer to comparable but still not
  identical to Datadog's published numbers (their GPT-5: 62.7% accuracy,
  51.9% F1) — they feed full series text/images; we feed compact stats.
- No image inputs: ARFBench has per-question plots; v2 is text-only.
- No shuffling: choice order is dataset order. The `choice()` scorer detects
  shuffled choices; add shuffling before any serious run.
- Single-tier filter only (`-T tier=N`); no category filter yet.
- Resolution fixed at 5-min bars (300s), falling back to 30-min/1-hour for
  very large groups. Datadog's harness picks per-question optimal intervals;
  ours picks a fixed sensible default.

## Verified

- Dataset schema: 750 rows; `correct_answer` matches an option on all 750;
  2-option (111) and 5-option (639) questions; tiers 1/2/3 = 111/306/333.
- query_group → parquet mapping: `arfbench-ts-data/<group>_<sec>.parquet`;
  134 of 406 CSV query_groups have ts-data; 333 questions name two groups.
- mockllm validation 2026-10-17 (v1): 5-sample, 20-sample, tier-filtered
  3-sample runs — `status: success`; scorer executes (accuracy 0.000 as
  expected — mockllm emits no answer letter).
- mockllm validation 2026-10-18 (v2): 5-sample `-T series_context=true` run —
  `status: success`; context blocks render in prompts (~235 tokens for a
  5-variate group, ~540 for a two-group question); multi-group and
  no-data fallback paths verified directly; `series_context=false`
  reproduces v1 prompts. Scorer executes on all samples.
- No commits, pushes, or publishes. Local files only.

## Hack-pass: reward-hacking check (2026-10-19)

Prompted by Terminal-Bench's verifier hardening: can a zero-reasoning agent
score above chance here? Five heuristic hackers run against all 750 rows,
scored exactly as the task scores them. Blended random chance: 639
five-option questions (20%) + 111 two-option questions (50%) = **24.4%**.

| Hacker heuristic | Score | vs chance |
|---|---|---|
| Always pick A | **61.7%** (463/750) | p < 0.0001 — was gameable |
| Always pick longest choice | 33.6% | p < 0.0001 |
| Pick max question-word overlap | 33.3% | p < 0.0001 |
| Always pick B / C / D / E, shortest choice | 4–17% | not above chance |

Root cause of the big one: the upstream CSV lists the correct answer first
61.7% of the time (verified in Datadog's raw file — their data, not this
wrap), and inspect_ai 0.3.280's `multiple_choice()` does not shuffle choices.
Datadog's own harness shuffles options, so their leaderboard is unaffected —
the vulnerability was in this wrap. Fixed with
`dataset.shuffle_choices(seed=42)` (fixed seed: reproducible runs); post-fix,
always-A scores 25.2% ≈ chance. Verified: all 750 targets remap correctly,
mockllm smoke run passes.

**Residual, by design:** even shuffled, longest-choice (33.6%) and
max-overlap (33.3%) heuristics beat chance — inherent distractor weakness in
the questions (correct answers skew longer and share more stem vocabulary).
Treat **~33% as the no-reasoning baseline** when reading scores from this
task, not 24.4%.

Lesson: a faithful format conversion silently dropped a defense the original
authors had. Hack-pass every eval before trusting a score — this one costs a
single script and no API calls.
