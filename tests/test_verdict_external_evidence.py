"""Verdict step: trusted exact-SHA external validation evidence.

Spec: specs/security-fail-closed (SECFC-7.1 to SECFC-7.10; SECFC-1 stays).
The real `v` step of the governance verdict job is extracted and run with a controlled environment and a stub
`gh` first on PATH that serves canned check-runs JSON. No network, no secrets.
"""
import json
import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SHA = "a" * 40
OTHER = "b" * 40
CHECK = "validate"


def verdict_script():
    doc = yaml.safe_load((ROOT / ".github/workflows/governance.yml").read_text(encoding="utf-8"))
    for step in doc["jobs"]["verdict"]["steps"]:
        if step.get("id") == "v":
            return step["run"]
    raise AssertionError("verdict step (id: v) not found")


def run_obj(name=CHECK, sha=SHA, status="completed", conclusion="success", app="github-actions", completed="2026-11-25T10:00:00Z"):
    return {"name": name, "head_sha": sha, "status": status, "conclusion": conclusion,
            "app": {"slug": app}, "completed_at": completed}


class Verdict(unittest.TestCase):
    def run_v(self, runs=None, gh_exit=0, raw=None, **env):
        """Run the verdict step. `runs` is the check_runs list the stub gh returns."""
        tmp = tempfile.mkdtemp()
        bindir = Path(tmp, "bin")
        bindir.mkdir()
        body = raw if raw is not None else json.dumps({"total_count": len(runs or []), "check_runs": runs or []})
        Path(tmp, "api.json").write_text(body, encoding="utf-8")
        gh = bindir / "gh"
        gh.write_text(textwrap.dedent(f"""\
            #!/bin/sh
            echo "$@" >> "{tmp}/gh-calls"
            [ "{gh_exit}" = 0 ] || {{ echo "gh: stub failure" >&2; exit {gh_exit}; }}
            cat "{tmp}/api.json"
            """), encoding="utf-8")
        gh.chmod(0o755)
        script = Path(tmp, "v.sh")
        script.write_text(verdict_script(), encoding="utf-8")
        out, summary = Path(tmp, "out"), Path(tmp, "summary")
        out.touch()
        summary.touch()
        base = {
            "PATH": f"{bindir}:{os.environ['PATH']}", "GITHUB_OUTPUT": str(out), "GITHUB_STEP_SUMMARY": str(summary),
            "QUALITY": "skipped", "POLICY": "success", "SECRETS": "success", "SECURITY": "success",
            "RUN_QUALITY": "false", "SYSTEM_QUALITY_DEFINITION": "", "PREREQUISITE_RESULT": "success",
            "PREREQUISITE_CHECK": CHECK, "HEAD_SHA": SHA, "GITHUB_REPOSITORY": "KyPython/example",
            "GH_TOKEN": "stub", "EVENT_NAME": "pull_request", "COMPLETION_MODE": "advisory",
        }
        base.update(env)
        base = {k: v for k, v in base.items() if v is not None}
        r = subprocess.run(["bash", str(script)], env=base, capture_output=True, text=True, timeout=60)
        verdict = next((l.split("=", 1)[1] for l in out.read_text().splitlines() if l.startswith("verdict=")), None)
        calls = Path(tmp, "gh-calls").read_text() if Path(tmp, "gh-calls").exists() else ""
        return r, verdict, calls

    def assertPass(self, *a, **k):
        r, verdict, _ = self.run_v(*a, **k)
        self.assertEqual((r.returncode, verdict), (0, "pass"), r.stdout + r.stderr)

    def assertFail(self, *a, **k):
        r, verdict, calls = self.run_v(*a, **k)
        self.assertEqual((r.returncode, verdict), (1, "fail"), r.stdout + r.stderr)
        return r, calls

    # SECFC-7.1, 7.3, 7.4: the good case needs evidence from the API
    def test_SECFC_7_4_matching_successful_run_passes(self):
        self.assertPass([run_obj()])

    def test_SECFC_7_3_api_is_queried_for_the_head_sha(self):
        _, _, calls = self.run_v([run_obj()])
        self.assertIn(f"commits/{SHA}/check-runs", calls)

    # SECFC-7.10 negative cases
    def test_SECFC_7_1_hardcoded_success_with_validation_absent_fails(self):
        self.assertFail([])

    def test_SECFC_7_1_hardcoded_success_with_validation_skipped_fails(self):
        self.assertFail([run_obj(conclusion="skipped")])

    def test_SECFC_7_10_skipped_native_needs_result_fails(self):
        self.assertFail([run_obj()], PREREQUISITE_RESULT="skipped")

    def test_SECFC_7_10_empty_prerequisite_result_fails(self):
        self.assertFail([run_obj()], PREREQUISITE_RESULT="")

    def test_SECFC_7_3_stale_sha_fails(self):
        self.assertFail([run_obj(sha=OTHER)])

    def test_SECFC_7_4_failed_evidence_fails(self):
        self.assertFail([run_obj(conclusion="failure")])

    def test_SECFC_7_4_neutral_cancelled_timed_out_fail(self):
        for c in ("neutral", "cancelled", "timed_out", None, ""):
            with self.subTest(conclusion=c):
                self.assertFail([run_obj(conclusion=c)])

    def test_SECFC_7_4_not_completed_fails(self):
        for s in ("queued", "in_progress"):
            with self.subTest(status=s):
                self.assertFail([run_obj(status=s, conclusion=None)])

    def test_SECFC_7_4_other_app_fails(self):
        self.assertFail([run_obj(app="some-other-app")])

    def test_SECFC_7_4_other_check_name_fails(self):
        self.assertFail([run_obj(name="lint")])

    def test_SECFC_7_4_latest_run_wins_and_a_later_failure_fails(self):
        self.assertFail([run_obj(completed="2026-11-25T10:00:00Z"), run_obj(conclusion="failure", completed="2026-11-25T11:00:00Z")])

    def test_SECFC_7_4_a_rerun_that_succeeds_after_a_failure_passes(self):
        self.assertPass([run_obj(conclusion="failure", completed="2026-11-25T10:00:00Z"), run_obj(completed="2026-11-25T11:00:00Z")])

    def test_SECFC_7_4_tied_latest_runs_with_different_outcomes_fail(self):
        self.assertFail([run_obj(), run_obj(conclusion="failure")])

    def test_SECFC_7_5_api_error_fails(self):
        self.assertFail([run_obj()], gh_exit=1)

    def test_SECFC_7_5_unparseable_body_fails(self):
        self.assertFail(raw="not json")

    def test_SECFC_7_5_incomplete_page_set_fails(self):
        self.assertFail(raw=json.dumps({"total_count": 5, "check_runs": [run_obj()]}))

    def test_SECFC_7_5_paginated_output_is_read_across_pages(self):
        pages = json.dumps({"total_count": 2, "check_runs": [run_obj(name="lint")]}) + json.dumps(
            {"total_count": 2, "check_runs": [run_obj()]})
        self.assertPass(raw=pages)

    def test_SECFC_7_2_empty_check_name_fails(self):
        self.assertFail([run_obj()], PREREQUISITE_CHECK="")

    def test_SECFC_7_6_verdict_cannot_name_itself(self):
        self.assertFail([run_obj(name="ai-governance / verdict")], PREREQUISITE_CHECK="ai-governance / verdict")

    def test_SECFC_7_3_missing_or_malformed_head_sha_fails_without_an_api_call(self):
        for sha in ("", "main", "../x", SHA + "/../../x", "A" * 40, "a" * 39):
            with self.subTest(sha=sha):
                _, calls = self.assertFail([run_obj()], HEAD_SHA=sha)
                self.assertEqual(calls, "")

    def test_SECFC_7_10_failed_security_fails_despite_good_evidence(self):
        self.assertFail([run_obj()], SECURITY="failure")

    def test_SECFC_7_10_failed_policy_secrets_or_quality_fail_despite_good_evidence(self):
        for name in ("POLICY", "SECRETS", "QUALITY"):
            with self.subTest(name=name):
                self.assertFail([run_obj()], **{name: "failure"})

    # SECFC-7.7: run-quality true is unchanged and needs no API evidence
    def test_SECFC_7_7_run_quality_true_needs_no_api_evidence(self):
        self.assertPass([], RUN_QUALITY="true", QUALITY="success", PREREQUISITE_RESULT="", PREREQUISITE_CHECK="", HEAD_SHA="")

    def test_SECFC_7_7_run_quality_true_still_rejects_a_bad_prerequisite_result(self):
        self.assertFail([], RUN_QUALITY="true", QUALITY="success", PREREQUISITE_RESULT="skipped")

    # SECFC-7.8, 7.9
    def test_SECFC_7_8_verdict_job_requests_only_checks_read(self):
        doc = yaml.safe_load((ROOT / ".github/workflows/governance.yml").read_text(encoding="utf-8"))
        self.assertEqual(doc["jobs"]["verdict"]["permissions"], {"checks": "read"})

    def test_SECFC_7_2_input_prerequisite_check_exists_with_empty_default(self):
        doc = yaml.safe_load((ROOT / ".github/workflows/governance.yml").read_text(encoding="utf-8"))
        spec = doc[True]["workflow_call"]["inputs"]["prerequisite-check"]
        self.assertEqual((spec["type"], spec.get("default")), ("string", ""))

    def test_SECFC_7_8_in_repo_caller_and_template_grant_checks_read(self):
        for rel in (".github/workflows/self-test.yml", "templates/ai-governance.yml"):
            with self.subTest(caller=rel):
                doc = yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))
                self.assertEqual(doc["jobs"]["ai-governance"].get("permissions"), {"contents": "read", "checks": "read"})

    def test_SECFC_7_9_verdict_step_is_valid_shell(self):
        r = subprocess.run(["bash", "-n"], input=verdict_script() + "\n", capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
