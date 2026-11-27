"""Self-tests for the SAD shared harness (specs/spec-author-delegation-check, task T2).

These check the harness itself (SAD-6.1 to SAD-6.4): that it drives the real policy script, that a broken
script is caught, that base-branch fixtures and commit times are controlled, and that every scenario in
scenarios.md is mapped to exactly one implementing task. They assert no delegation behavior; the tests that
do are added by T4, T3 and T5 with the behavior that makes them pass.
Run: python3 -m unittest discover -s tests -v
"""
import re
import unittest
from datetime import datetime
from pathlib import Path

from sad_harness import (
    DELEGATE,
    DELEGATIONS_PATH,
    POLICY,
    SCENARIO_TASK,
    SadRepo,
    delegation_yaml,
)
from test_policy import KY

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = (ROOT / "specs/spec-author-delegation-check/scenarios.md").read_text()
SPEC_TEXT = "# Requirements: x\n1. X-1.1 WHEN a THEN the system SHALL b.\n"


class Harness(unittest.TestCase):
    def repo(self):
        r = SadRepo()
        self.addCleanup(r.cleanup)
        return r

    def test_SAD_6_4_every_scenario_maps_to_exactly_one_task(self):
        declared = set(re.findall(r"Scenario(?: Outline)?: ([PA]\d+) ", SCENARIOS))
        self.assertTrue(declared, "no scenarios parsed from scenarios.md")
        self.assertEqual(declared, set(SCENARIO_TASK), "scenario-to-task map drifted from scenarios.md")
        self.assertTrue(set(SCENARIO_TASK.values()) <= {"T3", "T4", "T5"})

    def test_SAD_6_1_harness_runs_the_real_policy_script(self):
        # The workflow's own role gate rejects a spec change by a non-spec-author. Seeing that message
        # proves the harness executed the real script, not a stand-in.
        r = self.repo(); r.write({"specs/x/requirements.md": SPEC_TEXT})
        code, out = r.run_policy(body="Relates to #1", title="docs(spec): x",
                                 author=("codex", "codex@openai.com"), opener="codex")
        self.assertEqual(code, 1, out)
        self.assertIn("only the spec-author role", out)

    def test_SAD_6_1_harness_passes_a_legitimate_spec_author_today(self):
        # Positive control for the harness: an enrolled spec author's spec-only PR passes the current gate.
        r = self.repo(); r.write({"specs/x/requirements.md": SPEC_TEXT})
        code, out = r.run_policy(body="Relates to #1", title="docs(spec): x", author=DELEGATE, opener=DELEGATE[0])
        self.assertEqual(code, 0, out)

    def test_SAD_6_3_a_broken_policy_script_is_detected(self):
        r = self.repo(); r.write({"specs/x/requirements.md": SPEC_TEXT})
        code, out = r.run_policy(script="def (\n" + POLICY, body="Relates to #1",
                                 title="docs(spec): x", author=DELEGATE, opener=DELEGATE[0])
        self.assertNotEqual(code, 0, out)

    def test_SAD_6_3_a_mutated_role_gate_is_visible_to_the_harness(self):
        # If the role gate's rejection were removed, the real-script check above would no longer see it.
        # This guards against a harness that passes whatever the script does.
        mutated = POLICY.replace("only the spec-author role", "role gate disabled for mutation test")
        self.assertNotEqual(mutated, POLICY, "mutation target not found in the policy script")
        r = self.repo(); r.write({"specs/x/requirements.md": SPEC_TEXT})
        _code, out = r.run_policy(script=mutated, body="Relates to #1", title="docs(spec): x",
                                 author=("codex", "codex@openai.com"), opener="codex")
        self.assertNotIn("only the spec-author role", out)
        self.assertIn("role gate disabled for mutation test", out)

    def test_SAD_6_2_base_fixture_and_commit_time_are_controlled(self):
        r = self.repo()
        when = "2026-11-01T10:00:00+00:00"
        rec = {"identity": DELEGATE[0], "repository": "KyPython/demo", "issue": 1,
               "spec_folders": ["specs/x"], "expires": "2026-12-01T00:00:00Z", "revoked": False}
        sha = r.put_on_base({DELEGATIONS_PATH: delegation_yaml([rec])}, when, KY)
        self.assertEqual(datetime.fromisoformat(r.commit_time(sha)), datetime.fromisoformat(when))
        self.assertEqual(r.base, sha)
        text = (r.dir / DELEGATIONS_PATH).read_text()
        self.assertIn("identity: delegate-bot[bot]", text)
        self.assertIn("spec_folders: [specs/x]", text)
        self.assertIn("revoked: false", text)

    def test_SAD_6_2_pr_created_at_reaches_the_policy_environment(self):
        r = self.repo(); r.write({"specs/x/requirements.md": SPEC_TEXT})
        probe = "import os, sys; sys.exit(0 if os.environ.get('PR_CREATED_AT') == '2026-11-02T00:00:00Z' else 5)"
        code, out = r.run_policy(script=probe, pr_created_at="2026-11-02T00:00:00Z")
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
