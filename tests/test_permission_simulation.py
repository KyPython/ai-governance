"""Tests for the read-only permission simulator and diagnosis stop-list
(AIV Task T5).

Verifies criteria:
- AIV-4.1: While diagnosing, the agent operates under a read-only
  diagnostic identity without mutation authority — the simulator issues
  no token, writes no log, and mutates no state.
- AIV-4.2: When diagnosing an access issue, the agent evaluates an
  explicit stop-list and halts immediately when access is already
  GRANTED, identity state is UNKNOWN, or a diagnostic call returns
  403 / PERMISSION_DENIED.
- AIV-4.3: Before applying any scope modification, the system simulates
  the access change, producing a deterministic diff (access_before vs
  access_after) whose verdict is always one of GRANTED / UNKNOWN / 403.
- AIV-4.4: An ambiguous, unsupported, or unverified simulation result
  fails closed — an unknown agent returns UNKNOWN, never a grant.
- AIV-3.4: Missing or unparseable configuration fails closed.

Tests use a fixture registry and fixture scope contracts, not the real
registry file, except for one integration test that loads the real pilot
registry to prove the simulator works against it.
"""

import inspect
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_vault.broker import BrokerConfigError
from agent_vault.registry import DEFAULT_REGISTRY_PATH
from agent_vault.simulator import (
    VERDICT_FORBIDDEN,
    VERDICT_GRANTED,
    VERDICT_UNKNOWN,
    VERDICTS,
    PermissionSimulator,
    evaluate_stop_list,
)

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

#: Contract permitting every pilot capability.
FULL_CONTRACT = {
    "permitted_scopes": [
        "repo:read",
        "repo:write",
        "subprocess:exec",
        "spec:read",
        "spec:write",
    ]
}


def _make_simulator(registry_data=None, scope_contract=None):
    """Build a simulator on fixture data (no key, no token path)."""
    return PermissionSimulator(
        registry_data=registry_data if registry_data is not None else FIXTURE_REGISTRY,
        scope_contract=scope_contract if scope_contract is not None else FIXTURE_CONTRACT,
    )


class TestReadOnlyDiagnosticIdentity(unittest.TestCase):
    """AIV-4.1: the simulator is a read-only diagnostic identity."""

    def test_AIV_4_1_simulator_has_no_token_issuing_capability(self):
        """AIV-4.1: The simulator holds no private key and exposes no
        token-issuing path — it cannot issue a grant."""
        sim = _make_simulator()
        self.assertFalse(hasattr(sim, "_private_key"))
        self.assertFalse(hasattr(sim, "private_key"))
        self.assertFalse(hasattr(sim, "request_grant"))
        self.assertFalse(hasattr(sim, "create_token"))
        params = inspect.signature(PermissionSimulator.__init__).parameters
        self.assertNotIn("private_key", params)

    def test_AIV_4_1_simulation_result_carries_no_token(self):
        """AIV-4.1: A simulation result is a diff, not a credential —
        it carries no token."""
        sim = _make_simulator()
        result = sim.simulate("antigravity", "AIV-PILOT-01", ["repo:read"])
        self.assertFalse(hasattr(result, "token"))
        self.assertEqual(result.verdict, VERDICT_GRANTED)

    def test_AIV_4_1_simulation_writes_nothing(self):
        """AIV-4.1: Running simulations (granted, denied, unknown)
        writes nothing — no file in the workspace changes and no new
        file appears."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            registry_path = tmp_path / "agents.json"
            contract_path = tmp_path / "scopes.json"
            audit_path = tmp_path / "vault-audit.jsonl"
            revocation_path = tmp_path / "revoked.json"
            registry_path.write_text(
                json.dumps(FIXTURE_REGISTRY), encoding="utf-8"
            )
            contract_path.write_text(
                json.dumps(FIXTURE_CONTRACT), encoding="utf-8"
            )
            audit_path.write_text(
                '{"event_type": "GRANT_ISSUED"}\n', encoding="utf-8"
            )
            revocation_path.write_text("[]", encoding="utf-8")

            def _snapshot():
                return {
                    p.name: p.read_bytes()
                    for p in sorted(tmp_path.iterdir())
                    if p.is_file()
                }

            before = _snapshot()
            sim = PermissionSimulator(
                registry_path=registry_path, scope_contract_path=contract_path
            )
            sim.simulate("antigravity", "AIV-PILOT-01", ["repo:read"])
            sim.simulate("kiro", "AIV-PILOT-01", ["spec:write"])
            sim.simulate("ghost", "AIV-PILOT-01", ["repo:read"])
            sim.current_access("antigravity")
            evaluate_stop_list(False, True, 403)
            after = _snapshot()
            self.assertEqual(before, after)

    def test_AIV_4_1_simulator_needs_no_private_key(self):
        """AIV-4.1: The simulator constructs on registry + contract
        alone — no credential material is required to diagnose."""
        sim = PermissionSimulator(
            registry_data=FIXTURE_REGISTRY, scope_contract=FULL_CONTRACT
        )
        self.assertEqual(
            sim.permitted_scopes,
            {"repo:read", "repo:write", "subprocess:exec", "spec:read", "spec:write"},
        )


class TestDiagnosisStopList(unittest.TestCase):
    """AIV-4.2: the explicit stop-list halts diagnosis immediately."""

    def test_AIV_4_2_stop_list_granted_halts(self):
        """AIV-4.2: Access already GRANTED halts — the failure is
        application-level, not IAM."""
        decision = evaluate_stop_list(
            access_granted=True, identity_known=True, diagnostic_status=None
        )
        self.assertTrue(decision.halt)
        self.assertEqual(decision.verdict, VERDICT_GRANTED)

    def test_AIV_4_2_stop_list_unknown_halts(self):
        """AIV-4.2: Identity or group membership state UNKNOWN halts
        and reports the visibility gap."""
        decision = evaluate_stop_list(
            access_granted=False, identity_known=False, diagnostic_status=None
        )
        self.assertTrue(decision.halt)
        self.assertEqual(decision.verdict, VERDICT_UNKNOWN)

    def test_AIV_4_2_stop_list_403_halts(self):
        """AIV-4.2: A diagnostic call returning 403 halts instead of
        probing alternate endpoints."""
        for status in (403, "PERMISSION_DENIED", "permission_denied"):
            decision = evaluate_stop_list(
                access_granted=False, identity_known=True, diagnostic_status=status
            )
            self.assertTrue(decision.halt)
            self.assertEqual(decision.verdict, VERDICT_FORBIDDEN)

    def test_AIV_4_2_stop_list_no_condition_continues(self):
        """AIV-4.2: With no stop condition, the decision is to continue
        — no verdict, no halt."""
        decision = evaluate_stop_list(
            access_granted=False, identity_known=True, diagnostic_status=200
        )
        self.assertFalse(decision.halt)
        self.assertIsNone(decision.verdict)

    def test_AIV_4_2_stop_list_precedence_granted_over_unknown(self):
        """AIV-4.2: When several stop conditions apply, GRANTED wins —
        the spec lists it first."""
        decision = evaluate_stop_list(
            access_granted=True, identity_known=False, diagnostic_status=403
        )
        self.assertEqual(decision.verdict, VERDICT_GRANTED)

    def test_AIV_4_2_stop_list_precedence_unknown_over_403(self):
        """AIV-4.2: UNKNOWN wins over 403 — the visibility gap is
        reported before probing stops."""
        decision = evaluate_stop_list(
            access_granted=False, identity_known=False, diagnostic_status=403
        )
        self.assertEqual(decision.verdict, VERDICT_UNKNOWN)


class TestPermissionSimulationDiff(unittest.TestCase):
    """AIV-4.3: the pre-scope simulation diff (access_before vs
    access_after) with a three-state verdict."""

    def test_AIV_4_3_simulate_grantable_request_returns_granted_diff(self):
        """AIV-4.3: A fully grantable request simulates to GRANTED with
        a deterministic diff: access_before is the agent's current
        effective access, and the grant adds no new standing access
        (it attests to existing permission)."""
        sim = _make_simulator()
        result = sim.simulate(
            "antigravity", "AIV-PILOT-01", ["repo:read", "repo:write"]
        )
        self.assertEqual(result.verdict, VERDICT_GRANTED)
        self.assertIn(result.verdict, VERDICTS)
        self.assertEqual(
            result.access_before, ["repo:read", "repo:write", "subprocess:exec"]
        )
        self.assertEqual(result.access_after, result.access_before)
        self.assertEqual(result.granted_scopes, ["repo:read", "repo:write"])
        self.assertEqual(result.denied_scopes, {})
        self.assertEqual(result.added_scopes, [])
        self.assertEqual(result.requested_scopes, ["repo:read", "repo:write"])

    def test_AIV_4_3_simulation_diff_shows_denied_scopes_with_reasons(self):
        """AIV-4.3: A mixed request simulates to 403 with the diff
        naming each blocked scope and why — a capability excess cites
        AIV-1.3, an out-of-contract scope cites AIV-2.5."""
        sim = _make_simulator()
        result = sim.simulate(
            "kiro", "AIV-PILOT-01", ["spec:read", "spec:write"]
        )
        self.assertEqual(result.verdict, VERDICT_FORBIDDEN)
        self.assertIn(result.verdict, VERDICTS)
        self.assertEqual(result.granted_scopes, ["spec:read"])
        self.assertEqual(set(result.denied_scopes), {"spec:write"})
        self.assertIn("AIV-2.5", result.denied_scopes["spec:write"])
        # A rejected change adds no access.
        self.assertEqual(result.access_after, result.access_before)
        self.assertEqual(result.added_scopes, [])

        result = sim.simulate(
            "antigravity", "AIV-PILOT-01", ["repo:read", "spec:write"]
        )
        self.assertEqual(result.verdict, VERDICT_FORBIDDEN)
        self.assertEqual(result.granted_scopes, ["repo:read"])
        self.assertEqual(set(result.denied_scopes), {"spec:write"})
        self.assertIn("AIV-1.3", result.denied_scopes["spec:write"])

    def test_AIV_4_3_current_access_is_capabilities_intersect_contract(self):
        """AIV-4.3: access_before is the agent's registered capabilities
        intersected with the scope contract — kiro's spec:write is in
        the registry but outside the fixture contract, so it is not
        current access."""
        sim = _make_simulator()
        self.assertEqual(
            sim.current_access("kiro"),
            ["repo:read", "spec:read", "subprocess:exec"],
        )
        self.assertEqual(
            sim.current_access("antigravity"),
            ["repo:read", "repo:write", "subprocess:exec"],
        )
        self.assertIsNone(sim.current_access("ghost"))

    def test_AIV_4_3_simulation_diff_is_deterministic(self):
        """AIV-4.3: The same inputs always produce the same diff —
        the simulation is a pure function of registry, contract,
        agent, and scopes."""
        sim = _make_simulator()
        first = sim.simulate("kiro", "AIV-PILOT-01", ["spec:read", "spec:write"])
        second = sim.simulate("kiro", "AIV-PILOT-01", ["spec:write", "spec:read"])
        self.assertEqual(first, second)

    def test_AIV_4_3_verdict_is_always_one_of_three(self):
        """AIV-4.3: Every simulation result carries exactly one of
        GRANTED / UNKNOWN / 403 — never a bare pass/fail."""
        sim = _make_simulator()
        cases = [
            sim.simulate("antigravity", "AIV-PILOT-01", ["repo:read"]),
            sim.simulate("kiro", "AIV-PILOT-01", ["spec:write"]),
            sim.simulate("ghost", "AIV-PILOT-01", ["repo:read"]),
        ]
        for result in cases:
            self.assertIn(result.verdict, VERDICTS)


class TestFailClosedSimulation(unittest.TestCase):
    """AIV-4.4: an ambiguous simulation fails closed, never a grant."""

    def test_AIV_4_4_unknown_agent_returns_unknown(self):
        """AIV-4.4: An agent not in the registry is an unresolvable
        identity — the simulation returns UNKNOWN with no access
        assumed and nothing granted."""
        sim = _make_simulator()
        result = sim.simulate("ghost", "AIV-PILOT-01", ["repo:read"])
        self.assertEqual(result.verdict, VERDICT_UNKNOWN)
        self.assertEqual(result.access_before, [])
        self.assertEqual(result.access_after, [])
        self.assertEqual(result.granted_scopes, [])
        self.assertEqual(result.denied_scopes, {})
        self.assertEqual(result.added_scopes, [])
        self.assertIn("UNKNOWN", result.reason)

    def test_AIV_4_4_approver_equals_requester_denied(self):
        """AIV-2.4 / AIV-4.4: An approver equal to the requester would
        be denied — the simulation returns 403 and grants nothing."""
        sim = _make_simulator()
        result = sim.simulate(
            "antigravity",
            "AIV-PILOT-01",
            ["repo:read"],
            approver="antigravity",
        )
        self.assertEqual(result.verdict, VERDICT_FORBIDDEN)
        self.assertEqual(result.granted_scopes, [])
        self.assertEqual(result.access_after, result.access_before)
        self.assertIn("AIV-2.4", result.reason)

    def test_AIV_4_4_malformed_arguments_fail_closed(self):
        """AIV-4.4: Malformed simulation arguments raise ValueError —
        no result is produced on a failed check."""
        sim = _make_simulator()
        with self.assertRaises(ValueError):
            sim.simulate("antigravity", "AIV-PILOT-01", [])
        with self.assertRaises(ValueError):
            sim.simulate("antigravity", "AIV-PILOT-01", ["repo:read", ""])
        with self.assertRaises(ValueError):
            sim.simulate("antigravity", "AIV-PILOT-01", "repo:read")
        with self.assertRaises(ValueError):
            sim.simulate("", "AIV-PILOT-01", ["repo:read"])
        with self.assertRaises(ValueError):
            sim.simulate("antigravity", "", ["repo:read"])

    def test_AIV_3_4_missing_or_unparseable_config_fails_closed(self):
        """AIV-3.4: A missing registry, an unparseable contract, or no
        contract at all makes the simulator refuse to construct."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            missing = tmp_path / "no-such-registry.json"
            with self.assertRaises(BrokerConfigError):
                PermissionSimulator(
                    registry_path=missing, scope_contract=FIXTURE_CONTRACT
                )
            bad_contract = tmp_path / "bad-contract.json"
            bad_contract.write_text("{not json", encoding="utf-8")
            with self.assertRaises(BrokerConfigError):
                PermissionSimulator(
                    registry_data=FIXTURE_REGISTRY,
                    scope_contract_path=bad_contract,
                )
            with self.assertRaises(BrokerConfigError):
                PermissionSimulator(registry_data=FIXTURE_REGISTRY)
            with self.assertRaises(BrokerConfigError):
                PermissionSimulator(
                    registry_data={"agents": "not-a-list"},
                    scope_contract=FIXTURE_CONTRACT,
                )


class TestSimulatorRealRegistry(unittest.TestCase):
    """Integration: the simulator against the real pilot registry."""

    def test_AIV_4_3_real_registry_pilot_pair_simulates(self):
        """AIV-4.3: Against the real registry and a full contract, the
        pilot pair simulates to GRANTED for its own capabilities."""
        registry = json.loads(DEFAULT_REGISTRY_PATH.read_text(encoding="utf-8"))
        sim = PermissionSimulator(
            registry_data=registry, scope_contract=FULL_CONTRACT
        )
        antigravity = sim.simulate(
            "antigravity", "AIV-PILOT-01", ["repo:read", "repo:write"]
        )
        self.assertEqual(antigravity.verdict, VERDICT_GRANTED)
        kiro = sim.simulate(
            "kiro", "AIV-PILOT-01", ["spec:read", "spec:write"]
        )
        self.assertEqual(kiro.verdict, VERDICT_GRANTED)
        self.assertEqual(
            kiro.access_before,
            ["repo:read", "spec:read", "spec:write", "subprocess:exec"],
        )


if __name__ == "__main__":
    unittest.main()
