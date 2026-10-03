"""Behavioral tests for the `policy` job of .github/workflows/governance.yml.

Each test runs the job's real Python script against a throwaway git repo and
cites the spec criterion it verifies (specs/ai-governance-gate/requirements.md).
Run: python3 -m unittest discover -s tests -v
"""
import json, os, re, subprocess, tempfile, textwrap, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github/workflows/governance.yml").read_text()
def step_script(after, until):
    """The Python body of the first `shell: python3 {0}` step after `after`, up to `until`."""
    tail = WORKFLOW.split(after, 1)[1]
    return textwrap.dedent(tail.split("shell: python3 {0}\n        run: |\n", 1)[1].split(until, 1)[0])


POLICY = step_script("- name: Governance policy checks", "\n  security:")
TEST_PARSER = step_script("- name: Parse test results (scorecard)", "\n  policy:")
SCORECARD = step_script("- name: Scorecard (machine-readable summary)", "\n      - name: Upload scorecard artifact")
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
               author=KY, committer=None, opener="KyPython", repo="KyPython/demo", roles=ROLES, output=None):
        head = self.commit("change", author, committer)
        summary = self.dir / ".summary"
        env = dict(os.environ, EVENT_NAME="pull_request", PR_TITLE=title, PR_BODY=body, PR_BASE_SHA=self.base,
                   PR_HEAD_SHA=head, PR_HEAD_REF=head_ref, PUSH_BEFORE="", PUSH_AFTER=head, REQUIRE_ISSUE="false",
                   ENFORCE_TITLE="true", STC_MODE="off", BASELINE_MODE="changed", PR_AUTHOR=opener, REPO=repo,
                   ROLES_FILE=str(roles), GITHUB_STEP_SUMMARY=str(summary), GITHUB_OUTPUT=str(output or os.devnull))
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

    def test_GATE_1_5_file_purpose_inventory_is_repo_metadata(self):
        r = self.repo(); r.write({"config/purpose-inventory.json": '{"paths": {"AGENTS.md": {"purpose": "rules"}}}\n', "AGENTS.md": "<!-- AI-GOVERNANCE:v1 -->\nx\n"})
        code, out = r.policy(body="Closes #1")
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


class KiroAsCoder(Base):
    def test_GATE_3_6_kiro_code_pr_implementing_base_spec_passes(self):
        r = self.code_repo(); r.write({"src/app.js": "export const x = 2;\n", "tests/app.test.js": "// DEMO-1.1\n"})
        code, out = r.policy(author=KIRO, opener="kiro-agent[bot]")
        self.assertEqual(code, 0, out)


class Scorecard(Base):
    def run_script(self, script, env, cwd):
        p = subprocess.run(["python3", "-c", script], cwd=cwd, env=dict(os.environ, **env), capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def test_GATE_4_2_policy_reports_ids_spec_errors_and_changed_lines(self):
        r = self.code_repo(); r.write({"src/app.js": "export const x = 2;\nexport const y = 3;\n", "tests/app.test.js": "// DEMO-1.1\n",
                                       "pnpm-lock.yaml": "lockfileVersion: '9.0'\n" * 50})
        out_file = r.dir / ".out"
        code, out = r.policy(output=out_file)
        self.assertEqual(code, 0, out)
        got = dict(l.split("=", 1) for l in out_file.read_text().splitlines())
        self.assertEqual(got["requirement_ids"], "DEMO-1.1"); self.assertEqual(got["spec"], "specs/demo")
        self.assertEqual(got["policy_errors"], "0"); self.assertEqual(got["files_changed"], "3")
        # src/app.js: +2/-1, tests/app.test.js: +1; the lockfile's 50 lines are excluded
        self.assertEqual((got["lines_added"], got["lines_deleted"]), ("3", "1"))

    def test_GATE_4_3_parses_common_test_runner_output(self):
        samples = {
            "Tests:       1 failed, 45 passed, 46 total\n": (45, 1, 46),                           # Jest
            " Test Files  2 passed (2)\n      Tests  2 failed | 10 passed (12)\n": (10, 2, 12),   # Vitest
            "=========== 7 passed, 1 failed, 2 skipped in 0.12s ===========\n": (7, 1, 10),       # pytest
            "Ran 28 tests in 1.6s\n\nFAILED (failures=2, errors=1)\n": (25, 3, 28),             # unittest
            "# tests 5\n# suites 1\n# pass 4\n# fail 1\n": (4, 1, 5),                          # node:test
            "  9 passing (20ms)\n  1 failing\n": (9, 1, 10),                                    # Mocha
            "\x1b[1mTests:\x1b[22m 3 passed, 3 total\nTests:       2 passed, 2 total\n": (5, 0, 5),  # ANSI + monorepo sum
        }
        for text, (p, f, t) in samples.items():
            with self.subTest(text=text), tempfile.TemporaryDirectory() as d:
                Path(d, "test-output.log").write_text(text); out = Path(d, "out")
                code, log = self.run_script(TEST_PARSER, {"RUNNER_TEMP": d, "GITHUB_OUTPUT": str(out)}, d)
                self.assertEqual(code, 0, log)
                self.assertEqual(out.read_text(), f"passed={p}\nfailed={f}\ntotal={t}\n")

    def test_GATE_4_3_unrecognized_output_reports_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "test-output.log").write_text("all good\n"); out = Path(d, "out")
            code, log = self.run_script(TEST_PARSER, {"RUNNER_TEMP": d, "GITHUB_OUTPUT": str(out)}, d)
            self.assertEqual(code, 0, log); self.assertFalse(out.exists() and out.read_text().strip())

    def test_GATE_4_1_scorecard_json_output_and_job_summary(self):
        with tempfile.TemporaryDirectory() as d:
            env = {"QUALITY": "success", "POLICY": "success", "SECRETS": "success", "SECURITY": "success", "RUN_QUALITY": "true",
                   "TESTS_PASSED": "45", "TESTS_FAILED": "1", "TESTS_TOTAL": "46", "REQUIREMENT_IDS": "GOV-1.1,GOV-1.2",
                   "SPEC": "specs/gov", "POLICY_ERRORS": "0", "LINES_ADDED": "30", "LINES_DELETED": "4", "FILES_CHANGED": "3",
                   "REPO": "KyPython/demo", "PR_NUMBER": "7", "PR_AUTHOR": "cursor[bot]", "HEAD_SHA": "abc", "RUN_URL": "u",
                   "GITHUB_OUTPUT": str(Path(d, "out")), "GITHUB_STEP_SUMMARY": str(Path(d, "sum"))}
            code, log = self.run_script(SCORECARD, env, d)
            self.assertEqual(code, 0, log)
            card = json.loads(Path(d, "ai-governance-summary.json").read_text())
            self.assertEqual(card["schema"], "ai-governance-summary/v1")
            self.assertEqual(card["tests"], {"passed": 45, "failed": 1, "total": 46})
            self.assertEqual(card["requirement_ids"], ["GOV-1.1", "GOV-1.2"]); self.assertEqual(card["failed_checks"], 0)
            self.assertEqual(card["changed_lines"], {"added": 30, "deleted": 4, "total": 34}); self.assertEqual(card["pr"], 7)
            self.assertEqual(json.loads(Path(d, "out").read_text().split("summary=", 1)[1]), card)
            self.assertIn("| pass | 45/46 (1 failed) | GOV-1.1, GOV-1.2 | 0 | 34 (+30/-4) | 3 |", Path(d, "sum").read_text())
            self.assertIn("AI_GOVERNANCE_SUMMARY {", log)

    def test_GATE_4_4_scorecard_counts_failures_but_never_fails_itself(self):
        with tempfile.TemporaryDirectory() as d:
            env = {"QUALITY": "failure", "POLICY": "success", "SECRETS": "cancelled", "SECURITY": "success", "RUN_QUALITY": "true",
                   "GITHUB_OUTPUT": str(Path(d, "out")), "GITHUB_STEP_SUMMARY": str(Path(d, "sum"))}
            code, log = self.run_script(SCORECARD, env, d)
            self.assertEqual(code, 0, log)
            card = json.loads(Path(d, "ai-governance-summary.json").read_text())
            self.assertEqual(card["verdict"], "fail"); self.assertEqual(card["failed_checks"], 2)
            self.assertEqual(card["tests"]["total"], None); self.assertEqual(card["changed_lines"]["total"], None)

    def test_GATE_4_4_verdict_decision_does_not_read_the_scorecard(self):
        verdict_step = WORKFLOW.split("      - id: v\n", 1)[1]
        self.assertNotIn("card", verdict_step); self.assertNotIn("summary=", verdict_step)


DEP_REVIEW = textwrap.dedent(WORKFLOW.split("- name: Dependency review (osv-scanner", 1)[1].split("<<'PY'\n", 1)[1].split("\n          PY\n", 1)[0])


class StrictParity(Base):
    """Checks carried over from LamportLogic (validate-constitution.sh, pre-tool-use hook, deploy-all.yml,
    validate-container-hardening.js, security-lint.yml, ci.yml shellcheck, dependency review)."""

    def test_GATE_5_1_hand_rolled_jwt_auth_added_fails(self):
        r = self.repo(); r.write({"src/login.ts": "import jwt from 'jsonwebtoken';\nexport const t = jwt.sign({}, 'k');\n"})
        code, out = r.policy(body="Closes #1")
        self.assertEqual(code, 1, out); self.assertIn("hand-rolled JWT auth added", out)

    def test_GATE_5_1_shared_auth_package_and_legacy_code_are_allowed(self):
        r = self.repo({"src/legacy.ts": "import jwt from 'jsonwebtoken';\n"})
        r.write({"packages/auth/src/jwt.ts": "export const v = jwt.verify;\n", "src/legacy.ts": "import jwt from 'jsonwebtoken';\nexport {};\n", "README.md": "x\n"})
        code, out = r.policy(body="Closes #1")
        self.assertNotIn("hand-rolled JWT", out); self.assertIn("guardrails: no hand-rolled auth", out)

    def test_GATE_5_2_direct_prisma_client_added_fails(self):
        r = self.repo(); r.write({"apps/api/db.js": "const db = new PrismaClient();\n"})
        code, out = r.policy(body="Closes #1")
        self.assertEqual(code, 1, out); self.assertIn("direct `new PrismaClient` added", out)

    def test_GATE_5_3_destructive_command_in_script_fails(self):
        r = self.repo(); r.write({"scripts/reset.sh": "#!/bin/sh\ngit reset --hard origin/main\n", "package.json": json.dumps({"name": "x", "scripts": {"test": "node --test", "nuke": "prisma migrate reset --force"}, "dependencies": {"a": "1.0.0"}}, indent=2)})
        code, out = r.policy(body="Closes #1")
        self.assertEqual(code, 1, out); self.assertIn("scripts/reset.sh (hard reset)", out); self.assertIn("package.json (database reset)", out)

    def test_GATE_5_3_destructive_text_in_docs_is_not_flagged(self):
        r = self.repo(); r.write({"docs/runbook.md": "Never run `git reset --hard` or `terraform destroy`.\n"})
        code, out = r.policy(body="Closes #1")
        self.assertEqual(code, 0, out); self.assertIn("no destructive commands added", out)

    def test_GATE_5_4_deploy_workflow_on_pull_request_fails(self):
        r = self.repo(); r.write({".github/workflows/deploy.yml": "name: Deploy\non:\n  pull_request:\n  push:\n    branches: [main]\npermissions: {}\njobs: {}\n"})
        code, out = r.policy(body="Closes #1")
        self.assertEqual(code, 1, out); self.assertIn("deploys on pull_request events", out)

    def test_GATE_5_4_workflow_run_deploy_must_check_success(self):
        wf = "name: Deploy all\non:\n  workflow_run:\n    workflows: [CI]\n    types: [completed]\npermissions: {}\njobs:\n  d:\n    if: %s\n    runs-on: ubuntu-latest\n    steps: []\n"
        r = self.repo(); r.write({".github/workflows/release.yml": wf % "true"})
        code, out = r.policy(body="Closes #1")
        self.assertEqual(code, 1, out); self.assertIn("never checks `github.event.workflow_run.conclusion == 'success'`", out)
        r2 = self.repo(); r2.write({".github/workflows/release.yml": wf % "github.event.workflow_run.conclusion == 'success'"})
        code, out = r2.policy(body="Closes #1")
        self.assertEqual(code, 0, out); self.assertIn("deploy after CI: `.github/workflows/release.yml` is gated", out)

    def test_GATE_5_5_dockerfile_latest_base_and_root_user_fail(self):
        r = self.repo(); r.write({"Dockerfile": "FROM node:latest\nCOPY . .\nCMD [\"node\", \"x.js\"]\n"})
        code, out = r.policy(body="Closes #1")
        self.assertEqual(code, 1, out); self.assertIn("unversioned or :latest base image", out); self.assertIn("runs as root", out)

    def test_GATE_5_5_pinned_non_root_dockerfile_passes(self):
        r = self.repo(); r.write({"apps/x/Dockerfile": "FROM node:22.11.0-alpine AS build\nRUN echo hi\nFROM node:22.11.0-alpine@sha256:abc\nUSER node\nCMD [\"node\"]\n"})
        code, out = r.policy(body="Closes #1")
        self.assertIn("container: `apps/x/Dockerfile` pins its base image and runs as non-root", out)

    def test_GATE_5_6_security_job_is_pinned_and_required_by_verdict(self):
        self.assertIn('ZIZMOR_SHA256: "eee12266b793cb87ad4a7e3af2e72404f8a63e3de5eb099b80bf7b1cfd232a8e"', WORKFLOW)
        self.assertIn("--require-hashes", WORKFLOW); self.assertIn("--min-severity medium", WORKFLOW)
        self.assertIn('echo "${OSV_SHA256}  $RUNNER_TEMP/osv-scanner" | sha256sum -c -', WORKFLOW)
        self.assertIn("shellcheck --severity=error", WORKFLOW)
        self.assertIn("needs: [quality, policy, security, secret-scan]", WORKFLOW)
        self.assertIn('[ "$SECURITY" = "success" ]', WORKFLOW)

    def test_GATE_5_7_dependency_review_fails_only_on_newly_introduced_vulns(self):
        def res(*vs):
            return {"results": [{"packages": [{"package": {"ecosystem": "npm", "name": n, "version": ver}, "vulnerabilities": [{"id": i}]} for n, ver, i in vs]}]}
        with tempfile.TemporaryDirectory() as d:
            b, h, summ = Path(d, "b.json"), Path(d, "h.json"), Path(d, "s")
            b.write_text(json.dumps(res(("old", "1.0.0", "GHSA-old"))))
            h.write_text(json.dumps(res(("old", "1.0.1", "GHSA-old"))))
            p = subprocess.run(["python3", "-c", DEP_REVIEW, str(b), str(h)], env=dict(os.environ, GITHUB_STEP_SUMMARY=str(summ)), capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            h.write_text(json.dumps(res(("old", "1.0.1", "GHSA-old"), ("evil", "2.0.0", "GHSA-new"))))
            p = subprocess.run(["python3", "-c", DEP_REVIEW, str(b), str(h)], env=dict(os.environ, GITHUB_STEP_SUMMARY=str(summ)), capture_output=True, text=True)
            self.assertEqual(p.returncode, 1); self.assertIn("npm evil@2.0.0 introduces GHSA-new", p.stdout)


class CallerTemplate(unittest.TestCase):
    def test_GATE_2_1_template_reruns_on_edited(self):
        self.assertRegex(TEMPLATE, r"types:\s*\[[^\]]*\bedited\b")

    def test_GATE_2_2_template_does_not_cancel_same_sha_reruns(self):
        self.assertIn("github.event.action == 'synchronize'", TEMPLATE)


if __name__ == "__main__":
    unittest.main()
