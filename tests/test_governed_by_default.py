"""The creation path and its documentation (spec: specs/governed-by-default, GBD-2.2, GBD-2.3, GBD-5.2)."""
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
NEW_REPO = ROOT / "scripts" / "ky-new-repo"
README = ROOT / "README.md"


def dry_run(*args):
    with tempfile.TemporaryDirectory() as d:
        env = dict(os.environ, KY_NEW_REPO_SHARED_ROOT=str(Path(d) / "elsewhere"))
        r = subprocess.run(["bash", str(NEW_REPO), "--dry-run", *args], cwd=d, env=env, capture_output=True,
                           text=True, timeout=30)
    return r


class CreationPath(unittest.TestCase):
    def test_GBD_2_2_new_repos_pin_the_gate_to_main_at_creation(self):
        r = dry_run("demo-repo")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("GOV_SHA=$(gh api repos/KyPython/ai-governance/commits/main --jq .sha)", r.stdout)
        src = NEW_REPO.read_text()
        self.assertIn('GOV_SHA="$(gh api "repos/$GOV_REPO/commits/main" --jq .sha)"', src)
        self.assertIn('"${TEMPLATE//__AI_GOVERNANCE_SHA__/$GOV_SHA}" > .github/workflows/ai-governance.yml', src)

    def test_GBD_2_2_new_repos_start_with_the_governance_bundle(self):
        out = dry_run("demo-repo").stdout
        bundle = next(l for l in out.splitlines() if "install bundle:" in l)
        for part in (".github/workflows/ai-governance.yml (pinned)", "AGENTS.md section", ".github/CODEOWNERS"):
            self.assertIn(part, bundle)
        self.assertLess(out.index("install bundle:"), out.index("git push"), "the bundle is in the first push")

    def test_GBD_2_3_template_creation_uses_repo_starter(self):
        self.assertIn("--template KyPython/repo-starter", dry_run("--template", "demo-repo").stdout)

    def test_GBD_2_2_readme_names_ky_new_repo_the_only_supported_way(self):
        text = README.read_text()
        section = text[text.index("## Governed by default"):text.index("## Deploys")]
        self.assertIn("`scripts/ky-new-repo` is the only supported way to create a repo", section)
        self.assertIn("./scripts/ky-new-repo --dry-run", section)

    def test_GBD_5_2_readme_states_the_token_scopes_and_the_personal_account_limit(self):
        section = README.read_text()
        section = section[section.index("## Governed by default"):section.index("## Deploys")]
        self.assertIn("`SWEEP_TOKEN` repository secret", section)
        self.assertTrue(re.search(r"`repo` and `workflow` scopes", section))
        self.assertIn("cannot be blocked at creation", section)
        self.assertIn("Ky creates it", section)


if __name__ == "__main__":
    unittest.main()
