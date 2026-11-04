"""Offline contract tests for scripts/ky-new-repo (KYNEW-1/2).

Only argument validation, shared-checkout refusal, and --dry-run are
covered: live creation needs gh auth and creates real repos, so CI never
runs it.
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ky-new-repo"


def run_script(args, cwd, extra_env=None):
    env = None
    if extra_env:
        env = dict(os.environ)
        env.update(extra_env)
    return subprocess.run(
        [str(SCRIPT), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )


class KyNewRepoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ky-new-repo-")
        self.addCleanup(self.tmp.cleanup)
        # /tmp is outside the shared checkout, so validation (not refusal) runs.
        # realpath: TMPDIR contains symlinks (/var -> /private/var) that would
        # defeat the textual prefix match the script performs on $PWD.
        self.scratch = os.path.realpath(self.tmp.name)

    def test_missing_name_exits_2(self):
        # KYNEW-1.1
        result = run_script([], self.scratch)
        self.assertEqual(result.returncode, 2)

    def test_invalid_name_exits_2(self):
        # KYNEW-1.1
        result = run_script(["-bad name!"], self.scratch)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Invalid repo name", result.stderr)

    def test_two_names_exits_2(self):
        # KYNEW-1.1
        result = run_script(["one", "two"], self.scratch)
        self.assertEqual(result.returncode, 2)

    def test_bad_ci_kind_exits_2(self):
        # KYNEW-1.2
        result = run_script(["--ci", "rust", "name"], self.scratch)
        self.assertEqual(result.returncode, 2)

    def test_shared_checkout_refused(self):
        # KYNEW-1.3: point the shared root at the scratch dir, run inside it.
        result = run_script(
            ["--dry-run", "name"],
            self.scratch,
            extra_env={"KY_NEW_REPO_SHARED_ROOT": self.scratch},
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("Refusing to run inside the shared checkout", result.stderr)

    def test_unknown_flag_exits_2(self):
        # KYNEW-1.4
        result = run_script(["--frobnicate", "name"], self.scratch)
        self.assertEqual(result.returncode, 2)

    def test_dry_run_prints_plan_and_executes_nothing(self):
        # KYNEW-2.1
        result = run_script(["--dry-run", "demo"], self.scratch)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("DRY-RUN complete: nothing executed.", result.stdout)
        self.assertIn("gh repo create", result.stdout)
        self.assertFalse(os.path.exists("/tmp/ky-new-repo-demo"))

    def test_dry_run_org_mentions_ruleset_user_mentions_protect(self):
        # KYNEW-2.2
        org = run_script(["--dry-run", "--org", "Acme", "demo"], self.scratch)
        self.assertEqual(org.returncode, 0, org.stderr)
        self.assertIn("ruleset", org.stdout)
        user = run_script(["--dry-run", "--user", "someone", "demo"], self.scratch)
        self.assertEqual(user.returncode, 0, user.stderr)
        self.assertIn("optin.sh --protect", user.stdout)


if __name__ == "__main__":
    unittest.main()
