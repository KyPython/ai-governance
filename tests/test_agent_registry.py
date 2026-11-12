"""Tests for Agent Registry and Pilot Agent Pair (AIV Task T1).

Verifies criteria:
- AIV-1.1: Registry format and schema compliance.
- AIV-1.2: Pilot agent pair definitions and capabilities.
- AIV-5.5: Author != Reviewer role separation enforcement.
"""

import json
from pathlib import Path
import unittest

import jsonschema

from agent_vault.registry import (
    DEFAULT_REGISTRY_PATH,
    DEFAULT_SCHEMA_PATH,
    enforce_role_separation,
    get_agent,
    load_registry,
    load_schema,
    validate_capability,
)


class TestAgentRegistry(unittest.TestCase):
    """Test suite for agent identity registry schema, pilot pair, and role separation."""

    def test_AIV_1_1_registry_schema_compliance(self):
        """AIV-1.1: registry/agents.json resides in repo and matches registry/agents.schema.json."""
        self.assertTrue(DEFAULT_REGISTRY_PATH.exists(), f"Registry file missing: {DEFAULT_REGISTRY_PATH}")
        self.assertTrue(DEFAULT_SCHEMA_PATH.exists(), f"Schema file missing: {DEFAULT_SCHEMA_PATH}")

        schema = load_schema()
        registry = load_registry(validate=True)

        self.assertEqual(registry["version"], 1)
        self.assertIsInstance(registry["agents"], list)
        self.assertGreaterEqual(len(registry["agents"]), 2)

        # Test schema rejection of invalid agent missing required fields
        invalid_missing_key = {
            "version": 1,
            "agents": [
                {
                    "agent_id": "test-agent",
                    "role": "author",
                    "permitted_capabilities": ["repo:read"],
                }
            ],
        }
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid_missing_key, schema=schema)

        # Test schema rejection of invalid role
        invalid_role = {
            "version": 1,
            "agents": [
                {
                    "agent_id": "test-agent",
                    "role": "admin",  # not in enum
                    "public_key": "0" * 64,
                    "permitted_capabilities": ["repo:read"],
                }
            ],
        }
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid_role, schema=schema)

        # Test schema rejection of invalid public key (non-hex or incorrect length)
        invalid_key_length = {
            "version": 1,
            "agents": [
                {
                    "agent_id": "test-agent",
                    "role": "author",
                    "public_key": "not-a-valid-hex-key",
                    "permitted_capabilities": ["repo:read"],
                }
            ],
        }
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid_key_length, schema=schema)

    def test_AIV_1_2_pilot_agent_pair_defined(self):
        """AIV-1.2: Pilot agent pair defined with antigravity (author) and kiro (reviewer)."""
        registry = load_registry()

        antigravity = get_agent("antigravity", registry)
        self.assertIsNotNone(antigravity, "antigravity pilot identity must exist")
        self.assertEqual(antigravity["role"], "author")
        self.assertEqual(len(antigravity["public_key"]), 64)
        int(antigravity["public_key"], 16)  # must parse as valid hex
        self.assertIn("repo:read", antigravity["permitted_capabilities"])
        self.assertIn("repo:write", antigravity["permitted_capabilities"])
        self.assertIn("subprocess:exec", antigravity["permitted_capabilities"])

        kiro = get_agent("kiro", registry)
        self.assertIsNotNone(kiro, "kiro pilot identity must exist")
        self.assertEqual(kiro["role"], "reviewer")
        self.assertEqual(len(kiro["public_key"]), 64)
        int(kiro["public_key"], 16)  # must parse as valid hex
        self.assertIn("repo:read", kiro["permitted_capabilities"])
        self.assertIn("spec:read", kiro["permitted_capabilities"])
        self.assertIn("spec:write", kiro["permitted_capabilities"])
        self.assertIn("subprocess:exec", kiro["permitted_capabilities"])

        # Test capability queries
        self.assertTrue(validate_capability("antigravity", "repo:write", registry))
        self.assertFalse(validate_capability("antigravity", "spec:write", registry))
        self.assertTrue(validate_capability("kiro", "spec:write", registry))
        self.assertFalse(validate_capability("unknown-agent", "repo:read", registry))

    def test_AIV_5_5_author_reviewer_role_separation(self):
        """AIV-5.5: Author agent of a change shall not act as reviewer/checker for that change."""
        registry = load_registry()

        # Same agent attempting to both author and review must be rejected
        self.assertFalse(
            enforce_role_separation("antigravity", "antigravity", registry),
            "Agent must not be permitted to review its own changes",
        )
        self.assertFalse(
            enforce_role_separation("kiro", "kiro", registry),
            "Reviewer must not self-certify as author",
        )

        # Proper separation between author and reviewer
        self.assertTrue(
            enforce_role_separation("antigravity", "kiro", registry),
            "Author antigravity and Reviewer kiro must pass role separation",
        )

        # Reversed roles (kiro authoring, antigravity reviewing) must fail role check
        self.assertFalse(
            enforce_role_separation("kiro", "antigravity", registry),
            "Kiro is not an author in the pilot registry",
        )

        # Unknown agent must fail
        self.assertFalse(enforce_role_separation("antigravity", "unknown-bot", registry))


if __name__ == "__main__":
    unittest.main()
