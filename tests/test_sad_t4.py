"""SAD task T4: delegation file, standing designations and the owner-only rule.

Spec: specs/spec-author-delegation-check (scenarios A7, A10, P3; criteria SAD-1.4, SAD-1.5, SAD-2.2,
SAD-2.4, SAD-3.1, SAD-5.2). Every test runs the real policy script from .github/workflows/governance.yml
through tests/sad_harness.py. Record matching against a pull request (NO_DELEGATION and the other reasons)
is task T3 and is not tested here.
Run: python3 -m unittest discover -s tests -v
"""
import unittest
from pathlib import Path

from sad_harness import (
    DELEGATE,
    DELEGATIONS_PATH,
    ROLES_WITH_DELEGATE,
    SadRepo,
    delegation_yaml,
)
from test_policy import KIRO, KY

ROOT = Path(__file__).resolve().parents[1]
SPEC_TEXT = "# Requirements: x\n1. X-1.1 WHEN a THEN the system SHALL b.\n"
GOV = "KyPython/ai-governance"
VALID = {"identity": DELEGATE[0], "repository": "KyPython/demo", "issue": 1, "spec_folders": ["specs/x"],
         "issued": "2026-11-01T00:00:00Z", "expires": "2026-11-30T00:00:00Z", "revoked": False}
CODER = ("cursor[bot]", "206951365+cursor[bot]@users.noreply.github.com")


class Base(unittest.TestCase):
    def repo(self, roles=ROLES_WITH_DELEGATE):
        r = SadRepo(roles=roles)
        self.addCleanup(r.cleanup)
        return r

    def spec_pr(self, r, author, **kw):
        r.write({"specs/x/requirements.md": SPEC_TEXT})
        return r.run_policy(body="Relates to #1", title="docs(spec): x", author=author, opener=author[0], **kw)


class A7UnreadableDelegationFile(Base):
    """A7: an unreadable delegation file fails closed for a delegation-required identity (SAD-3.1)."""

    def _expect_unreadable(self, r, **kw):
        code, out = self.spec_pr(r, DELEGATE, **kw)
        self.assertEqual(code, 1, out)
        self.assertIn("DELEGATION_UNREADABLE", out)
        self.assertIn(DELEGATE[0], out)
        self.assertIn("specs/x", out)

    def test_SAD_3_1_missing_delegation_file_fails_closed(self):
        r = self.repo()
        self._expect_unreadable(r, delegations=r.dir / "no-such-delegations.yml")

    def test_SAD_3_1_invalid_yaml_fails_closed(self):
        r = self.repo(); r.sad_delegations.write_text("version: 1\ndelegations\n  : [\n")
        self._expect_unreadable(r)

    def test_SAD_3_1_SAD_2_2_record_missing_a_required_field_fails_closed(self):
        for field in ("identity", "repository", "issue", "spec_folders", "issued", "expires", "revoked"):
            with self.subTest(missing=field):
                r = self.repo()
                rec = {k: v for k, v in VALID.items() if k != field}
                r.sad_delegations.write_text(delegation_yaml([rec]))
                self._expect_unreadable(r)

    def test_SAD_2_2_SAD_2_6_lifetime_over_30_days_fails_closed(self):
        # Decision D4 on #238: maximum delegation lifetime 30 days.
        r = self.repo(); r.sad_delegations.write_text(delegation_yaml([dict(VALID, expires="2026-12-15T00:00:00Z")]))
        self._expect_unreadable(r)

    def test_SAD_5_5_wildcard_identity_in_a_record_fails_closed(self):
        r = self.repo(); r.sad_delegations.write_text(delegation_yaml([dict(VALID, identity="*")]))
        self._expect_unreadable(r)

    def test_SAD_3_1_unreadable_file_does_not_block_a_standing_author(self):
        # Positive control: standing identities never consult the delegation file.
        r = self.repo()
        code, out = self.spec_pr(r, KIRO, delegations=r.dir / "no-such-delegations.yml")
        self.assertEqual(code, 0, out)
        self.assertNotIn("DELEGATION_UNREADABLE", out)


class P3StandingDesignations(Base):
    """P3: identities listed as spec authors when the check ships are recorded explicitly as standing."""

    def test_SAD_5_2_repository_role_map_records_kiro_and_owner_as_standing(self):
        text = (ROOT / "roles.yml").read_text()
        section = text.split("  spec-author:", 1)[1].split("\n  coder:", 1)[0]
        self.assertIn("    standing:", section, "roles.yml spec-author has no explicit standing list")
        standing = section.split("    standing:", 1)[1]
        self.assertIn("- kiro-agent[bot]", standing)
        self.assertIn("- KyPython", standing)

    def test_SAD_1_2_SAD_5_2_standing_kiro_spec_pr_passes_with_no_delegation(self):
        r = self.repo()
        code, out = self.spec_pr(r, KIRO)
        self.assertEqual(code, 0, out)
        self.assertIn("standing", out)

    def test_SAD_1_4_undesignated_identity_is_delegation_required(self):
        # DELEGATE is a spec author with no standing designation, so an unreadable file must stop it.
        r = self.repo()
        code, out = self.spec_pr(r, DELEGATE, delegations=r.dir / "missing.yml")
        self.assertEqual(code, 1, out)
        self.assertIn("DELEGATION_UNREADABLE", out)

    def test_SAD_1_5_standing_identity_not_enrolled_fails_role_map_closed(self):
        roles = ROLES_WITH_DELEGATE.replace("    standing:\n      - KyPython\n",
                                            "    standing:\n      - KyPython\n      - stranger[bot]\n")
        r = self.repo(roles=roles)
        code, out = self.spec_pr(r, KIRO)
        self.assertEqual(code, 1, out)
        self.assertIn("standing", out)
        self.assertIn("stranger[bot]", out)


class A10OwnerOnlyDelegationFile(Base):
    """A10: only the owner may change the delegation file or the role map (SAD-2.4)."""

    def _change(self, files, author):
        r = self.repo(); r.write(files)
        return r.run_policy(body="Relates to #238\n\nSpec: specs/spec-author-delegation-check", repo=GOV,
                            title="chore(governance): change", author=author, opener=author[0])

    def test_SAD_2_4_delegation_file_change_by_non_owner_fails(self):
        for actor in (DELEGATE, CODER, ("someone", "someone@example.com")):
            with self.subTest(actor=actor[0]):
                code, out = self._change({DELEGATIONS_PATH: delegation_yaml([VALID])}, actor)
                self.assertEqual(code, 1, out)
                self.assertIn("delegations.yml may only be changed by the owner", out)

    def test_SAD_2_4_delegation_file_change_by_owner_passes(self):
        code, out = self._change({DELEGATIONS_PATH: delegation_yaml([VALID])}, KY)
        self.assertEqual(code, 0, out)
        self.assertIn("delegations.yml changed by the owner identity only", out)

    def test_SAD_2_4_role_map_change_by_coder_still_fails(self):
        code, out = self._change({"roles.yml": ROLES_WITH_DELEGATE}, CODER)
        self.assertEqual(code, 1, out)
        self.assertIn("roles.yml may only be changed by the owner", out)

    def test_SAD_2_2_owner_cannot_merge_a_malformed_delegation_file(self):
        bad = delegation_yaml([{k: v for k, v in VALID.items() if k != "expires"}])
        code, out = self._change({DELEGATIONS_PATH: bad}, KY)
        self.assertEqual(code, 1, out)
        self.assertIn("delegations.yml is invalid", out)


if __name__ == "__main__":
    unittest.main()
