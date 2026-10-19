"""
ARFBench wrapped as an inspect_ai task — v2 (local exploration).

Datadog's Anomaly Reasoning Framework Benchmark: 750 multiple-choice QA pairs
drawn from 63 real production incidents, testing time-series anomaly reasoning.
  Source: https://github.com/DataDog/ARFBench (Apache 2.0 — see LICENSE)
  Dataset: https://huggingface.co/datasets/Datadog/ARFBench (public, not gated;
    time-series downloads pinned to revision HF_REVISION below)
  Paper: arXiv 2604.21199 (Stephan Xie et al.)

v2 adds compact time-series context per question (v1 attached nothing):
- Each question's `query_group` maps to parquet files at
  arfbench-ts-data/<query_group>_<seconds>.parquet on Hugging Face
  (resolutions: 10/60/300/1800/3600/86400s; same mapping Datadog's own
  eval code uses via get_time_series_paths()).
- Parquet files are fetched lazily per query_group and cached under
  data/ts/ (git-ignored). Only 134 of the 406 query_groups in the CSV have
  ts-data; the rest fall back to v1 behavior (descriptions only). Groups
  with no data at any resolution are memoized for the run.
- The summary is STATISTICAL, not raw data: per-variate mean/std/min/max
  plus the largest local deviation (rolling z-score) with its timestamp.
  No anomaly labels are asserted — the model does the reasoning.
  Raw dumps are never put in prompts (a single group can hold 2,283
  variates x thousands of points).
- Questions naming second-precision timestamps use 10/60s data and keep
  second precision; coarser questions keep 5-min+ bars and HH:MM.
- Every prompt carries Datadog's task instructions (anomaly definitions),
  distilled from the upstream benchmark prompt — omitting them changes what
  the categorization/magnitude questions measure.
- Download failures: HTTP 404 falls back silently; transient/infra errors
  raise instead of producing a silently invalid score.

Anti-reward-hacking (hack-pass 2026-10-19): the upstream CSV lists the
correct answer first 61.7% of the time and multiple_choice() does not
shuffle, so choices are shuffled per sample with a seed derived from the
sample id (stable across tier slices and runs). Residual no-reasoning
baseline ~33% (longest-choice / question-overlap heuristics) — inherent
distractor weakness, not the harness.

Task params:
  limit          - max samples to run (e.g. -T limit=10 for a quick smoke run)
  tier           - filter to one difficulty tier: 1, 2, or 3 (e.g. -T tier=1)
  series_context - attach the compact time-series summary (true/false,
                   default true). -T series_context=false restores v1
                   behavior for quick/cheap runs.

Run (from the repo root, after pip install -r requirements.txt):
  inspect eval evals/arfbench/arfbench_eval.py \
      --model mockllm/model -T limit=5 -T series_context=true \
      --log-dir evals/arfbench/logs

inspect_ai 0.3.280. pandas+pyarrow required when series_context=true
(declared in requirements.txt). No API key needed for mockllm validation.
Regression tests: evals/arfbench/test_arfbench.py (no network needed).
"""

import csv
import hashlib
import json
import random
import re
import urllib.error
import urllib.request
from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import choice
from inspect_ai.solver import multiple_choice

DATA = Path(__file__).parent / "data" / "arfbench-qa.csv.gz"
TS_CACHE = Path(__file__).parent / "data" / "ts"

# Fine -> coarse; first resolution with <= TS_MAX_ROWS wins.
TS_RESOLUTIONS = ["300", "1800", "3600"]
# Used when the question needs second-level precision (timestamp choices like
# 18:19:10 vs 18:19:43 collapse into one 5-min bar otherwise).
TS_RESOLUTIONS_FINE = ["10", "60", "300", "1800", "3600"]
TS_MAX_ROWS = 50_000
TS_MAX_VARIATES = 8
# Pinned dataset revision (Codex review 2026-10-18): resolving from the mutable
# `main` ref made scores depend on cache state and run date — upstream has
# already replaced uploads (see Datadog/ARFBench@1cc8ae5). Pinned 2026-10-19;
# main pointed at this revision on that date, so existing caches stay valid.
HF_REVISION = "1cc8ae54e9633f596b755f7c4bce54ccb0cb9f5a"
HF_TS_URL = (
    "https://huggingface.co/datasets/Datadog/ARFBench/resolve/"
    + HF_REVISION
    + "/arfbench-ts-data/{group}_{res}.parquet"
)

# Groups with no ts-data at any resolution, memoized for the task lifetime
# (Codex review 2026-10-18: without this, heavily repeated groups retried all
# resolutions on every sample — thousands of redundant requests per run).
_TS_UNAVAILABLE: set[str] = set()

# Second-precision timestamps in a question or its choices.
_TS_SEC_RE = re.compile(r"\d{1,2}:\d{2}:\d{2}")

V1_NOTE = (
    "\n\n[Note: this harness does not attach the raw time-series data. "
    "Answer from the question text and series descriptions above.]"
)

# Task instructions, distilled from Datadog's upstream ARFBench benchmark
# prompt (Apache 2.0; utils/prompt_test_benchmark.py). Upstream supplies these
# definitions on every evaluation; omitting them changes what the
# categorization and magnitude questions measure (Codex review 2026-10-18).
# Adapted to this text-only harness (no plot images).
TASK_INSTRUCTIONS = """\
[Task instructions — adapted from Datadog's ARFBench benchmark prompt]
You are an expert at analyzing time-series data and answering questions about anomalies.
An anomaly is present if the time-series has a value significantly different from its counterfactual (non-anomalous) values.
First consider whether an anomaly exists at all — this is the most important step. If none exists, answer "No Anomaly".

Anomaly categories (for categorization questions):
- Level Shift: sustained change in mean value.
- Transient Spike: one or more sudden spikes; the value returns to normal quickly with no intervention.
- Change in Seasonality: change in the seasonal pattern of the data.
- Change in Variance: major sustained change in variance.
- Change in Trend: major change in the long-term increase or decrease.
- No Anomaly.

Anomaly magnitude: the maximum ratio of anomaly values to counterfactual non-anomalous values (if the counterfactual is 0, use the absolute deviation from the mean counterfactual).
Anomaly correlation (paired questions): anomalies are correlated if they have a known causal relation, similar trends over time, or the same underlying root cause.
Leading/lagging indicator (paired questions): use the timing of the anomalies to decide which came first.

If no answer choice matches your result exactly, choose the closest one. Only answer when your reasoning supports it — do not guess.
"""


def _load_rows() -> list[dict]:
    import gzip
    import base64
    import io

    raw = DATA.read_bytes()
    if raw[:2] != b"\x1f\x8b":
        # The committed artifact is base64 text (the push path can't carry
        # binary); decode it before gunzipping. A real gzip file on disk
        # takes the fast path. (Codex review 2026-10-18: committed blob was
        # base64, which made every invocation raise BadGzipFile.)
        raw = base64.b64decode(raw)
    with gzip.open(io.BytesIO(raw), "rt", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _letter(idx: int) -> str:
    return chr(ord("A") + idx)


def _fetch_ts(
    query_group: str, resolutions: list[str]
) -> tuple[Path | None, str | None]:
    """Lazily download one query_group's parquet (cached). Returns
    (path, resolution) or (None, None) when no usable file exists.

    Only an expected not-found (HTTP 404) falls back silently. Transient or
    infrastructure failures (timeouts, DNS/TLS errors, 5xx) raise: silently
    continuing with description-only prompts would produce a complete but
    invalid benchmark score (Codex review 2026-10-18)."""
    if query_group in _TS_UNAVAILABLE:
        return None, None
    TS_CACHE.mkdir(parents=True, exist_ok=True)
    for res in resolutions:
        dest = TS_CACHE / f"{query_group}_{res}.parquet"
        if not dest.exists():
            url = HF_TS_URL.format(group=query_group, res=res)
            req = urllib.request.Request(
                url, headers={"User-Agent": "muse-agent"}
            )
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    if r.status != 200:
                        continue
                    dest.write_bytes(r.read())
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    continue  # expected: no data at this resolution
                raise RuntimeError(
                    f"time-series download failed for {query_group} "
                    f"at {res}s resolution: HTTP {e.code}"
                ) from e
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                raise RuntimeError(
                    f"time-series download failed for {query_group} "
                    f"at {res}s resolution: {e}"
                ) from e
        # Row-count check without loading everything: read just epoch col.
        try:
            import pandas as pd

            n = pd.read_parquet(dest, columns=["epoch"]).shape[0]
        except Exception:
            dest.unlink(missing_ok=True)
            continue
        if n <= TS_MAX_ROWS:
            return dest, res
        # Too big at this resolution: drop it and try coarser.
        dest.unlink(missing_ok=True)
    _TS_UNAVAILABLE.add(query_group)
    return None, None


def _summarize_one(
    query_group: str, fine: bool
) -> tuple[str | None, str | None]:
    """Compact textual summary of a single query_group's series.

    Returns (summary_text, resolution) or (None, None) when the series
    is unavailable. Never raises for missing data — callers fall back
    to the v1 note.
    """
    import pandas as pd
    import numpy as np

    resolutions = TS_RESOLUTIONS_FINE if fine else TS_RESOLUTIONS
    path, res = _fetch_ts(query_group, resolutions)
    if path is None:
        return None, None
    try:
        df = pd.read_parquet(path, columns=["epoch", "group", "value"])
    except Exception:
        return None, None
    if df.empty:
        return None, None

    df = df.sort_values("epoch")
    t0 = df["epoch"].min().strftime("%Y-%m-%d %H:%M")
    t1 = df["epoch"].max().strftime("%Y-%m-%d %H:%M")
    res_label = {
        "10": "10-sec",
        "60": "1-min",
        "300": "5-min",
        "1800": "30-min",
        "3600": "1-hour",
    }[res]
    # Second-precision questions need second-precision timestamps; coarser
    # questions keep HH:MM to save tokens (Codex review 2026-10-18).
    ts_fmt = "%H:%M:%S" if fine else "%H:%M"

    # Strip a common label prefix to save tokens (e.g. "datacenter:1,").
    labels = [str(g) for g in df["group"].unique()]
    prefix = labels[0]
    for lab in labels[1:]:
        while not lab.startswith(prefix) and prefix:
            prefix = prefix[:-1]
    # Only strip up to the last comma so fragments stay readable.
    if "," in prefix:
        prefix = prefix[: prefix.rfind(",") + 1]
    else:
        prefix = ""

    def short(lab: str) -> str:
        return lab[len(prefix):] if prefix and lab.startswith(prefix) else lab

    stats = []
    for lab, s in df.groupby("group"):
        s = s.reset_index(drop=True)
        v = s["value"].astype(float)
        n = len(v)
        mu, sd = float(v.mean()), float(v.std())
        # Largest local deviation: rolling z-score.
        w = max(6, min(48, n // 10))
        if sd == 0 or n < w:
            peak_z, peak_t = 0.0, None
        else:
            rm = v.rolling(w, center=True, min_periods=max(1, w // 2)).mean()
            rsd = v.rolling(w, center=True, min_periods=max(1, w // 2)).std()
            z = (v - rm) / rsd.replace(0, np.nan)
            za = z.abs().dropna()
            if za.empty:
                peak_z, peak_t = 0.0, None
            else:
                pi = za.idxmax()
                peak_z = float(za.loc[pi])
                peak_t = s["epoch"].loc[pi].strftime(ts_fmt)
        stats.append(
            {
                "label": short(str(lab)),
                "n": n,
                "mean": mu,
                "std": sd,
                "min": float(v.min()),
                "max": float(v.max()),
                "peak_z": peak_z,
                "peak_t": peak_t,
            }
        )
    stats.sort(key=lambda d: -d["peak_z"])
    shown = stats[:TS_MAX_VARIATES]
    hidden = len(stats) - len(shown)

    lines = [
        f"[Time-series context — query_group {query_group}, {res_label} bars, "
        f"{len(stats)} variates x ~{shown[0]['n'] if shown else 0} points, "
        f"{t0} → {t1}]"
    ]
    for st in shown:
        if st["std"] == 0:
            dev = "flat series"
        elif st["peak_t"]:
            dev = f"largest local deviation |z|={st['peak_z']:.1f} @ {st['peak_t']}"
        else:
            dev = "no local deviation computed"
        lines.append(
            f"- {st['label']}: mean {st['mean']:.1f}, std {st['std']:.1f}, "
            f"range {st['min']:.1f}–{st['max']:.1f} | {dev}"
        )
    if hidden:
        lines.append(
            f"(+{hidden} more variates; top {TS_MAX_VARIATES} by local "
            "deviation shown)"
        )
    lines.append(
        "[Deviations are descriptive only, not anomaly labels — "
        "reason from the data.]"
    )
    return "\n".join(lines), res


def _summarize_ts(
    query_group: str, fine: bool
) -> tuple[str | None, str | None]:
    """Summarize one or more comma-separated query_groups (correlation
    questions name two). Returns (combined_text, resolutions) or
    (None, None) when no group has usable data."""
    parts = [g.strip() for g in query_group.split(",") if g.strip()]
    blocks, resolutions = [], []
    for part in parts:
        text, res = _summarize_one(part, fine)
        if text:
            blocks.append(text)
            resolutions.append(res)
    if not blocks or len(blocks) != len(parts):
        # Paired (correlation / leading-indicator) questions name two series:
        # emitting context for only one side would look complete but be
        # invalid, so paired context is all-or-none. Fall back to the
        # descriptions-only note instead (Codex review 2026-10-19).
        return None, None
    return "\n".join(blocks), ",".join(resolutions)


def _needs_fine_resolution(question: str, options: list[str]) -> bool:
    """True when the question or choices name second-precision timestamps
    (e.g. 18:19:10 vs 18:19:43): those collapse into one bar at 5-min
    resolution, so the sample needs 10/60s data to be answerable."""
    return bool(
        _TS_SEC_RE.search(question)
        or any(_TS_SEC_RE.search(o) for o in options)
    )


def _to_sample(row: dict, series_context: bool) -> Sample:
    options = [o["value"] for o in json.loads(row["options"])]
    try:
        correct_idx = options.index(row["correct_answer"])
    except ValueError:
        raise ValueError(
            f"correct_answer not in options for row {row['Unnamed: 0']}"
        )
    # Hack-pass 2026-10-19: the upstream CSV lists the correct answer first
    # 61.7% of the time, and multiple_choice() does not shuffle — so an
    # "always pick A" agent scored 61.7% with zero reasoning. Shuffle here,
    # per sample, with a seed derived from the sample id: the permutation is
    # then identical whether the question runs alone, in a tier slice, or in
    # the full 750 (a single shared RNG would shift permutations whenever the
    # sample set changes — Codex review 2026-10-19). Datadog's own harness
    # shuffles too, so this matches upstream behavior.
    sample_id = f"arfbench-{row['Unnamed: 0']}"
    seed = int(hashlib.sha256(sample_id.encode()).hexdigest(), 16) % (2**31)
    rng = random.Random(seed)
    perm = list(range(len(options)))
    rng.shuffle(perm)
    options = [options[i] for i in perm]
    correct_idx = perm.index(correct_idx)
    context_text = ""
    ts_resolution = None
    if series_context:
        fine = _needs_fine_resolution(row["question"], options)
        summary, ts_resolution = _summarize_ts(row["query_group"], fine)
        if summary:
            context_text = "\n\n" + summary
    note = V1_NOTE if not context_text else ""
    return Sample(
        input=TASK_INSTRUCTIONS + "\n" + row["question"].strip() + context_text + note,
        choices=options,
        target=_letter(correct_idx),
        id=sample_id,
        metadata={
            "task_category": row["task_category"],
            "difficulty": row["difficulty"],
            "query_group": row["query_group"],
            "correct_answer": row["correct_answer"],
            "series_context": bool(context_text),
            "ts_resolution": ts_resolution,
        },
    )


@task
def arfbench(
    limit: int | None = None,
    tier: int | None = None,
    series_context: bool | str = True,
):
    if isinstance(series_context, str):
        v = series_context.strip().lower()
        if v in ("true", "1", "yes"):
            series_context = True
        elif v in ("false", "0", "no"):
            series_context = False
        else:
            raise ValueError(
                f"series_context={series_context!r} not recognized "
                "(use true/false)"
            )
    if series_context:
        try:
            import pandas  # noqa: F401
            import pyarrow  # noqa: F401
        except ImportError:
            raise RuntimeError(
                "series_context=true needs pandas+pyarrow "
                "(see requirements.txt), or run with "
                "-T series_context=false"
            )
    rows = _load_rows()
    if tier is not None:
        want = f"Tier {tier}"
        rows = [r for r in rows if r["difficulty"] == want]
        if not rows:
            raise ValueError(f"No rows at difficulty {want!r}")
    if limit is not None:
        limit = int(limit)
        if limit <= 0:
            raise ValueError(f"limit must be a positive integer, got {limit}")
        rows = rows[:limit]
    dataset = [_to_sample(r, series_context) for r in rows]
    # Residual note (hack-pass 2026-10-19): even shuffled, no-reasoning
    # heuristics (longest choice, max question-overlap) still beat chance
    # ~33% vs ~24% — inherent distractor weakness in the questions, not the
    # harness. Treat ~33% as the no-reasoning baseline when reading scores.
    return Task(
        dataset=dataset,
        solver=multiple_choice(),
        scorer=choice(),
    )
