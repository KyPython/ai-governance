"""Contract validation logic and security maps for the Completion Gate (Spec ID: COMP).

Validates completion contracts against the schema requirements defined in COMP-1.1 to COMP-1.8.
Standard library only: zero external dependencies.
"""

import json
import os
from typing import Any, Tuple, List

REQUIRED_TOP_LEVEL_KEYS = [
    "contract_version", "task_id", "instruction", "completion_criteria", "out_of_authorization_actions",
    "enforcement_points", "immutable_boundaries", "deny_route",
    "execution_contexts", "inherited_fence",
    "instruction_source", "authority_source",
    "agent_identity", "credential_grant",
    "allowed_destinations", "destination_trust", "send_contents",
    "approval_lifetime", "drift_triggers"
]

FAIL_MAP = {
    "bypasses_detected": "Boundary bypass or disabled sandbox detected (E-1)",
    "out_of_scope_reads": "Out-of-scope file access detected (E-2/E-5)",
    "mutated_approvals": "Action dispatched under mutated/voided approval (E-3/W-3)",
    "untrusted_content_as_authority": "Untrusted content accepted as authority (E-4)",
    "undeclared_credentials": "Undeclared credential derivation detected (Talked-Past-It)",
    "borrowed_human_credentials": "Agent acted under borrowed human identity (W-1)",
    "unapproved_egress": "Unapproved or adverse external network egress (W-2)",
    "adverse_egress": "Unapproved or adverse external network egress (W-2)",
}

UNKNOWN_MAP = {
    "unverified_fences": "Execution context fence unverified (E-2)",
    "unverified_authorities": "Authority source unverified (E-4)",
    "unverified_identities": "Agent identity or credential grant unverified (W-1)",
    "unverified_destinations": "Destination trust unverified (W-2)",
    "missing_periodic_evidence": "Periodic evidence missing or incomplete (W-3)",
    "omitted_events": "Material security events omitted from evidence (W-4)",
    "unverified_provenance": "Downstream code provenance unverified (W-5)",
}


def validate_contract(data: Any) -> List[str]:
    """Validates contract structure per COMP-REQ-1, returning a list of error strings."""
    if not isinstance(data, dict):
        return ["Contract must be a JSON object"]

    errors: List[str] = []
    for k in REQUIRED_TOP_LEVEL_KEYS:
        if k not in data:
            errors.append(f"Missing required field: '{k}'")

    for k in ("task_id", "instruction", "contract_version", "instruction_source", "authority_source",
              "agent_identity", "destination_trust", "approval_lifetime"):
        if k in data and (not isinstance(data[k], str) or not data[k].strip()):
            errors.append(f"'{k}' must be a non-empty string")

    if "completion_criteria" in data:
        crit = data["completion_criteria"]
        if not isinstance(crit, list) or len(crit) == 0:
            errors.append("'completion_criteria' must be a non-empty list")
        else:
            seen_ids = set()
            for idx, c in enumerate(crit):
                if not isinstance(c, dict):
                    errors.append(f"Check at index {idx} must be a dict")
                    continue
                cid = c.get("check_id")
                cmd = c.get("command")
                to = c.get("timeout_seconds")
                if not isinstance(cid, str) or not cid.strip():
                    errors.append(f"Check {idx} missing check_id")
                elif cid in seen_ids:
                    errors.append(f"Duplicate check_id: {cid}")
                else:
                    seen_ids.add(cid)
                if not isinstance(cmd, str) or not cmd.strip():
                    errors.append(f"Check {idx} missing command")
                if isinstance(to, bool) or not isinstance(to, int) or to < 1:
                    errors.append(f"Check {idx} timeout_seconds must be integer >= 1")
                if "expected_exit_code" in c:
                    errors.append(f"Check {idx} declares expected_exit_code; a check passes only on exit 0 (A1-D2)")

    if "out_of_authorization_actions" in data:
        o = data["out_of_authorization_actions"]
        if not isinstance(o, list):
            errors.append("'out_of_authorization_actions' must be a list")
        elif not any(x in o for x in ("identity_borrowing", "borrow_human_credentials")):
            errors.append("out_of_authorization_actions must include identity_borrowing or borrow_human_credentials (COMP-1.6)")

    if "deny_route" in data and data["deny_route"] != "terminal_human_intervention_only":
        errors.append("deny_route must be terminal_human_intervention_only (COMP-1.3)")

    if "inherited_fence" in data and data["inherited_fence"] is not True:
        errors.append("inherited_fence must be true (COMP-1.4)")

    for key, expected_type in [
        ("enforcement_points", dict), ("immutable_boundaries", list), ("credential_grant", dict),
        ("allowed_destinations", list), ("drift_triggers", list), ("execution_contexts", list),
        ("send_contents", list)
    ]:
        if key in data and not isinstance(data[key], expected_type):
            errors.append(f"'{key}' must be of type {expected_type.__name__}")

    if "periodic_evidence" in data and data["periodic_evidence"] is not None and not isinstance(data["periodic_evidence"], dict):
        errors.append("'periodic_evidence' must be dict or null")

    return errors


def validate_file(path: str) -> Tuple[int, str, List[str]]:
    """Reads and validates a contract JSON file per COMP-1.1 and COMP-6.1."""
    if not os.path.exists(path):
        return (2, "UNKNOWN", [f"Contract file not found: {path}"])
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        return (2, "UNKNOWN", [f"Contract JSON decode error: {exc}"])
    errors = validate_contract(data)
    if errors:
        return (2, "UNKNOWN", errors)
    return (0, "VALID", [])
