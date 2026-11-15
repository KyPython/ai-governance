"""Vault Broker: grant request handler with TTL bounding (AIV Task T3).

Implements AIV-1.3, AIV-1.4, AIV-2.1, AIV-2.2, AIV-2.4, and AIV-2.5 from
specs/agent-identity-vault, plus the fail-closed config rule AIV-3.4.

The broker is the only path to a signed grant token. A grant request is
checked, in order, against:

1. The agent registry (``registry/agents.json``): the declared ``agent_id``
   must exist and the requested scopes must be a subset of that agent's
   registered ``permitted_capabilities`` (AIV-1.3). An unknown agent or an
   excess capability is a fail-closed ``DENY`` and the authorization failure
   is logged (AIV-1.4).
2. Approver separation: ``approver != requester``; an agent SHALL NOT
   authorize its own grant or scope elevation (AIV-2.4).
3. The human-curated scope contract (``scopes.json`` or
   ``completion-contract.json``): the exclusive Source of Truth for
   permitted execution scopes (AIV-2.5). A scope outside the contract is
   denied even if the registry would allow it.
4. TTL bounding: a grant gets a default TTL of 15 minutes (AIV-2.1); a
   requested TTL above 60 minutes is clamped to 60 minutes and the clamp is
   recorded on the returned grant (AIV-2.2).

A grant that passes every check is issued by signing a token through
``agent_vault/token.py`` (T2) with ``agent_id``, ``role`` (taken from the
registry, never caller-supplied), ``task_id``, ``scopes``, ``scopes_hash``,
``iat``, ``exp``, and ``jti``.

Fail-closed behaviour (AIV-3.4): a missing or unparseable registry or scope
contract makes the broker refuse to construct (``BrokerConfigError``), and
any denial raises ``GrantDeniedError`` — no token is ever issued on a failed
check.

Authorization failures are recorded in ``VaultBroker.authorization_failures``
as audit-shaped records (``event_type`` ``"GRANT_REJECTED"``, following
design.md section 3.3) and also emitted through the ``logging`` module, so
Task T4 (``agent_vault/audit.py``) can persist them to
``logs/vault-audit.jsonl``. This module does not write the JSONL audit log
itself; that is T4's scope.

Scope contract format (human-curated, either shape is accepted):

- ``scopes.json`` shape: ``{"permitted_scopes": ["repo:read", ...]}``.
- ``completion-contract.json`` shape: ``{"credential_grant": {"<name>":
  "<scope>" | ["<scope>", ...], ...}}`` — the permitted scopes are the
  union of the mapping's values.

Either shape must yield a non-empty permitted-scopes set; otherwise the
contract is unparseable and the broker fails closed.
"""

import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from agent_vault.registry import DEFAULT_REGISTRY_PATH, get_agent
from agent_vault.token import (
    DEFAULT_TTL_SECONDS,
    create_token,
    ed25519_public_key,
    parse_token,
)

logger = logging.getLogger(__name__)

#: Hard maximum grant lifetime in seconds (60 minutes, AIV-2.2).
MAX_TTL_SECONDS = 3600


class BrokerError(Exception):
    """Base class for Vault Broker errors."""


class BrokerConfigError(BrokerError):
    """The registry or scope contract is missing or unparseable (AIV-3.4).

    Raised at construction. A broker that cannot load its configuration
    fails closed: it is never constructed, so it can issue no grants.
    """


class GrantDeniedError(BrokerError):
    """A grant request was rejected with a fail-closed DENY (AIV-1.4).

    Carries the denial ``reason``. The denial is also recorded in
    ``VaultBroker.authorization_failures`` before this is raised.
    """

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


@dataclass
class Grant:
    """An issued credential grant (AIV-2.1, AIV-2.2, AIV-2.3).

    ``ttl_seconds`` is the effective TTL actually encoded in the token;
    ``requested_ttl_seconds`` is what the caller asked for. When the
    request exceeded the 60-minute ceiling, ``ttl_clamped`` is True and
    ``ttl_seconds`` is 60 minutes — that is the recorded clamp (AIV-2.2).
    """

    token: str
    agent_id: str
    role: str
    task_id: str
    approver: str
    scopes: List[str]
    scopes_hash: str
    ttl_seconds: int
    requested_ttl_seconds: int
    ttl_clamped: bool
    iat: int
    exp: int
    jti: str


def _load_json_file(path: Path, what: str) -> Dict[str, Any]:
    """Load a JSON config file, failing closed on any problem (AIV-3.4)."""
    if not path.exists():
        raise BrokerConfigError(what + " not found: " + str(path))
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        raise BrokerConfigError(what + " is unparseable: " + str(path)) from exc
    if not isinstance(data, dict):
        raise BrokerConfigError(what + " must be a JSON object: " + str(path))
    return data


def _permitted_scopes_from_contract(contract: Dict[str, Any]) -> Set[str]:
    """Extract the permitted-scopes set from a scope contract (AIV-2.5).

    Accepts the ``scopes.json`` shape (``permitted_scopes`` list) and the
    ``completion-contract.json`` shape (``credential_grant`` mapping of
    credential name to scope or list of scopes). Raises BrokerConfigError
    when the contract yields no usable permitted scopes.
    """
    scopes: Set[str] = set()
    permitted = contract.get("permitted_scopes")
    if permitted is not None:
        if not isinstance(permitted, list) or not all(
            isinstance(scope, str) and scope for scope in permitted
        ):
            raise BrokerConfigError(
                "scope contract 'permitted_scopes' must be a list of non-empty strings"
            )
        scopes.update(permitted)
    credential_grant = contract.get("credential_grant")
    if credential_grant is not None:
        if not isinstance(credential_grant, dict):
            raise BrokerConfigError(
                "scope contract 'credential_grant' must be an object"
            )
        for _name, value in credential_grant.items():
            if isinstance(value, str) and value:
                scopes.add(value)
            elif isinstance(value, list) and all(
                isinstance(scope, str) and scope for scope in value
            ):
                scopes.update(value)
            else:
                raise BrokerConfigError(
                    "scope contract 'credential_grant' values must be a scope "
                    "string or a list of scope strings"
                )
    if not scopes:
        raise BrokerConfigError(
            "scope contract declares no permitted scopes "
            "(expected 'permitted_scopes' or 'credential_grant')"
        )
    return scopes


def _iso8601_utc(timestamp: int) -> str:
    """Format a Unix timestamp as ISO-8601 UTC with a ``Z`` suffix."""
    return (
        datetime.fromtimestamp(timestamp, tz=timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


class VaultBroker:
    """Grant request handler: validates, TTL-bounds, and signs grants.

    Args:
        private_key: 32-byte Ed25519 private seed of the issuing vault.
        registry_data: Registry dict (fixture data for tests). When given,
            it is used instead of reading a registry file.
        registry_path: Path to ``registry/agents.json``. Defaults to the
            repo's registry. Ignored when ``registry_data`` is given.
        scope_contract: Scope contract dict (fixture data for tests). When
            given, it is used instead of reading a contract file.
        scope_contract_path: Path to a ``scopes.json`` or
            ``completion-contract.json`` file. Required when
            ``scope_contract`` is not given.

    Raises:
        ValueError: If the private key is not 32 bytes.
        BrokerConfigError: If the registry or scope contract is missing or
            unparseable (AIV-3.4) — the broker fails closed at construction.
    """

    def __init__(
        self,
        private_key: bytes,
        registry_data: Optional[Dict[str, Any]] = None,
        registry_path: Optional[Path] = None,
        scope_contract: Optional[Dict[str, Any]] = None,
        scope_contract_path: Optional[Path] = None,
    ):
        if len(private_key) != 32:
            raise ValueError("private key must be 32 bytes")
        self._private_key = private_key
        self.public_key = ed25519_public_key(private_key)

        if registry_data is not None:
            if not isinstance(registry_data, dict) or not isinstance(
                registry_data.get("agents"), list
            ):
                raise BrokerConfigError(
                    "registry data must be an object with an 'agents' list"
                )
            self._registry_data = registry_data
        else:
            path = Path(registry_path or DEFAULT_REGISTRY_PATH)
            self._registry_data = _load_json_file(path, "agent registry")
            if not isinstance(self._registry_data.get("agents"), list):
                raise BrokerConfigError(
                    "agent registry must contain an 'agents' list: " + str(path)
                )

        if scope_contract is not None:
            if not isinstance(scope_contract, dict):
                raise BrokerConfigError("scope contract must be a JSON object")
            self._permitted_scopes = _permitted_scopes_from_contract(scope_contract)
        elif scope_contract_path is not None:
            contract = _load_json_file(
                Path(scope_contract_path), "scope contract"
            )
            self._permitted_scopes = _permitted_scopes_from_contract(contract)
        else:
            raise BrokerConfigError(
                "a scope contract is required (AIV-2.5): pass scope_contract "
                "or scope_contract_path"
            )

        #: Authorization failures, recorded as audit-shaped records
        #: (design.md section 3.3, ``event_type`` ``"GRANT_REJECTED"``).
        #: T4 persists these to ``logs/vault-audit.jsonl``.
        self.authorization_failures: List[Dict[str, Any]] = []

    @property
    def permitted_scopes(self) -> Set[str]:
        """The permitted-scopes set from the scope contract (AIV-2.5)."""
        return set(self._permitted_scopes)

    def _deny(
        self,
        agent_id: str,
        task_id: str,
        scopes: List[str],
        reason: str,
        now: Optional[int] = None,
    ) -> None:
        """Log an authorization failure (AIV-1.4) and raise the DENY."""
        timestamp = int(now if now is not None else time.time())
        record = {
            "timestamp": _iso8601_utc(timestamp),
            "event_type": "GRANT_REJECTED",
            "agent_id": agent_id,
            "task_id": task_id,
            "jti": None,
            "scopes": list(scopes),
            "details": reason,
        }
        self.authorization_failures.append(record)
        logger.warning("grant denied for %s on %s: %s", agent_id, task_id, reason)
        raise GrantDeniedError(reason)

    def request_grant(
        self,
        agent_id: str,
        task_id: str,
        scopes: List[str],
        approver: str,
        ttl_seconds: Optional[int] = None,
        now: Optional[int] = None,
        jti: Optional[str] = None,
    ) -> Grant:
        """Validate a grant request and issue a signed token (AIV-1.3, AIV-2).

        Checks, in order: the agent exists in the registry and the requested
        scopes are a subset of its registered capabilities (AIV-1.3);
        ``approver != requester`` (AIV-2.4); the requested scopes are a
        subset of the scope contract's permitted scopes (AIV-2.5). Any
        failure is a fail-closed DENY (AIV-1.4) recorded in
        ``authorization_failures``.

        TTL: ``None`` assigns the 15-minute default (AIV-2.1); a request
        above 60 minutes is clamped to 60 minutes and the clamp is recorded
        on the returned grant (AIV-2.2).

        Args:
            agent_id: Declared agent identity; must exist in the registry.
            task_id: Task the grant is bound to.
            scopes: Requested scopes (the capability set). Must be a
                non-empty list of non-empty strings.
            approver: Who authorizes the grant. Must differ from
                ``agent_id`` (AIV-2.4); normally the human owner.
            ttl_seconds: Requested lifetime in seconds; ``None`` means the
                15-minute default.
            now: Unix time for ``iat`` (defaults to the current time).
                Exposed for deterministic testing.
            jti: Unique token id; generated as ``"grant-<uuid4>"`` if
                omitted.

        Returns:
            The issued :class:`Grant`, including the signed token.

        Raises:
            ValueError: If any argument is missing, mistyped, or out of
                range (fail closed; no token is issued).
            GrantDeniedError: If any authorization check fails (AIV-1.4).
        """
        if not isinstance(agent_id, str) or not agent_id:
            raise ValueError("agent_id must be a non-empty string")
        if not isinstance(task_id, str) or not task_id:
            raise ValueError("task_id must be a non-empty string")
        if not isinstance(scopes, list) or not scopes or not all(
            isinstance(scope, str) and scope for scope in scopes
        ):
            raise ValueError("scopes must be a non-empty list of non-empty strings")
        if not isinstance(approver, str) or not approver:
            raise ValueError("approver must be a non-empty string")
        if ttl_seconds is not None and (
            not isinstance(ttl_seconds, int) or ttl_seconds <= 0
        ):
            raise ValueError("ttl_seconds must be a positive integer")
        if jti is not None and (not isinstance(jti, str) or not jti):
            raise ValueError("jti must be a non-empty string")

        # AIV-1.3: the agent must exist in the registry.
        agent = get_agent(agent_id, self._registry_data)
        if agent is None:
            self._deny(
                agent_id,
                task_id,
                scopes,
                "unknown agent_id: " + agent_id,
                now=now,
            )

        # AIV-2.4: an agent SHALL NOT authorize its own grant.
        if approver == agent_id:
            self._deny(
                agent_id,
                task_id,
                scopes,
                "approver must differ from requester (AIV-2.4)",
                now=now,
            )

        # AIV-1.3: requested scopes must be a subset of registered
        # capabilities. (get_agent returned an agent above; the assert
        # keeps mypy honest about the None case.)
        assert agent is not None
        permitted_capabilities = agent.get("permitted_capabilities", [])
        excess = sorted(set(scopes) - set(permitted_capabilities))
        if excess:
            self._deny(
                agent_id,
                task_id,
                scopes,
                "requested capabilities exceed registered capabilities: "
                + ", ".join(excess),
                now=now,
            )

        # AIV-2.5: the scope contract is the exclusive Source of Truth.
        out_of_contract = sorted(set(scopes) - self._permitted_scopes)
        if out_of_contract:
            self._deny(
                agent_id,
                task_id,
                scopes,
                "requested scopes are outside the scope contract: "
                + ", ".join(out_of_contract),
                now=now,
            )

        # AIV-2.1 / AIV-2.2: default 15 minutes; clamp above 60 minutes.
        requested_ttl = ttl_seconds if ttl_seconds is not None else DEFAULT_TTL_SECONDS
        ttl_clamped = requested_ttl > MAX_TTL_SECONDS
        effective_ttl = MAX_TTL_SECONDS if ttl_clamped else requested_ttl

        token = create_token(
            self._private_key,
            agent_id=agent_id,
            role=agent.get("role", ""),
            task_id=task_id,
            scopes=list(scopes),
            ttl_seconds=effective_ttl,
            jti=jti,
            now=now,
        )
        payload = parse_token(token)
        return Grant(
            token=token,
            agent_id=agent_id,
            role=agent.get("role", ""),
            task_id=task_id,
            approver=approver,
            scopes=list(scopes),
            scopes_hash=payload["scopes_hash"],
            ttl_seconds=effective_ttl,
            requested_ttl_seconds=requested_ttl,
            ttl_clamped=ttl_clamped,
            iat=payload["iat"],
            exp=payload["exp"],
            jti=payload["jti"],
        )
