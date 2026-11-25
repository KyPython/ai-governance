"""A `.pr-scope` file must not be committed to the repository root.

Spec: specs/ai-governance-gate (GATE-1.5: the closest criterion; no spec here covers the diff-hygiene manifest).
The diff-hygiene script reads its manifest from a committed `.pr-scope` first and only then from the PR body's
`## Files touched` section. A stale committed file therefore overrides the manifest every later PR declares.
"""
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def tracked_files():
    """Return the set of tracked paths, or None when this is not a git checkout."""
    try:
        r = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return set(r.stdout.splitlines()) if r.returncode == 0 else None


class NoCommittedPrScope(unittest.TestCase):
    def test_GATE_1_5_pr_scope_is_not_tracked_in_repo_root(self):
        """GATE-1.5: `.pr-scope` is counted as code and must not linger; declare the manifest in the PR body."""
        files = tracked_files()
        if files is None:
            self.skipTest("not a git checkout")
        self.assertNotIn(
            ".pr-scope",
            files,
            "`.pr-scope` is committed in the repo root. It overrides every PR's manifest in the diff-hygiene "
            "script. Delete it and declare the manifest in the PR body's `## Files touched` section instead.",
        )


if __name__ == "__main__":
    unittest.main()
