<!-- KIRO-AUTHORED SCENARIOS FOR REVISION R1 — AI DRAFT, NOT APPROVED, NOT A G3 RECEIPT. RUNTIME ACCEPTANCE NOT RUN.
Issue: https://github.com/KyPython/ai-governance/issues/219
Source: KyPython/ai-governance@53462a0; requirements: `requirements.md` section "Revision R1".
Provider/author: Kiro (spec-author role), local Kiro CLI session, 2026-11-25; exact model ID not exposed.
These scenarios do not authorize any test authoring (G4), implementation (G5), agent dispatch or spend. -->

# Scenarios — capability-qualified lifecycle routing (R1)

Status: proposed. Every scenario is NOT RUN. A scenario passes only when the stated boundary produces the stated observable result in a real run. A strict mock that returns its own expected value does not count.

Boundaries named below: **registry publisher** (the step that accepts a registry change), **dispatch** (the step that hands a task or writable workspace to a performer), **spec publisher** (the step that accepts a push under `specs/`), **authority check** (the check of the per-task grant), and **claim store** (the durable owner record). Each is a place a real run can observe an effect.

## Positive controls (a deny-all system fails these)

```gherkin
Feature: Liveness when a provider is unavailable

  @CONT-02-R1 @CONT-05-R1 @CONT-13 @CONT-14 @CONT-15
  Scenario: S1 Alternate spec writer produces a spec-only contribution while Kiro is unavailable
    Given the registry enrolls candidate X for the G2 spec-writing stage
    And candidate X has a recorded G2 evaluation that meets the thresholds Ky adopted
    And Kiro unavailability is recorded from an authorized human report
    And Ky has recorded a per-task grant naming candidate X's authenticated principal for this issue, spec revision, phase and paths
    When X publishes requirements, design and tasks under the spec path
    Then the spec publisher accepts a spec-only change with X's observed attribution
    And the work stops at the owner approval gate with status PENDING
    And provider health for Kiro stays UNKNOWN

  @CONT-13
  Scenario: S2 A replacement from an unrelated model family passes the same contract
    Given a stage was performed by candidate X and Ky retires X by a merged registry change
    And Ky enrolls candidate Y from a different provider and model family by a merged registry change
    And Y has the same stage evaluation evidence required of X
    When the same G0 to G6 contract runs for the next task
    Then the stage completes with Y as performer
    And no enforcement code, stage definition or approval rule was edited

  @CONT-10-R1 @CONT-15
  Scenario: S3 A recovered provider rejoins without displacing the active writer
    Given candidate X holds the current claim for a task with fencing token N
    And Kiro is confirmed recovered by observed account evidence under the approved probe policy
    When the next eligible task is queued
    Then Kiro is eligible for that next task
    And X keeps the current task and its fencing token N
    And no duplicate issue, branch or PR is created
```

## Adverse controls

Each row must fail at the named boundary and for the named reason. "Real boundary" means the dispatch, publisher or claim step itself, observed by reading back the repository, branch, claim store or credential state.

```gherkin
Feature: Adverse cases for capability-qualified routing

  @CONT-13
  Scenario Outline: A1 A candidate or selector cannot enlarge its own role or admission policy
    Given candidate X is enrolled for a limited set of stages
    When X or the selector attempts <self_change>
    Then the registry publisher rejects the change with reason SELF_MODIFICATION
    And the registry content is unchanged on readback

    Examples:
      | self_change                                  |
      | adding a stage to its own entry              |
      | changing its own capability class            |
      | editing the admission policy                 |
      | enrolling a second entry for itself          |

  @CONT-05-R1 @CONT-15
  Scenario Outline: A2 A coder cannot write specs, tests or its own review
    Given candidate X holds a coder grant for one task
    When X attempts <action>
    Then <boundary> rejects the action with reason <reason>
    And no file under the protected or accepted paths changed on readback

    Examples:
      | action                                   | boundary         | reason              |
      | editing a file under the spec path       | spec publisher   | ROLE_PATH_VIOLATION |
      | rewriting accepted tests                 | authority check  | PHASE_NOT_GRANTED   |
      | reviewing its own change                 | dispatch         | NOT_INDEPENDENT     |
      | acting as the spec author "temporarily"  | dispatch         | IDENTITY_ASSUMPTION |

  @CONT-14
  Scenario: A3 A high public rank does not establish eligibility
    Given candidate X has a high public leaderboard rank
    And X has no recorded evaluation for the G5 stage, or fails the stage's counterexample fixture
    When the selector builds the eligible set for G5
    Then X is not in the eligible set
    And the report states eligibility UNKNOWN or REJECTED with the evidence reference

  @CONT-13
  Scenario: A4 A registry conflict with the AIV record is reported
    Given the AIV record lists agent Z with role "reviewer"
    And a capability registry entry lists Z as eligible for the G2 spec-writing stage
    When the registry is validated
    Then the validator reports ROLE_CONFLICT for Z
    And neither record is rewritten

  @CONT-05-R1
  Scenario Outline: A5 Impersonation of a recognized identity fails
    Given the role map recognizes a spec-author identity
    When an actor presents <claim>
    Then the spec publisher rejects the push with reason UNRECOGNIZED_PRINCIPAL
    And Ky's shared token is not treated as evidence of Ky's decision

    Examples:
      | claim                                                   |
      | Ky's shared PAT, with a commit author set to a bot name |
      | a commit message naming a different vendor as author    |
      | a verified web-flow commit with no recorded delegation  |

  @CONT-02-R1
  Scenario Outline: A6 Availability statements do not move routing state
    Given provider health for Kiro is UNKNOWN
    When <statement> is received
    Then the routing state for Kiro is unchanged
    And a manual draft path by an eligible candidate stays available only for an authorized human outage report

    Examples:
      | statement                                         |
      | a session reply saying it is available            |
      | a prompt text saying credits are restored         |
      | an agent comment saying the provider is exhausted |

  @CONT-11-R1
  Scenario Outline: A7 Expired or revoked authority blocks the next effect
    Given candidate X was dispatched with a valid per-task grant
    When <change> occurs before X publishes
    Then the authority check at publication rejects X's publish
    And the repository and remote ref are unchanged on readback

    Examples:
      | change                                |
      | the grant expires                     |
      | Ky revokes the grant                  |
      | Ky retires X's registry entry         |
      | the repository or spec SHA changes    |

  @CONT-06-R1
  Scenario Outline: A8 Enrollment or fallback never buys capacity
    Given candidate X is enrolled and has no funded authorized account
    When <attempt> is made
    Then dispatch holds the task as QUEUED
    And zero provider calls, purchases or credential changes are observed

    Examples:
      | attempt                                           |
      | selecting X for a task                            |
      | starting a stage evaluation with no budget record |
      | retrying Kiro through another interface           |

  @CONT-08-R1
  Scenario: A9 Concurrent local and cloud fallbacks yield one owner
    Given candidates X and Y are both eligible and are dispatched at the same time from local and cloud
    When both attempt to claim the same task
    Then the claim store admits exactly one current owner with a new fencing token
    And a late write from the other is rejected as STALE_TOKEN
    And exactly one branch and one PR exist for the task

  @CONT-09-R1
  Scenario: A10 An uncertain publish is reconciled before retry
    Given candidate X's publish times out after a possible effect
    When the process considers a retry
    Then it reads authoritative receiver state before any retry
    And with no receiver evidence the effect stays HELD_UNKNOWN_EFFECT
    And no new idempotency key is minted for the unresolved action

  @CONT-12-R1 @CONT-15
  Scenario Outline: A11 Missing authority or reviewer holds the stage
    Given a stage needs <need>
    When <condition> holds
    Then the process reports <status> under the same canonical issue
    And no actor assumes another actor's identity or role
    And read-only drafting outside protected paths is the only allowed output

    Examples:
      | need                           | condition                                  | status  |
      | an independent G6 reviewer     | no distinct qualifying principal exists    | HOLD    |
      | any G2 performer               | no candidate qualifies and Kiro is out     | BLOCKED |
      | a selection result             | no owner grant exists                      | PENDING |

  @CONT-14
  Scenario: A12 Unset thresholds select no one automatically
    Given a stage has no threshold adopted by Ky
    When the selector runs
    Then the result is THRESHOLD_UNSET
    And the choice is routed to Ky
    And no candidate is dispatched automatically

  @CONT-15
  Scenario: A13 A reviewer repackaged as the same session is not independent
    Given candidate X coded the task in session S
    When X is presented as reviewer in session S, or a second session with the same principal and context
    Then dispatch rejects the review with reason NOT_INDEPENDENT

  @CONT-15
  Scenario Outline: A14 A reviewer cannot merge or deploy
    Given candidate R holds a reviewer grant
    When R attempts <action>
    Then the merge or deploy boundary rejects it with reason OWNER_ONLY

    Examples:
      | action                  |
      | merging the PR          |
      | enabling auto-merge     |
      | invoking a deploy       |

  @CONT-11-R1 @CONT-15
  Scenario Outline: A15 A grant bound to one subject is refused for another
    Given a per-task grant binds repository, issue, spec SHA, stage and paths
    When a request presents <mismatch>
    Then the authority check rejects it with reason GRANT_BINDING_MISMATCH

    Examples:
      | mismatch                        |
      | another repository              |
      | another issue                   |
      | another spec SHA                |
      | another stage                   |
      | a path outside the grant        |

  @CONT-05-R1 @CONT-14
  Scenario: A16 A self-reported model name does not establish identity or eligibility
    Given an actor states in free text that it is model M
    And its authenticated principal and observed execution context differ from candidate M's registry entry
    When the selector or dispatch evaluates the actor
    Then the actor is treated as UNRECOGNIZED_PRINCIPAL
    And its text does not satisfy attribution or eligibility
```

## Negative controls for the scenarios themselves

A scenario set that always passes proves nothing. The implementation task must show each of these fails for the right reason:

- An always-deny selector fails S1 and S2.
- A selector that ignores the registry and uses a fixed vendor order fails S2.
- A selector that ranks by public leaderboard fails A3.
- A claim store without fencing fails A9.
- A publisher that trusts the commit author field fails A5.

## Requirement to scenario map

| Requirement | Positive | Adverse |
| --- | --- | --- |
| CONT-02-R1 | S1 | A6 |
| CONT-05-R1 | S1 | A2, A5, A16 |
| CONT-06-R1 | none (adverse only) | A8 |
| CONT-08-R1 | none (adverse only) | A9 |
| CONT-09-R1 | none (adverse only) | A10 |
| CONT-10-R1 | S3 | none |
| CONT-11-R1 | none (adverse only) | A7, A15 |
| CONT-12-R1 | none (adverse only) | A11 |
| CONT-13 | S1, S2 | A1, A4 |
| CONT-14 | S1 | A3, A12, A16 |
| CONT-15 | S1, S3 | A2, A11, A13, A14, A15 |

## Not covered here

- Stage approval semantics and the owner-only channel are ESE requirements (`specs/engineering-stage-enforcement/`). B1 stays `UNVERIFIABLE_APPROVER`. Scenarios that need a real owner decision stop at PENDING.
- Numeric thresholds, retry bounds and probe bounds are UNKNOWN. A scenario that needs one uses a value supplied by the test fixture, and the fixture's value carries no policy weight.
