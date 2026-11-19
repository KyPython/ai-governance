"""Tests for the Vault Broker core and TTL bounding (AIV Task T3).

Verifies criteria:
- AIV-1.3: The broker verifies the declared agent_id exists in the
  registry and the requested capability set is a subset of the agent's
  registered capabilities.
- AIV-1.4: An unrecognized agent_id or an excess capability set is a
  fail-closed DENY and the authorization failure is logged.
- AIV-2.1: A grant is assigned a default TTL of 15 minutes.
- AIV-2.2: A requested TTL above 60 minutes is clamped to 60 minutes.
- AIV-2.4: approver != requester; an agent cannot authorize its own grant.
- AIV-2.5: A human-curated scope contract is the exclusive Source of Truth
  for permitted scopes.
- AIV-3.4: Missing or unparseable configuration fails closed.

Tests use a fixture registry and fixture scope contracts, not the real
registry file, except for one integration test that loads the real pilot
registry to prove the broker works against it.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_vault.broker import (
    MAX_TTL_SECONDS,
    BrokerConfigError,
    GrantDeniedError,
    VaultBroker,
)
from agent_vault.registry import DEFAULT_REGISTRY_PATH
from agent_vault.token import (
    DEFAULT_TTL_SECONDS,
    compute_scopes_hash,
    generate_keypair,
    verify_token,
)

# Fixed reference time used across tests (2026-11-06T21:20:00Z). Same value
# as tests/test_token_verifier.py.
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

#: Fixture scope contract. Deliberately omits ``spec:write`` so that an
#: out-of-contract scope can be tested against a capability the registry
#: would otherwise allow (AIV-2.5).
FIXTURE_CONTRACT = {
    "permitted_scopes": ["repo:read", "repo:write", "subprocess:exec", "spec:read"]
}

#: Contract permitting every pilot capability, for the real-registry test.
FULL_CONTRACT = {
    "permitted_scopes": [
        "repo:read",
        "repo:write",
        "subprocess:exec",
        "spec:read",
        "spec:write",
    ]
}


def _make_broker(registry_data=None, scope_contract=None):
    """Build a broker on fixture data with a fresh vault keypair."""
    private_key, _public_key = generate_keypair()
    return VaultBroker(
        private_key,
        registry_data=registry_data if registry_data is not None else FIXTURE_REGISTRY,
        scope_contract=scope_contract if scope_contract is not None else FIXTURE_CONTRACT,
    )


class TestVaultBrokerGrantIssuance(unittest.TestCase):
    """Grant issuance: registry check, capability subset, token (AIV-1.3)."""

    def test_AIV_1_3_known_agent_subset_capabilities_granted(self):
        """AIV-1.3: A known agent requesting a subset of its registered
        capabilities is granted a signed token."""
        broker = _make_broker()
        grant = broker.request_grant(
            agent_id="antigravity",
            task_id="AIV-PILOT-01",
            scopes=["repo:read", "repo:write"],
            approver="ky",
            now=NOW,
        )
        self.assertEqual(grant.agent_id, "antigravity")
        self.assertEqual(grant.role, "author")
        self.assertEqual(grant.task_id, "AIV-PILOT-01")
        self.assertEqual(grant.scopes, ["repo:read", "repo:write"])
        self.assertEqual(grant.scopes_hash, compute_scopes_hash(grant.scopes))
        self.assertEqual(grant.iat, NOW)
        payload = verify_token(grant.token, broker.public_key, now=NOW)
        self.assertEqual(payload["sub"], "antigravity")
        self.assertEqual(payload["role"], "author")
        self.assertEqual(payload["task_id"], "AIV-PILOT-01")
        self.assertEqual(payload["jti"], grant.jti)

    def test_AIV_1_3_unknown_agent_denied(self):
        """AIV-1.3 / AIV-1.4: An unrecognized agent_id is a fail-closed DENY."""
        broker = _make_broker()
        with self.assertRaises(GrantDeniedError):
            broker.request_grant(
                agent_id="mallory",
                task_id="AIV-PILOT-01",
                scopes=["repo:read"],
                approver="ky",
                now=NOW,
            )
        self.assertEqual(len(broker.authorization_failures), 1)
        failure = broker.authorization_failures[0]
        self.assertEqual(failure["agent_id"], "mallory")
        self.assertIn("unknown agent_id", failure["details"])

    def test_AIV_1_3_excess_capability_denied(self):
        """AIV-1.3 / AIV-1.4: A capability outside the agent's registered
        set is denied even when the scope contract would allow it."""
        broker = _make_broker()
        with self.assertRaises(GrantDeniedError):
            broker.request_grant(
                agent_id="antigravity",
                task_id="AIV-PILOT-01",
                scopes=["repo:read", "spec:write"],
                approver="ky",
                now=NOW,
            )
        self.assertEqual(len(broker.authorization_failures), 1)
        self.assertIn(
            "spec:write", broker.authorization_failures[0]["details"]
        )

    def test_AIV_1_3_real_registry_pilot_pair(self):
        """AIV-1.3: The broker grants against the real registry/agents.json
        pilot pair (integration check, not a fixture)."""
        private_key, _public_key = generate_keypair()
        broker = VaultBroker(
            private_key,
            registry_path=DEFAULT_REGISTRY_PATH,
            scope_contract=FULL_CONTRACT,
        )
        grant = broker.request_grant(
            agent_id="antigravity",
            task_id="AIV-PILOT-01",
            scopes=["repo:read"],
            approver="ky",
            now=NOW,
        )
        self.assertEqual(grant.role, "author")
        payload = verify_token(grant.token, broker.public_key, now=NOW)
        self.assertEqual(payload["sub"], "antigravity")


class TestVaultBrokerDenyLogging(unittest.TestCase):
    """DENY records an authorization failure (AIV-1.4)."""

    def test_AIV_1_4_deny_logs_authorization_failure(self):
        """AIV-1.4: A denied request is logged as an audit-shaped
        GRANT_REJECTED record and no token is issued."""
        broker = _make_broker()
        with self.assertRaises(GrantDeniedError):
            broker.request_grant(
                agent_id="mallory",
                task_id="AIV-PILOT-01",
                scopes=["repo:read"],
                approver="ky",
                now=NOW,
            )
        self.assertEqual(len(broker.authorization_failures), 1)
        failure = broker.authorization_failures[0]
        self.assertEqual(failure["event_type"], "GRANT_REJECTED")
        self.assertEqual(failure["agent_id"], "mallory")
        self.assertEqual(failure["task_id"], "AIV-PILOT-01")
        self.assertIsNone(failure["jti"])
        self.assertEqual(failure["scopes"], ["repo:read"])
        self.assertTrue(failure["details"])
        self.assertEqual(failure["timestamp"], "2026-11-06T21:20:00.000Z")

    def test_AIV_1_4_denials_accumulate_without_grants(self):
        """AIV-1.4: Repeated denials accumulate in the failure log and no
        grant is ever returned for a denied request."""
        broker = _make_broker()
        for agent_id, scopes in (
            ("mallory", ["repo:read"]),
            ("antigravity", ["spec:write"]),
        ):
            with self.assertRaises(GrantDeniedError):
                broker.request_grant(
                    agent_id=agent_id,
                    task_id="AIV-PILOT-01",
                    scopes=scopes,
                    approver="ky",
                    now=NOW,
                )
        self.assertEqual(len(broker.authorization_failures), 2)
        self.assertEqual(
            [f["agent_id"] for f in broker.authorization_failures],
            ["mallory", "antigravity"],
        )


class TestVaultBrokerTtlBounding(unittest.TestCase):
    """TTL: 15-minute default and 60-minute ceiling (AIV-2.1, AIV-2.2)."""

    def test_AIV_2_1_default_ttl_fifteen_minutes(self):
        """AIV-2.1: A grant with no requested TTL gets 15 minutes."""
        broker = _make_broker()
        grant = broker.request_grant(
            agent_id="antigravity",
            task_id="AIV-PILOT-01",
            scopes=["repo:read"],
            approver="ky",
            now=NOW,
        )
        self.assertEqual(grant.ttl_seconds, DEFAULT_TTL_SECONDS)
        self.assertEqual(grant.ttl_seconds, 900)
        self.assertEqual(grant.requested_ttl_seconds, 900)
        self.assertFalse(grant.ttl_clamped)
        self.assertEqual(grant.exp - grant.iat, 900)
        payload = verify_token(grant.token, broker.public_key, now=NOW)
        self.assertEqual(payload["exp"], NOW + 900)

    def test_AIV_2_2_ttl_above_sixty_clamped_to_sixty(self):
        """AIV-2.2: A requested TTL above 60 minutes is clamped to 60
        minutes and the clamp is recorded on the grant."""
        broker = _make_broker()
        grant = broker.request_grant(
            agent_id="antigravity",
            task_id="AIV-PILOT-01",
            scopes=["repo:read"],
            approver="ky",
            ttl_seconds=7200,
            now=NOW,
        )
        self.assertEqual(grant.ttl_seconds, MAX_TTL_SECONDS)
        self.assertEqual(grant.ttl_seconds, 3600)
        self.assertEqual(grant.requested_ttl_seconds, 7200)
        self.assertTrue(grant.ttl_clamped)
        self.assertEqual(grant.exp - grant.iat, 3600)
        payload = verify_token(grant.token, broker.public_key, now=NOW)
        self.assertEqual(payload["exp"], NOW + 3600)

    def test_AIV_2_2_ttl_exactly_sixty_not_clamped(self):
        """AIV-2.2: A TTL of exactly 60 minutes is at the ceiling, not
        above it, so it is granted as requested without a clamp."""
        broker = _make_broker()
        grant = broker.request_grant(
            agent_id="antigravity",
            task_id="AIV-PILOT-01",
            scopes=["repo:read"],
            approver="ky",
            ttl_seconds=3600,
            now=NOW,
        )
        self.assertEqual(grant.ttl_seconds, 3600)
        self.assertFalse(grant.ttl_clamped)

    def test_AIV_2_2_ttl_below_sixty_unchanged(self):
        """AIV-2.2: A TTL below the ceiling is granted as requested."""
        broker = _make_broker()
        grant = broker.request_grant(
            agent_id="antigravity",
            task_id="AIV-PILOT-01",
            scopes=["repo:read"],
            approver="ky",
            ttl_seconds=600,
            now=NOW,
        )
        self.assertEqual(grant.ttl_seconds, 600)
        self.assertFalse(grant.ttl_clamped)


class TestVaultBrokerApproverSeparation(unittest.TestCase):
    """approver != requester (AIV-2.4)."""

    def test_AIV_2_4_approver_same_as_requester_rejected(self):
        """AIV-2.4: An agent SHALL NOT authorize its own grant."""
        broker = _make_broker()
        with self.assertRaises(GrantDeniedError):
            broker.request_grant(
                agent_id="antigravity",
                task_id="AIV-PILOT-01",
                scopes=["repo:read"],
                approver="antigravity",
                now=NOW,
            )
        self.assertEqual(len(broker.authorization_failures), 1)
        self.assertIn("approver", broker.authorization_failures[0]["details"])

    def test_AIV_2_4_approver_different_from_requester_granted(self):
        """AIV-2.4: A grant authorized by someone other than the requester
        (here the human owner) is granted."""
        broker = _make_broker()
        grant = broker.request_grant(
            agent_id="antigravity",
            task_id="AIV-PILOT-01",
            scopes=["repo:read"],
            approver="ky",
            now=NOW,
        )
        self.assertEqual(grant.approver, "ky")
        self.assertEqual(grant.agent_id, "antigravity")


class TestVaultBrokerScopeContract(unittest.TestCase):
    """The scope contract is the exclusive Source of Truth (AIV-2.5)."""

    def test_AIV_2_5_out_of_contract_scope_denied(self):
        """AIV-2.5: A scope the registry allows but the contract does not
        is denied — the contract, not the registry, decides."""
        broker = _make_broker()
        with self.assertRaises(GrantDeniedError):
            broker.request_grant(
                agent_id="kiro",
                task_id="AIV-PILOT-01",
                scopes=["spec:write"],
                approver="ky",
                now=NOW,
            )
        self.assertEqual(len(broker.authorization_failures), 1)
        self.assertIn("spec:write", broker.authorization_failures[0]["details"])

    def test_AIV_2_5_in_contract_scope_granted(self):
        """AIV-2.5: A scope permitted by both the registry and the contract
        is granted."""
        broker = _make_broker()
        grant = broker.request_grant(
            agent_id="kiro",
            task_id="AIV-PILOT-01",
            scopes=["spec:read"],
            approver="ky",
            now=NOW,
        )
        self.assertEqual(grant.scopes, ["spec:read"])

    def test_AIV_2_5_completion_contract_shape_accepted(self):
        """AIV-2.5: A completion-contract.json shaped contract
        (``credential_grant`` mapping) is accepted as the Source of Truth."""
        private_key, _public_key = generate_keypair()
        broker = VaultBroker(
            private_key,
            registry_data=FIXTURE_REGISTRY,
            scope_contract={"credential_grant": {"vault": ["repo:read"]}},
        )
        grant = broker.request_grant(
            agent_id="antigravity",
            task_id="AIV-PILOT-01",
            scopes=["repo:read"],
            approver="ky",
            now=NOW,
        )
        self.assertEqual(grant.scopes, ["repo:read"])
        with self.assertRaises(GrantDeniedError):
            broker.request_grant(
                agent_id="antigravity",
                task_id="AIV-PILOT-01",
                scopes=["repo:write"],
                approver="ky",
                now=NOW,
            )


class TestVaultBrokerFailClosedConfig(unittest.TestCase):
    """Missing or unparseable configuration fails closed (AIV-3.4)."""

    def test_AIV_3_4_missing_scope_contract_fails_closed(self):
        """AIV-3.4 / AIV-2.5: No scope contract means no broker — the
        contract is the exclusive Source of Truth, so its absence is a
        fail-closed configuration error, not a grant."""
        private_key, _public_key = generate_keypair()
        with self.assertRaises(BrokerConfigError):
            VaultBroker(private_key, registry_data=FIXTURE_REGISTRY)

    def test_AIV_3_4_missing_registry_file_fails_closed(self):
        """AIV-3.4: A registry path that does not exist fails closed at
        construction."""
        private_key, _public_key = generate_keypair()
        with self.assertRaises(BrokerConfigError):
            VaultBroker(
                private_key,
                registry_path=ROOT / "registry" / "no-such-agents.json",
                scope_contract=FIXTURE_CONTRACT,
            )

    def test_AIV_3_4_unparseable_scope_contract_fails_closed(self):
        """AIV-3.4: A scope contract that declares no permitted scopes is
        unparseable and fails closed."""
        private_key, _public_key = generate_keypair()
        for bad_contract in (
            {},
            {"permitted_scopes": []},
            {"permitted_scopes": "repo:read"},
            {"credential_grant": {"vault": []}},
        ):
            with self.assertRaises(BrokerConfigError, msg=repr(bad_contract)):
                VaultBroker(
                    private_key,
                    registry_data=FIXTURE_REGISTRY,
                    scope_contract=bad_contract,
                )

    def test_AIV_3_4_malformed_grant_arguments_fail_closed(self):
        """AIV-3.4: Malformed grant arguments fail closed with no token."""
        broker = _make_broker()
        base = dict(
            agent_id="antigravity",
            task_id="AIV-PILOT-01",
            scopes=["repo:read"],
            approver="ky",
        )
        with self.assertRaises(ValueError):
            broker.request_grant(**{**base, "agent_id": ""}, now=NOW)
        with self.assertRaises(ValueError):
            broker.request_grant(**{**base, "scopes": []}, now=NOW)
        with self.assertRaises(ValueError):
            broker.request_grant(**{**base, "approver": ""}, now=NOW)
        with self.assertRaises(ValueError):
            broker.request_grant(**base, ttl_seconds=0, now=NOW)
        with self.assertRaises(ValueError):
            broker.request_grant(**base, ttl_seconds=-60, now=NOW)
        self.assertEqual(broker.authorization_failures, [])


if __name__ == "__main__":
    unittest.main()
