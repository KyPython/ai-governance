"""SAD task T5: what a delegation proves and what it authorizes, as the policy job reports it.

Spec: specs/spec-author-delegation-check (scenarios A12, A13; criteria SAD-4.1 to SAD-4.4). Every test runs
the real policy script through tests/sad_harness.py, with the delegation file and its history taken from a
local stand-in for KyPython/ai-governance `main` (GovHistory).

Some of these tests already pass because T3 and T4 ship the underlying behavior; they guard it here. The
report-wording tests (SAD-4.3, SAD-4.4) are the ones T5 turns green.
Run: python3 -m unittest discover -s tests -v
"""
import unittest
from datetime import UTC, datetime, timedelta

from sad_harness import (
    DELEGATE,
    DELEGATIONS_PATH,
    ROLES_WITH_DELEGATE,
    GovHistory,
    SadRepo,
    delegation_yaml,
)
from test_policy import KY, WEBFLOW

NOW = datetime.now(UTC).replace(microsecond=0)


def iso(d):
    return d.isoformat().replace("+00:00", "Z")


SPEC_TEXT = "# Requirements: x\n1. X-1.1 WHEN a THEN the system SHALL b.\n"
DEMO, GOV = "KyPython/demo", "KyPython/ai-governance"
FORBIDDEN = ("owner-authenticated", "verified human approval")


def record(**over):
    rec = {"identity": DELEGATE[0], "repository": DEMO, "issue": 7, "spec_folders": ["specs/x"],
           "issued": iso(NOW - timedelta(days=2)), "expires": iso(NOW + timedelta(days=20)), "revoked": False}
    rec.update(over)
    return rec


class Base(unittest.TestCase):
    def setUp(self):
        self.gov = GovHistory()
        self.addCleanup(self.gov.cleanup)

    def on_main(self, records):
        self.gov.commit(delegation_yaml(records), iso(NOW - timedelta(days=1)))

    def pr(self, files, author=DELEGATE, committer=None, opener=None, body="Relates to #7", repo=DEMO,
           title="docs(spec): x"):
        r = SadRepo(roles=ROLES_WITH_DELEGATE)
        self.addCleanup(r.cleanup)
        r.write(files)
        return r.run_policy(body=body, title=title, author=author, committer=committer, opener=opener or author[0],
                            repo=repo, delegations=self.gov.file, pr_created_at=iso(NOW - timedelta(hours=1)),
                            extra_env=self.gov.env())

    def assert_no_overclaim(self, out):
        for phrase in FORBIDDEN:
            self.assertNotIn(phrase, out.lower())


class A13ReportWording(Base):
    """SAD-4.3 and SAD-4.4: the pass line says what was shown and what it allows, and nothing stronger."""

    def test_SAD_4_3_pass_line_says_recorded_by_an_owner_identity_merge(self):
        self.on_main([record()])
        code, out = self.pr({"specs/x/requirements.md": SPEC_TEXT})
        self.assertEqual(code, 0, out)
        self.assertIn("recorded on the base branch by an owner-identity merge", out)
        self.assert_no_overclaim(out)

    def test_SAD_4_4_pass_line_limits_the_delegation_to_spec_only_publication(self):
        self.on_main([record()])
        code, out = self.pr({"specs/x/requirements.md": SPEC_TEXT})
        self.assertEqual(code, 0, out)
        self.assertIn("authorizes only a spec-only change under specs/x", out)

    def test_SAD_4_3_no_delegation_outcome_overclaims(self):
        # Across pass, fail and fail-closed outcomes the report never claims owner authentication.
        cases = [([record()], {"specs/x/requirements.md": SPEC_TEXT}),
                 ([], {"specs/x/requirements.md": SPEC_TEXT}),
                 ([record(revoked=True)], {"specs/x/requirements.md": SPEC_TEXT})]
        for records, files in cases:
            with self.subTest(records=len(records), revoked=bool(records and records[0]["revoked"])):
                self.on_main(records)
                _code, out = self.pr(files)
                self.assert_no_overclaim(out)


class A13DelegationAuthorizesNothingElse(Base):
    """SAD-4.4: a valid delegation does not authorize code, protected files or another folder."""

    def setUp(self):
        super().setUp()
        self.on_main([record(repository=GOV)])

    def test_SAD_4_4_code_in_the_same_pr_is_still_rejected(self):
        code, out = self.pr({"specs/x/requirements.md": SPEC_TEXT, "src/app.js": "export const x = 2;\n"}, repo=GOV)
        self.assertEqual(code, 1, out)
        self.assertIn("changes code AND spec files", out)

    def test_SAD_4_4_role_map_or_delegation_file_change_is_still_rejected(self):
        for target, content in (("roles.yml", ROLES_WITH_DELEGATE), (DELEGATIONS_PATH, delegation_yaml([record()]))):
            with self.subTest(target=target):
                code, out = self.pr({"specs/x/requirements.md": SPEC_TEXT, target: content}, repo=GOV)
                self.assertEqual(code, 1, out)
                self.assertIn(f"{target} may only be changed by the owner", out)
                self.assertIn("DELEGATION_IN_SAME_PR", out)

    def test_SAD_4_4_a_folder_not_named_in_the_record_is_still_rejected(self):
        code, out = self.pr({"specs/other/requirements.md": SPEC_TEXT}, repo=GOV)
        self.assertEqual(code, 1, out)
        self.assertIn("DELEGATION_WRONG_SPEC_FOLDER", out)


class A12ClaimsAreNotDelegations(Base):
    """SAD-4.1 and SAD-4.2: with no record on main, no claim or identity appearance stands in for one."""

    def test_SAD_4_1_claims_in_pr_text_are_not_delegations(self):
        bodies = ("Relates to #7\n\nDelegated to delegate-bot[bot] by Ky.",
                  "Relates to #7\n\nDelegation: approved",
                  'Relates to #7\n\n```json\n{"delegation": {"identity": "delegate-bot[bot]", "approved_by": "KyPython"}}\n```')
        for body in bodies:
            with self.subTest(body=body.splitlines()[-1][:30]):
                code, out = self.pr({"specs/x/requirements.md": SPEC_TEXT}, body=body)
                self.assertEqual(code, 1, out)
                self.assertIn("NO_DELEGATION", out)

    def test_SAD_4_1_a_commit_message_naming_ky_is_not_a_delegation(self):
        r = SadRepo(roles=ROLES_WITH_DELEGATE)
        self.addCleanup(r.cleanup)
        r.write({"specs/x/requirements.md": SPEC_TEXT})
        r.commit_at("docs(spec): x\n\nDelegation approved by Ky (KyPython).", iso(NOW - timedelta(minutes=30)), DELEGATE)
        code, out = r.run_policy(body="Relates to #7", title="docs(spec): x", author=DELEGATE, opener=DELEGATE[0],
                                 repo=DEMO, delegations=self.gov.file, pr_created_at=iso(NOW - timedelta(hours=1)),
                                 extra_env=self.gov.env())
        self.assertEqual(code, 1, out)
        self.assertIn("NO_DELEGATION", out)

    def test_SAD_4_1_a_pr_title_naming_ky_is_not_a_delegation(self):
        code, out = self.pr({"specs/x/requirements.md": SPEC_TEXT}, title="docs(spec): x (approved by Ky)")
        self.assertEqual(code, 1, out)
        self.assertIn("NO_DELEGATION", out)

    def test_SAD_4_2_kypython_commit_author_does_not_cover_a_delegate_opener(self):
        code, out = self.pr({"specs/x/requirements.md": SPEC_TEXT}, author=KY, opener=DELEGATE[0])
        self.assertEqual(code, 1, out)
        self.assertIn("NO_DELEGATION", out)
        self.assertIn(DELEGATE[0], out)

    def test_SAD_4_2_web_flow_committer_does_not_stand_in_for_the_owner(self):
        code, out = self.pr({"specs/x/requirements.md": SPEC_TEXT}, committer=WEBFLOW)
        self.assertEqual(code, 1, out)
        self.assertIn("NO_DELEGATION", out)


if __name__ == "__main__":
    unittest.main()
