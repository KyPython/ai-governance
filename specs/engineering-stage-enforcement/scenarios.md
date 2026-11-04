# Acceptance scenarios: Engineering-stage enforcement (G0–G6)

> **MARKED AI DRAFT ONLY — NOT APPROVED — NOT A G3 RECEIPT**
>
> Prepared by Codex in the `coder` role for Ky's personal review. This
> neutral-workspace draft is not Kiro-authored, has not been written to
> `specs/`, and does not authorize tests, step definitions, implementation,
> publication, merge, deployment, or spending.
>
> Proposed destination after truthful spec-author/owner publication:
> `specs/engineering-stage-enforcement/scenarios.md`
>
> Canonical inputs: issue #238 and the merged ESE `requirements.md`,
> `design.md`, and `tasks.md` at repository revision
> `9b189908bbb08540d066a53c1841a883d6beb5ac`.

## Conventions

- These are acceptance examples for owner review, not executable tests.
- `owner receipt` means an authenticated, non-agent-forgeable artifact
  satisfying ESE-2 and ESE-6.
- `real boundary` means the actual dispatch, writable-workspace, filesystem,
  credential, publisher, or admission boundary—not merely an isolated policy
  function.
- Every rejection must report the correct reason at the correct boundary.
- Unless a scenario says otherwise, no merge, deployment, spending,
  protected-file mutation, or new service is authorized.

```gherkin
Feature: ESE-1 — Ordered owner-approval stages G0 through G6
  # Maps ESE-1.1 through ESE-1.9

  Scenario Outline: A stage cannot advance without its exact predecessor decision
    Given work is bound to an exact repository, issue, spec revision, content digest, and path scope
    And the latest accepted stage is <accepted_stage>
    When an actor requests <requested_action> without a valid owner receipt for <required_stage>
    Then admission is held before the requested action begins
    And the decision is "HOLD/PENDING"
    And no later stage, spending action, merge, or deployment is inferred

    Examples:
      | accepted_stage | requested_action                          | required_stage |
      | none           | out-of-scope BDD discovery                | G0             |
      | G0             | authoritative spec authoring              | G1             |
      | G1             | scenario formulation or code change       | G2             |
      | G2             | executable acceptance/TDD test authoring  | G3             |
      | G3             | production implementation                 | G4             |
      | G4             | owner-authorized independent verification | G5             |
      | G5             | treatment beyond owner-review eligibility | G6             |

  Scenario: One approval authorizes one next phase only
    Given a valid G3 receipt bound to the accepted scenarios and exact scope
    When an actor requests test authoring and production implementation together
    Then only the G3-authorized test-authoring phase is eligible
    And implementation remains held pending separately accepted genuine G4 RED evidence

  Scenario: G6 stops at owner-review eligibility
    Given independent changed verification is bound to the exact candidate revision
    When Ky accepts that evidence at G6
    Then status becomes "eligible for owner review only"
    And the system does not auto-merge or deploy
```

```gherkin
Feature: ESE-2 — Genuine non-agent-forgeable authorization
  # Maps ESE-2.1 through ESE-2.5

  Scenario Outline: Identity metadata alone cannot approve a stage
    Given no non-agent-forgeable owner authorization artifact exists
    And <metadata> appears to identify or approve as Ky
    When stage admission is evaluated
    Then admission is "BLOCKED"
    And the reason is "UNVERIFIABLE_APPROVER"
    And the metadata is not converted into an owner receipt

    Examples:
      | metadata                                       |
      | a GitHub issue or pull-request comment         |
      | a PR author, label, YAML checkbox, or tag      |
      | git author or committer fields                 |
      | a verified commit signature                    |
      | bot-supplied JSON or CI actor metadata         |
      | a GitHub Actions OIDC workflow identity        |
      | a KyPython appearance produced by a shared PAT |

  Scenario: An agent cannot mint the owner's authority
    Given the principal is a coder or spec-author acting through agent credentials
    When it issues, stores, or presents a purported owner-approval receipt
    Then the receipt is rejected as untrusted
    And no owner decision is inferred
```

```gherkin
Feature: ESE-3 — Mandatory governed admission
  # Maps ESE-3.1 through ESE-3.9

  Scenario: A new owned repository begins quarantined
    Given an approved canonical intake binds the owner decision, account, classification, budgets, policy revision, and authorized creator
    When the trusted bootstrapper creates the repository
    Then governance enrollment is mandatory
    And the repository is "QUARANTINED" and not "GOVERNED_READY"
    And only the permitted full-SHA-pinned governance scaffold is installed
    And no production implementation agent receives write or push credentials

  Scenario: Readiness requires independently observed controls
    Given a quarantined repository has its governance scaffold
    When independent readback and real negative and positive admission checks pass
    Then the repository may become "GOVERNED_READY"
    But documentation or self-attestation alone cannot set readiness

  Scenario Outline: Self-declared exemptions do not bypass admission
    Given an agent labels work as <label>
    When governed admission is evaluated
    Then the label does not bypass admission

    Examples:
      | label     |
      | no-risk   |
      | docs-only |
      | emergency |
      | exempt    |

  Scenario: Every reachable repository receives an evidence-backed classification
    Given the inventory includes private, empty, archived, learner, external, and forked repositories
    When coverage is classified with owner review
    Then every repository is recorded as "GOVERNED", "QUARANTINED", "NOT_APPLICABLE_BY_AUTHORIZED_SCOPE", or "BLOCKED_UNAVAILABLE"
    And an unowned repository's own controls are never overridden

  Scenario: Runner choice is optional but governance is not
    Given Ky authenticates a scoped "FULL", "LIMITED", or "NOT_APPLICABLE" runner decision
    When the repository uses sufficient existing tests instead of Cucumber
    Then "EXISTING TESTS SUFFICIENT" may be a valid tool outcome
    And governance stages and baseline checks remain mandatory
```

```gherkin
Feature: ESE-4 — Local and cloud parity
  # Maps ESE-4.1 through ESE-4.8

  Scenario Outline: Location does not change authority
    Given local and cloud requests have identical canonical policy, receipt, stage, role, content digests, paths, and revocation state
    When admission is evaluated in <location>
    Then the decision and reason match the other location
    And the adapter changes only isolation mechanics, not authorization

    Examples:
      | location |
      | local    |
      | cloud    |

  Scenario: Failed admission provides no writable workspace
    Given stage, scope, isolation, or owner-receipt validation fails
    When either launcher handles the request
    Then it refuses a write-capable workspace
    And it does not expose an owner PAT or raw publish privilege

  Scenario: Offline work remains non-authoritative
    Given remote approval, required-check status, authentication, or live isolation is unavailable
    When an actor performs neutral drafting, research, diff inspection, or deterministic checks
    Then the result is accurately "PASS", "FAIL", "BLOCKED", "UNKNOWN", or "NOT_RUN"
    And no mutation or publication is self-authorized

  Scenario: Platform limitations are reported honestly
    Given a provider cannot meet the isolation bar or an unmanaged host is outside technical enforcement
    When coverage is reported
    Then that lane is "BLOCKED" or "OUTSIDE ENFORCED BOUNDARY / NOT PROVEN"
    And unprotected-branch code remains untrusted and unmergeable
```

```gherkin
Feature: ESE-5 — Isolation and trusted publication
  # Maps ESE-5.1 through ESE-5.6

  Scenario: A coder receives only a disposable least-privilege workspace
    Given a stage job is admitted
    When the coder workspace starts
    Then it is fresh, unprivileged, and disposable
    And upstream inputs are genuinely read-only
    And only scoped output is writable
    And no host Docker socket, owner credential, or broad secret is present
    And capabilities and network egress are explicitly constrained

  Scenario: Protected inputs remain immutable to a coder
    Given the principal has the coder role
    When it attempts to change features, specs, or tests
    Then the filesystem or publisher rejects the change
    And chmod 444 alone is not accepted as proof of isolation

  Scenario: Publisher revalidates before any push
    Given a coder proposes an output tree
    When the separate trusted publisher evaluates it
    Then it validates paths, permissions, authority, and receipts before pushing
    And post-PR CI alone is not considered sufficient

  Scenario: Authorities remain separated
    Given receipt issuance, stage execution, independent verification, controlled publication, and GitHub admission are configured
    Then no single orchestrator holds every agent credential or unilateral signing authority
    And third-party environment isolation is UNKNOWN until independently verified
```

```gherkin
Feature: ESE-6 — Receipt contract, lineage, replay, and revocation
  # Maps ESE-6.1 through ESE-6.7

  Scenario: A complete receipt is content-bound
    Given a stage receipt identifies stage, task, paths, operations, issuer, role, policy revision, predecessor IDs and digests, input digests, output digest, expiry, revocation reference, freshness, and owner decision
    When it is checked for the exact subject and content
    Then only the bound stage and scope can be authorized
    And scope expansion, stale SHA use, cross-repository reuse, and unrelated-issue reuse are rejected

  Scenario Outline: Invalid receipts fail closed twice
    Given a receipt is <condition>
    When it is checked at dispatch and immediately before publication
    Then the affected action is held
    And the status is accurately "PENDING", "BLOCKED", "REJECTED", "SUPERSEDED", or "VERIFIED"
    And an unavailable approval service never defaults to approval

    Examples:
      | condition |
      | missing   |
      | malformed |
      | reused    |
      | expired   |
      | revoked   |
      | drifted   |
      | untrusted |

  Scenario: Material change invalidates only descendants
    Given receipts form a dependency lineage with an unrelated valid branch
    When behavior, spec, input, expiry, or revocation changes one upstream node
    Then only that node's affected downstream descendants are invalidated
    And unrelated lineage remains valid

  Scenario: Merge authority does not imply deployment authority
    Given merge approval is valid
    When deployment is requested without its separate authority
    Then deployment is rejected
```

```gherkin
Feature: ESE-7 — Pre-dispatch blocking admission
  # Maps ESE-7.1 through ESE-7.4

  Scenario: Unauthorized work is blocked before mutation
    Given an agent lacks valid stage, role, path, or receipt authority
    When task dispatch or writable-workspace handoff is attempted
    Then the blocking guard denies it before mutation
    And the system does not rely on final PR checks alone

  Scenario: Final CI remains defense in depth
    Given an unauthorized phase artifact reaches a pull request
    When final CI evaluates the artifact or merge attempt
    Then CI blocks it independently of the pre-dispatch guard

  Scenario: Stronger repository gates remain additive
    Given a target requires per-file mutation authority
    When work is proposed for that target
    Then exact per-file authorization is required
    And existing protection is not relaxed

  Scenario: Impossible enforcement is not overstated
    Given a surface cannot technically be controlled
    When enforcement coverage is reported
    Then the surface is explicitly described as unenforceable
```

```gherkin
Feature: ESE-8 — Genuine RED, GREEN, and adequacy
  # Maps ESE-8.1 through ESE-8.7

  Scenario Outline: Harness failures are not RED
    Given the designated acceptance test result is <failure>
    When G4 evidence is classified
    Then the result is rejected as genuine RED

    Examples:
      | failure                  |
      | syntax error             |
      | import error             |
      | collection failure       |
      | fixture failure          |
      | skipped test             |
      | timeout                  |
      | wrong test selection     |
      | universal stub exception |
      | nonzero exit alone       |

  Scenario: Intended behavioral assertion is RED-eligible
    Given the designated new test fails on its intended behavioral assertion
    And fixture, import, collection, and harness are healthy
    And unrelated invariant and regression tests pass
    When G4 evidence is classified
    Then the result is RED-eligible

  Scenario: Trace markers are not coverage
    Given every requirement ID appears in a test name or comment
    But every assertion is vacuous
    When adequacy is evaluated
    Then trace intent is recorded
    But adequacy authorization is denied

  Scenario: GREEN requires preserved and contrasting evidence
    Given corresponding acceptance tests are green at the exact candidate revision
    When G5 evidence is evaluated
    Then existing tests must remain green
    And independent negative or contrast oracles must pass

  Scenario: Adequacy evidence remains method-based and honest
    Given mutation or equivalent analysis is meaningful only after production code exists
    When survivors, equivalent implementations, no valid mutants, skipped jobs, or a weak baseline prevent a conclusion
    Then disposition is honestly "UNKNOWN" or "FAIL"
    And no arbitrary global threshold or invented percentage is used
    And no vendor product is mandatory
```

```gherkin
Feature: ESE-9 / V1 — Out-of-order rejection
  # Maps ESE-9.1 and ESE-9.2

  Scenario Outline: V1 rejects a stage artifact before write or publish
    Given the required predecessor receipt is absent
    When a spec write or other stage artifact is attempted at a real <environment> boundary
    Then it is rejected before authorized write or publication
    And the reason is "OUT_OF_ORDER"
    And evidence distinguishes real provider rejection from offline policy simulation

    Examples:
      | environment            |
      | isolated local         |
      | provider-managed cloud |
```

```gherkin
Feature: ESE-10 / V2 — Role, path, and identity forgery rejection
  # Maps ESE-10.1 through ESE-10.3

  Scenario Outline: V2 blocks coder writes to protected inputs
    Given a coder has a scoped implementation workspace
    When the coder attempts to modify <path>
    Then the read-only boundary or trusted publisher rejects the change

    Examples:
      | path      |
      | tests/    |
      | specs/    |
      | features/ |

  Scenario Outline: V2 rejects identity theater
    Given no genuine owner receipt exists
    When an actor presents <forgery>
    Then it fails closed for "UNVERIFIABLE_APPROVER"

    Examples:
      | forgery                             |
      | spoofed human author or committer   |
      | signed commit claiming owner action |
      | forged owner approval               |
      | shared-credential collision         |
```

```gherkin
Feature: ESE-11 / V3 — False RED rejection
  # Maps ESE-11.1 through ESE-11.3

  Scenario Outline: V3 distinguishes false from genuine RED
    Given a submitted RED report is <report>
    When structured G4 classification runs
    Then the result is <decision>

    Examples:
      | report                                                        | decision     |
      | syntax, import, collection, fixture, or harness failure        | rejected     |
      | fake or synthetic report not bound to observed execution       | rejected     |
      | intended assertion failure with healthy harness and invariants | RED-eligible |
```

```gherkin
Feature: ESE-12 / V4 — Vacuous trace and blanket exemptions
  # Maps ESE-12.1 through ESE-12.3

  Scenario: V4 denies assert-true adequacy
    Given all ESE requirement IDs are cited
    And the assertions are equivalent to "assert True"
    When trace and adequacy are evaluated
    Then trace intent may pass
    But adequacy authorization is denied
    And post-code mutation or contrast checks on real code are still required

  Scenario Outline: V4 distinguishes forged and genuine applicability
    Given <decision_source> supplies a "NOT_APPLICABLE" decision
    When governed admission evaluates it
    Then the outcome is <outcome>
    And required baseline checks remain preserved

    Examples:
      | decision_source                              | outcome  |
      | an agent or forged owner identity            | denied   |
      | authenticated owner bound to the exact scope | accepted |
```

```gherkin
Feature: ESE-13 / V5 — Replay, revocation, drift, and concurrency
  # Maps ESE-13.1 through ESE-13.4

  Scenario Outline: V5 rejects invalid downstream lineage
    Given downstream authority depends on an upstream receipt and content digest
    When <change> occurs
    Then downstream authorization is rejected by content lineage
    And unaffected lineage remains valid

    Examples:
      | change                            |
      | upstream behavior changes         |
      | the specification changes         |
      | an accepted input changes          |
      | the receipt expires                |
      | the receipt is revoked             |

  Scenario: V5 handles concurrent change without duplication or deadlock
    Given creator and publisher observe different canonical inputs
    When publication admission runs
    Then incorrectly accepted work is rejected
    And the system neither duplicates the project nor deadlocks legitimate setup

  Scenario: Immutable pins drift through reviewed promotion only
    Given a shared caller is pinned to a full immutable SHA behind an approved revision
    When drift detection reports the difference
    Then no mutable tag replaces the pin
    And promotion requires independent review and the appropriate approved spec
    And no automatic merge occurs

  Scenario: Protected enforcement remains separately authorized
    Given realization would change a protected enforcement file, role map, workflow, or pinned caller
    When an agent lacks Ky's explicit protected-path request and merge
    Then the change is not made
    And it remains a proposed future task
```

```gherkin
Feature: ESE-14 / V6 — Positive traversal to owner-review eligibility
  # Maps ESE-14.1 through ESE-14.4

  Scenario Outline: V6 completes governed stages without auto-merge
    Given one existing scoped synthetic feature has authenticated receipts from G0 through G3
    And its fixture, policy version, actor, inputs, preconditions, and observations are recorded
    When genuine RED is accepted at G4
    And bounded GREEN plus preserved and contrast evidence is accepted at G5
    And a reviewer distinct from the coder independently verifies the exact revision at G6 in <environment>
    Then status becomes "eligible for owner review only"
    And no automatic merge, deployment, or cloud spend occurs

    Examples:
      | environment            |
      | isolated local         |
      | provider-managed cloud |

  Scenario: V6 proves one governed creation from quarantine to eligibility
    Given an approved new venture is registered exactly once
    When a trusted bootstrapper creates one bounded unready repository
    And independent readback proves initialized governance, identity, and checks
    And legitimate stage-specific proposals pass real RED, GREEN, adequacy, and independent verification
    Then the repository and proposal may become eligible for Ky's merge
    But neither is automatically merged or deployed
```

## Coverage matrix

| Requirement | Acceptance criteria explicitly mapped |
|---|---|
| ESE-1 | ESE-1.1, ESE-1.2, ESE-1.3, ESE-1.4, ESE-1.5, ESE-1.6, ESE-1.7, ESE-1.8, ESE-1.9 |
| ESE-2 | ESE-2.1, ESE-2.2, ESE-2.3, ESE-2.4, ESE-2.5 |
| ESE-3 | ESE-3.1, ESE-3.2, ESE-3.3, ESE-3.4, ESE-3.5, ESE-3.6, ESE-3.7, ESE-3.8, ESE-3.9 |
| ESE-4 | ESE-4.1, ESE-4.2, ESE-4.3, ESE-4.4, ESE-4.5, ESE-4.6, ESE-4.7, ESE-4.8 |
| ESE-5 | ESE-5.1, ESE-5.2, ESE-5.3, ESE-5.4, ESE-5.5, ESE-5.6 |
| ESE-6 | ESE-6.1, ESE-6.2, ESE-6.3, ESE-6.4, ESE-6.5, ESE-6.6, ESE-6.7 |
| ESE-7 | ESE-7.1, ESE-7.2, ESE-7.3, ESE-7.4 |
| ESE-8 | ESE-8.1, ESE-8.2, ESE-8.3, ESE-8.4, ESE-8.5, ESE-8.6, ESE-8.7 |
| ESE-9 | ESE-9.1, ESE-9.2 |
| ESE-10 | ESE-10.1, ESE-10.2, ESE-10.3 |
| ESE-11 | ESE-11.1, ESE-11.2, ESE-11.3 |
| ESE-12 | ESE-12.1, ESE-12.2, ESE-12.3 |
| ESE-13 | ESE-13.1, ESE-13.2, ESE-13.3, ESE-13.4 |
| ESE-14 | ESE-14.1, ESE-14.2, ESE-14.3, ESE-14.4 |

## G3 review boundary

Ky's review of this exact content may request changes, reject it, or direct
truthful publication by an authorized spec author or owner override. Until a
separately authenticated G3 decision is issued and bound to the exact published
content digest, executable acceptance/TDD test authoring remains blocked under
ESE-1.4. A hash, this draft, or an issue comment is integrity/provenance evidence
only and is not owner authentication.
