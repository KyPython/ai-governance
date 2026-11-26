<!-- KIRO-AUTHORED SCENARIOS — AI DRAFT, NOT APPROVED, NOT A G3 RECEIPT. RUNTIME ACCEPTANCE NOT RUN.
Issue: #238 · Source: KyPython/ai-governance@593f62f · Drafted 2026-11-25; model ID not exposed.
These scenarios authorize no test authoring, implementation, agent dispatch or spend. -->

# Scenarios — spec-author delegation check (SAD)

Status: proposed, NOT RUN. A scenario passes only when the real policy job returns the stated result and reason, read back from the job. A test that sets its own expected return value does not count.

Names used: **identity D** is an enrolled, delegation-required, non-owner spec-author identity. **Base** is `KyPython/ai-governance` `main`. **Folder F** is `specs/<slug>`.

## Positive controls (an always-deny check fails these)

```gherkin
Feature: Delegated spec publication

  @SAD-1.1 @SAD-2.1 @SAD-2.2 @SAD-3.4 @SAD-6.1
  Scenario: P1 A valid delegation on the base branch allows a spec-only PR
    Given Base holds a delegation record for identity D, this repository, issue N, folder F, with a future expiry and not revoked
    And the record was merged to Base before the pull request was opened
    When D opens a pull request that changes only files under F, and every commit author and committer is D
    Then the policy job passes the role gate
    And the pass line says the delegation was matched on the base branch and that identities are self-declared and not verified

  @SAD-1.2 @SAD-5.1 @SAD-5.2
  Scenario: P2 A standing identity keeps today's behavior with no delegation
    Given the owner has designated identity S as standing, or S is the owner
    And Base holds no delegation for S
    When S opens a spec-only pull request that changes files under F
    Then the policy job passes the role gate as it does today

  @SAD-1.4 @SAD-5.2
  Scenario: P3 Listed spec authors are explicitly standing when the check ships
    Given the check has shipped with kiro-agent[bot] and KyPython recorded as standing
    And Base holds no delegation for kiro-agent[bot]
    When kiro-agent[bot] opens a spec-only pull request under F
    Then the policy job passes the role gate as it does today
    And the role map holds an explicit standing designation for kiro-agent[bot], not an absent one
```

## Adverse controls (an always-pass check fails these)

```gherkin
Feature: Adverse cases for the delegation check

  @SAD-1.1 @SAD-3.2
  Scenario: A1 No delegation
    Given identity D is delegation-required and Base holds no record for D
    When D opens a spec-only pull request under F
    Then the policy job fails with reason NO_DELEGATION naming D and F

  @SAD-2.3 @SAD-3.2
  Scenario: A2 Expired delegation
    Given Base holds a record for D and F whose expiry is in the past
    When D opens a spec-only pull request under F
    Then the policy job fails with reason DELEGATION_EXPIRED

  @SAD-2.3 @SAD-3.2
  Scenario: A3 Revoked delegation
    Given Base holds a record for D and F marked revoked
    When D opens a spec-only pull request under F
    Then the policy job fails with reason DELEGATION_REVOKED

  @SAD-2.3 @SAD-3.2
  Scenario Outline: A4 Delegation for a different subject
    Given Base holds a valid delegation for D that names <recorded>
    When D opens a spec-only pull request that is for <actual>
    Then the policy job fails with reason <reason>

    Examples:
      | recorded                  | actual                    | reason                       |
      | repository R1             | repository R2             | DELEGATION_WRONG_REPOSITORY  |
      | issue N                   | issue M                   | DELEGATION_WRONG_ISSUE       |
      | folder specs/a            | folder specs/b            | DELEGATION_WRONG_SPEC_FOLDER |

  @SAD-2.3 @SAD-3.2
  Scenario: A5 Delegation belongs to another identity
    Given Base holds a valid delegation for identity E and folder F
    When identity D opens a spec-only pull request under F
    Then the policy job fails with reason DELEGATION_WRONG_IDENTITY

  @SAD-2.5 @SAD-3.2
  Scenario Outline: A6 A delegation created in the same pull request does not authorize it
    Given Base holds no delegation for D and F
    When D opens a pull request that <change> and also changes files under F
    Then the policy job fails
    And the reason is <reason>

    Examples:
      | change                                          | reason                              |
      | adds a delegation record for D and F            | DELEGATION_IN_SAME_PR               |
      | adds D to the role map                          | DELEGATION_IN_SAME_PR               |

  @SAD-3.1
  Scenario Outline: A7 An unreadable delegation file fails closed
    Given the delegation file on Base is <state>
    When D opens a spec-only pull request under F
    Then the policy job fails with reason DELEGATION_UNREADABLE

    Examples:
      | state                         |
      | missing                       |
      | not valid YAML                |
      | missing a required field      |

  @SAD-1.4 @SAD-3.2
  Scenario: A8 An undesignated identity is treated as delegation-required
    Given identity U is a spec-author identity with no designation
    And Base holds no delegation for U
    When U opens a spec-only pull request under F
    Then the policy job fails with reason NO_DELEGATION or UNDESIGNATED_IDENTITY

  @SAD-1.3
  Scenario: A9 One valid delegation does not cover a second folder
    Given Base holds a valid delegation for D and folder F1 only
    When D opens a spec-only pull request that changes files under F1 and F2
    Then the policy job fails for F2 with reason NO_DELEGATION naming F2

  @SAD-2.4 @SAD-5.4
  Scenario Outline: A10 Only the owner may change the delegation file or role map
    When <actor> opens a pull request that changes <target>
    Then the policy job fails the owner-only rule
    And the delegation file and role map on Base are unchanged

    Examples:
      | actor                          | target                |
      | identity D                     | the delegation file   |
      | a coder identity               | the role map          |
      | an identity with no enrollment | the delegation file   |

  @SAD-3.3 @SAD-6.5
  Scenario: A11 A skipped or missing delegation check is not a pass
    Given the delegation check did not run, or returned no result
    When the verdict is computed
    Then the verdict is not PASS
    And the report says the delegation check did not pass

  @SAD-4.1 @SAD-4.2
  Scenario Outline: A12 Comments, labels and shared-token appearances are not delegations
    Given Base holds no delegation for D and F
    And <evidence> is present
    When D opens a spec-only pull request under F
    Then the policy job fails with reason NO_DELEGATION

    Examples:
      | evidence                                                        |
      | an issue comment by KyPython saying "delegated to D"            |
      | a PR label "delegated"                                          |
      | a PR body line "Delegation: approved"                           |
      | a commit message naming Ky as approver                         |
      | a commit whose author is KyPython but whose actor is D          |
      | a verified commit signature alone                               |

  @SAD-4.3 @SAD-4.4
  Scenario Outline: A13 A delegation authorizes spec publication and nothing else
    Given Base holds a valid delegation for D and F
    When D attempts <action>
    Then the action is rejected at its own boundary and the delegation does not apply
    And any report of the delegation does not use the words "owner-authenticated" or "verified human approval"

    Examples:
      | action                                            |
      | changing code in the same pull request             |
      | merging or enabling auto-merge                     |
      | changing the role map or the delegation file       |
      | publishing under a folder not named in the record  |

  @SAD-5.1 @SAD-5.5
  Scenario Outline: A14 Existing rules and the no-wildcard rule hold
    When <case> is evaluated
    Then <result>

    Examples:
      | case                                                           | result                                              |
      | the existing GATE-3.1 to GATE-3.7 policy tests                 | they pass unchanged                                 |
      | a code PR that also touches a spec path                        | it fails as GATE-1.7 requires                       |
      | a role-map entry written as a pattern or wildcard              | the owner-only rule and schema reject it            |

  @SAD-2.5 @SAD-3.2
  Scenario: A15 A delegation merged after the pull request opened does not authorize it
    Given D opened a spec-only pull request under F at time t0
    And Base held no delegation for D and F at t0
    And Ky later merges a matching, unexpired, unrevoked delegation for D and F to Base
    When the policy job re-runs on the pull request
    Then the policy job fails with reason DELEGATION_AFTER_PR_OPENED
```

## Negative controls for the scenarios themselves

- An always-deny check fails P1.
- An always-pass check fails A1 to A12 and A15.
- A check that reads delegations from the pull request head fails A6.
- A check that treats a `KyPython` comment as a delegation fails A12.
- A check that matches the identity name by pattern fails A5 and A14.
- A check that reads only the current `main`, ignoring when the record arrived, fails A15.

## Requirement to scenario map

| Requirement | Positive | Adverse |
| --- | --- | --- |
| SAD-1 | P1, P2, P3 | A1, A8, A9 |
| SAD-2 | P1 | A2, A3, A4, A5, A6, A10, A15 |
| SAD-3 | P1 | A1 to A7, A11 |
| SAD-4 | none (adverse only) | A12, A13 |
| SAD-5 | P2, P3 | A10, A14 |
| SAD-6 | P1 | all adverse cases and the negative controls |

## Not covered

- Any real owner decision. A scenario that needs one stops at PENDING.
- Delegation lifetime values. A fixture supplies a value, and the value carries no policy weight.
