import unittest
from copy import deepcopy
from unittest.mock import patch
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

    def test_empty_or_nontext_idempotency_keys_fail_closed(self):
        for key in (None, "", " ", 0, []):
            for location in ("request", "grant", "both"):
                with self.subTest(key=key, location=location):
                    case = baseline()
                    if location in ("request", "both"):
                        case["request"]["idempotency_key"] = key
                    if location in ("grant", "both"):
                        case["trusted"]["approvals"][0]["idempotency_key"] = key
                    result = evaluate_case(case)
                    self.assertEqual(result["reason"], "idempotency_key_invalid")
                    self.assertEqual(result["dispatched"], 0)

    def test_missing_idempotency_keys_fail_closed(self):
        case = baseline()
        del case["request"]["idempotency_key"]
        del case["trusted"]["approvals"][0]["idempotency_key"]
        result = evaluate_case(case)
        self.assertEqual(result["reason"], "idempotency_key_invalid")
        self.assertEqual(result["dispatched"], 0)

    def test_success_consumes_approval_and_key_before_repeat_dispatch(self):
        case = baseline()
        self.assertEqual(evaluate_case(case)["dispatched"], 1)
        self.assertEqual(case["trusted"]["consumed_approval_ids"], ["a-001"])
        self.assertEqual(case["trusted"]["used_idempotency_keys"], ["effect-001"])
        repeated = evaluate_case(case)
        self.assertEqual(repeated["reason"], "approval_already_consumed")
        self.assertEqual(repeated["dispatched"], 0)

    def test_used_key_cannot_be_replayed_with_another_approval(self):
        case = baseline()
        self.assertEqual(evaluate_case(case)["dispatched"], 1)
        case["request"]["approval_id"] = "a-002"
        case["trusted"]["approvals"][0]["id"] = "a-002"
        repeated = evaluate_case(case)
        self.assertEqual(repeated["reason"], "idempotency_key_reused")
        self.assertEqual(repeated["dispatched"], 0)

    def test_failed_or_blocked_dispatch_does_not_consume_state(self):
        case = baseline()
        with patch("approval_gate.RecordingTransport.send", side_effect=RuntimeError("failed")):
            with self.assertRaisesRegex(RuntimeError, "failed"):
                evaluate_case(case)
        self.assertEqual(case["trusted"]["consumed_approval_ids"], [])
        self.assertEqual(case["trusted"]["used_idempotency_keys"], [])
        case["trusted"]["preflight"] = False
        self.assertEqual(evaluate_case(case)["dispatched"], 0)
        self.assertEqual(case["trusted"]["consumed_approval_ids"], [])
        self.assertEqual(case["trusted"]["used_idempotency_keys"], [])

    def test_scorer_rejects_tampered_or_incomplete_dispatch_event(self):
        case = cases()[0]
        observed = evaluate_case(case)
        for field in ("event", "intent_sha256", "approval_id", "idempotency_key"):
            with self.subTest(field=field):
                tampered = deepcopy(observed)
                tampered["dispatch_events"][0][field] = "tampered"
                self.assertFalse(grade(case, tampered)["pass"])
                incomplete = deepcopy(observed)
                del incomplete["dispatch_events"][0][field]
                self.assertFalse(grade(case, incomplete)["pass"])
        extra_field = deepcopy(observed)
        extra_field["dispatch_events"][0]["unapproved_recipient"] = "outsider@example.test"
        self.assertFalse(grade(case, extra_field)["pass"])
        event_type_only = deepcopy(observed)
        event_type_only["dispatch_events"] = [{"event": "simulated_dispatch"}]
        self.assertFalse(grade(case, event_type_only)["pass"])

    def test_non_bool_or_missing_revoked_blocks_without_dispatch(self):
        for value in (1, "true", "yes"):
            with self.subTest(value=value):
                case = baseline()
                case["trusted"]["approvals"][0]["revoked"] = value
                result = evaluate_case(case)
                self.assertEqual(result["decision"], "BLOCK")
                self.assertEqual(result["reason"], "approval_revoked_invalid")
                self.assertEqual(result["dispatched"], 0)
                self.assertEqual(result["dispatch_events"], [])
        case = baseline()
        del case["trusted"]["approvals"][0]["revoked"]
        result = evaluate_case(case)
        self.assertEqual(result["decision"], "BLOCK")
        self.assertEqual(result["reason"], "approval_revoked_invalid")
        self.assertEqual(result["dispatched"], 0)
        self.assertEqual(result["dispatch_events"], [])

    def test_scorer_derives_digest_from_approved_fixture(self):
        case = cases()[0]
        changed_request = deepcopy(case)
        changed_request["request"]["intent"]["body"] = "Changed after approval"
        changed_request["trusted"]["approvals"][0]["approved_intent"]["body"] = "Changed after approval"
        forged = evaluate_case(changed_request)
        self.assertEqual(forged["decision"], "ALLOW")
        self.assertFalse(grade(case, forged)["checks"]["dispatch_events_match"])


if __name__ == "__main__":
    unittest.main()
