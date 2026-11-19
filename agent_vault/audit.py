"""Append-only JSONL audit log for agent identity and vault credentials.

Implements AIV-3.3 (all credential requests, grants, rejections,
revocations, and stray detections are written to an append-only JSONL
audit log at ``logs/vault-audit.jsonl``) and AIV-3.4 (a missing or
unparseable configuration fails closed) from specs/agent-identity-vault.

Event schema (design.md section 3.3): one JSON object per line with
``timestamp`` (ISO-8601 UTC, milliseconds, ``Z`` suffix), ``event_type``
(one of ``GRANT_ISSUED``, ``GRANT_REJECTED``, ``GRANT_REVOKED``,
``STRAY_ACTION``), ``agent_id``, ``task_id``, ``jti``, ``scopes``, and
``details``.

The log is append-only: events are written with mode ``"a"`` and this
module never rewrites, truncates, or deletes existing entries. A missing
log file is created on first append. A missing or unparseable
configuration — a log path that is a directory, an unwritable parent, or
a corrupt existing log on read — raises :class:`AuditLogError` and fails
closed.

This module also provides the persistence entry points for the broker's
audit-shaped records: :func:`record_grant_issued` turns a broker
:class:`~agent_vault.broker.Grant` into a ``GRANT_ISSUED`` event, and
:func:`flush_authorization_failures` persists the broker's
``authorization_failures`` (``GRANT_REJECTED`` records) to the log. The
broker itself is not modified by T4; the owner console (T6) and the
completion gate (T7) call these helpers to wire issuance and rejection
into the log.
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

#: Default audit log location (design.md section 3.3, AIV-3.3).
DEFAULT_AUDIT_LOG_PATH = (
    Path(__file__).resolve().parent.parent / "logs" / "vault-audit.jsonl"
)

#: Event types permitted in the audit log (design.md section 3.3).
EVENT_TYPES = frozenset(
    {"GRANT_ISSUED", "GRANT_REJECTED", "GRANT_REVOKED", "STRAY_ACTION"}
)


class AuditLogError(Exception):
    """The audit log configuration is missing or unparseable (AIV-3.4).

    Raised when the log path is a directory, its parent cannot be created
    or written, an append fails, or an existing log line is corrupt on
    read. The system fails closed: no event is recorded and no caller
    may proceed as if the audit write succeeded.
    """


def _iso8601_utc(timestamp: int) -> str:
    """Format a Unix timestamp as ISO-8601 UTC with a ``Z`` suffix."""
    return (
        datetime.fromtimestamp(timestamp, tz=timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def build_event(
    event_type: str,
    agent_id: str,
    task_id: str,
    jti: Optional[str] = None,
    scopes: Optional[List[str]] = None,
    details: str = "",
    now: Optional[int] = None,
) -> Dict[str, Any]:
    """Build an audit event dict in the design.md section 3.3 schema.

    Args:
        event_type: One of ``EVENT_TYPES``.
        agent_id: Agent identity the event concerns.
        task_id: Task the event concerns.
        jti: Grant token id, or None when the event has no grant (for
            example a rejection before any token existed).
        scopes: Scopes involved; defaults to an empty list.
        details: Human-readable detail string.
        now: Unix time for ``timestamp`` (defaults to the current time).
            Exposed for deterministic testing.

    Returns:
        The event dict. It is not written; use :class:`AuditLog` to
        append it.

    Raises:
        ValueError: If the event type is unknown or any argument is
            missing, mistyped, or out of range.
    """
    if event_type not in EVENT_TYPES:
        raise ValueError("unknown audit event_type: " + str(event_type))
    if not isinstance(agent_id, str) or not agent_id:
        raise ValueError("agent_id must be a non-empty string")
    if not isinstance(task_id, str) or not task_id:
        raise ValueError("task_id must be a non-empty string")
    if jti is not None and (not isinstance(jti, str) or not jti):
        raise ValueError("jti must be a non-empty string or None")
    if scopes is not None and (
        not isinstance(scopes, list)
        or not all(isinstance(scope, str) and scope for scope in scopes)
    ):
        raise ValueError("scopes must be a list of non-empty strings or None")
    if not isinstance(details, str):
        raise ValueError("details must be a string")
    timestamp = int(now if now is not None else time.time())
    return {
        "timestamp": _iso8601_utc(timestamp),
        "event_type": event_type,
        "agent_id": agent_id,
        "task_id": task_id,
        "jti": jti,
        "scopes": list(scopes) if scopes is not None else [],
        "details": details,
    }


def _validate_record(record: Dict[str, Any]) -> None:
    """Check a pre-shaped audit record before it is appended.

    Raises ValueError when the record is not a dict, has an unknown
    event type, or is missing a required field.
    """
    if not isinstance(record, dict):
        raise ValueError("audit record must be a dict")
    if record.get("event_type") not in EVENT_TYPES:
        raise ValueError(
            "audit record has unknown event_type: " + str(record.get("event_type"))
        )
    for field in ("timestamp", "agent_id", "task_id"):
        if field not in record:
            raise ValueError("audit record is missing field: " + field)


class AuditLog:
    """Append-only JSONL audit log (AIV-3.3, AIV-3.4).

    Args:
        path: Log file path. Defaults to ``logs/vault-audit.jsonl`` in
            the repository root. The file is created on first append;
            its parent directories are created on first append too.

    Raises:
        AuditLogError: If the path exists and is not a file, or its
            parent exists and is not a directory (AIV-3.4) — the log
            fails closed at construction.
    """

    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path is not None else DEFAULT_AUDIT_LOG_PATH
        if self.path.exists() and not self.path.is_file():
            raise AuditLogError(
                "audit log path is not a file: " + str(self.path)
            )
        parent = self.path.parent
        if parent.exists() and not parent.is_dir():
            raise AuditLogError(
                "audit log parent is not a directory: " + str(parent)
            )

    def append(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Append one pre-shaped audit record as a single JSONL line.

        The record is validated (unknown event type or a missing field
        raises ValueError) and then written in append mode, so existing
        entries are never rewritten or truncated (AIV-3.3).

        Returns:
            The record that was appended.

        Raises:
            ValueError: If the record is malformed.
            AuditLogError: If the parent cannot be created or the append
                fails (AIV-3.4).
        """
        _validate_record(record)
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise AuditLogError(
                "cannot create audit log parent directory: "
                + str(self.path.parent)
            ) from exc
        line = json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(line)
        except OSError as exc:
            raise AuditLogError(
                "cannot append to audit log: " + str(self.path)
            ) from exc
        return record

    def append_event(
        self,
        event_type: str,
        agent_id: str,
        task_id: str,
        jti: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        details: str = "",
        now: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Build an event with :func:`build_event` and append it.

        Returns the appended event dict.
        """
        return self.append(
            build_event(
                event_type,
                agent_id,
                task_id,
                jti=jti,
                scopes=scopes,
                details=details,
                now=now,
            )
        )

    def read_events(self) -> List[Dict[str, Any]]:
        """Read back every event in the log, in append order.

        Returns an empty list when the log file does not exist yet.

        Raises:
            AuditLogError: If the log exists but a line is not a valid
                JSON object (AIV-3.4) — a corrupt log fails closed
                rather than silently skipping entries.
        """
        if not self.path.exists():
            return []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
        except OSError as exc:
            raise AuditLogError(
                "cannot read audit log: " + str(self.path)
            ) from exc
        events: List[Dict[str, Any]] = []
        for line in lines:
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise AuditLogError(
                    "audit log contains a corrupt line: " + str(self.path)
                ) from exc
            if not isinstance(event, dict):
                raise AuditLogError(
                    "audit log contains a non-object line: " + str(self.path)
                )
            events.append(event)
        return events


def record_grant_issued(audit_log: AuditLog, grant: Any, now: Optional[int] = None) -> Dict[str, Any]:
    """Record a broker-issued grant as a ``GRANT_ISSUED`` event (AIV-3.3).

    Args:
        audit_log: The log to append to.
        grant: A :class:`~agent_vault.broker.Grant` (any object with
            ``agent_id``, ``task_id``, ``jti``, ``scopes``, and
            ``ttl_seconds`` attributes).
        now: Unix time for the event timestamp (defaults to current
            time). Exposed for deterministic testing.

    Returns:
        The appended event dict.
    """
    details = (
        "Granted "
        + str(grant.ttl_seconds)
        + "s TTL against scope contract"
    )
    return audit_log.append_event(
        "GRANT_ISSUED",
        grant.agent_id,
        grant.task_id,
        jti=grant.jti,
        scopes=list(grant.scopes),
        details=details,
        now=now,
    )


def flush_authorization_failures(audit_log: AuditLog, broker: Any) -> int:
    """Persist a broker's ``GRANT_REJECTED`` records to the log (AIV-3.3).

    Appends every record currently in ``broker.authorization_failures``
    (the audit-shaped records T3 records on each fail-closed DENY,
    AIV-1.4). The broker's list is not cleared; callers that flush
    repeatedly should snapshot and clear it themselves to avoid
    appending the same record twice.

    Args:
        audit_log: The log to append to.
        broker: A :class:`~agent_vault.broker.VaultBroker` (any object
            with an ``authorization_failures`` list of audit-shaped
            records).

    Returns:
        The number of records appended.
    """
    count = 0
    for record in broker.authorization_failures:
        audit_log.append(record)
        count += 1
    return count
