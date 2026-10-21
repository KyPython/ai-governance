"""Regression tests for the ARFBench inspect_ai task.

Guards the packaging and anti-reward-hacking invariants:
- the committed data artifact loads (a base64-instead-of-gzip blob once
  broke every invocation),
- the task constructs in both context modes,
- choice shuffling kills the position hack and is stable across filters,
- invalid task params fail loudly.

No network access: time-series downloads are stubbed out.
"""

from collections import Counter

import pytest

import arfbench_eval as task_mod


def test_data_file_loads_750_rows():
    rows = task_mod._load_rows()
    assert len(rows) == 750


def test_task_constructs_without_context():
    task = task_mod.arfbench(series_context=False)
    assert len(task.dataset) == 750
    for s in task.dataset:
        assert s.target in "ABCDE"
        assert 2 <= len(s.choices) <= 5
        assert task_mod.TASK_INSTRUCTIONS.strip()[:20] in s.input


def test_task_constructs_with_context_when_no_ts_data(monkeypatch):
    monkeypatch.setattr(task_mod, "_fetch_ts_at", lambda group, res: None)
    task = task_mod.arfbench(series_context=True)
    assert len(task.dataset) == 750
    # No ts-data anywhere -> every prompt carries the v1 note.
    assert all(task_mod.V1_NOTE.strip()[:20] in s.input for s in task.dataset)


def test_shuffle_is_stable_across_filters():
    full = {
        s.id: s.choices for s in task_mod.arfbench(series_context=False).dataset
    }
    tier2 = {
        s.id: s.choices
        for s in task_mod.arfbench(tier=2, series_context=False).dataset
    }
    assert tier2
    for sid, choices in tier2.items():
        assert full[sid] == choices


def test_position_hack_is_dead():
    task = task_mod.arfbench(series_context=False)
    pos = Counter(s.target for s in task.dataset)
    # Blended chance is 24.4%; the pre-fix data scored 61.7% for always-A.
    assert pos["A"] / len(task.dataset) < 0.30


def test_invalid_series_context_raises():
    with pytest.raises(ValueError):
        task_mod.arfbench(limit=1, series_context="ture")


def test_nonpositive_limit_raises():
    with pytest.raises(ValueError):
        task_mod.arfbench(limit=0, series_context=False)
    with pytest.raises(ValueError):
        task_mod.arfbench(limit=-1, series_context=False)


def test_paired_context_is_all_or_none(monkeypatch):
    # Only the first of two groups has ts-data: the paired question must
    # fall back to descriptions-only rather than emit one-sided context.
    monkeypatch.setattr(
        task_mod, "_fetch_ts_at", lambda group, res: "p.parquet" if group == "g1" else None
    )
    text, res = task_mod._summarize_ts("g1,g2", fine=False)
    assert text is None and res is None


def test_paired_context_negotiates_common_resolution(monkeypatch):
    # g1 usable at 60s, g2 only at 300s: both sides must use 300s so their
    # peaks stay temporally comparable.
    usable = {("g1", "60"), ("g1", "300"), ("g2", "300")}

    def fake_fetch(group, res):
        return "p.parquet" if (group, res) in usable else None

    seen = []

    def fake_summarize(group, fine, res=None):
        seen.append((group, res))
        return (f"CTX-{group}@{res}", res)

    monkeypatch.setattr(task_mod, "_fetch_ts_at", fake_fetch)
    monkeypatch.setattr(task_mod, "_summarize_one", fake_summarize)
    text, res = task_mod._summarize_ts("g1,g2", fine=True)
    assert seen == [("g1", "300"), ("g2", "300")]
    assert "g1@300" in text and "g2@300" in text


def test_fine_resolution_detection():
    assert task_mod._needs_fine_resolution(
        "When did it start?", ["18:19:10", "18:19:43"]
    )
    assert not task_mod._needs_fine_resolution(
        "Was there an anomaly?", ["yes", "no"]
    )
    # Minute-aligned timestamps stay on coarser data.
    assert not task_mod._needs_fine_resolution(
        "When?", ["18:19:00", "18:24:00"]
    )
