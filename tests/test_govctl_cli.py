"""Tests for the owner console CLI (AIV Task T6).

Verifies criteria:
- AIV-6.1: The system SHALL provide a local CLI tool (``govctl``)
  requiring $0 external infrastructure.
- AIV-6.2: WHEN ``govctl grants list`` is executed THEN the CLI SHALL
  display all active grants, their bound ``agent_id``, ``task_id``,
  scopes, and remaining TTL.
- AIV-6.3: WHEN ``govctl revoke --all`` or ``govctl revoke <grant_id>``
  is executed THEN the CLI SHALL immediately invalidate the designated
  grants in the local broker.
- AIV-3.4: A missing or unparseable configuration fails closed.

Tests use a temporary directory for the audit log and the revocation
list, never the real ``logs/`` path. The broker fixture mirrors the
pilot pair in ``registry/agents.json`` (same fixture as
tests/test_vault_broker.py and tests/test_stray_trapping.py). CLI
functions are called directly (import + call); ``main()`` is exercised
with an argv list and captured stdout/stderr, not only via subprocess.
"""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_vault.audit import AuditLog, record_grant_issued
from agent_vault.broker import VaultBroker
from agent_vault.cli import (
    CliError,
    build_parser,
    format_grants,
    list_active_grants,
    main,
    revoke_all_grants,
    revoke_grant_by_id,
)
from agent_vault.stray import RevocationList
from agent_vault.token import generate_keypair

# Fixed reference time used across tests (2026-11-06T21:20:00Z). Same value
# as tests/test_token_verifier.py, tests/test_vault_broker.py, and
# tests/test_stray_trapping.py.
NOW = 1794000000

#: Fixture registry mirroring the pilot pair in registry/agents.json.
FIXTURE_REGISTRY = {
    "version": 1,
    "agents": [
        {
            "agent_id": "antigravity",
            "role": "author",
            "public_key": "01e9316a3561b13c7cb9d41b9d0bde54096b24fb7a4601494ad2029a0a020c63",
            "permitted_capabilities": ["repo:read", "repo:write", "subprocess:exec"],
        },
        {
            "agent_id": "kiro",
            "role": "reviewer",
            "public_key": "a57ea153373f6c700fbb89121b42083352bb79abf260ff9a7f036523494db3a4",
            "permitted_capabilities": [
                "repo:read",
                "spec:read",
                "spec:write",
                "subprocess:exec",
            ],
        },
    ],
}

#: Fixture scope contract permitting every pilot capability.
FULL_CONTRACT = {
    "permitted_scopes": [
        "repo:read",
        "repo:write",
        "subprocess:exec",
        "spec:read",
        "spec:write",
    ]
}


class GovctlCliTestCase(unittest.TestCase):
    """Shared fixture: a broker, a temp audit log, a temp revocation list."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.audit_path = self.dir / "vault-audit.jsonl"
        self.revocation_path = self.dir / "vault-revoked.json"
        self.audit_log = AuditLog(self.audit_path)
        self.revocation_list = RevocationList(self.revocation_path)
        private_key, _public_key = generate_keypair()
        self.broker = VaultBroker(
            private_key,
            registry_data=FIXTURE_REGISTRY,
            scope_contract=FULL_CONTRACT,
        )

    def _issue(self, agent_id, task_id, scopes, jti, ttl_seconds=900,
               now=NOW):
        """Issue a grant through the broker and log it (AIV-3.3)."""
        grant = self.broker.request_grant(
            agent_id,
            task_id,
            scopes,
            approver="ky",
            ttl_seconds=ttl_seconds,
            now=now,
            jti=jti,
        )
        record_grant_issued(self.audit_log, grant, now=now)
        return grant

    def _issue_live(self, agent_id, task_id, scopes, jti,
                    ttl_seconds=900):
        """Issue a grant at the real current time.

        Used for tests that exercise ``main()``: the CLI uses real time
        when listing, so a grant issued at the fixed test ``NOW``
        (2026-11-06) would already be expired. A live grant is active
        for its TTL from the moment it is issued.
        """
        import time

        return self._issue(
            agent_id, task_id, scopes, jti,
            ttl_seconds=ttl_seconds, now=int(time.time()),
        )

    def _fresh_revocation_list(self):
        """Re-read the revocation list from disk.

        A ``RevocationList`` loads its set at construction; one built
        before a separate process (here, ``main()``) revoked a grant
        does not see the change. Tests that call ``main()`` verify
        against a freshly loaded list.
        """
        return RevocationList(self.revocation_path)

    def _argv(self, *args):
        """Build an argv list pointing the CLI at the temp state."""
        return list(args) + [
            "--audit-log",
            str(self.audit_path),
            "--revocation-list",
            str(self.revocation_path),
        ]

    def _run_main(self, argv):
        """Run main(argv), capturing stdout and stderr."""
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(argv)
        return code, stdout.getvalue(), stderr.getvalue()


class TestAIV61CliExists(GovctlCliTestCase):
    """AIV-6.1: a local CLI tool (``govctl``) with $0 infrastructure."""

    def test_AIV_6_1_parser_has_grants_list_and_revoke(self):
        parser = build_parser()
        self.assertEqual(parser.prog, "govctl")
        args = parser.parse_args(["grants", "list"])
        self.assertEqual(args.command, "grants")
        self.assertEqual(args.grants_command, "list")
        args = parser.parse_args(["revoke", "grant-1"])
        self.assertEqual(args.command, "revoke")
        self.assertEqual(args.grant_id, "grant-1")
        self.assertFalse(args.all)
        args = parser.parse_args(["revoke", "--all"])
        self.assertTrue(args.all)

    def test_AIV_6_1_main_is_importable_and_returns_int(self):
        code, out, _err = self._run_main(self._argv("grants", "list"))
        self.assertEqual(code, 0)
        self.assertIn("No active grants.", out)


class TestAIV62GrantsList(GovctlCliTestCase):
    """AIV-6.2: ``govctl grants list`` displays active grants."""

    def test_AIV_6_2_list_shows_agent_task_scopes_and_remaining_ttl(self):
        self._issue("antigravity", "TASK-1", ["repo:read"], "grant-1")
        self._issue(
            "kiro", "TASK-2", ["spec:read", "spec:write"], "grant-2"
        )
        grants = list_active_grants(
            self.audit_log, self.revocation_list, now=NOW + 60
        )
        self.assertEqual(len(grants), 2)
        by_jti = {g["jti"]: g for g in grants}
        first = by_jti["grant-1"]
        self.assertEqual(first["agent_id"], "antigravity")
        self.assertEqual(first["task_id"], "TASK-1")
        self.assertEqual(first["scopes"], ["repo:read"])
        self.assertEqual(first["ttl_seconds"], 900)
        self.assertEqual(first["remaining_seconds"], 840)
        second = by_jti["grant-2"]
        self.assertEqual(second["agent_id"], "kiro")
        self.assertEqual(second["scopes"], ["spec:read", "spec:write"])

    def test_AIV_6_2_list_via_main_prints_grants(self):
        self._issue_live("antigravity", "TASK-1", ["repo:read"], "grant-1")
        code, out, _err = self._run_main(self._argv("grants", "list"))
        self.assertEqual(code, 0)
        self.assertIn("grant-1", out)
        self.assertIn("antigravity", out)
        self.assertIn("TASK-1", out)
        self.assertIn("repo:read", out)

    def test_AIV_6_2_expired_grant_is_not_listed(self):
        self._issue("antigravity", "TASK-1", ["repo:read"], "grant-1",
                    ttl_seconds=900)
        grants = list_active_grants(
            self.audit_log, self.revocation_list, now=NOW + 901
        )
        self.assertEqual(grants, [])

    def test_AIV_6_2_revoked_grant_is_not_listed(self):
        self._issue("antigravity", "TASK-1", ["repo:read"], "grant-1")
        revoke_grant_by_id(
            "grant-1", self.audit_log, self.revocation_list, now=NOW
        )
        grants = list_active_grants(
            self.audit_log, self.revocation_list, now=NOW + 60
        )
        self.assertEqual(grants, [])

    def test_AIV_6_2_unknown_ttl_is_listed_with_unknown_remaining(self):
        self.audit_log.append_event(
            "GRANT_ISSUED",
            "antigravity",
            "TASK-1",
            jti="grant-hand",
            scopes=["repo:read"],
            details="issued by hand, no TTL recorded",
            now=NOW,
        )
        grants = list_active_grants(
            self.audit_log, self.revocation_list, now=NOW + 60
        )
        self.assertEqual(len(grants), 1)
        self.assertIsNone(grants[0]["ttl_seconds"])
        self.assertIsNone(grants[0]["remaining_seconds"])
        self.assertIn("unknown", format_grants(grants))


class TestAIV63Revoke(GovctlCliTestCase):
    """AIV-6.3: ``govctl revoke`` invalidates the designated grants."""

    def test_AIV_6_3_revoke_by_id_removes_from_list_and_logs(self):
        self._issue("antigravity", "TASK-1", ["repo:read"], "grant-1")
        self._issue("kiro", "TASK-2", ["spec:read"], "grant-2")
        event = revoke_grant_by_id(
            "grant-1", self.audit_log, self.revocation_list, now=NOW
        )
        self.assertEqual(event["event_type"], "GRANT_REVOKED")
        self.assertEqual(event["jti"], "grant-1")
        self.assertEqual(event["agent_id"], "antigravity")
        self.assertEqual(event["task_id"], "TASK-1")
        self.assertTrue(self.revocation_list.is_revoked("grant-1"))
        self.assertFalse(self.revocation_list.is_revoked("grant-2"))
        grants = list_active_grants(
            self.audit_log, self.revocation_list, now=NOW + 60
        )
        self.assertEqual([g["jti"] for g in grants], ["grant-2"])

    def test_AIV_6_3_revoke_by_id_via_main_returns_zero(self):
        self._issue_live("antigravity", "TASK-1", ["repo:read"], "grant-1")
        code, out, _err = self._run_main(
            self._argv("revoke", "grant-1")
        )
        self.assertEqual(code, 0)
        self.assertIn("Revoked grant grant-1.", out)
        self.assertTrue(self._fresh_revocation_list().is_revoked("grant-1"))

    def test_AIV_6_3_revoke_all_clears_every_active_grant(self):
        self._issue("antigravity", "TASK-1", ["repo:read"], "grant-1")
        self._issue("kiro", "TASK-2", ["spec:read"], "grant-2")
        events = revoke_all_grants(
            self.audit_log, self.revocation_list, now=NOW
        )
        self.assertEqual(len(events), 2)
        self.assertEqual(
            sorted(e["jti"] for e in events), ["grant-1", "grant-2"]
        )
        self.assertTrue(
            all(e["event_type"] == "GRANT_REVOKED" for e in events)
        )
        self.assertEqual(
            list_active_grants(
                self.audit_log, self.revocation_list, now=NOW + 60
            ),
            [],
        )

    def test_AIV_6_3_revoke_all_via_main_returns_zero(self):
        self._issue_live("antigravity", "TASK-1", ["repo:read"], "grant-1")
        self._issue_live("kiro", "TASK-2", ["spec:read"], "grant-2")
        code, out, _err = self._run_main(self._argv("revoke", "--all"))
        self.assertEqual(code, 0)
        self.assertIn("Revoked 2 grant(s).", out)
        # The revocations are durable: a fresh list sees no active
        # grants (read at live time, so the live-issued grants would
        # otherwise still be active).
        import time

        self.assertEqual(
            list_active_grants(
                self.audit_log,
                self._fresh_revocation_list(),
                now=int(time.time()),
            ),
            [],
        )

    def test_AIV_6_3_revoke_unknown_id_is_fail_safe_but_exits_nonzero(self):
        with self.assertRaises(CliError):
            revoke_grant_by_id(
                "grant-nope", self.audit_log, self.revocation_list, now=NOW
            )
        # Fail-safe: the unknown jti is still in the revocation list,
        # so any later use of it is denied.
        self.assertTrue(self.revocation_list.is_revoked("grant-nope"))
        code, _out, err = self._run_main(
            self._argv("revoke", "grant-nope")
        )
        self.assertEqual(code, 1)
        self.assertIn("not found in audit log", err)

    def test_AIV_6_3_revoke_with_no_id_and_no_all_exits_nonzero(self):
        code, _out, err = self._run_main(self._argv("revoke"))
        self.assertEqual(code, 1)
        self.assertIn("specify a grant id or --all", err)


class TestAIV34FailClosed(GovctlCliTestCase):
    """AIV-3.4: a missing or unparseable configuration fails closed."""

    def test_AIV_3_4_unparseable_revocation_list_exits_two(self):
        self.revocation_path.write_text("{not json", encoding="utf-8")
        code, _out, err = self._run_main(self._argv("grants", "list"))
        self.assertEqual(code, 2)
        self.assertIn("revocation list", err)

    def test_AIV_3_4_audit_log_path_is_a_directory_exits_two(self):
        code, _out, err = self._run_main(
            [
                "grants",
                "list",
                "--audit-log",
                str(self.dir),
                "--revocation-list",
                str(self.revocation_path),
            ]
        )
        self.assertEqual(code, 2)
        self.assertIn("audit log", err)

    def test_AIV_3_4_corrupt_audit_log_line_exits_two(self):
        self.audit_path.write_text("{corrupt\n", encoding="utf-8")
        code, _out, err = self._run_main(self._argv("grants", "list"))
        self.assertEqual(code, 2)
        self.assertIn("audit log", err)

    def test_AIV_3_4_missing_audit_log_is_not_a_config_failure(self):
        # A missing log file is normal first use, not a config failure:
        # listing an empty log succeeds and does not create the file.
        code, out, _err = self._run_main(self._argv("grants", "list"))
        self.assertEqual(code, 0)
        self.assertIn("No active grants.", out)
        self.assertFalse(self.audit_path.exists())


if __name__ == "__main__":
    unittest.main()
