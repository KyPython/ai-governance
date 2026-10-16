import unittest
from copy import deepcopy
from approval_gate import evaluate_case
from cases import baseline, cases
from scoring import grade


class ApprovalTrialTests(unittest.TestCase):
    def test_all_expected_cases_have_correct_effects(self):
        for c in cases():
            with self.subTest(c=c["id"]):
                self.assertTrue(grade(c, evaluate_case(c))["pass"])

    def test_scorer_rejects_forged_success_without_real_dispatch(self):
        case = cases()[0]  # authorized dispatch is expected
        forged = {"decision": "ALLOW", "reason": "dispatched",
                  "dispatched": 0, "dispatch_events": []}
        self.assertFalse(grade(case, forged)["pass"])

    def test_scorer_rejects_unauthorized_dispatch(self):
        case = next(c for c in cases() if c["id"] == "B08")
        unsafe = {"decision": "ALLOW", "reason": "dispatched", "dispatched": 1,
                  "dispatch_events": [{"event": "simulated_dispatch"}]}
        self.assertFalse(grade(case, unsafe)["pass"])

    def test_unknown_envelope_field_fails_closed(self):
        case = baseline()
        case["request"]["intent"]["hidden_recipients"] = ["outsider@example.test"]
        result = evaluate_case(case)
        self.assertEqual(result["decision"], "BLOCK")
        self.assertEqual(result["reason"], "invalid_intent")
        self.assertEqual(result["dispatched"], 0)

    def test_inconsistent_preflight_revision_fails_closed(self):
        case = baseline()
        case["trusted"]["preflight_policy_revision"] = "POLICY-6"
        result = evaluate_case(case)
        self.assertEqual(result["reason"], "preflight_stale")
        self.assertEqual(result["dispatched"], 0)


if __name__ == "__main__":
    unittest.main()
