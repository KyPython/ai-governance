"""The governance sweep against a stateful fake GitHub API (spec: specs/governed-by-default, GBD-3.1 to GBD-3.5)."""
import base64
import http.server
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import textwrap
import threading
import unittest
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
SWEEP = ROOT / "scripts" / "sweep.py"
WORKFLOW = ROOT / ".github" / "workflows" / "sweep.yml"
GOV = "KyPython/ai-governance"
MAIN = "c" * 40
OLD = "a" * 40
CALLER = ".github/workflows/ai-governance.yml"


def caller_text(pin):
    return f"jobs:\n  ai-governance:\n    uses: KyPython/ai-governance/.github/workflows/governance.yml@{pin} # main\n"


class FakeGitHub:
    """In-memory GitHub: repos, files per (repo, branch), PRs, Actions allow-lists. Logs every request."""

    def __init__(self, test):
        self.repos, self.files, self.prs, self.actions, self.blocked = {}, {}, {}, {}, set()
        self.log, self.user_status, self.protected, self.verdict, self.fail = [], 200, set(), {}, set()
        gh = self

        class H(http.server.BaseHTTPRequestHandler):
            def _send(self, code, body=None):
                data = json.dumps(body).encode() if body is not None else b""
                self.send_response(code); self.send_header("Content-Type", "application/json"); self.end_headers()
                self.wfile.write(data)

            def _route(self, method):
                n = int(self.headers.get("Content-Length") or 0)
                body = json.loads(self.rfile.read(n)) if n else None
                u = urllib.parse.urlparse(self.path); qs = dict(urllib.parse.parse_qsl(u.query)); path = urllib.parse.unquote(u.path)
                gh.log.append((method, path, body))
                code, out = gh.handle(method, path, qs, body)
                self._send(code, out)

            def do_GET(self): self._route("GET")
            def do_POST(self): self._route("POST")
            def do_PUT(self): self._route("PUT")
            def do_PATCH(self): self._route("PATCH")
            def do_DELETE(self): self._route("DELETE")
            def log_message(self, *a): pass

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        test.addCleanup(self.server.shutdown)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def add_repo(self, fn, pin=None, selected=None):
        self.repos[fn] = {"full_name": fn, "default_branch": "main", "owner": {"login": fn.split("/")[0]},
                          "archived": False, "fork": False, "size": 10}
        if pin:
            self.files[(fn, "main")] = caller_text(pin)
        if selected is not None:
            self.actions[fn] = list(selected)
        self.prs[fn] = []

    def handle(self, method, path, qs, body):
        page = int(qs.get("page", "1"))
        if path == "/user":
            return (self.user_status, {"login": "KyPython"} if self.user_status == 200 else {"message": "Bad credentials"})
        if path == "/user/memberships/orgs":
            return 200, ([{"role": "admin", "organization": {"login": "KyLamportLogic"}}] if page == 1 else [])
        if path == "/user/repos":
            return 200, (list(self.repos.values()) if page == 1 else [])
        if path == f"/repos/{GOV}/commits/main":
            return 200, {"sha": MAIN}
        if path == f"/repos/{GOV}/contents/.github/workflows/governance.yml":
            return 200, {"content": base64.b64encode(b"ROLES_URL: x").decode(), "sha": "g"}
        m = re.match(r"^/repos/([^/]+/[^/]+)(/.*)?$", path)
        fn, rest = m.group(1), m.group(2) or ""
        for marker in self.fail:  # injected failures: (method, path-suffix)
            if method == marker[0] and rest.endswith(marker[1]):
                return 502, {"message": "injected failure"}
        if rest == f"/contents/{CALLER}":
            ref = qs.get("ref") or (body or {}).get("branch")
            if method == "GET":
                t = self.files.get((fn, ref))
                return (200, {"content": base64.b64encode(t.encode()).decode(), "sha": f"blob-{ref}"}) if t else (404, {"message": "Not Found"})
            if method == "PUT":
                if fn in self.blocked:
                    return 409, {"message": "Repository rule violations found\n\nChanges must be made through a pull request."}
                self.files[(fn, body["branch"])] = base64.b64decode(body["content"]).decode()
                return 200, {}
        if rest == "/commits":
            return 200, [{"sha": "x"}]
        if rest == "/actions/permissions":
            return 200, {"allowed_actions": "selected" if fn in self.actions else "all"}
        if rest == "/actions/permissions/selected-actions":
            if method == "PUT":
                self.actions[fn] = body["patterns_allowed"]; return 204, None
            if getattr(self, "partial_actions", False):
                return 200, {"patterns_allowed": self.actions.get(fn, [])}
            return 200, {"github_owned_allowed": True, "verified_allowed": False, "patterns_allowed": self.actions.get(fn, [])}
        if rest == "/pulls":
            if method == "POST":
                pr = {"head": {"ref": body["head"], "repo": {"full_name": fn}}, "base": {"ref": body["base"]}, "state": "open",
                      "merged_at": None, "html_url": f"https://github.com/{fn}/pull/{len(self.prs[fn]) + 1}", "title": body["title"]}
                self.prs[fn].append(pr); return 201, pr
            state = qs.get("state", "open")
            items = [x for x in self.prs[fn] if state == "all" or x.get("state", "open") == state]
            return 200, (items if page == 1 else [])
        if rest.startswith("/git/ref/heads/"):
            return 200, {"object": {"sha": "base-sha"}}
        if rest == "/git/refs" and method == "POST":
            branch = body["ref"][len("refs/heads/"):]
            self.files[(fn, branch)] = self.files[(fn, "main")]
            return 201, {}
        if rest.endswith("/protection"):
            if fn in self.protected:
                return 200, {"required_status_checks": {"checks": [{"context": "ai-governance / verdict"}]},
                             "enforce_admins": {"enabled": True}}
            return 404, {"message": "Branch not protected"}
        if rest.startswith("/branches/"):
            return 404, {"message": "Branch not found"}
        if "/check-runs" in rest:
            v = self.verdict.get(fn)
            return 200, {"check_runs": [{"conclusion": v}] if v else []}
        return 404, {"message": f"unhandled {method} {path}"}

    def writes(self):
        return [(m, p) for m, p, _ in self.log if m != "GET"]


class Sweep(unittest.TestCase):
    def run_sweep(self, gh, apply=True):
        d = tempfile.mkdtemp(prefix="sweep-")
        self.addCleanup(lambda: subprocess.run(["rm", "-rf", d]))
        optin = Path(d, "optin.sh")
        optin.write_text(f"#!/bin/sh\necho \"$@\" >> {d}/optin.log\n")
        optin.chmod(0o755)
        env = dict(os.environ, GITHUB_TOKEN="t", APPLY="1" if apply else "0", DIR=d, GITHUB_API_URL=gh.url,
                   SKIP_FILE="", PYTHONDONTWRITEBYTECODE="1")
        r = subprocess.run([sys.executable, str(SWEEP)], env=env, capture_output=True, text=True, timeout=60)
        self.optin_log = Path(d, "optin.log").read_text() if Path(d, "optin.log").exists() else ""
        return r

    def row(self, out, fn):
        return next(l for l in out.splitlines() if l.startswith(fn + " "))

    def test_GBD_3_3_stale_pin_gets_one_bump_pr_to_main(self):
        gh = FakeGitHub(self); gh.add_repo("KyPython/a", pin=OLD)
        r = self.run_sweep(gh)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("bump PR opened", self.row(r.stdout, "KyPython/a"))
        self.assertEqual(len(gh.prs["KyPython/a"]), 1)
        self.assertEqual(gh.files[("KyPython/a", "ci/bump-ai-governance-ccccccc")], caller_text(MAIN))
        self.assertEqual(gh.files[("KyPython/a", "main")], caller_text(OLD), "the default branch is never written")
        r2 = self.run_sweep(gh)
        self.assertEqual(len(gh.prs["KyPython/a"]), 1, "a second sweep must not open a duplicate PR")
        self.assertIn("bump PR open", self.row(r2.stdout, "KyPython/a"))

    def test_GBD_3_3_existing_bump_pr_is_updated_not_duplicated(self):
        gh = FakeGitHub(self); gh.add_repo("KyPython/b", pin=OLD)
        branch = "ci/bump-ai-governance-c2b9fc3"
        gh.files[("KyPython/b", branch)] = caller_text("b" * 40)
        gh.prs["KyPython/b"].append({"head": {"ref": branch, "repo": {"full_name": "KyPython/b"}}, "base": {"ref": "main"},
                                     "state": "open", "merged_at": None,
                                     "html_url": "https://github.com/KyPython/b/pull/12", "title": "ci: bump"})
        r = self.run_sweep(gh)
        self.assertEqual(len(gh.prs["KyPython/b"]), 1)
        self.assertEqual(gh.files[("KyPython/b", branch)], caller_text(MAIN))
        self.assertIn("pull/12", self.row(r.stdout, "KyPython/b"))

    def test_GBD_3_3_current_pin_opens_nothing(self):
        gh = FakeGitHub(self); gh.add_repo("KyPython/c", pin=MAIN)
        self.run_sweep(gh)
        self.assertEqual(gh.prs["KyPython/c"], [])
        self.assertFalse([w for w in gh.writes() if "/repos/KyPython/c/" in w[1]])

    def test_GBD_3_4_selected_actions_repos_allow_every_ai_governance_path(self):
        gh = FakeGitHub(self)
        gh.add_repo("KyLamportLogic/d", pin=MAIN, selected=[f"{GOV}/.github/workflows/governance.yml@*", "other/x@*"])
        r = self.run_sweep(gh)
        self.assertEqual(gh.actions["KyLamportLogic/d"], [f"{GOV}/.github/workflows/governance.yml@*", "other/x@*",
                                                          f"{GOV}/.github/actions/*@*"])
        self.assertIn("allowed KyPython/ai-governance/.github/actions/*@*", self.row(r.stdout, "KyLamportLogic/d"))

    def test_GBD_3_1_report_only_writes_nothing(self):
        gh = FakeGitHub(self)
        gh.add_repo("KyPython/a", pin=OLD); gh.add_repo("KyLamportLogic/d", pin=OLD, selected=[]); gh.add_repo("KyPython/new")
        r = self.run_sweep(gh, apply=False)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(gh.writes(), [])
        self.assertEqual(self.optin_log, "")
        self.assertIn("would bump the pin", self.row(r.stdout, "KyPython/a"))
        self.assertIn("would allow", self.row(r.stdout, "KyLamportLogic/d"))
        self.assertIn("would open opt-in PR", self.row(r.stdout, "KyPython/new"))

    def test_GBD_3_2_ungoverned_repo_gets_the_opt_in_pr(self):
        gh = FakeGitHub(self); gh.add_repo("KyPython/new")
        r = self.run_sweep(gh)
        self.assertEqual(self.optin_log.strip(), "KyPython/new")
        self.assertIn("opened", self.row(r.stdout, "KyPython/new"))

    def test_GBD_3_3_a_repo_that_cannot_take_a_commit_is_reported_blocked(self):
        gh = FakeGitHub(self); gh.add_repo("KyPython/odin", pin=OLD); gh.blocked.add("KyPython/odin")
        r = self.run_sweep(gh)
        self.assertEqual(r.returncode, 0)
        line = self.row(r.stdout, "KyPython/odin")
        self.assertIn("blocked", line)
        self.assertIn("Repository rule violations found", line)
        self.assertEqual(gh.prs["KyPython/odin"], [])

    def test_GBD_3_4_unreadable_allow_list_is_never_overwritten(self):
        gh = FakeGitHub(self)
        gh.add_repo("KyLamportLogic/d", pin=MAIN, selected=["other/keep@*"])
        gh.fail.add(("GET", "/actions/permissions/selected-actions"))
        r = self.run_sweep(gh)
        self.assertEqual(gh.actions["KyLamportLogic/d"], ["other/keep@*"])
        self.assertFalse([w for w in gh.writes() if w[1].endswith("/selected-actions")])
        self.assertIn("allow-list not changed: could not read it", self.row(r.stdout, "KyLamportLogic/d"))

    def test_GBD_3_3_stale_pin_never_blocks_branch_protection(self):
        gh = FakeGitHub(self); gh.add_repo("KyPython/e", pin=OLD); gh.verdict["KyPython/e"] = "success"
        r = self.run_sweep(gh)
        self.assertIn("--protect KyPython/e", self.optin_log)
        line = self.row(r.stdout, "KyPython/e")
        self.assertIn("protected", line)
        self.assertIn("bump PR opened", line)

    def test_GBD_3_3_protected_current_repo_is_ok_and_stale_one_reports_the_bump(self):
        gh = FakeGitHub(self)
        gh.add_repo("KyPython/ok", pin=MAIN); gh.protected.add("KyPython/ok")
        gh.add_repo("KyPython/old", pin=OLD); gh.protected.add("KyPython/old")
        r = self.run_sweep(gh)
        self.assertTrue(self.row(r.stdout, "KyPython/ok").split()[1] == "ok")
        old = self.row(r.stdout, "KyPython/old")
        self.assertEqual(old.split()[1], "bump-pr")
        self.assertEqual(len(gh.prs["KyPython/old"]), 1)

    def test_GBD_3_3_odd_pins_are_left_alone(self):
        gh = FakeGitHub(self)
        gh.add_repo("KyPython/tag"); gh.files[("KyPython/tag", "main")] = "uses: KyPython/ai-governance/.github/workflows/governance.yml@main\n"
        gh.add_repo("KyPython/two"); gh.files[("KyPython/two", "main")] = caller_text(OLD) + caller_text(MAIN)
        r = self.run_sweep(gh)
        self.assertEqual(gh.prs["KyPython/tag"], []); self.assertEqual(gh.prs["KyPython/two"], [])
        self.assertIn("caller has 0 SHA pins", self.row(r.stdout, "KyPython/tag"))
        self.assertIn("caller has 2 SHA pins", self.row(r.stdout, "KyPython/two"))

    def test_GBD_3_3_failed_pr_listing_opens_no_pr(self):
        gh = FakeGitHub(self); gh.add_repo("KyPython/a", pin=OLD); gh.fail.add(("GET", "/pulls"))
        r = self.run_sweep(gh)
        self.assertEqual(gh.prs["KyPython/a"], [])
        self.assertFalse([w for w in gh.writes() if "/repos/KyPython/a/" in w[1]])
        self.assertIn("could not list pull requests", self.row(r.stdout, "KyPython/a"))

    def test_GBD_3_3_closed_bump_pr_is_not_reopened(self):
        gh = FakeGitHub(self); gh.add_repo("KyPython/a", pin=OLD)
        gh.prs["KyPython/a"].append({"head": {"ref": "ci/bump-ai-governance-ccccccc", "repo": {"full_name": "KyPython/a"}},
                                     "base": {"ref": "main"}, "state": "closed", "merged_at": None, "html_url": "u", "title": "t"})
        r = self.run_sweep(gh)
        self.assertEqual(len(gh.prs["KyPython/a"]), 1)
        self.assertIn("closed without merging; not reopened", self.row(r.stdout, "KyPython/a"))

    def test_GBD_3_3_only_same_repo_prs_into_the_default_branch_are_reused(self):
        gh = FakeGitHub(self); gh.add_repo("KyPython/a", pin=OLD)
        gh.prs["KyPython/a"] += [
            {"head": {"ref": "ci/bump-ai-governance-x", "repo": {"full_name": "someone/fork"}}, "base": {"ref": "main"},
             "state": "open", "merged_at": None, "html_url": "fork-pr", "title": "t"},
            {"head": {"ref": "ci/bump-ai-governance-y", "repo": {"full_name": "KyPython/a"}}, "base": {"ref": "release"},
             "state": "open", "merged_at": None, "html_url": "other-base", "title": "t"}]
        gh.files[("KyPython/a", "ci/bump-ai-governance-y")] = caller_text(OLD)
        self.run_sweep(gh)
        self.assertEqual(gh.files[("KyPython/a", "ci/bump-ai-governance-y")], caller_text(OLD), "a PR into another base is not touched")
        self.assertEqual(len(gh.prs["KyPython/a"]), 3)
        self.assertEqual(gh.prs["KyPython/a"][-1]["head"]["ref"], "ci/bump-ai-governance-ccccccc")

    def test_GBD_3_2_indeterminate_reads_never_trigger_opt_in_or_protection(self):
        cases = {"caller read fails": ("GET", "/contents/.github/workflows/ai-governance.yml"),
                 "protection read fails": ("GET", "/protection"),
                 "opt-in branch read fails": ("GET", "/branches/governance/enforce-ai-governance")}
        for name, marker in cases.items():
            with self.subTest(case=name):
                gh = FakeGitHub(self); gh.add_repo("KyPython/new"); gh.add_repo("KyPython/gated", pin=MAIN)
                gh.verdict["KyPython/gated"] = "success"
                gh.fail.add(marker)
                r = self.run_sweep(gh)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual(self.optin_log, "", "an indeterminate read must not open an opt-in PR or apply protection")
                for fn in ("KyPython/new", "KyPython/gated"):
                    self.assertIn("stopped before any opt-in or protection change", self.row(r.stdout, fn))

    def test_GBD_3_4_allow_list_needs_both_flags_from_the_read(self):
        gh = FakeGitHub(self); gh.add_repo("KyLamportLogic/d", pin=MAIN, selected=[])
        gh.partial_actions = True
        r = self.run_sweep(gh)
        self.assertFalse([w for w in gh.writes() if w[1].endswith("/selected-actions")])
        self.assertIn("allow-list not changed", self.row(r.stdout, "KyLamportLogic/d"))

    def test_GBD_3_1_network_errors_do_not_crash_or_write(self):
        gh = FakeGitHub(self); gh.add_repo("KyPython/a", pin=OLD)
        d = tempfile.mkdtemp(prefix="sweep-")
        self.addCleanup(lambda: subprocess.run(["rm", "-rf", d]))
        env = dict(os.environ, GITHUB_TOKEN="t", APPLY="1", DIR=d, GITHUB_API_URL="http://127.0.0.1:9",
                   SKIP_FILE="", PYTHONDONTWRITEBYTECODE="1", RUNNER_TEMP=d)
        r = subprocess.run([sys.executable, str(SWEEP)], env=env, capture_output=True, text=True, timeout=60)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("could not reach GitHub (GET /user returned HTTP 599)", r.stdout)
        self.assertIn("could not reach GitHub", Path(d, "sweep-failure").read_text())

    def test_GBD_3_1_rejected_token_fails_the_run(self):
        gh = FakeGitHub(self); gh.user_status = 401
        r = self.run_sweep(gh)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("token was rejected", r.stdout)

    def test_GBD_3_5_never_merges_deletes_changes_visibility_or_rulesets(self):
        gh = FakeGitHub(self)
        gh.add_repo("KyPython/a", pin=OLD); gh.add_repo("KyLamportLogic/d", pin=OLD, selected=[]); gh.add_repo("KyPython/new")
        self.run_sweep(gh)
        for method, path in gh.writes():
            with self.subTest(request=f"{method} {path}"):
                self.assertNotEqual(method, "DELETE")
                self.assertNotEqual(method, "PATCH")
                self.assertNotRegex(path, r"/merge$|/rulesets|/transfer")
                self.assertRegex(path, r"/git/refs$|/contents/\.github/workflows/ai-governance\.yml$|/pulls$|"
                                       r"/actions/permissions/selected-actions$")
        src = SWEEP.read_text()
        self.assertNotRegex(src, r'api\("(DELETE|PATCH)"')
        self.assertNotIn("/merge", src)
        self.assertNotIn("/rulesets", src)


class SweepWorkflow(unittest.TestCase):
    def step(self, name):
        lines = WORKFLOW.read_text().splitlines()
        start = lines.index(f"      - name: {name}")
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("      - ")), len(lines))
        block = lines[start:end]
        first = next(i for i, l in enumerate(block) if l == "        run: |") + 1
        return "\n".join(block), textwrap.dedent("\n".join(block[first:])) + "\n"

    def run_report(self, existing):
        d = Path(tempfile.mkdtemp(prefix="sweep-report-"))
        self.addCleanup(lambda: subprocess.run(["rm", "-rf", str(d)]))
        (d / "bin").mkdir()
        gh = d / "bin" / "gh"
        gh.write_text("#!" + sys.executable + "\n" + textwrap.dedent(f"""
            import json, sys
            open({str(d / 'gh.log')!r}, 'a').write(json.dumps(sys.argv[1:]) + '\\n')
            if sys.argv[1:3] == ['issue', 'list']:
                print({existing!r}, end='')
        """))
        gh.chmod(0o755)
        (d / "tmp").mkdir()
        (d / "tmp" / "sweep-failure").write_text("SWEEP_TOKEN is missing\n")
        _, script = self.step("Report a failed sweep")
        env = {"PATH": f"{d / 'bin'}:{os.defpath}", "RUNNER_TEMP": str(d / "tmp"), "GH_TOKEN": "x", "REPO": GOV,
               "RUN_URL": "https://example/run/1"}
        r = subprocess.run(["/bin/bash", "-c", script], env=env, capture_output=True, text=True, timeout=30)
        calls = [json.loads(l) for l in (d / "gh.log").read_text().splitlines()]
        return r, calls

    def test_GBD_3_1_failed_sweep_opens_one_issue(self):
        r, calls = self.run_report("")
        self.assertEqual(r.returncode, 0, r.stderr)
        create = [c for c in calls if c[:2] == ["issue", "create"]]
        self.assertEqual(len(create), 1)
        self.assertIn("Governance sweep cannot run", create[0])
        self.assertTrue(any("SWEEP_TOKEN is missing" in a for a in create[0]))

    def test_GBD_3_1_failed_sweep_updates_the_open_issue_instead_of_duplicating(self):
        r, calls = self.run_report("17")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse([c for c in calls if c[:2] == ["issue", "create"]])
        self.assertTrue([c for c in calls if c[:3] == ["issue", "comment", "17"]])

    def test_GBD_3_1_workflow_reports_on_failure_with_a_scoped_token(self):
        text = WORKFLOW.read_text()
        block, _ = self.step("Report a failed sweep")
        self.assertIn("        if: failure()", block)
        self.assertIn("GH_TOKEN: ${{ github.token }}", block)
        self.assertIn("      issues: write", text)
        self.assertNotIn("contents: write", text)
        token_step, _ = self.step("Require the sweep token")
        self.assertIn("if: env.SWEEP_TOKEN_SET != 'true'", token_step)


if __name__ == "__main__":
    unittest.main()
