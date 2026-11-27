"""Owner console CLI (``govctl``) for agent identity and vault (AIV Task T6).

Implements AIV-6.1 (a local CLI tool requiring $0 external
infrastructure), AIV-6.2 (``govctl grants list`` displays all active
grants with their bound ``agent_id``, ``task_id``, scopes, and remaining
TTL), and AIV-6.3 (``govctl revoke --all`` or ``govctl revoke
<grant_id>`` immediately invalidates the designated grants in the local
broker) from specs/agent-identity-vault, plus the fail-closed config
rule AIV-3.4.

Source of active grants
-----------------------
There is no separate persistent grant store in T2/T3/T4: the broker
issues grants in memory and the only durable record of issuance is the
append-only JSONL audit log (``logs/vault-audit.jsonl``, AIV-3.3).
``govctl`` therefore reconstructs the active-grant set from the audit
log itself:

* a grant is **issued** when a ``GRANT_ISSUED`` event names its ``jti``;
* a grant is **revoked** when its ``jti`` appears in a ``GRANT_REVOKED``
  event *or* in the :class:`~agent_vault.stray.RevocationList`
  (the list is what :func:`~agent_vault.stray.verify_grant` consults,
  so it is authoritative even for a revoke that was never logged);
* a grant is **expired** when its issue time plus its TTL is in the past.

A grant is active when it is issued, not revoked, and not expired.
The issue time is the ``GRANT_ISSUED`` event's timestamp and the TTL is
parsed from the event's details string (``record_grant_issued`` writes
``"Granted <n>s TTL against scope contract"``); a grant whose TTL
cannot be parsed is listed with an unknown remaining TTL rather than
being silently dropped, because the revocation check — not the TTL
display — is the hard security gate.

Revocation wiring (the T6 half of T4)
-------------------------------------
``govctl revoke`` calls :func:`~agent_vault.stray.revoke_grant`, which
adds the ``jti`` to the revocation list (a hard cut — any later use is
denied even before the token's TTL expires, AIV-3.1) and records a
``GRANT_REVOKED`` audit event (design.md section 3.3). This is the
wiring T4 left open: the broker's in-memory denials become durable
revocations only through this CLI. Revoking a ``jti`` that has no
``GRANT_ISSUED`` event is still performed (fail-safe — a revoked
unknown ``jti`` can only deny, never grant) but exits non-zero with a
warning, because the operator most likely mistyped the id.

Exit codes (design.md section 4)
---------------------------------
* ``0`` — the command succeeded.
* ``1`` — operational failure (for example an unknown grant id on
  revoke, or a denied use).
* ``2`` — missing or unparseable configuration (AIV-3.4); the CLI fails
  closed and does nothing.

Entry point
-----------
The repo has no packaging file (no ``pyproject.toml`` / ``setup.py`` /
``setup.cfg``), so there is no console-script entry point to wire.
``govctl`` is invoked as ``python -m agent_vault.cli`` from the repo
root, and :func:`main` is the importable entry point tests call
directly.
"""

import argparse
import logging
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent_vault.audit import (
    DEFAULT_AUDIT_LOG_PATH,
    AuditLog,
    AuditLogError,
)
from agent_vault.stray import (
    RevocationError,
    RevocationList,
    revoke_grant,
)

logger = logging.getLogger(__name__)

#: Default revocation list location. T4's ``RevocationList`` is
#: file-backed when given a path; there is no repo-wide default, so the
#: CLI defines one next to the audit log (design.md section 4.3:
#: "``govctl revoke`` writes to local active grant revocation list").
DEFAULT_REVOCATION_PATH = (
    Path(__file__).resolve().parent.parent / "logs" / "vault-revoked.json"
)

#: Details format written by ``record_grant_issued`` (AIV-3.3).
_ISSUED_DETAILS_RE = re.compile(r"^Granted (\d+)s TTL")


class CliError(Exception):
    """An operational CLI failure (exit 1)."""


class ConfigError(CliError):
    """A missing or unparseable configuration (AIV-3.4, exit 2)."""


def _parse_iso8601_utc(value: str) -> Optional[int]:
    """Parse an ISO-8601 UTC timestamp to a Unix time, or None.

    Accepts the ``Z`` suffix written by the audit log. Returns None
    when the value is not a parseable timestamp, so a single malformed
    event never aborts a listing.
    """
    if not isinstance(value, str) or not value:
        return None
    try:
        return int(
            datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
        )
    except (ValueError, OverflowError, OSError):
        return None


def _parse_issued_ttl(details: str) -> Optional[int]:
    """Parse the TTL seconds from a ``GRANT_ISSUED`` details string.

    ``record_grant_issued`` writes ``"Granted <n>s TTL against scope
    contract"``. Returns None when the details do not match that
    format (for example an event appended by hand), so the grant is
    listed with an unknown remaining TTL.
    """
    if not isinstance(details, str):
        return None
    match = _ISSUED_DETAILS_RE.match(details)
    if match is None:
        return None
    return int(match.group(1))


def list_active_grants(
    audit_log: AuditLog,
    revocation_list: Optional[RevocationList] = None,
    now: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Reconstruct the active grants from the audit log (AIV-6.2).

    A grant is active when it has a ``GRANT_ISSUED`` event, its ``jti``
    is neither in a ``GRANT_REVOKED`` event nor in the revocation
    list, and it has not expired (issue time plus TTL is in the future).
    Grants whose TTL cannot be parsed are listed with
    ``remaining_seconds`` None (unknown) rather than dropped.

    Args:
        audit_log: The append-only audit log to read issued and
            revoked events from.
        revocation_list: The revocation list to consult, or None to
            consult only the ``GRANT_REVOKED`` events.
        now: Unix time to check expiry against (defaults to current
            time). Exposed for deterministic testing.

    Returns:
        Active grants as dicts with ``jti``, ``agent_id``, ``task_id``,
        ``scopes``, ``issued_at`` (ISO-8601 string), ``ttl_seconds``
        (or None), and ``remaining_seconds`` (or None when unknown),
        sorted by issue time, oldest first.
    """
    current = int(now if now is not None else time.time())
    events = audit_log.read_events()

    issued: Dict[str, Dict[str, Any]] = {}
    revoked: set = set()
    for event in events:
        event_type = event.get("event_type")
        jti = event.get("jti")
        if event_type == "GRANT_ISSUED" and isinstance(jti, str) and jti:
            issued[jti] = {
                "jti": jti,
                "agent_id": event.get("agent_id", "unknown"),
                "task_id": event.get("task_id", "unknown"),
                "scopes": list(event.get("scopes") or []),
                "issued_at": event.get("timestamp", ""),
                "ttl_seconds": _parse_issued_ttl(event.get("details", "")),
                "_issued_unix": _parse_iso8601_utc(event.get("timestamp", "")),
            }
        elif event_type == "GRANT_REVOKED" and isinstance(jti, str) and jti:
            revoked.add(jti)

    if revocation_list is not None:
        revoked.update(revocation_list.revoked_jtis)

    active: List[Dict[str, Any]] = []
    for jti, grant in issued.items():
        if jti in revoked:
            continue
        ttl = grant["ttl_seconds"]
        issued_unix = grant["_issued_unix"]
        if ttl is not None and issued_unix is not None:
            remaining = (issued_unix + ttl) - current
            if remaining <= 0:
                continue
            grant["remaining_seconds"] = remaining
        else:
            grant["remaining_seconds"] = None
        active.append(
            {
                "jti": grant["jti"],
                "agent_id": grant["agent_id"],
                "task_id": grant["task_id"],
                "scopes": grant["scopes"],
                "issued_at": grant["issued_at"],
                "ttl_seconds": grant["ttl_seconds"],
                "remaining_seconds": grant["remaining_seconds"],
            }
        )
    active.sort(key=lambda g: (g["issued_at"], g["jti"]))
    return active


def format_grants(grants: List[Dict[str, Any]]) -> str:
    """Format active grants as a human-readable table (AIV-6.2)."""
    if not grants:
        return "No active grants."
    lines = ["jti  agent_id  task_id  scopes  remaining"]
    for grant in grants:
        remaining = grant["remaining_seconds"]
        remaining_text = (
            str(remaining) + "s" if remaining is not None else "unknown"
        )
        lines.append(
            grant["jti"]
            + "  "
            + str(grant["agent_id"])
            + "  "
            + str(grant["task_id"])
            + "  "
            + ", ".join(grant["scopes"])
            + "  "
            + remaining_text
        )
    return "\n".join(lines)


def _grant_attribution(
    audit_log: AuditLog, jti: str
) -> Dict[str, str]:
    """Find the agent/task a ``jti`` was issued to, or "unknown".

    Looks up the latest ``GRANT_ISSUED`` event for the ``jti``. Used so
    a ``GRANT_REVOKED`` event is attributed to the grant's owner when
    the owner is known.
    """
    agent_id = "unknown"
    task_id = "unknown"
    for event in audit_log.read_events():
        if event.get("event_type") == "GRANT_ISSUED" and event.get("jti") == jti:
            agent_id = event.get("agent_id") or "unknown"
            task_id = event.get("task_id") or "unknown"
    return {"agent_id": agent_id, "task_id": task_id}


def revoke_grant_by_id(
    jti: str,
    audit_log: AuditLog,
    revocation_list: RevocationList,
    now: Optional[int] = None,
) -> Dict[str, Any]:
    """Revoke one grant by ``jti`` (AIV-6.3).

    Writes the ``jti`` to the revocation list and records a
    ``GRANT_REVOKED`` audit event (the T6 wiring of T4). Revoking a
    ``jti`` with no ``GRANT_ISSUED`` event is still performed
    (fail-safe) but raises :class:`CliError`, because the operator most
    likely mistyped the id.

    Args:
        jti: Grant token id to revoke.
        audit_log: The audit log to record the revocation in.
        revocation_list: The revocation list to add the ``jti`` to.
        now: Unix time for the event timestamp (defaults to current
            time). Exposed for deterministic testing.

    Returns:
        The recorded ``GRANT_REVOKED`` audit event.

    Raises:
        ValueError: If ``jti`` is not a non-empty string.
        CliError: If the ``jti`` has no ``GRANT_ISSUED`` event (the
            revocation itself still happened).
        AuditLogError / RevocationError: If the audit log or the
            revocation list fails (AIV-3.4).
    """
    if not isinstance(jti, str) or not jti:
        raise ValueError("jti must be a non-empty string")
    attribution = _grant_attribution(audit_log, jti)
    event = revoke_grant(
        jti,
        attribution["agent_id"],
        attribution["task_id"],
        revocation_list,
        audit_log,
        now=now,
    )
    if attribution["agent_id"] == "unknown":
        raise CliError(
            "grant "
            + jti
            + " not found in audit log; revoked defensively "
            "(added to revocation list and logged)"
        )
    return event


def revoke_all_grants(
    audit_log: AuditLog,
    revocation_list: RevocationList,
    now: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Revoke every active grant (AIV-6.3).

    Revokes each grant returned by :func:`list_active_grants` in turn.
    A grant that was already revoked between the listing and its revoke
    is a no-op (the revocation list deduplicates).

    Args:
        audit_log: The audit log to record the revocations in.
        revocation_list: The revocation list to add the ``jti`` values
            to.
        now: Unix time for the event timestamps (defaults to current
            time). Exposed for deterministic testing.

    Returns:
        The recorded ``GRANT_REVOKED`` audit events, one per revoked
        grant.
    """
    events: List[Dict[str, Any]] = []
    for grant in list_active_grants(audit_log, revocation_list, now=now):
        events.append(
            revoke_grant(
                grant["jti"],
                grant["agent_id"],
                grant["task_id"],
                revocation_list,
                audit_log,
                now=now,
            )
        )
    return events


def build_parser() -> argparse.ArgumentParser:
    """Build the ``govctl`` argument parser (AIV-6.1)."""
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--audit-log",
        type=Path,
        default=None,
        help="audit log path (default: logs/vault-audit.jsonl)",
    )
    common.add_argument(
        "--revocation-list",
        type=Path,
        default=None,
        help="revocation list path (default: logs/vault-revoked.json)",
    )

    # The shared options live only on the leaf subparsers (``list`` and
    # ``revoke``), not on the top-level or intermediate parsers:
    # argparse lets a subparser's default overwrite a value the parent
    # already parsed, so defining the same option at two levels would
    # silently drop a path given before the subcommand.
    parser = argparse.ArgumentParser(
        prog="govctl",
        description="Owner console for agent identity and vault grants.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    grants_parser = subparsers.add_parser("grants", help="inspect grants")
    grants_sub = grants_parser.add_subparsers(
        dest="grants_command", required=True
    )
    grants_sub.add_parser(
        "list",
        parents=[common],
        help="display all active grants (AIV-6.2)",
    )

    revoke_parser = subparsers.add_parser(
        "revoke",
        parents=[common],
        help="immediately invalidate grants (AIV-6.3)",
    )
    revoke_parser.add_argument(
        "grant_id",
        nargs="?",
        default=None,
        help="grant jti to revoke (omit with --all)",
    )
    revoke_parser.add_argument(
        "--all",
        action="store_true",
        help="revoke every active grant",
    )
    return parser


def _open_state(args: argparse.Namespace) -> tuple:
    """Open the audit log and revocation list, failing closed (AIV-3.4).

    Returns the ``(AuditLog, RevocationList)`` pair. Raises
    :class:`ConfigError` (exit 2) when either is missing or
    unparseable.
    """
    audit_path = (
        args.audit_log if args.audit_log is not None else DEFAULT_AUDIT_LOG_PATH
    )
    revocation_path = (
        args.revocation_list
        if args.revocation_list is not None
        else DEFAULT_REVOCATION_PATH
    )
    try:
        audit_log = AuditLog(audit_path)
    except AuditLogError as exc:
        raise ConfigError("audit log configuration failed: " + str(exc)) from exc
    try:
        revocation_list = RevocationList(revocation_path)
    except RevocationError as exc:
        raise ConfigError(
            "revocation list configuration failed: " + str(exc)
        ) from exc
    return audit_log, revocation_list


def main(argv: Optional[List[str]] = None) -> int:
    """Run the ``govctl`` CLI. Returns a process exit code.

    ``argv`` is the argument list without the program name (defaults to
    ``sys.argv[1:]``). Returns 0 on success, 1 on an operational
    failure, and 2 on a missing or unparseable configuration (AIV-3.4).
    """
    args = build_parser().parse_args(argv)
    try:
        audit_log, revocation_list = _open_state(args)
    except ConfigError as exc:
        print("govctl: " + str(exc), file=sys.stderr)
        return 2

    try:
        if args.command == "grants" and args.grants_command == "list":
            grants = list_active_grants(audit_log, revocation_list)
            print(format_grants(grants))
            return 0
        if args.command == "revoke":
            if args.all:
                events = revoke_all_grants(audit_log, revocation_list)
                print("Revoked " + str(len(events)) + " grant(s).")
                return 0
            if args.grant_id is None:
                print(
                    "govctl revoke: specify a grant id or --all",
                    file=sys.stderr,
                )
                return 1
            try:
                revoke_grant_by_id(
                    args.grant_id, audit_log, revocation_list
                )
            except CliError as exc:
                print("govctl: " + str(exc), file=sys.stderr)
                return 1
            print("Revoked grant " + args.grant_id + ".")
            return 0
    except (AuditLogError, RevocationError) as exc:
        print("govctl: " + str(exc), file=sys.stderr)
        return 2
    except (ValueError, CliError) as exc:
        print("govctl: " + str(exc), file=sys.stderr)
        return 1
    print("govctl: unknown command", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
