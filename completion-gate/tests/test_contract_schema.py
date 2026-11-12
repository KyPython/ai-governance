"""Task 1 tests: COMP-1.1 to COMP-1.8, COMP-6.1. Invalid or indeterminate -> UNKNOWN, exit status 2."""
import copy, json, os, sys, tempfile, unittest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from contract_validator import validate_contract, validate_file

FIX = os.path.join(ROOT, "tests", "fixtures")
def load(name):
    with open(os.path.join(FIX, name)) as f:
        return json.load(f)

class TestContractSchema(unittest.TestCase):
    def test_valid_contract_passes(self):  # COMP-1.1..1.8
        self.assertEqual(validate_contract(load("contract_valid.json")), [])

    def test_valid_file_status_0(self):
        self.assertEqual(validate_file(os.path.join(FIX, "contract_valid.json")), (0, "VALID", []))

    def test_missing_fields_fail_closed(self):  # COMP-1.1, 1.3-1.8
        code, verdict, errs = validate_file(os.path.join(FIX, "contract_invalid_missing_fields.json"))
        self.assertEqual((code, verdict), (2, "UNKNOWN"))
        for key in ("out_of_authorization_actions", "enforcement_points", "agent_identity", "allowed_destinations", "approval_lifetime"):
            self.assertTrue(any(key in e for e in errs), key)

    def test_each_required_key_is_required(self):
        base = load("contract_valid.json")
        with open(os.path.join(ROOT, "schemas", "completion-contract-v1.json")) as f:
            required = json.load(f)["required"]
        for key in required:
            c = copy.deepcopy(base); del c[key]
            self.assertTrue(validate_contract(c), f"missing {key} must be rejected")

    def test_missing_file_is_unknown_status_2(self):  # COMP-6.1
        self.assertEqual(validate_file("/nonexistent/contract.json")[:2], (2, "UNKNOWN"))

    def test_invalid_json_is_unknown_status_2(self):  # COMP-6.1
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as t:
            t.write("{not json")
        try:
            self.assertEqual(validate_file(t.name)[:2], (2, "UNKNOWN"))
        finally:
            os.unlink(t.name)

    def test_non_object_contract_rejected(self):
        self.assertTrue(validate_contract([]))

    def test_criteria_rules(self):  # COMP-1.2
        base = load("contract_valid.json")
        bad = [
            lambda c: c["completion_criteria"].clear(),
            lambda c: c["completion_criteria"][0].update(command=""),
            lambda c: c["completion_criteria"][0].update(timeout_seconds=0),
            lambda c: c["completion_criteria"][0].update(timeout_seconds=-5),
            lambda c: c["completion_criteria"][0].update(timeout_seconds=1.5),
            lambda c: c["completion_criteria"][0].update(timeout_seconds=True),
            lambda c: c["completion_criteria"][0].update(timeout_seconds="30"),
            lambda c: c["completion_criteria"][1].update(check_id="CHK-01"),
            lambda c: c["completion_criteria"][0].update(check_id=""),
        ]
        for mutate in bad:
            c = copy.deepcopy(base); mutate(c)
            self.assertTrue(validate_contract(c))

    def test_deny_route_must_be_terminal(self):  # COMP-1.3
        c = load("contract_valid.json"); c["deny_route"] = "agent_may_retry"
        self.assertTrue(validate_contract(c))

    def test_inherited_fence_must_be_true(self):  # COMP-1.4
        for v in (False, "true", None):
            c = load("contract_valid.json"); c["inherited_fence"] = v
            self.assertTrue(validate_contract(c))

    def test_identity_borrowing_must_be_listed_unauthorized(self):  # COMP-1.6
        c = load("contract_valid.json"); c["out_of_authorization_actions"] = ["disable_sandbox"]
        self.assertTrue(any("identity_borrowing" in e for e in validate_contract(c)))

    def test_legacy_design_label_accepted(self):  # design example uses borrow_human_credentials
        c = load("contract_valid.json"); c["out_of_authorization_actions"] = ["borrow_human_credentials"]
        self.assertEqual(validate_contract(c), [])

    def test_wrong_types_rejected(self):
        for key, val in (("enforcement_points", []), ("immutable_boundaries", "sandbox"), ("credential_grant", "x"),
                         ("allowed_destinations", "127.0.0.1"), ("drift_triggers", None), ("agent_identity", "")):
            c = load("contract_valid.json"); c[key] = val
            self.assertTrue(validate_contract(c), key)

    def test_periodic_evidence_optional(self):  # COMP-1.8: null allowed, absence allowed
        c = load("contract_valid.json"); del c["periodic_evidence"]
        self.assertEqual(validate_contract(c), [])

if __name__ == "__main__":
    unittest.main()
