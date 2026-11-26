<!-- KIRO-AUTHORED SCENARIOS FOR AMENDMENT R1 — AI DRAFT, NOT APPROVED, NOT A G3 RECEIPT. RUNTIME ACCEPTANCE NOT RUN.
Issue: https://github.com/KyPython/ai-governance/issues/238 · Source: KyPython/ai-governance@53462a0 · Author: Kiro (spec-author), local session 2026-11-25; model ID not exposed.
These scenarios authorize no test authoring (G4), no implementation (G5), no agent dispatch and no spend. G3 acceptance of the existing `scenarios.md` is separate and is not changed by this file. -->

# Scenarios — capability-qualified assignment, independence, binding (ESE-15 to ESE-17)

Status: proposed, NOT RUN. A scenario passes only when the named boundary produces the stated result in a real run, read back from the repository, claim store or credential state. A mock that returns its own expected value does not count. Boundaries: **dispatch**, **publisher**, **authority check**, **registry publisher**.

## Positive controls

```gherkin
Feature: Assignment records and independence on fixed gates

  @ESE-15.2 @ESE-15.4 @ESE-17.1
  Scenario: R1-P1 A replacement candidate runs the same stage contract
    Given a phase was granted to candidate X with a recorded principal and execution context
    And Ky retires X and enrolls candidate Y by a merged registry change
    And Ky issues a new grant for the remaining work naming Y's principal and context
    When the phase runs
    Then the broker admits Y under the same stage checks
    And receipts for completed work keep their lineage
    And no enforcement code was edited

  @ESE-16.1 @ESE-16.2
  Scenario: R1-P2 A distinct reviewer in a different family and context is recorded as independent
    Given the coder principal is A in context C1
    And the reviewer principal is B in a different model family and context C2
    When the review phase is admitted
    Then the receipt records independence INDEPENDENT
    And the work can reach "eligible for owner review only" and no further

  @ESE-15.6
  Scenario: R1-P3 A recognized identity with a recorded delegation publishes a spec-only change
    Given the role map recognizes the publishing identity
    And an issue-specific delegation and scope is recorded
    When the identity pushes a change that touches only the spec path
    Then the publisher accepts it
    And the status is PENDING owner approval
```

## Adverse controls

```gherkin
Feature: Adverse cases on the assignment surface

  @ESE-15.1
  Scenario Outline: R1-A1 A vendor name is not a role
    Given a request names <claim>
    When dispatch evaluates the request
    Then it is admitted only if the grant names that authenticated principal for that phase
    And a vendor label with no grant is rejected with reason NO_GRANT

    Examples:
      | claim                                              |
      | "the Kiro agent" with no recorded principal        |
      | "the usual reviewer" with no recorded principal    |
      | an IDE name used as the principal                  |

  @ESE-15.3
  Scenario: R1-A2 Selection is not approval
    Given candidate X is eligible and selected for G5
    And Ky has issued no G4 acceptance and no G5 grant
    When X requests a writable workspace
    Then dispatch holds the request with the ESE-1 status and reason
    And no workspace, credential or file mutation is issued

  @ESE-15.5
  Scenario: R1-A3 No qualifying candidate holds the stage
    Given no enrolled candidate qualifies for the G2 stage
    When a spec is requested
    Then the status is HOLD with reason NO_QUALIFYING_CANDIDATE
    And only draft-only output outside protected paths is possible
    And no actor is permitted to act under another actor's identity

  @ESE-15.6
  Scenario Outline: R1-A4 An unrecognized identity cannot publish a spec
    Given the spec path is protected by the role gate
    When <actor> pushes a change under the spec path
    Then the publisher rejects it with reason UNRECOGNIZED_PRINCIPAL
    And the repository and remote ref are unchanged on readback

    Examples:
      | actor                                                              |
      | an agent using Ky's shared token with a bot-style author name      |
      | an identity with no recorded issue-specific delegation             |
      | a coder in a code PR that also touches the spec path               |

  @ESE-16.1 @ESE-16.3
  Scenario Outline: R1-A5 A reviewer who is not independent is rejected
    Given the coder principal is A in context C1
    When <reviewer> is presented as the reviewer
    Then dispatch rejects the review with reason NOT_INDEPENDENT

    Examples:
      | reviewer                                                       |
      | principal A in context C1                                      |
      | principal A in a second session with the same context          |
      | an actor whose free-text name differs but whose principal is A |

  @ESE-16.2
  Scenario: R1-A6 Same-family independence is recorded as limited and waits for Ky
    Given the only distinct reviewer is principal B in the same model family as the coder
    When the review phase is admitted
    Then the receipt records INDEPENDENCE_LIMITED with the reason
    And the stage does not advance until Ky accepts the limit

  @ESE-16.4 @ESE-16.5
  Scenario Outline: R1-A7 Role separation holds at the real boundary
    Given the actor holds only <grant>
    When it attempts <action>
    Then <boundary> rejects it with reason <reason>

    Examples:
      | grant                  | action                              | boundary        | reason              |
      | a G4 test-author grant | implementing production code        | authority check | PHASE_NOT_GRANTED   |
      | a G5 coder grant       | rewriting the accepted spec or tests| publisher       | ROLE_PATH_VIOLATION |
      | a reviewer grant       | merging, auto-merge, or deploying   | dispatch        | OWNER_ONLY          |

  @ESE-17.1
  Scenario Outline: R1-A8 A grant is bound to one principal, context and subject
    Given a grant binds principal, context, repository, issue, spec SHA, stage and paths
    When a request presents <mismatch>
    Then the authority check rejects it with reason GRANT_BINDING_MISMATCH at dispatch
    And the same check rejects it again immediately before publication

    Examples:
      | mismatch                           |
      | a different principal              |
      | the right principal in a new context |
      | another repository                 |
      | another issue                      |
      | another spec SHA                   |
      | another stage                      |
      | a path outside the grant           |

  @ESE-17.2
  Scenario Outline: R1-A9 Self-asserted identity does not establish the principal
    Given the grant names principal P
    When the actor presents <assertion>
    Then the actor is not treated as P
    And dispatch rejects it with reason UNRECOGNIZED_PRINCIPAL

    Examples:
      | assertion                                              |
      | a free-text model name matching the candidate          |
      | a Git author or committer field matching P             |
      | a shared-token appearance as KyPython                  |
      | an issue or PR comment saying it is P                  |
      | a verified commit signature alone                      |

  @ESE-17.3
  Scenario Outline: R1-A10 Owner decisions stay blocked until the channel is demonstrated
    Given no independent owner-only signing channel with trusted verification has been demonstrated
    When a stage that needs an owner decision is evaluated with <evidence>
    Then the status is BLOCKED with reason UNVERIFIABLE_APPROVER
    And no writable capability, dispatch, scoped credential, merge or deployment is issued

    Examples:
      | evidence                                    |
      | a chat message saying "approved"            |
      | a GitHub comment from the shared owner token|
      | an agent-produced signature                 |
      | a label, checkbox or @approved tag          |

  @ESE-17.4
  Scenario Outline: R1-A11 Retired, revoked or expired authority blocks the next effect
    Given candidate X was dispatched with a valid grant
    When <change> occurs before X publishes
    Then the publisher rejects X's publish
    And a selector rerun does not recreate the authority
    And the remote ref is unchanged on readback

    Examples:
      | change                         |
      | Ky retires X's registry entry  |
      | Ky revokes the grant           |
      | the grant expires              |
```

## Negative controls for the scenarios themselves

- An always-deny broker fails R1-P1, R1-P2 and R1-P3.
- A broker that compares vendor labels instead of principals fails R1-A5 and R1-A9.
- A publisher that trusts the commit author field fails R1-A4 and R1-A9.
- A broker that checks the grant only at dispatch fails R1-A8 and R1-A11 at the publication check.

## Requirement to scenario map

| Requirement | Positive | Adverse |
| --- | --- | --- |
| ESE-15.1 | R1-P1 | R1-A1 |
| ESE-15.2 | R1-P1 | R1-A1 |
| ESE-15.3 | none (adverse only) | R1-A2 |
| ESE-15.4 | R1-P1 | R1-A11 |
| ESE-15.5 | none (adverse only) | R1-A3 |
| ESE-15.6 | R1-P3 | R1-A4 |
| ESE-16.1 | R1-P2 | R1-A5 |
| ESE-16.2 | R1-P2 | R1-A6 |
| ESE-16.3 | R1-P2 | R1-A5 |
| ESE-16.4 | none (adverse only) | R1-A7 |
| ESE-16.5 | none (adverse only) | R1-A7 |
| ESE-17.1 | R1-P1 | R1-A8 |
| ESE-17.2 | none (adverse only) | R1-A9 |
| ESE-17.3 | none (adverse only) | R1-A10 |
| ESE-17.4 | none (adverse only) | R1-A11 |
