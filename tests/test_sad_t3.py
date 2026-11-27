"""SAD task T3: the policy job matches delegation records to the pull request.

Spec: specs/spec-author-delegation-check (scenarios P1, P2, A1 to A6, A8, A9, A11, A14, A15; criteria SAD-1.1,
SAD-1.3, SAD-2.1, SAD-2.3, SAD-2.5, SAD-3.2 to SAD-3.4, SAD-5.1, SAD-5.5). Every test runs the real policy
script through tests/sad_harness.py. The delegation file and its first-parent history come from a local
stand-in for KyPython/ai-governance `main` (GovHistory), never from the pull request head.
Report wording beyond SAD-3.4 (SAD-4.3) and claims of other powers (A12, A13) are task T5.
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
from test_policy import KIRO, KY

NOW = datetime.now(UTC).replace(microsecond=0)
def iso(d):
    return d.isoformat().replace("+00:00", "Z")

SPEC_TEXT = "# Requirements: x\n1. X-1.1 WHEN a THEN the system SHALL b.\n"
DEMO, GOV = "KyPython/demo", "KyPython/ai-governance"
OTHER = ("other-bot[bot]", "998+other-bot[bot]@users.noreply.github.com")
ROLES_TWO_DELEGATES = ROLES_WITH_DELEGATE.replace("      - delegate-bot[bot]\n", "      - delegate-bot[bot]\n      - other-bot[bot]\n", 1)
INTRO = iso(NOW - timedelta(days=1))        # record reaches main
PR_OPENED = iso(NOW - timedelta(hours=1))   # after INTRO


def record(**over):
    rec = {"identity": DELEGATE[0], "repository": DEMO, "issue": 7, "spec_folders": ["specs/x"],
           "issued": iso(NOW - timedelta(days=2)), "expires": iso(NOW + timedelta(days=20)), "revoked": False}
    rec.update(over)
    return rec


class Base(unittest.TestCase):
    def setUp(self):
        self.gov = GovHistory()
        self.addCleanup(self.gov.cleanup)

    def on_main(self, records, when=INTRO):
        self.gov.commit(delegation_yaml(records), when)

    def spec_pr(self, author=DELEGATE, folders=("specs/x",), body="Relates to #7", repo=DEMO, roles=ROLES_WITH_DELEGATE,
                extra_files=None, created=PR_OPENED, env=None):
        r = SadRepo(roles=roles)
        self.addCleanup(r.cleanup)
        r.write({f"{f}/requirements.md": SPEC_TEXT for f in folders})
        r.write(extra_files or {})
        extra = self.gov.env() if env is None else env
        return r.run_policy(body=body, title="docs(spec): x", author=author, opener=author[0], repo=repo,
                            delegations=self.gov.file, pr_created_at=created, extra_env=extra)

    def assert_fails(self, result, reason, folder="specs/x", identity=DELEGATE[0]):
        code, out = result
        self.assertEqual(code, 1, out)
        self.assertIn(reason, out)
        self.assertIn(identity, out)
        self.assertIn(folder, out)


class Positive(Base):
    def test_SAD_1_1_SAD_3_4_P1_valid_delegation_on_main_allows_spec_only_pr(self):
        self.on_main([record()])
        code, out = self.spec_pr()
        self.assertEqual(code, 0, out)
        self.assertIn("matched on the base branch", out)
        self.assertIn("self-declared, not verified", out)

    def test_SAD_5_1_P2_standing_author_needs_no_delegation(self):
        code, out = self.spec_pr(author=KIRO)
        self.assertEqual(code, 0, out)
        self.assertNotIn("NO_DELEGATION", out)

    def test_SAD_1_3_one_record_may_cover_several_folders(self):
        self.on_main([record(spec_folders=["specs/x", "specs/y"])])
        code, out = self.spec_pr(folders=("specs/x", "specs/y"))
        self.assertEqual(code, 0, out)


class Adverse(Base):
    def test_SAD_1_1_A1_no_delegation(self):
        self.assert_fails(self.spec_pr(), "NO_DELEGATION")

    def test_SAD_2_3_A2_expired_delegation(self):
        self.on_main([record(issued=iso(NOW - timedelta(days=40)), expires=iso(NOW - timedelta(days=12)))],
                     when=iso(NOW - timedelta(days=39)))
        self.assert_fails(self.spec_pr(), "DELEGATION_EXPIRED")

    def test_SAD_2_3_A3_revoked_delegation(self):
        self.on_main([record(revoked=True)])
        self.assert_fails(self.spec_pr(), "DELEGATION_REVOKED")

    def test_SAD_2_3_A4_wrong_repository(self):
        self.on_main([record(repository="KyPython/elsewhere")])
        self.assert_fails(self.spec_pr(), "DELEGATION_WRONG_REPOSITORY")

    def test_SAD_2_3_A4_wrong_issue(self):
        self.on_main([record(issue=8)])
        self.assert_fails(self.spec_pr(), "DELEGATION_WRONG_ISSUE")

    def test_SAD_2_3_A4_wrong_spec_folder(self):
        self.on_main([record(spec_folders=["specs/a"])])
        self.assert_fails(self.spec_pr(), "DELEGATION_WRONG_SPEC_FOLDER")

    def test_SAD_2_3_A5_delegation_belongs_to_another_identity(self):
        self.on_main([record(identity=OTHER[0])])
        self.assert_fails(self.spec_pr(roles=ROLES_TWO_DELEGATES), "DELEGATION_WRONG_IDENTITY")

    def test_SAD_2_5_A6_delegation_added_in_the_same_pr(self):
        files = {DELEGATIONS_PATH: delegation_yaml([record(repository=GOV, issue=7)])}
        self.assert_fails(self.spec_pr(repo=GOV, extra_files=files), "DELEGATION_IN_SAME_PR")

    def test_SAD_2_5_A6_role_map_changed_in_the_same_pr(self):
        self.assert_fails(self.spec_pr(repo=GOV, extra_files={"roles.yml": ROLES_WITH_DELEGATE}), "DELEGATION_IN_SAME_PR")

    def test_SAD_2_5_A6_owner_also_cannot_mix_role_map_and_spec_changes(self):
        code, out = self.spec_pr(author=KY, repo=GOV, extra_files={"roles.yml": ROLES_WITH_DELEGATE})
        self.assertEqual(code, 1, out)
        self.assertIn("DELEGATION_IN_SAME_PR", out)

    def test_SAD_1_1_A8_undesignated_identity_without_delegation(self):
        code, out = self.spec_pr()
        self.assertEqual(code, 1, out)
        self.assertTrue("NO_DELEGATION" in out or "UNDESIGNATED_IDENTITY" in out, out)

    def test_SAD_1_3_A9_one_delegation_does_not_cover_a_second_folder(self):
        # scenarios.md A9 names NO_DELEGATION; A4 names DELEGATION_WRONG_SPEC_FOLDER for a record on another
        # folder. Both describe the same uncovered folder, so either reason is accepted; it must name F2.
        self.on_main([record(spec_folders=["specs/x"])])
        code, out = self.spec_pr(folders=("specs/x", "specs/y"))
        self.assertEqual(code, 1, out)
        self.assertTrue("NO_DELEGATION" in out or "DELEGATION_WRONG_SPEC_FOLDER" in out, out)
        self.assertIn("specs/y", out)

    def test_SAD_3_3_A11_missing_pr_creation_time_is_not_a_pass(self):
        self.on_main([record()])
        code, out = self.spec_pr(created="")
        self.assertEqual(code, 1, out)
        self.assertIn("delegation check did not pass", out)

    def test_SAD_3_3_A11_unavailable_history_is_not_a_pass(self):
        self.on_main([record()])
        code, out = self.spec_pr(env={"DELEGATIONS_GIT": str(self.gov.dir / "no-such-repo")})
        self.assertEqual(code, 1, out)
        self.assertIn("delegation check did not pass", out)

    def test_SAD_5_5_A14_wildcard_identity_in_role_map_fails_closed(self):
        roles = ROLES_WITH_DELEGATE.replace("      - delegate-bot[bot]\n", "      - delegate-*\n", 1)
        code, out = self.spec_pr(author=KIRO, roles=roles)
        self.assertEqual(code, 1, out)
        self.assertIn("pattern", out)

    def test_SAD_2_5_A15_delegation_merged_after_the_pr_opened(self):
        self.on_main([record()], when=iso(NOW - timedelta(minutes=30)))
        self.assert_fails(self.spec_pr(created=iso(NOW - timedelta(hours=2))), "DELEGATION_AFTER_PR_OPENED")

    def test_SAD_2_5_A15_re_added_record_counts_from_its_latest_introduction(self):
        self.on_main([record()], when=iso(NOW - timedelta(days=3)))
        self.on_main([], when=iso(NOW - timedelta(days=2)))
        self.on_main([record()], when=iso(NOW - timedelta(minutes=30)))
        self.assert_fails(self.spec_pr(created=iso(NOW - timedelta(hours=2))), "DELEGATION_AFTER_PR_OPENED")


class NegativeControls(Base):
    """Implementations that would pass the suite by accident must fail here."""

    def test_SAD_2_1_record_in_pr_head_is_ignored(self):
        files = {DELEGATIONS_PATH: delegation_yaml([record()])}
        self.assert_fails(self.spec_pr(extra_files=files), "NO_DELEGATION")

    def test_SAD_2_1_pr_body_claim_is_not_a_delegation(self):
        self.assert_fails(self.spec_pr(body="Relates to #7\n\nDelegation: approved by Ky"), "NO_DELEGATION")

    def test_SAD_2_3_issue_must_come_from_the_pr_body_reference(self):
        self.on_main([record()])
        self.assert_fails(self.spec_pr(body="Relates to #8"), "DELEGATION_WRONG_ISSUE")


if __name__ == "__main__":
    unittest.main()
