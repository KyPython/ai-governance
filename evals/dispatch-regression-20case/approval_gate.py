"""Reference approval boundary for a *simulated*, never-networked send operation.

This is a fixture policy implementation, not a deployed agent or authorization service.
A real integration must fetch approvals and preflight evidence from trusted infrastructure.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Any

# Deliberately strict: adding capabilities (attachments, extra recipients, etc.)
# requires a new approval envelope schema and new tests.
INTENT_FIELDS = frozenset({
    "action", "channel", "sender", "to", "cc", "bcc",
    "subject", "body", "reply_to", "attachments"
})


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Time must include UTC offset")
    return parsed.astimezone(timezone.utc)


def _intent_hash(intent: dict[str, Any]) -> str:
    if not isinstance(intent, dict) or set(intent) != INTENT_FIELDS:
        raise ValueError("intent has missing/unknown fields")
    for field in ("action", "channel", "sender", "subject", "body", "reply_to"):
        if not isinstance(intent[field], str):
            raise ValueError(f"{field} must be text")
    for field in ("to", "cc", "bcc", "attachments"):
        if not isinstance(intent[field], list) or not all(isinstance(x, str) for x in intent[field]):
            raise ValueError(f"{field} must be an array of text")
    if not intent["to"] or any(not x for x in intent["to"]):
        raise ValueError("at least one non-empty recipient required")
    # Normalize only email case/spacing, NOT subject/body/attachments or recipient set.
    normalized = dict(intent)
    for field in ("to", "cc", "bcc"):
        normalized[field] = sorted(x.strip().lower() for x in intent[field])
    normalized["sender"] = intent["sender"].strip().lower()
    payload = json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class RecordingTransport:
    """Captures events only. This object cannot deliver an email or message."""
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def send(self, *, intent_hash: str, approval_id: str, idempotency_key: str) -> None:
        self.events.append({
            "event": "simulated_dispatch",
            "intent_sha256": intent_hash,
            "approval_id": approval_id,
            "idempotency_key": idempotency_key,
        })


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    """Enforce evidence-backed approvals at a mocked side-effect boundary."""
    request = case["request"]
    trusted = case["trusted"]
    sink = RecordingTransport()

    def finish(reason: str, intent_hash: str | None = None) -> dict[str, Any]:
        return {
            "decision": "ALLOW" if sink.events else "BLOCK",
            "reason": reason,
            "dispatched": len(sink.events),
            "dispatch_events": list(sink.events),
            "intent_sha256": intent_hash,
        }

    # Trusted state must be supplied by a preflight/approval service, NEVER an agent string.
    if trusted["preflight"] is not True:
        return finish("preflight_failed")
    if trusted["preflight_policy_revision"] != trusted["policy_revision"]:
        return finish("preflight_stale")

    approval_id = request.get("approval_id")
    if not isinstance(approval_id, str) or not approval_id:
        return finish("approval_missing")

    approvals = [grant for grant in trusted["approvals"] if grant["id"] == approval_id]
    if len(approvals) != 1:
        return finish("approval_unknown")
    grant = approvals[0]
    if grant["status"] != "approved":
        return finish("approval_not_approved")
    if grant["authorized_by"] not in trusted["human_approvers"] or not grant["authorized_by"].startswith("human:"):
        return finish("approver_not_authorized")
    revoked = grant.get("revoked")
    if not isinstance(revoked, bool):
        return finish("approval_revoked_invalid")
    if revoked is True:
        return finish("approval_revoked")

    now = _parse_time(trusted["now"])
    if now < _parse_time(grant["issued_at"]):
        return finish("approval_not_yet_valid")
    if now >= _parse_time(grant["expires_at"]):
        return finish("approval_expired")
    if grant["policy_revision"] != trusted["policy_revision"]:
        return finish("policy_revision_mismatch")
    if grant["workflow_id"] != request.get("workflow_id"):
        return finish("workflow_mismatch")
    if approval_id in trusted["consumed_approval_ids"]:
        return finish("approval_already_consumed")
    idempotency_key = request.get("idempotency_key")
    approved_key = grant.get("idempotency_key")
    if any(not isinstance(key, str) or not key.strip()
           for key in (idempotency_key, approved_key)):
        return finish("idempotency_key_invalid")
    if idempotency_key in trusted["used_idempotency_keys"]:
        return finish("idempotency_key_reused")
    if approved_key != idempotency_key:
        return finish("idempotency_key_mismatch")

    try:
        actual_hash = _intent_hash(request["intent"])
        approved_hash = _intent_hash(grant["approved_intent"])
    except (KeyError, TypeError, ValueError):
        return finish("invalid_intent")
    if not hmac.compare_digest(actual_hash, approved_hash):
        return finish("approval_scope_mismatch", actual_hash)

    # This is the ONLY point at which an effect can execute. The transport is inert.
    sink.send(intent_hash=actual_hash, approval_id=approval_id,
              idempotency_key=idempotency_key)
    # Keep sequential calls sharing this trusted state from replaying the effect.
    # Production storage must make dispatch and consumption atomic under concurrency.
    trusted["consumed_approval_ids"].append(approval_id)
    trusted["used_idempotency_keys"].append(idempotency_key)
    return finish("dispatched", actual_hash)
