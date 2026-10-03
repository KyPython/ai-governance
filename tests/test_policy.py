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
ROLES = ROOT / "roles.yml"

SPEC = """# Requirements: demo
### Requirement 1: Demo (DEMO-1)
#### Acceptance Criteria
1. DEMO-1.1 WHEN a user greets THEN the system SHALL answer hello.
"""
KY = ("KyPython", "179089861+KyPython@users.noreply.github.com")
KIRO = ("kiro-agent[bot]", "123+kiro-agent[bot]@users.noreply.github.com")
CURSOR = ("cursor[bot]", "206951365+cursor[bot]@users.noreply.github.com")
WEBFLOW = ("GitHub", "noreply@github.com")


def sh(cwd, *args, env=None):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout.strip()


class Repo:
    def __init__(self, base_files=None):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        sh(self.dir, "git", "init", "-q", "-b", "main")
        files = {"AGENTS.md": "<!-- AI-GOVERNANCE:v1 -->\n", ".github/CODEOWNERS": "* @KyPython\n",
                 "package.json": json.dumps({"name": "x", "scripts": {"test": "node --test"}, "dependencies": {"a": "1.0.0"}}, indent=2),
                 "src/app.js": "export const x = 1;\n"}
        files.update(base_files or {})
        self.write(files)
        self.base = self.commit("base", KY, KY)
        sh(self.dir, "git", "checkout", "-q", "-b", "feature")

    def write(self, files):
        for name, content in files.items():
            p = self.dir / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)

    def commit(self, msg, author=KY, committer=None):
        committer = committer or author
        env = dict(os.environ, GIT_AUTHOR_NAME=author[0], GIT_AUTHOR_EMAIL=author[1],
                   GIT_COMMITTER_NAME=committer[0], GIT_COMMITTER_EMAIL=committer[1])
        sh(self.dir, "git", "add", "-A")
        sh(self.dir, "git", "commit", "-q", "--allow-empty", "-m", msg, env=env)
        return sh(self.dir, "git", "rev-parse", "HEAD")

    def policy(self, body="Closes #1\n\nSpec: specs/demo", title="feat(app): change", head_ref="feature",
               author=KY, committer=None, opener="KyPython", repo="KyPython/demo", roles=ROLES):
        head = self.commit("change", author, committer)
        summary = self.dir / ".summary"
        env = dict(os.environ, EVENT_NAME="pull_request", PR_TITLE=title, PR_BODY=body, PR_BASE_SHA=self.base,
                   PR_HEAD_SHA=head, PR_HEAD_REF=head_ref, PUSH_BEFORE="", PUSH_AFTER=head, REQUIRE_ISSUE="false",
                   ENFORCE_TITLE="true", STC_MODE="off", BASELINE_MODE="changed", PR_AUTHOR=opener, REPO=repo,
                   ROLES_FILE=str(roles), GITHUB_STEP_SUMMARY=str(summary))
        p = subprocess.run(["python3", "-c", POLICY], cwd=self.dir, env=env, capture_output=True, text=True)
        summary.unlink(missing_ok=True)
        return p.returncode, p.stdout + p.stderr


class Base(unittest.TestCase):
    def repo(self, base_files=None):
        r = Repo(base_files)
        self.addCleanup(r.tmp.cleanup)
        return r

    def code_repo(self):
        """A repo whose main branch already has the Kiro-authored spec specs/demo."""
        return self.repo({"specs/demo/requirements.md": SPEC})


class SpecGate(Base):
    def test_GATE_1_1_code_pr_without_issue_link_fails(self):
        r = self.code_repo(); r.write({"src/app.js": "export const x = 2;\n", "tests/app.test.js": "// DEMO-1.1\n"})
        code, out = r.policy(body="Spec: specs/demo")
        self.assertEqual(code, 1, out); self.assertIn("must link an issue", out)

    def test_GATE_1_2_code_pr_without_spec_reference_fails(self):
        r = self.code_repo(); r.write({"src/app.js": "export const x = 2;\n", "tests/app.test.js": "// DEMO-1.1\n"})
        code, out = r.policy(body="Closes #1")
        self.assertEqual(code, 1, out); self.assertIn("references no spec", out)

    def test_GATE_1_2_spec_on_base_referenced_in_body_passes(self):
        r = self.code_repo(); r.write({"src/app.js": "export const x = 2;\n", "tests/app.test.js": "test('DEMO-1.1 greets', () => {});\n"})
        code, out = r.policy(body="Relates to #3\n\n**Spec:** `specs/demo/requirements.md`", author=CURSOR, opener="cursor[bot]")
        self.assertEqual(code, 0, out); self.assertIn("(on base branch)", out); self.assertIn("traceability", out)

    def test_GATE_1_2_kiro_spec_dir_on_base_passes(self):
        r = self.repo({".kiro/specs/demo/requirements.md": SPEC})
        r.write({"src/app.js": "export const x = 2;\n", "src/app.test.js": "// verifies DEMO-1\n"})
        code, out = r.policy(body="Closes #1\nSpec: .kiro/specs/demo")
        self.assertEqual(code, 0, out)

    def test_GATE_1_2_spec_not_on_base_branch_fails(self):
        r = self.repo(); r.write({"specs/demo/requirements.md": SPEC}); r.commit("spec on a side branch", KIRO)
        r.write({"src/app.js": "export const x = 2;\n", "tests/app.test.js": "// DEMO-1.1\n"})
        code, out = r.policy()
        self.assertEqual(code, 1, out); self.assertIn("does not exist on the base branch", out)

    def test_GATE_1_3_base_spec_without_ears_criteria_fails(self):
        r = self.repo({"specs/demo/requirements.md": "# Requirements\nJust prose.\n"})
        r.write({"src/app.js": "export const x = 2;\n", "tests/app.test.js": "// DEMO-1.1\n"})
        code, out = r.policy()
        self.assertEqual(code, 1, out); self.assertIn("no numbered EARS acceptance criteria", out)

    def test_GATE_1_3_spec_folder_without_requirements_md_fails(self):
        r = self.repo({"specs/demo/design.md": "# Design\n"})
        r.write({"src/app.js": "export const x = 2;\n", "tests/app.test.js": "// DEMO-1.1\n"})
        code, out = r.policy()
        self.assertEqual(code, 1, out); self.assertIn("specs/demo/requirements.md` does not exist", out)

    def test_GATE_1_4_no_test_change_fails(self):
        r = self.code_repo(); r.write({"src/app.js": "export const x = 2;\n"})
        code, out = r.policy()
        self.assertEqual(code, 1, out); self.assertIn("no test was added or changed", out)

    def test_GATE_1_4_test_without_requirement_id_fails(self):
        r = self.code_repo(); r.write({"src/app.js": "export const x = 2;\n", "tests/app.test.js": "test('works', () => {}); // DEMO-12.1 is not ours\n"})
        code, out = r.policy()
        self.assertEqual(code, 1, out); self.assertIn("do not cite any requirement ID", out)

    def test_GATE_1_4_underscore_id_in_test_name_traces(self):
        r = self.code_repo(); r.write({"src/app.js": "export const x = 2;\n", "tests/test_app.py": "def test_DEMO_1_1_greets():\n    pass\n"})
        code, out = r.policy()
        self.assertEqual(code, 0, out); self.assertIn("tests/test_app.py -> DEMO-1.1", out)

    def test_GATE_1_4_similar_but_different_id_does_not_trace(self):
        r = self.code_repo(); r.write({"src/app.js": "export const x = 2;\n", "tests/test_app.py": "def test_DEMO_12_1():\n    pass  # SUBDEMO-1.1\n"})
        code, out = r.policy()
        self.assertEqual(code, 1, out); self.assertIn("do not cite any requirement ID", out)

    def test_GATE_1_5_docs_only_pr_is_exempt(self):
        r = self.repo(); r.write({"README.md": "# docs\n", "docs/guide.md": "x\n"})
        code, out = r.policy(body="no issue", author=CURSOR, opener="cursor[bot]")
        self.assertEqual(code, 0, out); self.assertIn("exempt by path rule", out)

    def test_GATE_1_5_dependency_only_package_json_is_exempt(self):
        r = self.repo(); r.write({"package.json": json.dumps({"name": "x", "scripts": {"test": "node --test"}, "dependencies": {"a": "1.1.0"}}, indent=2),
                                  "pnpm-lock.yaml": "lockfileVersion: '9.0'\n"})
        code, out = r.policy(body="bump", opener="dependabot[bot]", author=("dependabot[bot]", "49699333+dependabot[bot]@users.noreply.github.com"))
        self.assertEqual(code, 0, out)

    def test_GATE_1_5_package_json_script_change_is_code(self):
        r = self.repo(); r.write({"package.json": json.dumps({"name": "x", "scripts": {"test": "true"}, "dependencies": {"a": "1.0.0"}}, indent=2)})
        code, out = r.policy(body="Closes #1")
        self.assertEqual(code, 1, out); self.assertIn("Code paths requiring a spec: package.json", out)

    def test_GATE_1_6_dependabot_branch_name_does_not_exempt_code(self):
        r = self.repo(); r.write({"src/app.js": "export const x = 3;\n"})
        code, out = r.policy(body="", head_ref="dependabot/npm_and_yarn/a-1.1.0")
        self.assertEqual(code, 1, out); self.assertIn("must link an issue", out)

    def test_GATE_1_7_code_and_spec_in_same_pr_fails(self):
        r = self.code_repo(); r.write({"src/app.js": "export const x = 2;\n", "specs/demo/requirements.md": SPEC + "2. DEMO-1.2 WHEN x THEN the system SHALL y.\n",
                                       "tests/app.test.js": "// DEMO-1.1\n"})
        code, out = r.policy(author=KIRO, opener="kiro-agent[bot]")
        self.assertEqual(code, 1, out); self.assertIn("changes code AND spec files", out)

    def test_GATE_1_8_spec_only_pr_by_kiro_passes(self):
        r = self.repo(); r.write({"specs/demo/requirements.md": SPEC, "specs/demo/design.md": "# Design\n"})
        code, out = r.policy(body="Relates to #4", author=KIRO, committer=WEBFLOW, opener="kiro-agent[bot]")
        self.assertEqual(code, 0, out); self.assertIn("spec-only PR", out); self.assertIn("role gate: every PR opener", out)


class RoleGate(Base):
    def test_GATE_3_1_spec_change_committed_by_coder_fails(self):
        r = self.repo(); r.write({"specs/demo/requirements.md": SPEC})
        code, out = r.policy(body="Relates to #4", author=CURSOR, opener="kiro-agent[bot]")
        self.assertEqual(code, 1, out); self.assertIn("author cursor[bot]", out); self.assertIn("role: coder", out)

    def test_GATE_3_1_spec_pr_opened_by_coder_fails_even_with_owner_commits(self):
        r = self.repo(); r.write({"specs/demo/requirements.md": SPEC})
        code, out = r.policy(body="Relates to #4", author=KY, opener="chatgpt-codex-connector[bot]")
        self.assertEqual(code, 1, out); self.assertIn("PR opener @chatgpt-codex-connector[bot] (role: coder)", out)

    def test_GATE_3_1_unknown_committer_on_spec_change_fails(self):
        r = self.repo(); r.write({"specs/demo/requirements.md": SPEC})
        code, out = r.policy(body="Relates to #4", author=KIRO, committer=("box", "box@example.com"), opener="kiro-agent[bot]")
        self.assertEqual(code, 1, out); self.assertIn("committer box <box@example.com> (role: unknown)", out)

    def test_GATE_3_1_owner_override_passes(self):
        r = self.repo(); r.write({".kiro/specs/demo/requirements.md": SPEC})
        code, out = r.policy(body="Relates to #4", author=KY, opener="KyPython")
        self.assertEqual(code, 0, out)

    def test_GATE_3_2_web_flow_committer_is_ignored_but_author_is_checked(self):
        r = self.repo(); r.write({"specs/demo/requirements.md": SPEC})
        code, out = r.policy(body="Relates to #4", author=CURSOR, committer=WEBFLOW, opener="KyPython")
        self.assertEqual(code, 1, out); self.assertIn("author cursor[bot]", out); self.assertNotIn("committer GitHub", out)

    def test_GATE_3_3_roles_yml_change_by_non_owner_fails(self):
        r = self.repo(); r.write({"roles.yml": "version: 2\n"})
        code, out = r.policy(body="Relates to #2", author=KIRO, opener="kiro-agent[bot]", repo="KyPython/ai-governance")
        self.assertEqual(code, 1, out); self.assertIn("roles.yml may only be changed by the owner", out)

    def test_GATE_3_3_roles_yml_change_by_owner_passes(self):
        r = self.repo(); r.write({"roles.yml": "version: 2\n"})
        code, out = r.policy(body="Relates to #2", repo="KyPython/ai-governance")
        self.assertEqual(code, 0, out); self.assertIn("roles.yml changed by the owner identity only", out)

    def test_GATE_3_4_missing_role_map_fails_closed(self):
        r = self.repo(); r.write({"README.md": "# docs\n"})
        code, out = r.policy(body="Closes #1", roles=r.dir / "nope.yml")
        self.assertEqual(code, 1, out); self.assertIn("fails closed", out)

    def test_GATE_3_5_role_map_comes_from_ai_governance_main_not_caller_inputs(self):
        self.assertIn("ROLES_URL: https://raw.githubusercontent.com/KyPython/ai-governance/main/roles.yml", WORKFLOW)
        inputs = WORKFLOW.split("inputs:", 1)[1].split("outputs:", 1)[0]
        names = re.findall(r"(?m)^      ([\w-]+):$", inputs)
        self.assertIn("require-tests", names)
        self.assertFalse([n for n in names if "spec" in n or "role" in n], names)


class CallerTemplate(unittest.TestCase):
    def test_GATE_2_1_template_reruns_on_edited(self):
        self.assertRegex(TEMPLATE, r"types:\s*\[[^\]]*\bedited\b")

    def test_GATE_2_2_template_does_not_cancel_same_sha_reruns(self):
        self.assertIn("github.event.action == 'synchronize'", TEMPLATE)


if __name__ == "__main__":
    unittest.main()
