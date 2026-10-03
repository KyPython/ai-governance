"""Behavioral tests for the `policy` job of .github/workflows/governance.yml.

Each test runs the job's real Python script against a throwaway git repo and
cites the spec criterion it verifies (specs/ai-governance-gate/requirements.md).
Run: python3 -m unittest discover -s tests -v
"""
import json, os, re, subprocess, tempfile, textwrap, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github/workflows/governance.yml").read_text()
POLICY = textwrap.dedent(WORKFLOW.split("shell: python3 {0}\n        run: |\n", 1)[1].split("\n  secret-scan:", 1)[0])
TEMPLATE = (ROOT / "templates/ai-governance.yml").read_text()

SPEC = """# Requirements: demo
### Requirement 1: Demo (DEMO-1)
#### Acceptance Criteria
1. DEMO-1.1 WHEN a user greets THEN the system SHALL answer hello.
"""


def sh(cwd, *args):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


class Repo:
    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        sh(self.dir, "git", "init", "-q", "-b", "main")
        sh(self.dir, "git", "config", "user.email", "t@example.com")
        sh(self.dir, "git", "config", "user.name", "t")
        self.write({"AGENTS.md": "<!-- AI-GOVERNANCE:v1 -->\n", ".github/CODEOWNERS": "* @KyPython\n",
                    "package.json": json.dumps({"name": "x", "scripts": {"test": "node --test"}, "dependencies": {"a": "1.0.0"}}, indent=2),
                    "src/app.js": "export const x = 1;\n"})
        self.base = self.commit("base")
        sh(self.dir, "git", "checkout", "-q", "-b", "feature")

    def write(self, files):
        for name, content in files.items():
            p = self.dir / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)

    def commit(self, msg):
        sh(self.dir, "git", "add", "-A")
        sh(self.dir, "git", "commit", "-q", "-m", msg)
        return sh(self.dir, "git", "rev-parse", "HEAD")

    def policy(self, body="Closes #1", title="feat(app): change", head_ref="feature"):
        head = self.commit("change")
        summary = self.dir / ".summary"
        env = dict(os.environ, EVENT_NAME="pull_request", PR_TITLE=title, PR_BODY=body, PR_BASE_SHA=self.base,
                   PR_HEAD_SHA=head, PR_HEAD_REF=head_ref, PUSH_BEFORE="", PUSH_AFTER=head, REQUIRE_ISSUE="false",
                   ENFORCE_TITLE="true", STC_MODE="off", BASELINE_MODE="changed", SPEC_DIRS="specs,.kiro/specs",
                   GITHUB_STEP_SUMMARY=str(summary))
        p = subprocess.run(["python3", "-c", POLICY], cwd=self.dir, env=env, capture_output=True, text=True)
        summary.unlink(missing_ok=True)
        return p.returncode, p.stdout + p.stderr


class SpecGate(unittest.TestCase):
    def repo(self):
        r = Repo()
        self.addCleanup(r.tmp.cleanup)
        return r

    def test_GATE_1_1_code_pr_without_issue_link_fails(self):
        r = self.repo(); r.write({"src/app.js": "export const x = 2;\n", "specs/demo/requirements.md": SPEC,
                             "tests/app.test.js": "// DEMO-1.1\n"})
        code, out = r.policy(body="no link here")
        self.assertEqual(code, 1, out); self.assertIn("must link an issue", out)

    def test_GATE_1_2_code_pr_without_spec_fails(self):
        r = self.repo(); r.write({"src/app.js": "export const x = 2;\n", "tests/app.test.js": "// DEMO-1.1\n"})
        code, out = r.policy()
        self.assertEqual(code, 1, out); self.assertIn("no spec was added or referenced", out)

    def test_GATE_1_2_spec_referenced_in_body_passes(self):
        r = self.repo(); r.write({"specs/demo/requirements.md": SPEC}); r.base = r.commit("spec on main")
        r.write({"src/app.js": "export const x = 2;\n", "tests/app.test.js": "test('DEMO-1.1 greets', () => {});\n"})
        code, out = r.policy(body="Relates to #3\n\nSpec: specs/demo")
        self.assertEqual(code, 0, out); self.assertIn("traceability", out)

    def test_GATE_1_2_kiro_spec_folder_passes(self):
        r = self.repo(); r.write({"src/app.js": "export const x = 2;\n", ".kiro/specs/demo/requirements.md": SPEC,
                             "src/app.test.js": "// verifies DEMO-1\n"})
        code, out = r.policy()
        self.assertEqual(code, 0, out)

    def test_GATE_1_3_spec_without_ears_criteria_fails(self):
        r = self.repo(); r.write({"src/app.js": "export const x = 2;\n", "specs/demo/requirements.md": "# Requirements\nJust prose.\n",
                             "tests/app.test.js": "// DEMO-1.1\n"})
        code, out = r.policy()
        self.assertEqual(code, 1, out); self.assertIn("no numbered EARS acceptance criteria", out)

    def test_GATE_1_3_spec_folder_without_requirements_md_fails(self):
        r = self.repo(); r.write({"src/app.js": "export const x = 2;\n", "specs/demo/design.md": "# Design\n",
                             "tests/app.test.js": "// DEMO-1.1\n"})
        code, out = r.policy()
        self.assertEqual(code, 1, out); self.assertIn("does not exist", out)

    def test_GATE_1_4_no_test_change_fails(self):
        r = self.repo(); r.write({"src/app.js": "export const x = 2;\n", "specs/demo/requirements.md": SPEC})
        code, out = r.policy()
        self.assertEqual(code, 1, out); self.assertIn("no test was added or changed", out)

    def test_GATE_1_4_test_without_requirement_id_fails(self):
        r = self.repo(); r.write({"src/app.js": "export const x = 2;\n", "specs/demo/requirements.md": SPEC,
                             "tests/app.test.js": "test('works', () => {}); // DEMO-12.1 is not ours\n"})
        code, out = r.policy()
        self.assertEqual(code, 1, out); self.assertIn("do not cite any requirement ID", out)

    def test_GATE_1_4_underscore_id_in_test_name_traces(self):
        r = self.repo(); r.write({"src/app.js": "export const x = 2;\n", "specs/demo/requirements.md": SPEC,
                                  "tests/test_app.py": "def test_DEMO_1_1_greets():\n    pass\n"})
        code, out = r.policy()
        self.assertEqual(code, 0, out); self.assertIn("tests/test_app.py -> DEMO-1.1", out)

    def test_GATE_1_4_similar_but_different_id_does_not_trace(self):
        r = self.repo(); r.write({"src/app.js": "export const x = 2;\n", "specs/demo/requirements.md": SPEC,
                                  "tests/test_app.py": "def test_DEMO_12_1():\n    pass  # SUBDEMO-1.1\n"})
        code, out = r.policy()
        self.assertEqual(code, 1, out); self.assertIn("do not cite any requirement ID", out)

    def test_GATE_1_5_docs_only_pr_is_exempt(self):
        r = self.repo(); r.write({"README.md": "# docs\n", "docs/guide.md": "x\n"})
        code, out = r.policy(body="no issue")
        self.assertEqual(code, 0, out); self.assertIn("exempt by path rule", out)

    def test_GATE_1_5_dependency_only_package_json_is_exempt(self):
        r = self.repo(); r.write({"package.json": json.dumps({"name": "x", "scripts": {"test": "node --test"}, "dependencies": {"a": "1.1.0"}}, indent=2),
                             "pnpm-lock.yaml": "lockfileVersion: '9.0'\n"})
        code, out = r.policy(body="bump")
        self.assertEqual(code, 0, out)

    def test_GATE_1_5_package_json_script_change_is_code(self):
        r = self.repo(); r.write({"package.json": json.dumps({"name": "x", "scripts": {"test": "true"}, "dependencies": {"a": "1.0.0"}}, indent=2)})
        code, out = r.policy()
        self.assertEqual(code, 1, out); self.assertIn("Code paths requiring a spec: package.json", out)

    def test_GATE_1_6_dependabot_branch_name_does_not_exempt_code(self):
        r = self.repo(); r.write({"src/app.js": "export const x = 3;\n"})
        code, out = r.policy(body="", head_ref="dependabot/npm_and_yarn/a-1.1.0")
        self.assertEqual(code, 1, out); self.assertIn("must link an issue", out)


class CallerTemplate(unittest.TestCase):
    def test_GATE_2_1_template_reruns_on_edited(self):
        self.assertRegex(TEMPLATE, r"types:\s*\[[^\]]*\bedited\b")

    def test_GATE_2_2_template_does_not_cancel_same_sha_reruns(self):
        self.assertIn("github.event.action == 'synchronize'", TEMPLATE)


if __name__ == "__main__":
    unittest.main()
