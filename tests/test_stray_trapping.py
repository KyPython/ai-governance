"""Tests for hard-cut revocation and stray trapping (AIV Task T4).

Verifies criteria:
- AIV-3.1: When a task completes, fails, or is cancelled the Vault
  Broker SHALL immediately revoke the associated ``jti`` and invalidate
  any active process grants — revocation is a hard cut, not a TTL
  boundary.
- AIV-3.2: An agent executing an action using an expired, revoked, or
  out-of-scope credential SHALL have a ``STRAY_ACTION`` recorded in the
  audit log and the use SHALL be denied.
- AIV-3.4: A missing or unparseable configuration fails closed.

Tests use a temporary directory for the audit log and the revocation
list, never the real ``logs/`` path. The broker fixture mirrors the
pilot pair in ``registry/agents.json`` (same fixture as
tests/test_vault_broker.py).
"""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_vault.audit import AuditLog
from agent_vault.broker import VaultBroker
from agent_vault.stray import (
    RevocationError,
    RevocationList,
    RevokedTokenError,
    StrayActionError,
    check_use,
    revoke_grant,
    verify_grant,
)
from agent_vault.token import generate_keypair, verify_token

# Fixed reference time used across tests (2026-11-06T21:20:00Z). Same value
# as tests/test_token_verifier.py and tests/test_vault_broker.py.
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


def _make_broker():
    """Build a broker on fixture data with a fresh vault keypair."""
    private_key, _public_key = generate_keypair()
    return VaultBroker(
        private_key,
        registry_data=FIXTURE_REGISTRY,
        scope_contract=FULL_CONTRACT,
    )


def _issue_grant(broker, scopes=None, ttl_seconds=None):
    """Issue a grant for antigravity on AIV-PILOT-01 at the fixed NOW."""
    return broker.request_grant(
        agent_id="antigravity",
        task_id="AIV-PILOT-01",
        scopes=scopes if scopes is not None else ["repo:read"],
        approver="ky",
        ttl_seconds=ttl_seconds,
        now=NOW,
    )


class TestHardRevocation(unittest.TestCase):
    """Hard-cut revocation (AIV-3.1)."""

    def test_AIV_3_1_revoked_token_denied_before_expiry(self):
        """AIV-3.1: A revoked token is denied immediately, while its
        TTL is still valid — revocation is a hard cut, not a TTL
        boundary. The same token verifies fine before revocation."""
        broker = _make_broker()
        grant = _issue_grant(broker, ttl_seconds=900)
        # The token is otherwise valid 60s after issuance.
        verify_token(grant.token, broker.public_key, now=NOW + 60)
        verify_grant(grant.token, broker.public_key, None, now=NOW + 60)
        # Revoke, then the same token is denied at the same instant.
        revocations = RevocationList()
        revoke_grant(
            grant.jti, "antigravity", "AIV-PILOT-01", revocations, now=NOW + 60
        )
        self.assertTrue(revocations.is_revoked(grant.jti))
        with self.assertRaises(RevokedTokenError):
            verify_grant(
                grant.token, broker.public_key, revocations, now=NOW + 60
            )

    def test_AIV_3_1_revoke_records_grant_revoked_event(self):
        """AIV-3.1: Revoking a grant records a GRANT_REVOKED audit event
        carrying the grant's agent, task, and jti."""
        with tempfile.TemporaryDirectory() as tmp:
            log = AuditLog(Path(tmp) / "vault-audit.jsonl")
            revocations = RevocationList()
            event = revoke_grant(
                "grant-abc", "antigravity", "AIV-PILOT-01",
                revocations, audit_log=log, now=NOW,
            )
            self.assertIsNotNone(event)
            self.assertEqual(event["event_type"], "GRANT_REVOKED")
            self.assertEqual(event["jti"], "grant-abc")
            self.assertEqual(event["agent_id"], "antigravity")
            self.assertEqual(event["task_id"], "AIV-PILOT-01")
            self.assertEqual(len(log.read_events()), 1)

    def test_AIV_3_1_revocation_persists_across_instances(self):
        """AIV-3.1: A file-backed revocation list survives a broker
        restart — a fresh list loaded from the same file still denies
        the revoked jti."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "revoked-jtis.json"
            revocations = RevocationList(path)
            revocations.revoke("grant-abc")
            self.assertTrue(path.exists())
            reloaded = RevocationList(path)
            self.assertTrue(reloaded.is_revoked("grant-abc"))
            self.assertEqual(len(reloaded), 1)
            self.assertFalse(reloaded.is_revoked("grant-other"))


class TestStrayTrapping(unittest.TestCase):
    """Stray-credential trapping (AIV-3.2)."""

    def test_AIV_3_2_expired_token_use_trapped(self):
        """AIV-3.2: Using an expired credential is trapped: a
        STRAY_ACTION is recorded and the use is denied."""
        with tempfile.TemporaryDirectory() as tmp:
            log = AuditLog(Path(tmp) / "vault-audit.jsonl")
            broker = _make_broker()
            grant = _issue_grant(broker, ttl_seconds=60)
            with self.assertRaises(StrayActionError) as ctx:
                check_use(
                    grant.token, broker.public_key, ["repo:read"],
                    audit_log=log, now=NOW + 120,
                )
            self.assertIn("expired", ctx.exception.reason)
            self.assertIsNotNone(ctx.exception.audit_event)
            events = log.read_events()
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["event_type"], "STRAY_ACTION")
            self.assertEqual(events[0]["jti"], grant.jti)
            self.assertEqual(events[0]["agent_id"], "antigravity")

    def test_AIV_3_2_revoked_token_use_trapped(self):
        """AIV-3.2: Using a revoked credential is trapped: a
        STRAY_ACTION is recorded and the use is denied, even though
        the token's TTL has not expired."""
        with tempfile.TemporaryDirectory() as tmp:
            log = AuditLog(Path(tmp) / "vault-audit.jsonl")
            broker = _make_broker()
            grant = _issue_grant(broker, ttl_seconds=900)
            revocations = RevocationList()
            revoke_grant(
                grant.jti, "antigravity", "AIV-PILOT-01",
                revocations, now=NOW + 60,
            )
            with self.assertRaises(StrayActionError) as ctx:
                check_use(
                    grant.token, broker.public_key, ["repo:read"],
                    revocation_list=revocations, audit_log=log,
                    now=NOW + 60,
                )
            self.assertIn("revoked", ctx.exception.reason)
            events = log.read_events()
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["event_type"], "STRAY_ACTION")

    def test_AIV_3_2_out_of_scope_use_trapped(self):
        """AIV-3.2: Using a credential for a scope outside the token's
        granted scopes is trapped and the offending scope is named."""
        with tempfile.TemporaryDirectory() as tmp:
            log = AuditLog(Path(tmp) / "vault-audit.jsonl")
            broker = _make_broker()
            grant = _issue_grant(broker, scopes=["repo:read"])
            with self.assertRaises(StrayActionError) as ctx:
                check_use(
                    grant.token, broker.public_key,
                    ["repo:read", "repo:write"], audit_log=log, now=NOW,
                )
            self.assertIn("repo:write", ctx.exception.reason)
            events = log.read_events()
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["event_type"], "STRAY_ACTION")
            self.assertEqual(
                events[0]["scopes"], ["repo:read", "repo:write"]
            )

    def test_AIV_3_2_valid_in_scope_use_allowed(self):
        """AIV-3.2: A valid, unrevoked token used within its granted
        scopes is allowed, returns the verified payload, and records
        no STRAY_ACTION."""
        with tempfile.TemporaryDirectory() as tmp:
            log = AuditLog(Path(tmp) / "vault-audit.jsonl")
            broker = _make_broker()
            grant = _issue_grant(broker, scopes=["repo:read", "repo:write"])
            revocations = RevocationList()
            payload = check_use(
                grant.token, broker.public_key, ["repo:read"],
                revocation_list=revocations, audit_log=log, now=NOW,
            )
            self.assertEqual(payload["sub"], "antigravity")
            self.assertEqual(payload["task_id"], "AIV-PILOT-01")
            self.assertEqual(payload["jti"], grant.jti)
            self.assertEqual(log.read_events(), [])

    def test_AIV_3_2_tampered_token_use_trapped(self):
        """AIV-3.2: A token whose payload was tampered with (so its
        signature no longer verifies) is trapped as a stray use."""
        with tempfile.TemporaryDirectory() as tmp:
            log = AuditLog(Path(tmp) / "vault-audit.jsonl")
            broker = _make_broker()
            grant = _issue_grant(broker)
            header, payload_segment, signature = grant.token.split(".")
            first = payload_segment[0]
            tampered_first = "A" if first != "A" else "B"
            tampered = header + "." + tampered_first + payload_segment[1:] + "." + signature
            with self.assertRaises(StrayActionError):
                check_use(
                    tampered, broker.public_key, ["repo:read"],
                    audit_log=log, now=NOW,
                )
            events = log.read_events()
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["event_type"], "STRAY_ACTION")

    def test_AIV_3_2_check_use_rejects_empty_requested_scopes(self):
        """AIV-3.2: A use with no requested scopes is a caller error
        (ValueError), not a stray use — nothing is trapped or logged."""
        with tempfile.TemporaryDirectory() as tmp:
            log = AuditLog(Path(tmp) / "vault-audit.jsonl")
            broker = _make_broker()
            grant = _issue_grant(broker)
            with self.assertRaises(ValueError):
                check_use(
                    grant.token, broker.public_key, [],
                    audit_log=log, now=NOW,
                )
            self.assertEqual(log.read_events(), [])


class TestRevocationFailClosed(unittest.TestCase):
    """Fail-closed revocation configuration (AIV-3.4)."""

    def test_AIV_3_4_unparseable_revocation_file_fails_closed(self):
        """AIV-3.4: A revocation list file that is not valid JSON, or
        not a list of strings, fails closed at construction instead of
        proceeding as if nothing were revoked."""
        with tempfile.TemporaryDirectory() as tmp:
            bad_json = Path(tmp) / "bad.json"
            bad_json.write_text("{not valid json", encoding="utf-8")
            with self.assertRaises(RevocationError):
                RevocationList(bad_json)
            bad_shape = Path(tmp) / "bad-shape.json"
            bad_shape.write_text('{"jti": "grant-abc"}', encoding="utf-8")
            with self.assertRaises(RevocationError):
                RevocationList(bad_shape)
            bad_entry = Path(tmp) / "bad-entry.json"
            bad_entry.write_text('["grant-abc", 42]', encoding="utf-8")
            with self.assertRaises(RevocationError):
                RevocationList(bad_entry)

    def test_AIV_3_4_revoke_requires_nonempty_jti(self):
        """AIV-3.4: Revoking an empty or non-string jti is rejected
        instead of recording a meaningless revocation."""
        revocations = RevocationList()
        with self.assertRaises(ValueError):
            revocations.revoke("")
        with self.assertRaises(ValueError):
            revocations.revoke(None)  # type: ignore[arg-type]
        self.assertEqual(len(revocations), 0)


if __name__ == "__main__":
    unittest.main()
