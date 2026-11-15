"""Hard-cut revocation and stray-credential trapping (AIV Task T4).

Implements AIV-3.1 (when a task completes, fails, or is cancelled the
Vault Broker SHALL immediately revoke the associated ``jti`` and
invalidate any active process grants) and AIV-3.2 (an agent executing an
action using an expired, revoked, or out-of-scope credential SHALL have
a ``STRAY_ACTION`` recorded in the audit log and the use SHALL be
denied) from specs/agent-identity-vault, plus the fail-closed config
rule AIV-3.4.

Revocation is a hard cut, not a TTL boundary: :func:`verify_grant`
consults the :class:`RevocationList` after the token's signature and
expiry check, so a revoked ``jti`` is denied immediately even while its
``exp`` is still in the future. :func:`revoke_grant` is the entry point
for task completion, failure, or cancellation — it adds the ``jti`` to
the revocation list and records a ``GRANT_REVOKED`` audit event.

:func:`check_use` is the stray trap. It verifies a token, consults the
revocation list, and checks that the scopes the agent wants to use are
a subset of the scopes the token grants. Any failure — malformed token,
bad signature, expired token, revoked ``jti``, or out-of-scope use — is
recorded as a ``STRAY_ACTION`` audit event (when an audit log is
provided) and the use is denied by raising :class:`StrayActionError`.
A use that passes every check returns the verified token payload.

The revocation list is in-memory by default. When a ``path`` is given
it is persisted as a JSON list of revoked ``jti`` strings, so a revoke
survives a broker restart; an unparseable revocation file fails closed
with :class:`RevocationError` (AIV-3.4). This module does not write the
JSONL audit log itself except through the :class:`~agent_vault.audit.AuditLog`
it is given; that is T4's ``agent_vault/audit.py`` scope.
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Optional

from agent_vault.audit import AuditLog
from agent_vault.token import (
    ExpiredTokenError,
    InvalidSignatureError,
    MalformedTokenError,
    TokenError,
    parse_token,
    verify_token,
)

logger = logging.getLogger(__name__)


class StrayError(Exception):
    """Base class for revocation and stray-trapping errors."""


class RevocationError(StrayError):
    """The revocation list configuration is missing or unparseable (AIV-3.4).

    Raised when a file-backed revocation list cannot be loaded or saved.
    The system fails closed: a broker that cannot trust its revocation
    state must not proceed as if no token were revoked.
    """


class RevokedTokenError(StrayError, TokenError):
    """The token's ``jti`` has been revoked (AIV-3.1).

    A subclass of :class:`~agent_vault.token.TokenError` so revocation
    composes with the token verification flow: a revoked token is a
    token validity failure, denied immediately and before its TTL
    expires.
    """


class StrayActionError(StrayError):
    """A credential use was trapped as a stray (AIV-3.2).

    Carries the denial ``reason`` and the ``STRAY_ACTION`` audit event
    that was recorded (or None when no audit log was provided).
    """

    def __init__(self, reason: str, audit_event: Optional[Dict[str, Any]] = None):
        super().__init__(reason)
        self.reason = reason
        self.audit_event = audit_event


class RevocationList:
    """The set of revoked grant ``jti`` values (AIV-3.1, AIV-3.4).

    Args:
        path: Optional JSON file persisting the revoked ``jti`` list.
            When given and the file exists, it is loaded at
            construction; when given and missing, the list starts empty
            (normal first use). When None the list is in-memory only.

    Raises:
        RevocationError: If a given file exists but is unparseable JSON,
            is not a list, or contains a non-string entry (AIV-3.4).
    """

    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path is not None else None
        self._revoked: set = set()
        if self.path is not None and self.path.exists():
            self._load()

    def _load(self) -> None:
        """Load the persisted revoked-jti list, failing closed (AIV-3.4)."""
        assert self.path is not None
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
            raise RevocationError(
                "revocation list is unparseable: " + str(self.path)
            ) from exc
        if not isinstance(data, list) or not all(
            isinstance(jti, str) and jti for jti in data
        ):
            raise RevocationError(
                "revocation list must be a JSON list of non-empty strings: "
                + str(self.path)
            )
        self._revoked = set(data)

    def _save(self) -> None:
        """Persist the revoked-jti list atomically, failing closed."""
        assert self.path is not None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise RevocationError(
                "cannot create revocation list parent directory: "
                + str(self.path.parent)
            ) from exc
        tmp_path = self.path.with_name(self.path.name + ".tmp")
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(sorted(self._revoked), f)
            os.replace(tmp_path, self.path)
        except OSError as exc:
            raise RevocationError(
                "cannot save revocation list: " + str(self.path)
            ) from exc

    def revoke(self, jti: str) -> None:
        """Add a ``jti`` to the revocation list (AIV-3.1).

        Persists the list when a path was given. Revoking an already
        revoked ``jti`` is a no-op (still persisted, still revoked).

        Raises:
            ValueError: If ``jti`` is not a non-empty string.
            RevocationError: If the list cannot be saved (AIV-3.4).
        """
        if not isinstance(jti, str) or not jti:
            raise ValueError("jti must be a non-empty string")
        self._revoked.add(jti)
        if self.path is not None:
            self._save()

    def is_revoked(self, jti: str) -> bool:
        """Return True when ``jti`` is in the revocation list."""
        return jti in self._revoked

    @property
    def revoked_jtis(self) -> FrozenSet[str]:
        """The revoked ``jti`` values as an immutable set."""
        return frozenset(self._revoked)

    def __len__(self) -> int:
        """The number of revoked ``jti`` values."""
        return len(self._revoked)


def revoke_grant(
    jti: str,
    agent_id: str,
    task_id: str,
    revocation_list: RevocationList,
    audit_log: Optional[AuditLog] = None,
    details: Optional[str] = None,
    now: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """Immediately revoke a grant ``jti`` and log the revocation (AIV-3.1).

    This is the entry point for task completion, failure, or
    cancellation: the ``jti`` is added to the revocation list (a hard
    cut — any later use is denied even before the token's TTL expires)
    and a ``GRANT_REVOKED`` audit event is recorded when an audit log
    is provided.

    Args:
        jti: Grant token id to revoke.
        agent_id: Agent identity the grant belonged to.
        task_id: Task the grant was bound to.
        revocation_list: The list to add the ``jti`` to.
        audit_log: Audit log to record the revocation in, or None to
            revoke without logging.
        details: Detail string for the audit event; defaults to
            ``"Revoked jti <jti>"``.
        now: Unix time for the event timestamp (defaults to current
            time). Exposed for deterministic testing.

    Returns:
        The recorded ``GRANT_REVOKED`` audit event, or None when no
        audit log was provided.
    """
    revocation_list.revoke(jti)
    logger.warning("revoked grant %s for %s on %s", jti, agent_id, task_id)
    if audit_log is None:
        return None
    return audit_log.append_event(
        "GRANT_REVOKED",
        agent_id,
        task_id,
        jti=jti,
        scopes=[],
        details=details if details is not None else "Revoked jti " + jti,
        now=now,
    )


def verify_grant(
    token: str,
    public_key: bytes,
    revocation_list: Optional[RevocationList] = None,
    now: Optional[int] = None,
) -> Dict[str, Any]:
    """Verify a grant token and consult the revocation list (AIV-3.1).

    Checks, in order: token structure, Ed25519 signature, scopes_hash
    consistency, expiry, and finally whether the payload's ``jti`` is
    revoked. A revoked ``jti`` raises :class:`RevokedTokenError` even
    while the token's ``exp`` is still in the future — revocation is a
    hard cut, not a TTL boundary.

    Args:
        token: The compact token string to verify.
        public_key: 32-byte Ed25519 public key of the issuing vault.
        revocation_list: Revocation list to consult, or None to skip
            the revocation check.
        now: Unix time to check expiry against (defaults to current
            time). Exposed for deterministic testing.

    Returns:
        The verified payload dict.

    Raises:
        MalformedTokenError: Token is structurally invalid.
        InvalidSignatureError: The signature does not verify.
        ExpiredTokenError: The token is past its ``exp`` claim.
        RevokedTokenError: The token's ``jti`` is revoked (AIV-3.1).
        ValueError: The public key is not 32 bytes.
    """
    payload = verify_token(token, public_key, now=now)
    if revocation_list is not None and revocation_list.is_revoked(payload["jti"]):
        raise RevokedTokenError("token jti is revoked: " + payload["jti"])
    return payload


def check_use(
    token: str,
    public_key: bytes,
    requested_scopes: List[str],
    revocation_list: Optional[RevocationList] = None,
    audit_log: Optional[AuditLog] = None,
    now: Optional[int] = None,
) -> Dict[str, Any]:
    """Trap a stray credential use or allow a valid in-scope use (AIV-3.2).

    Verifies the token (structure, signature, expiry, revocation) and
    checks that every requested scope is granted by the token. Any
    failure — malformed token, bad signature, expired token, revoked
    ``jti``, or a requested scope outside the token's scopes — is
    recorded as a ``STRAY_ACTION`` audit event (when an audit log is
    provided) and the use is denied by raising
    :class:`StrayActionError`. A use that passes every check returns
    the verified token payload.

    Args:
        token: The compact token string presented for the use.
        public_key: 32-byte Ed25519 public key of the issuing vault.
        requested_scopes: Scopes the agent wants to use. Must be a
            non-empty list of non-empty strings.
        revocation_list: Revocation list to consult, or None to skip
            the revocation check.
        audit_log: Audit log to record a ``STRAY_ACTION`` in when the
            use is trapped, or None to trap without logging.
        now: Unix time to check expiry against (defaults to current
            time). Exposed for deterministic testing.

    Returns:
        The verified token payload dict when the use is allowed.

    Raises:
        ValueError: If ``requested_scopes`` is missing, mistyped, or
            empty (a caller error, not a stray use).
        StrayActionError: If the use is trapped as a stray (AIV-3.2).
    """
    if not isinstance(requested_scopes, list) or not requested_scopes or not all(
        isinstance(scope, str) and scope for scope in requested_scopes
    ):
        raise ValueError(
            "requested_scopes must be a non-empty list of non-empty strings"
        )

    # Audit identity comes from the token payload when it parses, so a
    # trapped use is attributed even when verification itself fails.
    agent_id: Optional[str] = None
    task_id: Optional[str] = None
    jti: Optional[str] = None
    try:
        parsed = parse_token(token)
        agent_id = parsed.get("sub")
        task_id = parsed.get("task_id")
        jti = parsed.get("jti")
    except (MalformedTokenError, ValueError):
        pass

    def _trap(reason: str) -> None:
        event: Optional[Dict[str, Any]] = None
        if audit_log is not None:
            event = audit_log.append_event(
                "STRAY_ACTION",
                agent_id if agent_id else "unknown",
                task_id if task_id else "unknown",
                jti=jti,
                scopes=list(requested_scopes),
                details=reason,
                now=now,
            )
        logger.warning("stray action trapped: %s", reason)
        raise StrayActionError(reason, event)

    try:
        payload = verify_grant(token, public_key, revocation_list, now=now)
    except ExpiredTokenError:
        _trap("token has expired")
    except RevokedTokenError as exc:
        _trap(str(exc))
    except InvalidSignatureError:
        _trap("token signature does not verify")
    except MalformedTokenError:
        _trap("token is malformed")
    except TokenError as exc:
        _trap("token verification failed: " + str(exc))

    out_of_scope = sorted(set(requested_scopes) - set(payload["scopes"]))
    if out_of_scope:
        _trap(
            "requested scopes are outside the granted scopes: "
            + ", ".join(out_of_scope)
        )
    return payload
