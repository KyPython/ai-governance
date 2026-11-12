"""The completion-contract template (spec: specs/completion-gate-wiring, CGW-2.1, CGW-2.3)."""
import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE_DIR = os.path.join(ROOT, "completion-gate")
TEMPLATE = os.path.join(ROOT, "templates", "spec", "completion-contract.json")
FIXED = {"contract_version", "deny_route", "inherited_fence", "periodic_evidence"}  # values the schema pins


def leaves(value):
    """Every scalar inside a JSON value (dict keys are placeholders too where they are not schema names)."""
    if isinstance(value, dict):
        for k, v in value.items():
            yield k
            yield from leaves(v)
    elif isinstance(value, list):
        for v in value:
            yield from leaves(v)
    else:
        yield value


class ContractTemplate(unittest.TestCase):
    def setUp(self):
        with open(TEMPLATE, encoding="utf-8") as fh:
            self.template = json.load(fh)
        sys.path.insert(0, GATE_DIR)
        import contract_validator  # noqa: E402  (the gate's own validator, CGW-2.1)
        self.validator = contract_validator
        with open(os.path.join(GATE_DIR, "schemas", "completion-contract-v1.json"), encoding="utf-8") as fh:
            self.required = json.load(fh)["required"]

    def tearDown(self):
        sys.path.remove(GATE_DIR)

    def test_CGW_2_1_template_is_valid_under_the_gate_schema(self):
        self.assertEqual(self.validator.validate_contract(self.template), [])

    def test_CGW_2_3_template_has_every_required_key(self):
        self.assertEqual(sorted(k for k in self.required if k not in self.template), [])

    def test_CGW_2_3_every_free_field_holds_a_placeholder(self):
        for key in self.required:
            if key in FIXED or key == "completion_criteria":
                continue
            with self.subTest(key=key):
                self.assertTrue(any(isinstance(x, str) and re.search(r"<[^>]+>", x) for x in leaves(self.template[key])),
                                "%s has no <placeholder>" % key)
        for field in ("check_id", "description", "command"):
            with self.subTest(criterion=field):
                self.assertRegex(self.template["completion_criteria"][0][field], r"<[^>]+>")

    def test_CGW_2_3_template_keeps_identity_borrowing_unauthorized(self):
        self.assertIn("identity_borrowing", self.template["out_of_authorization_actions"])


if __name__ == "__main__":
    unittest.main()
