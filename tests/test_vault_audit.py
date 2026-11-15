"""Tests for the append-only JSONL audit log (AIV Task T4).

Verifies criteria:
- AIV-3.3: All credential requests, grants, rejections, revocations,
  and stray detections are written to an append-only JSONL audit log
  (``logs/vault-audit.jsonl``). Entries accumulate; existing entries
  are never rewritten.
- AIV-3.4: A missing or unparseable configuration fails closed.

Tests use a temporary directory for the log path, never the real
``logs/`` path. The broker fixture mirrors the pilot pair in
``registry/agents.json`` (same fixture as tests/test_vault_broker.py).
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_vault.audit import (
    AuditLog,
    AuditLogError,
    build_event,
    flush_authorization_failures,
    record_grant_issued,
)
from agent_vault.broker import GrantDeniedError, VaultBroker
from agent_vault.token import generate_keypair

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


class TestAuditLogAppendOnly(unittest.TestCase):
    """Append-only JSONL logging (AIV-3.3)."""

    def test_AIV_3_3_events_append_as_jsonl_in_order(self):
        """AIV-3.3: Events are appended as one JSON object per line, in
        append order, with the design.md section 3.3 fields."""
        with tempfile.TemporaryDirectory() as tmp:
            log = AuditLog(Path(tmp) / "vault-audit.jsonl")
            log.append_event(
                "GRANT_ISSUED", "antigravity", "AIV-PILOT-01",
                jti="grant-1", scopes=["repo:read"], details="Granted",
                now=NOW,
            )
            log.append_event(
                "GRANT_REJECTED", "unknown-agent", "AIV-PILOT-01",
                scopes=["repo:write"], details="unknown agent_id",
                now=NOW + 1,
            )
            log.append_event(
                "GRANT_REVOKED", "antigravity", "AIV-PILOT-01",
                jti="grant-1", details="Revoked jti grant-1",
                now=NOW + 2,
            )
            lines = (Path(tmp) / "vault-audit.jsonl").read_text(
                encoding="utf-8"
            ).splitlines()
            self.assertEqual(len(lines), 3)
            events = [json.loads(line) for line in lines]
            self.assertEqual(
                [event["event_type"] for event in events],
                ["GRANT_ISSUED", "GRANT_REJECTED", "GRANT_REVOKED"],
            )
            for event in events:
                for field in (
                    "timestamp",
                    "event_type",
                    "agent_id",
                    "task_id",
                    "jti",
                    "scopes",
                    "details",
                ):
                    self.assertIn(field, event)
            self.assertEqual(events[0]["jti"], "grant-1")
            self.assertEqual(events[0]["scopes"], ["repo:read"])
            self.assertEqual(events[1]["jti"], None)
            self.assertEqual(events[0]["timestamp"], "2026-11-06T21:20:00.000Z")

    def test_AIV_3_3_existing_entries_never_rewritten(self):
        """AIV-3.3: Appending a new event leaves every existing line
        byte-identical — the log is append-only, never rewritten."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "vault-audit.jsonl"
            log = AuditLog(path)
            log.append_event(
                "GRANT_ISSUED", "antigravity", "AIV-PILOT-01",
                jti="grant-1", scopes=["repo:read"], now=NOW,
            )
            first_bytes = path.read_bytes()
            log.append_event(
                "STRAY_ACTION", "antigravity", "AIV-PILOT-01",
                jti="grant-1", scopes=["repo:write"],
                details="out of scope", now=NOW + 1,
            )
            all_bytes = path.read_bytes()
            self.assertTrue(all_bytes.startswith(first_bytes))
            self.assertEqual(len(all_bytes.splitlines()), 2)
            first_event = json.loads(all_bytes.splitlines()[0])
            self.assertEqual(first_event["event_type"], "GRANT_ISSUED")
            self.assertEqual(first_event["jti"], "grant-1")

    def test_AIV_3_3_unknown_event_type_rejected(self):
        """AIV-3.3: Only the four design.md section 3.3 event types are
        accepted; an unknown type is rejected, not written."""
        with self.assertRaises(ValueError):
            build_event("BOGUS", "antigravity", "AIV-PILOT-01", now=NOW)
        with tempfile.TemporaryDirectory() as tmp:
            log = AuditLog(Path(tmp) / "vault-audit.jsonl")
            with self.assertRaises(ValueError):
                log.append(
                    {
                        "timestamp": "2026-11-06T21:20:00.000Z",
                        "event_type": "BOGUS",
                        "agent_id": "antigravity",
                        "task_id": "AIV-PILOT-01",
                    }
                )
            self.assertFalse((Path(tmp) / "vault-audit.jsonl").exists())

    def test_AIV_3_3_missing_log_reads_empty(self):
        """AIV-3.3: Reading a log that does not exist yet returns an
        empty list instead of failing."""
        with tempfile.TemporaryDirectory() as tmp:
            log = AuditLog(Path(tmp) / "vault-audit.jsonl")
            self.assertEqual(log.read_events(), [])

    def test_AIV_3_3_record_grant_issued(self):
        """AIV-3.3: A broker-issued grant is recorded as a GRANT_ISSUED
        event carrying the grant's agent, task, jti, and scopes."""
        with tempfile.TemporaryDirectory() as tmp:
            log = AuditLog(Path(tmp) / "vault-audit.jsonl")
            broker = _make_broker()
            grant = broker.request_grant(
                agent_id="antigravity",
                task_id="AIV-PILOT-01",
                scopes=["repo:read"],
                approver="ky",
                now=NOW,
            )
            event = record_grant_issued(log, grant, now=NOW)
            self.assertEqual(event["event_type"], "GRANT_ISSUED")
            self.assertEqual(event["jti"], grant.jti)
            events = log.read_events()
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["agent_id"], "antigravity")
            self.assertEqual(events[0]["task_id"], "AIV-PILOT-01")
            self.assertEqual(events[0]["scopes"], ["repo:read"])

    def test_AIV_3_3_flush_authorization_failures(self):
        """AIV-3.3: A broker's fail-closed DENY records (AIV-1.4) are
        persisted to the log as GRANT_REJECTED events."""
        with tempfile.TemporaryDirectory() as tmp:
            log = AuditLog(Path(tmp) / "vault-audit.jsonl")
            broker = _make_broker()
            with self.assertRaises(GrantDeniedError):
                broker.request_grant(
                    agent_id="unknown-agent",
                    task_id="AIV-PILOT-01",
                    scopes=["repo:read"],
                    approver="ky",
                    now=NOW,
                )
            self.assertEqual(len(broker.authorization_failures), 1)
            flushed = flush_authorization_failures(log, broker)
            self.assertEqual(flushed, 1)
            events = log.read_events()
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["event_type"], "GRANT_REJECTED")
            self.assertEqual(events[0]["agent_id"], "unknown-agent")
            self.assertIn("unknown agent_id", events[0]["details"])


class TestAuditLogFailClosed(unittest.TestCase):
    """Fail-closed configuration handling (AIV-3.4)."""

    def test_AIV_3_4_log_path_is_directory_fails_closed(self):
        """AIV-3.4: An audit log path that is a directory (not a file)
        fails closed at construction instead of writing anywhere."""
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(AuditLogError):
                AuditLog(Path(tmp))

    def test_AIV_3_4_unwritable_parent_fails_closed(self):
        """AIV-3.4: An audit log whose parent path is a file (not a
        directory) fails closed at construction."""
        with tempfile.TemporaryDirectory() as tmp:
            blocker = Path(tmp) / "blocker"
            blocker.write_text("not a directory", encoding="utf-8")
            with self.assertRaises(AuditLogError):
                AuditLog(blocker / "vault-audit.jsonl")

    def test_AIV_3_4_corrupt_existing_log_read_fails_closed(self):
        """AIV-3.4: An existing log containing a corrupt (non-JSON) line
        fails closed on read instead of silently skipping the entry."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "vault-audit.jsonl"
            log = AuditLog(path)
            log.append_event(
                "GRANT_ISSUED", "antigravity", "AIV-PILOT-01",
                jti="grant-1", scopes=["repo:read"], now=NOW,
            )
            with open(path, "a", encoding="utf-8") as f:
                f.write("{not valid json\n")
            with self.assertRaises(AuditLogError):
                log.read_events()

    def test_AIV_3_4_malformed_record_rejected(self):
        """AIV-3.4: A record missing a required field is rejected and
        nothing is written."""
        with tempfile.TemporaryDirectory() as tmp:
            log = AuditLog(Path(tmp) / "vault-audit.jsonl")
            with self.assertRaises(ValueError):
                log.append({"event_type": "GRANT_ISSUED"})
            self.assertFalse((Path(tmp) / "vault-audit.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
