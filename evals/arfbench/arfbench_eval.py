"""
ARFBench wrapped as an inspect_ai task — v2 (local exploration).

Datadog's Anomaly Reasoning Framework Benchmark: 750 multiple-choice QA pairs
drawn from 63 real production incidents, testing time-series anomaly reasoning.
  Source: https://github.com/DataDog/ARFBench (Apache 2.0)
  Dataset: https://huggingface.co/datasets/Datadog/ARFBench (public, not gated)
  Paper: arXiv 2604.21199 (Stephan Xie et al.)

v2 adds compact time-series context per question (v1 attached nothing):
- Each question's `query_group` maps to parquet files at
  arfbench-ts-data/<query_group>_<seconds>.parquet on Hugging Face
  (resolutions: 10/60/300/1800/3600/86400s; same mapping Datadog's own
  eval code uses via get_time_series_paths()).
- Parquet files are fetched lazily per query_group and cached under
  data/ts/. Only 134 of the 406 query_groups in the CSV have ts-data;
  the rest fall back to v1 behavior (descriptions only).
- The summary is STATISTICAL, not raw data: per-variate mean/std/min/max
  plus the largest local deviation (rolling z-score) with its timestamp.
  No anomaly labels are asserted — the model does the reasoning.
  Raw dumps are never put in prompts (a single group can hold 2,283
  variates x thousands of points).

Task params:
  limit          - max samples to run (e.g. -T limit=10 for a quick smoke run)
  tier           - filter to one difficulty tier: 1, 2, or 3 (e.g. -T tier=1)
  series_context - attach the compact time-series summary (true/false,
                   default true). -T series_context=false restores v1
                   behavior for quick/cheap runs.

Run (from this directory, reuses the sibling eval's venv):
  ../first-approval-eval/.venv/bin/inspect eval arfbench_eval.py \
      --model mockllm/model -T limit=5 -T series_context=true --log-dir ./logs

inspect_ai 0.3.280. pandas+pyarrow required in the venv when
series_context=true (already installed in first-approval-eval/.venv).
No API key needed for mockllm validation.
"""

import csv
import json
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
TS_MAX_ROWS = 50_000
TS_MAX_VARIATES = 8
HF_TS_URL = (
    "https://huggingface.co/datasets/Datadog/ARFBench/resolve/main/"
    "arfbench-ts-data/{group}_{res}.parquet"
)

V1_NOTE = (
    "\n\n[Note: this harness does not attach the raw time-series data. "
    "Answer from the question text and series descriptions above.]"
)


def _load_rows() -> list[dict]:
    import gzip

    with gzip.open(DATA, "rt", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _letter(idx: int) -> str:
    return chr(ord("A") + idx)


def _fetch_ts(query_group: str) -> tuple[Path | None, str | None]:
    """Lazily download one query_group's parquet (cached). Returns
    (path, resolution) or (None, None) when no usable file exists."""
    TS_CACHE.mkdir(parents=True, exist_ok=True)
    for res in TS_RESOLUTIONS:
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
            except Exception:
                if dest.exists():
                    dest.unlink(missing_ok=True)
                continue
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
    return None, None


def _summarize_one(query_group: str) -> tuple[str | None, str | None]:
    """Compact textual summary of a single query_group's series.

    Returns (summary_text, resolution) or (None, None) when the series
    is unavailable. Never raises for missing data — callers fall back
    to the v1 note.
    """
    import pandas as pd
    import numpy as np

    path, res = _fetch_ts(query_group)
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
    res_label = {"300": "5-min", "1800": "30-min", "3600": "1-hour"}[res]

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
                peak_t = s["epoch"].loc[pi].strftime("%H:%M")
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


def _summarize_ts(query_group: str) -> tuple[str | None, str | None]:
    """Summarize one or more comma-separated query_groups (correlation
    questions name two). Returns (combined_text, resolutions) or
    (None, None) when no group has usable data."""
    parts = [g.strip() for g in query_group.split(",") if g.strip()]
    blocks, resolutions = [], []
    for part in parts:
        text, res = _summarize_one(part)
        if text:
            blocks.append(text)
            resolutions.append(res)
    if not blocks:
        return None, None
    return "\n".join(blocks), ",".join(resolutions)


def _to_sample(row: dict, series_context: bool) -> Sample:
    options = [o["value"] for o in json.loads(row["options"])]
    try:
        correct_idx = options.index(row["correct_answer"])
    except ValueError:
        raise ValueError(
            f"correct_answer not in options for row {row['Unnamed: 0']}"
        )
    context_text = ""
    ts_resolution = None
    if series_context:
        summary, ts_resolution = _summarize_ts(row["query_group"])
        if summary:
            context_text = "\n\n" + summary
    note = V1_NOTE if not context_text else ""
    return Sample(
        input=row["question"].strip() + context_text + note,
        choices=options,
        target=_letter(correct_idx),
        id=f"arfbench-{row['Unnamed: 0']}",
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
        series_context = series_context.strip().lower() in ("true", "1", "yes")
    if series_context:
        try:
            import pandas  # noqa: F401
        except ImportError:
            raise RuntimeError(
                "series_context=true needs pandas+pyarrow in the venv "
                "(pip install pandas pyarrow), or run with "
                "-T series_context=false"
            )
    rows = _load_rows()
    if tier is not None:
        want = f"Tier {tier}"
        rows = [r for r in rows if r["difficulty"] == want]
        if not rows:
            raise ValueError(f"No rows at difficulty {want!r}")
    if limit is not None:
        rows = rows[: int(limit)]
    dataset = [_to_sample(r, series_context) for r in rows]
    return Task(
        dataset=dataset,
        solver=multiple_choice(),
        scorer=choice(),
    )
