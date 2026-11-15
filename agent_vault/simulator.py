"""Read-only permission simulator and diagnosis stop-list (AIV Task T5).

Implements AIV-4.1, AIV-4.2, AIV-4.3, and AIV-4.4 from
specs/agent-identity-vault.

Two pieces, both strictly read-only — neither mutates any state:

1. The diagnosis stop-list (:func:`evaluate_stop_list`, AIV-4.2): given
   the state of an access diagnosis, decide whether the agent must halt
   immediately. It halts when access is already ``GRANTED`` (the failure
   is application-level, not IAM), when identity or group membership
   state is ``UNKNOWN`` (report the visibility gap rather than
   escalating), or when a diagnostic call returns ``403`` /
   ``PERMISSION_DENIED`` (halt instead of probing alternate endpoints).
   The verdict is always one of the three stop-list values — never a
   bare pass/fail.

2. The permission simulator (:class:`PermissionSimulator`, AIV-4.1,
   AIV-4.3, AIV-4.4): given an ``agent_id``, a proposed scope set, and
   the same registry + scope contract the broker uses, it returns a
   deterministic simulation diff (``access_before`` vs ``access_after``)
   WITHOUT issuing any token, writing any log, or mutating any state.
   The simulator has no private key and never calls
   ``VaultBroker.request_grant`` or ``agent_vault.token.create_token``;
   it cannot issue a grant. It reuses the broker's registry/capability
   and scope-contract parsing (``agent_vault.broker``) so a simulation
   answers exactly what the broker would decide — without the side
   effect of issuing the token.

Simulation verdicts (AIV-4.3, AIV-4.4). A simulation result is always
exactly one of ``GRANTED``, ``UNKNOWN``, or ``403``:

- ``GRANTED``: every requested scope would be granted — the agent is
  registered, every scope is within its registered capabilities and
  inside the scope contract. The diff shows the access the grant would
  add (``access_after`` = ``access_before`` plus the granted scopes).
- ``403``: the grant as requested would be denied (``PERMISSION_DENIED``)
  — a requested scope exceeds the agent's registered capabilities
  (AIV-1.3), sits outside the scope contract (AIV-2.5), or the approver
  equals the requester (AIV-2.4). The diff shows the blockers in
  ``denied_scopes``; ``access_after`` equals ``access_before`` because
  a rejected change adds no access.
- ``UNKNOWN``: the result cannot be resolved — the agent is not in the
  registry (identity state unknown, AIV-4.2). The simulation fails
  closed (AIV-4.4): no access is assumed, ``access_before`` and
  ``access_after`` are empty, and nothing is granted. An ambiguous diff
  returns ``UNKNOWN``, never a grant.

Fail-closed behaviour (AIV-3.4): a missing or unparseable registry or
scope contract makes the simulator refuse to construct
(``BrokerConfigError``, the same error the broker raises), and malformed
simulation arguments raise ``ValueError`` — no result is ever produced
on a failed check.

Determinism (AIV-4.3): ``simulate`` is a pure function of its inputs
(registry, contract, agent, scopes). It reads no clock, no randomness,
and no mutable state, so the same inputs always produce the same diff.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from agent_vault.broker import (
    BrokerConfigError,
    _load_json_file,
    _permitted_scopes_from_contract,
)
from agent_vault.registry import DEFAULT_REGISTRY_PATH, get_agent

#: The three diagnosis stop-list verdicts (AIV-4.2). A simulation
#: result is always exactly one of these — never a bare pass/fail.
VERDICT_GRANTED = "GRANTED"
VERDICT_UNKNOWN = "UNKNOWN"
VERDICT_FORBIDDEN = "403"
VERDICTS = frozenset({VERDICT_GRANTED, VERDICT_UNKNOWN, VERDICT_FORBIDDEN})


@dataclass
class StopListDecision:
    """The outcome of evaluating the diagnosis stop-list (AIV-4.2).

    ``verdict`` is one of the three stop-list values when a stop
    condition applies, or None when no stop condition applies (the
    diagnosis may continue). ``halt`` is True exactly when a stop
    condition applies. ``reason`` explains the decision in one line.
    """

    verdict: Optional[str]
    halt: bool
    reason: str


def evaluate_stop_list(
    access_granted: bool,
    identity_known: bool,
    diagnostic_status: Optional[Any] = None,
) -> StopListDecision:
    """Evaluate the read-only diagnosis stop-list (AIV-4.2).

    The agent diagnosing an access issue SHALL halt immediately when:

    - access is already ``GRANTED`` (an application-level, non-IAM
      failure — the diagnosis stops instead of re-probing IAM);
    - identity or group membership state is ``UNKNOWN`` (report the
      visibility gap rather than escalating);
    - a diagnostic call returns ``403`` / ``PERMISSION_DENIED``
      (halt instead of probing alternate endpoints).

    Conditions are evaluated in the order the spec lists them, so when
    several apply at once the first one wins: ``GRANTED`` over
    ``UNKNOWN`` over ``403``.

    Args:
        access_granted: True when the access under diagnosis is already
            granted.
        identity_known: True when the identity / group membership state
            is known; False when it is unknown.
        diagnostic_status: The status of a diagnostic call — the HTTP
            status code as an int (``403`` stops), or the string
            ``"PERMISSION_DENIED"`` (case-insensitive). None when no
            diagnostic call was made.

    Returns:
        A :class:`StopListDecision`. ``halt`` is False and ``verdict``
        is None only when no stop condition applies.
    """
    if access_granted:
        return StopListDecision(
            VERDICT_GRANTED,
            True,
            "Access is already GRANTED; the failure is application-level, "
            "not IAM — halt instead of re-probing permissions (AIV-4.2).",
        )
    if not identity_known:
        return StopListDecision(
            VERDICT_UNKNOWN,
            True,
            "Identity or group membership state is UNKNOWN; report the "
            "visibility gap rather than escalating (AIV-4.2).",
        )
    if diagnostic_status == 403 or (
        isinstance(diagnostic_status, str)
        and diagnostic_status.upper() == "PERMISSION_DENIED"
    ):
        return StopListDecision(
            VERDICT_FORBIDDEN,
            True,
            "Diagnostic call returned 403 / PERMISSION_DENIED; halt "
            "instead of probing alternate endpoints (AIV-4.2).",
        )
    return StopListDecision(
        None,
        False,
        "No stop condition applies; diagnosis may continue.",
    )


@dataclass
class SimulationResult:
    """The deterministic diff of a simulated scope change (AIV-4.3).

    ``verdict`` is always one of ``GRANTED``, ``UNKNOWN``, or ``403``
    — never a bare pass/fail. ``access_before`` is the agent's current
    effective access (registered capabilities intersected with the scope
    contract); ``access_after`` is the access the agent would hold if
    the change were applied. ``granted_scopes`` are the requested scopes
    that would be granted; ``denied_scopes`` maps each blocked scope to
    its reason. ``added_scopes`` is the new access the change would add
    (``access_after`` minus ``access_before``). ``reason`` summarises
    the verdict in one line.

    On a ``403`` verdict the change is rejected, so ``access_after``
    equals ``access_before`` (no access is added) and ``added_scopes``
    is empty. On an ``UNKNOWN`` verdict nothing can be resolved, so
    ``access_before``, ``access_after``, ``granted_scopes``, and
    ``added_scopes`` are all empty and ``denied_scopes`` is empty.

    Note that a grant confers only scopes the agent is already
    permitted, so on a ``GRANTED`` result ``access_after`` equals
    ``access_before`` as well — the grant attests to existing
    permission rather than elevating it, and ``added_scopes`` is empty.
    The diagnostic signal is the ``granted_scopes`` / ``denied_scopes``
    breakdown, not an access change.
    """

    verdict: str
    agent_id: str
    task_id: str
    requested_scopes: List[str]
    access_before: List[str]
    access_after: List[str]
    granted_scopes: List[str]
    denied_scopes: Dict[str, str]
    added_scopes: List[str]
    reason: str


class PermissionSimulator:
    """Read-only permission simulator (AIV-4.1, AIV-4.3, AIV-4.4).

    Simulates what the Vault Broker would decide for a proposed grant
    — without issuing any token, writing any log, or mutating any state.
    The simulator holds no private key and has no token-issuing path;
    it is the read-only diagnostic identity of AIV-4.1.

    Args:
        registry_data: Registry dict (fixture data for tests). When
            given, it is used instead of reading a registry file.
        registry_path: Path to ``registry/agents.json``. Defaults to the
            repo's registry. Ignored when ``registry_data`` is given.
        scope_contract: Scope contract dict (fixture data for tests).
            When given, it is used instead of reading a contract file.
        scope_contract_path: Path to a ``scopes.json`` or
            ``completion-contract.json`` file. Required when
            ``scope_contract`` is not given.

    Raises:
        BrokerConfigError: If the registry or scope contract is missing
            or unparseable (AIV-3.4) — the simulator fails closed at
            construction, exactly as the broker does.
    """

    def __init__(
        self,
        registry_data: Optional[Dict[str, Any]] = None,
        registry_path: Optional[Path] = None,
        scope_contract: Optional[Dict[str, Any]] = None,
        scope_contract_path: Optional[Path] = None,
    ):
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

    @property
    def permitted_scopes(self) -> Set[str]:
        """The permitted-scopes set from the scope contract (AIV-2.5)."""
        return set(self._permitted_scopes)

    def current_access(self, agent_id: str) -> Optional[List[str]]:
        """Return an agent's current effective scopes (AIV-4.3).

        The effective scopes are the agent's registered
        ``permitted_capabilities`` intersected with the scope
        contract's permitted scopes — what the agent is already
        permitted to do. Returns None when the agent is not in the
        registry (identity state unknown, AIV-4.2).

        Raises:
            ValueError: If ``agent_id`` is not a non-empty string.
            BrokerConfigError: If the agent's registered capabilities
                are malformed (AIV-3.4) — the simulation fails closed.
        """
        if not isinstance(agent_id, str) or not agent_id:
            raise ValueError("agent_id must be a non-empty string")
        agent = get_agent(agent_id, self._registry_data)
        if agent is None:
            return None
        capabilities = agent.get("permitted_capabilities", [])
        if not isinstance(capabilities, list) or not all(
            isinstance(capability, str) and capability for capability in capabilities
        ):
            raise BrokerConfigError(
                "agent '" + agent_id + "' has malformed "
                "'permitted_capabilities' in the registry"
            )
        return sorted(set(capabilities) & self._permitted_scopes)

    def simulate(
        self,
        agent_id: str,
        task_id: str,
        scopes: List[str],
        approver: Optional[str] = None,
    ) -> SimulationResult:
        """Simulate a proposed grant and return its deterministic diff.

        Runs the broker's checks — registry membership and capability
        subset (AIV-1.3), approver separation (AIV-2.4, when an approver
        is given), and scope-contract membership (AIV-2.5) — against the
        requested scopes, and returns what the broker would decide, as
        a ``GRANTED`` / ``UNKNOWN`` / ``403`` verdict with an
        ``access_before`` vs ``access_after`` diff (AIV-4.3). No token
        is issued, no log is written, and no state is mutated (AIV-4.1).

        An unknown agent returns ``UNKNOWN`` and fails closed (AIV-4.4):
        no access is assumed and nothing is granted. A request that
        would be denied returns ``403`` with the blocking scopes in
        ``denied_scopes``.

        Args:
            agent_id: Declared agent identity; must exist in the
                registry for the simulation to resolve.
            task_id: Task the simulated grant would be bound to.
            scopes: Proposed scopes (the capability set). Must be a
                non-empty list of non-empty strings.
            approver: Who would authorize the grant. When given and
                equal to ``agent_id`` the grant would be denied
                (AIV-2.4). When omitted the approver check is skipped.

        Returns:
            The :class:`SimulationResult` diff.

        Raises:
            ValueError: If any argument is missing, mistyped, or out
                of range (fail closed; no result is produced).
            BrokerConfigError: If the agent's registered capabilities
                are malformed (AIV-3.4).
        """
        if not isinstance(agent_id, str) or not agent_id:
            raise ValueError("agent_id must be a non-empty string")
        if not isinstance(task_id, str) or not task_id:
            raise ValueError("task_id must be a non-empty string")
        if not isinstance(scopes, list) or not scopes or not all(
            isinstance(scope, str) and scope for scope in scopes
        ):
            raise ValueError("scopes must be a non-empty list of non-empty strings")
        if approver is not None and (not isinstance(approver, str) or not approver):
            raise ValueError("approver must be a non-empty string or None")

        requested = sorted(set(scopes))

        # AIV-4.4: an unknown agent is an unresolvable identity — the
        # simulation fails closed as UNKNOWN, never a grant.
        agent = get_agent(agent_id, self._registry_data)
        if agent is None:
            return SimulationResult(
                verdict=VERDICT_UNKNOWN,
                agent_id=agent_id,
                task_id=task_id,
                requested_scopes=requested,
                access_before=[],
                access_after=[],
                granted_scopes=[],
                denied_scopes={},
                added_scopes=[],
                reason=(
                    "unknown agent_id: " + agent_id + "; identity state is "
                    "UNKNOWN (AIV-4.2) — simulation cannot be resolved, "
                    "failing closed (AIV-4.4)"
                ),
            )

        # AIV-4.3: the "before" state is the agent's current effective
        # access (registered capabilities intersected with the contract).
        access_before = self.current_access(agent_id)
        assert access_before is not None  # get_agent returned an agent above
        before_set = set(access_before)
        capabilities = set(
            agent.get("permitted_capabilities", [])
        )

        # AIV-2.4: an agent SHALL NOT authorize its own grant. A
        # request-level denial — no scope is granted, and the change
        # adds no access.
        if approver is not None and approver == agent_id:
            return SimulationResult(
                verdict=VERDICT_FORBIDDEN,
                agent_id=agent_id,
                task_id=task_id,
                requested_scopes=requested,
                access_before=access_before,
                access_after=list(access_before),
                granted_scopes=[],
                denied_scopes={},
                added_scopes=[],
                reason=(
                    "approver must differ from requester (AIV-2.4); "
                    "the grant as requested would be denied"
                ),
            )

        # AIV-1.3 / AIV-2.5, per scope, in the broker's check order:
        # registry capabilities first, then the scope contract.
        granted: List[str] = []
        denied: Dict[str, str] = {}
        for scope in requested:
            if scope not in capabilities:
                denied[scope] = (
                    "requested capability exceeds registered "
                    "capabilities (AIV-1.3)"
                )
            elif scope not in self._permitted_scopes:
                denied[scope] = (
                    "requested scope is outside the scope contract (AIV-2.5)"
                )
            else:
                granted.append(scope)

        if denied:
            return SimulationResult(
                verdict=VERDICT_FORBIDDEN,
                agent_id=agent_id,
                task_id=task_id,
                requested_scopes=requested,
                access_before=access_before,
                access_after=list(access_before),
                granted_scopes=granted,
                denied_scopes=denied,
                added_scopes=[],
                reason=(
                    "the grant as requested would be denied "
                    "(PERMISSION_DENIED): "
                    + ", ".join(sorted(denied))
                ),
            )

        access_after = sorted(before_set | set(granted))
        added = sorted(set(access_after) - before_set)
        return SimulationResult(
            verdict=VERDICT_GRANTED,
            agent_id=agent_id,
            task_id=task_id,
            requested_scopes=requested,
            access_before=access_before,
            access_after=access_after,
            granted_scopes=granted,
            denied_scopes={},
            added_scopes=added,
            reason="all requested scopes would be granted",
        )
