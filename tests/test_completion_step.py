"""Run the governance workflow's actual completion-gate steps (spec: specs/completion-gate-wiring, CGW-3).

No test seam exists in the workflow: contracts are served by a local HTTP server standing in for the GitHub API,
and the gate is fetched by commit SHA from a local git repository standing in for github.com.
"""
import hashlib
import http.server
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/governance.yml"
FETCH = "      - name: Completion contract from base branch"
RUN = "      - name: Completion gate"
VERDICT = "      - id: v"
POLICY = "      - name: Governance policy checks"
BASE_SHA = "b" * 40


def step_block(marker):
    lines = WORKFLOW.read_text().splitlines()
    start = lines.index(marker)
    end = next((i for i in range(start + 1, len(lines))
                if lines[i].startswith("      - ") or (lines[i].strip() and not lines[i].startswith("      "))), len(lines))
    return lines[start:end]


def step_script(marker):
    block = step_block(marker)
    first = next(i for i, l in enumerate(block) if l == "        run: |") + 1
    return textwrap.dedent("\n".join(block[first:])) + "\n"


def contract(*commands, timeout=60):
    with open(ROOT / "completion-gate/tests/fixtures/contract_valid.json", encoding="utf-8") as fh:
        c = json.load(fh)
    c["completion_criteria"] = [{"check_id": f"CHK-{i}", "command": cmd, "timeout_seconds": timeout}
                                for i, cmd in enumerate(commands, 1)]
    return c


def py(code):
    return f"{sys.executable} -c {json.dumps(code)}"


def git(*args, cwd):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd, check=True,
                   capture_output=True, text=True)


def gate_repo(where, gate_source=ROOT / "completion-gate"):
    """A local repo holding completion-gate/ at one commit; returns (server_url, repo_name, sha)."""
    repo = where / "srv" / "gate.git"
    work = where / "gate-work"
    shutil.copytree(gate_source, work / "completion-gate", ignore=shutil.ignore_patterns("__pycache__"))
    git("init", "-q", cwd=work)
    git("add", ".", cwd=work)
    git("commit", "-q", "-m", "gate", cwd=work)
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=work, capture_output=True, text=True, check=True).stdout.strip()
    repo.parent.mkdir(parents=True)
    git("clone", "-q", "--bare", str(work), str(repo), cwd=where)
    git("config", "uploadpack.allowAnySHA1InWant", "true", cwd=repo)
    return "file://" + str(repo.parent), "gate.git", sha


class Api:
    """Stand-in for the GitHub contents API: serves contracts by path at BASE_SHA and logs every request."""
    def __init__(self, test):
        self.files, self.log, self.roles = {}, [], None
        api = self

        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                api.log.append((self.path, self.headers.get("Authorization")))
                if self.path == "/roles.yml" and api.roles is not None:
                    self.send_response(200); self.end_headers(); self.wfile.write(api.roles.encode()); return
                if "/contents/specs/redirect/" in self.path:
                    self.send_response(302); self.send_header("Location", "/elsewhere"); self.end_headers(); return
                m = re.match(r"^/repos/o/r/contents/(.+)\?ref=(\w+)$", self.path)
                body = api.files.get(m.group(1)) if m and m.group(2) == BASE_SHA else None
                self.send_response(200 if body is not None else 404)
                self.end_headers()
                self.wfile.write((body or "{}").encode())

            def log_message(self, *a):
                pass
        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        test.addCleanup(self.server.shutdown)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def serve(self, spec, data):
        self.files[f"{spec}/completion-contract.json"] = json.dumps(data)


class Fixture:
    def __init__(self, test, gate_source=ROOT / "completion-gate"):
        d = tempfile.TemporaryDirectory(prefix="completion-step-")
        test.addCleanup(d.cleanup)
        self.root = Path(d.name)
        self.temp = self.root / "runner-temp"
        self.temp.mkdir()
        self.workspace = self.root / "ws"
        self.workspace.mkdir()
        self.api = Api(test)
        self.server_url, self.gate_name, self.gate_sha = gate_repo(self.root, gate_source)

    def env(self, **extra):
        e = {"PATH": os.environ.get("PATH", os.defpath), "RUNNER_TEMP": str(self.temp), "HOME": str(self.root),
             "GITHUB_OUTPUT": str(self.root / "output"), "GITHUB_STEP_SUMMARY": str(self.root / "summary"),
             "GITHUB_ENV": str(self.root / "github-env"), "GITHUB_WORKSPACE": str(self.workspace),
             "PYTHONDONTWRITEBYTECODE": "1"}
        e.update(extra)
        return e

    def fetch(self, body, mode="advisory"):
        script = self.root / "fetch.py"
        script.write_text(step_script(FETCH))
        return subprocess.run([sys.executable, str(script)], cwd=self.workspace, capture_output=True, text=True, timeout=60,
                              env=self.env(MODE=mode, GH_TOKEN="test-token", REPO="o/r", PR_BODY=body, PR_BASE_SHA=BASE_SHA,
                                           GATE_REPO=self.gate_name, GATE_SHA=self.gate_sha, API_URL=self.api.url,
                                           SERVER_URL=self.server_url, ROLES_URL=self.api.url + "/roles.yml",
                                           GITHUB_OUTPUT=str(self.root / "fetch-output")))

    def plan(self):
        p = self.root / "fetch-output"
        lines = [l[5:] for l in p.read_text().splitlines() if l.startswith("plan=")] if p.exists() else []
        return lines[-1] if lines else ""

    def run_gate(self, mode="advisory", **extra_env):
        script = self.root / "run.py"
        script.write_text(step_script(RUN))
        # The workflow's shell line, with the interpreter swapped for this test's Python (flags kept).
        shell = next(l for l in step_block(RUN) if l.startswith("        shell: ")).split(": ", 1)[1].split()
        argv = [sys.executable] + [a for a in shell[1:] if a != "{0}"] + [str(script)]
        return subprocess.run(argv, cwd=self.workspace, capture_output=True, text=True,
                              timeout=180, env=self.env(MODE=mode, PLAN=self.plan(), **extra_env))

    def outputs(self):
        p = self.root / "output"
        return dict(l.split("=", 1) for l in p.read_text().splitlines() if "=" in l) if p.exists() else {}

    def summary(self):
        p = self.root / "summary"
        return p.read_text() if p.exists() else ""

    def both(self, body, mode="advisory"):
        self.fetch(body, mode)
        return self.run_gate(mode)


class CompletionFetch(unittest.TestCase):
    def test_CGW_3_4_mode_must_be_off_advisory_or_required(self):
        for bad in ("Required", "on", "blocking"):  # empty means the default, advisory (test_CGW_3_4_empty_mode_means_advisory)
            with self.subTest(mode=bad):
                f = Fixture(self)
                r = f.fetch("Spec: specs/x", mode=bad)
                self.assertNotEqual(r.returncode, 0)
                self.assertEqual(json.loads(f.plan())["status"], "invalid-mode")

    def test_CGW_3_1_no_spec_line_is_not_applicable(self):
        f = Fixture(self)
        r = f.fetch("No spec here.\nRelates to #1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(f.plan())["status"], "not-applicable")
        self.assertEqual([p for p, _ in f.api.log if "/contents/" in p], [])

    def test_CGW_3_2_contract_is_read_from_the_base_branch_with_the_token(self):
        f = Fixture(self)
        f.api.serve("specs/demo", contract("true"))
        r = f.fetch("Relates to #1\n\nSpec: specs/demo\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([x for x in f.api.log if "/contents/" in x[0]],
                         [(f"/repos/o/r/contents/specs/demo/completion-contract.json?ref={BASE_SHA}", "Bearer test-token")])
        self.assertEqual(json.loads((f.temp / "completion/contracts/1.json").read_text()), contract("true"))

    def test_CGW_3_2_gate_is_fetched_at_the_pinned_sha(self):
        f = Fixture(self)
        f.api.serve("specs/demo", contract("true"))
        f.fetch("Spec: specs/demo")
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=f.temp / "completion/gate", capture_output=True,
                              text=True).stdout.strip()
        self.assertEqual(head, f.gate_sha)
        self.assertTrue((f.temp / "completion/gate/completion-gate/completion_gate.py").is_file())

    def test_CGW_3_1_spec_lines_are_parsed_exactly_like_the_policy_gate(self):
        policy, fetch = step_script(POLICY), step_script(FETCH)
        spec_re = r'r"(?im)^\W*specs?\W*:[\s*`]*([\w./-]+)"'
        strip_re = r'r"/(requirements|design|tasks)\.md$"'
        for src, name in ((policy, "policy"), (fetch, "fetch")):
            with self.subTest(step=name):
                self.assertIn(spec_re, src)
                self.assertIn(strip_re, src)
                self.assertIn('folder.startswith(d + "/") and folder.count("/") == d.count("/") + 1 for d in spec_dirs', src)
        for body in ("- Spec: specs/demo", "**Spec:** `specs/demo`", "spec: specs/demo/requirements.md", "> Specs: specs/demo"):
            with self.subTest(body=body):
                f = Fixture(self)
                f.api.serve("specs/demo", contract("true"))
                f.fetch(body)
                self.assertEqual([c["spec"] for c in json.loads(f.plan())["contracts"]], ["specs/demo"])

    def test_CGW_3_2_hostile_spec_values_never_reach_the_api_or_verify(self):
        for body in ("Spec: specs/demo?ref=HEAD&x=", "Spec: specs/demo#", "Spec: specs/..", "Spec: specs/x/y",
                     "Spec: ../../etc", "Spec: src/app"):
            with self.subTest(body=body):
                f = Fixture(self)
                r = f.both(body, mode="required")
                self.assertTrue(all("?ref=" + BASE_SHA in p and "#" not in p.split("?")[0]
                                    for p, _ in f.api.log if "/contents/" in p), f.api.log)
                self.assertNotEqual(r.returncode, 0)
                self.assertNotEqual(f.outputs().get("verdict"), "VERIFIED")

    def test_CGW_3_2_dot_slugs_make_no_api_request(self):
        for body in ("Spec: specs/..", "Spec: specs/.", "Spec: .kiro/specs/.."):
            with self.subTest(body=body):
                f = Fixture(self)
                f.fetch(body)
                self.assertEqual([p for p, _ in f.api.log if "/contents/" in p], [],
                                 "a '.' or '..' slug must be rejected before any request")
                self.assertTrue(json.loads(f.plan())["unverified"])

    def test_CGW_3_5_spec_without_contract_is_recorded(self):
        f = Fixture(self)
        f.fetch("Spec: `specs/nocontract`")
        plan = json.loads(f.plan())
        self.assertEqual(plan["unverified"], [{"spec": "specs/nocontract", "why": "no completion contract; not gate-verified"}])
        self.assertEqual(plan["contracts"], [])

    def test_CGW_3_2_leftover_files_in_the_gate_folder_are_wiped_before_fetch(self):
        f = Fixture(self)
        stray = f.temp / "completion/gate/completion-gate"
        stray.mkdir(parents=True)
        (stray / "json.py").write_text("raise SystemExit('stray module shadowed the standard library')\n")
        f.api.serve("specs/demo", contract(py("pass")))
        r = f.both("Spec: specs/demo", mode="required")
        self.assertFalse((stray / "json.py").exists(), "leftover files must not survive into the fetched gate")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_CGW_3_2_leftover_state_is_wiped_before_fetch(self):
        f = Fixture(self)
        planted = f.temp / "completion"
        (planted / "evidence").mkdir(parents=True)
        (planted / "evidence/1.json").write_text('{"verdict": "VERIFIED"}')
        f.api.serve("specs/demo", contract(py("import sys; sys.exit(1)")))
        r = f.both("Spec: specs/demo", mode="required")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(f.outputs()["verdict"], "FAILED")


class CompletionRun(unittest.TestCase):
    def test_CGW_3_1_passing_contract_is_verified(self):
        f = Fixture(self)
        f.api.serve("specs/a", contract(py("pass")))
        r = f.both("Spec: specs/a", mode="required")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(f.outputs(), {"status": "ran", "verdict": "VERIFIED"})

    def test_CGW_3_3_evidence_and_summary_carry_verdict_reasons_and_hash(self):
        f = Fixture(self)
        c = contract(py("import sys; sys.exit(3)"))
        f.api.serve("specs/a", c)
        f.both("Spec: specs/a")
        ev = json.loads((f.temp / "completion/evidence/1.json").read_text())
        self.assertEqual(ev["verdict"], "FAILED")
        self.assertEqual(ev["contract_hash"], "sha256:" + hashlib.sha256(json.dumps(c).encode()).hexdigest())
        self.assertIn("| `specs/a` | FAILED | `" + ev["contract_hash"] + "` |", f.summary())
        self.assertIn("CHK-1 failed (exit 3)", f.summary())

    def test_CGW_3_4_advisory_reports_but_does_not_fail(self):
        f = Fixture(self)
        f.api.serve("specs/a", contract(py("import sys; sys.exit(1)")))
        r = f.both("Spec: specs/a", mode="advisory")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(f.outputs()["verdict"], "FAILED")
        self.assertIn("::warning::Completion gate FAILED", r.stdout)

    def test_CGW_3_4_required_fails_on_anything_but_verified(self):
        cases = {"failed": contract(py("import sys; sys.exit(1)")),
                 "timeout": contract(py("import time; time.sleep(30)"), timeout=1)}
        for name, c in cases.items():
            with self.subTest(case=name):
                f = Fixture(self)
                f.api.serve("specs/a", c)
                r = f.both("Spec: specs/a", mode="required")
                self.assertNotEqual(r.returncode, 0)
                self.assertNotEqual(f.outputs()["verdict"], "VERIFIED")
        f = Fixture(self)
        r = f.both("Spec: specs/missing", mode="required")
        self.assertNotEqual(r.returncode, 0)

    def test_CGW_3_5_spec_without_contract_is_never_verified(self):
        f = Fixture(self)
        f.both("Spec: specs/b")
        self.assertEqual(f.outputs(), {"status": "no-contract", "verdict": "UNKNOWN"})
        self.assertIn("no completion contract; not gate-verified", f.summary())

    def test_CGW_3_5_one_unverified_spec_makes_the_run_unverified(self):
        f = Fixture(self)
        f.api.serve("specs/a", contract(py("pass")))
        f.both("Spec: specs/a\nSpec: specs/b")
        self.assertEqual(f.outputs()["verdict"], "UNKNOWN")

    def test_CGW_3_2_gate_that_cannot_be_fetched_is_unknown(self):
        f = Fixture(self)
        f.api.serve("specs/a", contract(py("pass")))
        f.gate_sha = "d" * 40  # not in the repo
        r = f.both("Spec: specs/a", mode="required")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(f.outputs()["verdict"], "UNKNOWN")

    def test_CGW_3_2_verified_needs_gate_exit_zero_and_matching_contract_hash(self):
        liars = {"exits 1 but says VERIFIED": "1", "says VERIFIED for another contract": "0"}
        for name, code in liars.items():
            with self.subTest(case=name):
                d = tempfile.mkdtemp(prefix="liar-gate-")
                self.addCleanup(shutil.rmtree, d, True)
                os.makedirs(os.path.join(d, "completion-gate"))
                Path(d, "completion-gate/completion_gate.py").write_text(textwrap.dedent(f"""
                    import json, sys
                    ev = sys.argv[sys.argv.index("--evidence") + 1]
                    json.dump({{"verdict": "VERIFIED", "contract_hash": "sha256:{'0' * 64}", "verdict_reasons": []}}, open(ev, "w"))
                    sys.exit({code})
                """))
                f = Fixture(self, gate_source=Path(d, "completion-gate"))
                f.api.serve("specs/a", contract(py("pass")))
                r = f.both("Spec: specs/a", mode="required")
                self.assertNotEqual(r.returncode, 0)
                self.assertEqual(f.outputs()["verdict"], "UNKNOWN")

    def test_CGW_3_6_contract_commands_cannot_reach_runner_control_files(self):
        probe = py("import os, sys; bad = [k for k in ('GITHUB_ENV', 'GITHUB_PATH', 'GITHUB_OUTPUT', 'GITHUB_STEP_SUMMARY') "
                   "if k in os.environ]; sys.exit(9 if bad else 0)")
        f = Fixture(self)
        f.api.serve("specs/a", contract(probe))
        r = f.both("Spec: specs/a", mode="required")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(f.outputs()["verdict"], "VERIFIED")

    def test_CGW_3_1_not_applicable_writes_no_verdict(self):
        f = Fixture(self)
        r = f.both("no spec", mode="required")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(f.outputs(), {"status": "not-applicable", "verdict": ""})

    def test_CGW_3_2_spec_dirs_come_from_roles_yml_like_the_policy_gate(self):
        f = Fixture(self)
        f.api.roles = "version: 1\nspec_paths:\n  - docs/specs/   # comment\n  - .kiro/specs\n"
        f.api.serve("docs/specs/demo", contract(py("pass")))
        r = f.both("Spec: docs/specs/demo", mode="required")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(f.outputs(), {"status": "ran", "verdict": "VERIFIED"})
        g = Fixture(self)  # roles.yml unreadable: same fallback as the policy job
        g.api.serve("specs/demo", contract(py("pass")))
        self.assertEqual(g.both("Spec: specs/demo", mode="required").returncode, 0)

    def test_CGW_3_2_redirects_are_refused_and_the_token_is_not_forwarded(self):
        f = Fixture(self)
        r = f.both("Spec: specs/redirect", mode="required")
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("/elsewhere", [p for p, _ in f.api.log])
        self.assertIn("could not fetch (HTTP 302)", f.summary())

    def test_CGW_3_5_empty_spec_reference_is_never_verified(self):
        f = Fixture(self)
        r = f.both("Spec: /", mode="required")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(f.outputs().get("verdict"), "UNKNOWN")


class CompletionTamper(unittest.TestCase):
    def tampered(self, change):
        f = Fixture(self)
        f.api.serve("specs/a", contract(py("import sys; sys.exit(1)")))
        f.api.serve("specs/b", contract(py("pass")))
        f.fetch("Spec: specs/a\nSpec: specs/b\nSpec: specs/nocontract")
        change(f.temp / "completion")
        return f, f.run_gate(mode="required")

    def test_CGW_3_2_contract_swapped_after_fetch_is_unknown(self):
        def swap(out):
            (out / "contracts/1.json").write_text(json.dumps(contract(py("pass"))))
        f, r = self.tampered(swap)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("staged contract changed after it was fetched", f.summary())
        self.assertNotEqual(f.outputs()["verdict"], "VERIFIED")

    def test_CGW_3_2_gate_swapped_after_fetch_is_unknown(self):
        def swap(out):
            (out / "gate/completion-gate/completion_gate.py").write_text(
                "import json,sys\njson.dump({'verdict':'VERIFIED'},open(sys.argv[3],'w'))\n")
        f, r = self.tampered(swap)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("staged gate missing or changed after it was fetched", f.summary())

    def test_CGW_3_5_deleting_staged_files_cannot_drop_unverified_entries(self):
        def wipe(out):
            for p in list((out / "contracts").glob("*")):
                p.unlink()
        f, r = self.tampered(wipe)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(f.outputs()["verdict"], "UNKNOWN")
        self.assertIn("specs/nocontract", f.summary())


    def test_CGW_3_2_an_earlier_contract_cannot_swap_the_gate_for_a_later_one(self):
        liar = textwrap.dedent("""
            import hashlib, json, sys
            c = sys.argv[1]; ev = sys.argv[sys.argv.index("--evidence") + 1]
            h = "sha256:" + hashlib.sha256(open(c, "rb").read()).hexdigest()
            json.dump({"verdict": "VERIFIED", "contract_hash": h, "verdict_reasons": []}, open(ev, "w"))
        """)
        swap = py("import os; open(os.path.join(os.environ['RUNNER_TEMP'], 'completion/gate/completion-gate/completion_gate.py'),"
                  " 'w').write(" + json.dumps(liar) + ")")
        f = Fixture(self)
        f.api.serve("specs/a", contract(swap))
        f.api.serve("specs/b", contract(py("import sys; sys.exit(1)")))
        f.fetch("Spec: specs/a\nSpec: specs/b")
        r = f.run_gate(mode="required")
        self.assertNotEqual(r.returncode, 0)
        self.assertNotEqual(f.outputs()["verdict"], "VERIFIED")
        self.assertIn("| `specs/b` | UNKNOWN |", f.summary())
        self.assertIn("staged gate missing or changed after it was fetched", f.summary())

    def test_CGW_3_2_pythonpath_hooks_do_not_reach_the_step_or_the_gate(self):
        hook = Path(tempfile.mkdtemp(prefix="hook-"))
        self.addCleanup(shutil.rmtree, hook, True)
        marker = hook / "imported"
        (hook / "sitecustomize.py").write_text(f"open({str(marker)!r}, 'a').write('x')\n")
        f = Fixture(self)
        f.api.serve("specs/a", contract("false"))
        f.fetch("Spec: specs/a")
        r = f.run_gate(mode="required", PYTHONPATH=str(hook))
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(f.outputs()["verdict"], "FAILED")
        self.assertFalse(marker.exists(), "sitecustomize on PYTHONPATH was imported by the run step or the gate")

    def test_CGW_3_4_empty_mode_means_advisory(self):
        f = Fixture(self)
        f.api.serve("specs/a", contract(py("import sys; sys.exit(1)")))
        self.assertEqual(f.fetch("Spec: specs/a", mode="").returncode, 0)
        r = f.run_gate(mode="")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(f.outputs()["verdict"], "FAILED")

    def test_CGW_3_5_too_many_spec_references_is_never_verified(self):
        f = Fixture(self)
        for i in range(25):
            f.api.serve(f"specs/s{i:02d}", contract(py("pass")))
        r = f.both("\n".join(f"Spec: specs/s{i:02d}" for i in range(25)), mode="required")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(f.outputs()["verdict"], "UNKNOWN")
        self.assertEqual(len(json.loads(f.plan())["contracts"]), 20)


class CompletionVerdict(unittest.TestCase):
    def verdict(self, mode, status, verdict, event="pull_request", policy_spec=""):
        with tempfile.TemporaryDirectory(prefix="completion-verdict-") as d:
            root = Path(d)
            script = root / "v.sh"
            script.write_text(step_script(VERDICT))
            env = {"PATH": os.defpath, "QUALITY": "success", "POLICY": "success", "SECRETS": "success", "SECURITY": "success",
                   "RUN_QUALITY": "true", "SYSTEM_QUALITY_DEFINITION": "", "PREREQUISITE_RESULT": "success",
                   "EVENT_NAME": event, "COMPLETION_MODE": mode, "COMPLETION_STATUS": status, "COMPLETION_VERDICT": verdict,
                   "POLICY_SPEC": policy_spec, "GITHUB_OUTPUT": str(root / "out"), "GITHUB_STEP_SUMMARY": str(root / "summary")}
            r = subprocess.run(["/bin/bash", str(script)], cwd=root, env=env, capture_output=True, text=True, timeout=10)
            return r.returncode, (root / "out").read_text()

    def test_CGW_3_4_required_needs_verified(self):
        self.assertEqual(self.verdict("required", "ran", "VERIFIED", policy_spec="specs/a")[0], 0)
        for status, v in (("ran", "FAILED"), ("ran", "UNKNOWN"), ("no-contract", "UNKNOWN"), ("", ""), ("not-run", "")):
            with self.subTest(status=status, verdict=v):
                code, out = self.verdict("required", status, v)
                self.assertNotEqual(code, 0)
                self.assertIn("verdict=fail", out)

    def test_CGW_3_4_required_fails_when_policy_saw_a_spec_the_completion_step_did_not(self):
        code, out = self.verdict("required", "not-applicable", "", policy_spec="specs/demo")
        self.assertNotEqual(code, 0)
        self.assertIn("verdict=fail", out)

    def test_CGW_3_4_mode_must_match_exactly_in_the_verdict(self):
        for bad in ("Advisory", "REQUIRED", "on"):
            with self.subTest(mode=bad):
                self.assertNotEqual(self.verdict(bad, "not-applicable", "")[0], 0)

    def test_CGW_3_4_advisory_never_fails_the_verdict(self):
        for status, v in (("ran", "FAILED"), ("no-contract", "UNKNOWN"), ("", "")):
            with self.subTest(status=status):
                self.assertEqual(self.verdict("advisory", status, v, policy_spec="specs/a")[0], 0)

    def test_CGW_3_4_required_ignores_prs_without_a_spec_and_pushes(self):
        self.assertEqual(self.verdict("required", "not-applicable", "")[0], 0)
        self.assertEqual(self.verdict("required", "", "", event="push")[0], 0)


class CompletionWorkflowShape(unittest.TestCase):
    def test_CGW_3_4_default_mode_is_advisory(self):
        m = re.search(r"\n      completion-gate:\n(?:        .*\n)+?        default: \"(\w+)\"", WORKFLOW.read_text())
        self.assertTrue(m)
        self.assertEqual(m.group(1), "advisory")

    def test_CGW_3_4_only_advisory_continues_on_error(self):
        for marker in (FETCH, RUN):
            with self.subTest(step=marker.strip()):
                self.assertIn("        continue-on-error: ${{ inputs.completion-gate == 'advisory' || inputs.completion-gate == '' }}",
                              step_block(marker))

    def test_CGW_3_2_run_step_uses_the_system_interpreter_isolated_from_python_env(self):
        self.assertIn("        shell: /usr/bin/python3 -E -s -B {0}", step_block(RUN))

    def test_CGW_3_6_run_step_has_no_token_or_secrets(self):
        block = "\n".join(step_block(RUN))
        self.assertNotRegex(block, r"secrets\.|github\.token|GH_TOKEN|GITHUB_TOKEN")
        self.assertNotIn("--audit", block)

    def test_CGW_3_6_quality_job_is_read_only(self):
        text = WORKFLOW.read_text()
        quality = text[text.index("\n  quality:\n"):text.index("\n  policy:\n")]
        self.assertIn("    permissions:\n      contents: read\n", quality)
        self.assertNotRegex(quality, r"secrets\.")

    def test_CGW_3_2_fetch_runs_before_any_pr_code(self):
        lines = WORKFLOW.read_text().splitlines()
        q = lines.index("  quality:")
        steps = [l for l in lines[q:lines.index("  policy:")] if l.startswith("      - ")]
        self.assertEqual(steps[:2], ["      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1", FETCH])

    def test_CGW_3_2_gate_comes_from_the_pinned_workflow_revision(self):
        block = "\n".join(step_block(FETCH))
        self.assertIn("GATE_REPO: ${{ job.workflow_repository }}", block)
        self.assertIn("GATE_SHA: ${{ job.workflow_sha }}", block)

    def test_CGW_3_3_evidence_is_uploaded(self):
        text = WORKFLOW.read_text()
        self.assertIn("      - name: Upload completion evidence", text)
        self.assertIn("path: ${{ runner.temp }}/completion/evidence/*.json", text)


if __name__ == "__main__":
    unittest.main()
