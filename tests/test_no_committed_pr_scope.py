"""A `.pr-scope` file must not be committed to the repository root.

Spec: specs/pr-scope-manifest
- PRS-1.1: the default branch has no tracked `.pr-scope` at the repository root.
- PRS-2.1: the test fails when it is tracked, and the failure message names the file and cites PRS-1.1.
- PRS-2.2: the decision uses `git ls-files` (tracked state), not working-tree existence.
- PRS-2.3: the test name and this header cite PRS-1.1.
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
    def test_PRS_1_1_pr_scope_is_not_tracked_in_repo_root(self):
        """PRS-1.1 / PRS-2.1 / PRS-2.2: `.pr-scope` must not be tracked; declare the manifest in the PR body."""
        files = tracked_files()
        if files is None:
            self.skipTest("not a git checkout")
        self.assertNotIn(
            ".pr-scope",
            files,
            "PRS-1.1 violated: `.pr-scope` is committed in the repo root. It overrides every PR's manifest "
            "in the diff-hygiene script. Delete it and declare the manifest in the PR body's `## Files touched` section instead.",
        )


if __name__ == "__main__":
    unittest.main()
