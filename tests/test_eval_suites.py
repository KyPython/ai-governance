"""Run each published suite in isolation to avoid colliding module names."""

import os
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "suite",
    ["approval-gate", "dispatch-regression-20case", "delegation-judgment", "arfbench"],
)
def test_suite_regressions(suite):
    suite_root = ROOT / "evals" / suite
    test_files = sorted(
        str(path.relative_to(suite_root))
        for path in suite_root.rglob("test_*.py")
        if path.name.count(".") == 1
    )
    assert test_files, f"No regression tests found in {suite}"
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *test_files],
        cwd=suite_root,
        env={**os.environ, "PYTEST_ADDOPTS": "", "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_archived_v2_scorer():
    result = subprocess.run(
        [sys.executable, "test_v2_scorer.v2.py"],
        cwd=ROOT / "evals" / "approval-gate",
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
