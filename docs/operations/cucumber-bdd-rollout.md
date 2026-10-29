# Cucumber / Gherkin behavior testing — cross-repo adoption guide (proposal)

**Status:** proposed documentation only; NOT an implemented testing framework, approved Kiro spec, or new CI policy.  
**Canonical work record:** [KyPython/ai-governance#238](https://github.com/KyPython/ai-governance/issues/238).  
**Authorship:** GPT-6 drafted this guide using the owner's connected GitHub access on the owner's October 29, 2026 request. It is not Kiro-authored and does not assert owner acceptance.  
**Merge authority:** owner only. No agent may merge or deploy this proposal.

## Purpose

Use executable Gherkin examples at a *small number of critical user-observable or external-effect boundaries*, without replacing unit, integration, Playwright, security, formal verification, incident, or performance tests. Avoid adding `.feature` files which are not bound to real assertions. No BDD score is evidence of human skill mastery or model quality by itself.

Upstream references:
- [Cucumber installation / language support](https://cucumber.io/docs/installation/)
- [Cucumber-JS](https://cucumber.io/docs/installation/javascript/)
- [Gherkin reference](https://cucumber.io/docs/gherkin/reference/)
- [Cucumber-JS maintained runtime requirements](https://github.com/cucumber/cucumber-js/blob/main/package.json)

## Default workflow: BDD discovery → SDD → BDD formulation → TDD → implementation → independent verification

**Applicability:** For every new or changed user-visible behavior, authorization boundary, cross-component effect, state transition, or consequential failure path, consider a *brief behavior-discovery checkpoint* before Kiro writes a spec. For refactors, security remediation, tiny technical changes, mature unit-tested components, generated code and upstream forks, use existing tests where sufficient; do not force a Gherkin runner. The absence of new .feature files is not failure if observable examples already have trustworthy coverage.

1. **Behavior discovery (before SDD):** Owner/product viewpoint, specification author and verifier identify the actor's outcome, actual trigger, rules, counterexamples, unknowns, and measurable success/failure. Source actual requirements and behavior. Distinguish accepted examples from AI-proposed examples; the owner retains formative judgments. Do not fabricate agreement or a stakeholder workshop.
2. **SDD specification and approval:** Kiro (or an explicitly permitted, truthfully attributed owner override) writes requirements, design, and tasks in a **spec-only PR**. Link each scenario/rule to exact stable EARS requirement IDs and existing business, security or state-machine constraints. Owner reviews and merges the spec before code. BDD examples *inform* SDD; they do not bypass the spec gate or replace requirement sentences.
3. **BDD formulation (before code):** Express just the agreed high-value examples as domain-level `Given/When/Then` cases (or equivalently precise acceptance examples when a separate runner adds no value). Freeze positive, adverse, ambiguity, denied, timeout and idempotent outcomes *as applicable*. Any material spec ambiguity goes back to the spec author and owner; never silently change an accepted EARS sentence to fit the test.
4. **ATDD + TDD red (authorized code phase):** One assigned coder links a scenario to production behavior through real step definitions/test fixtures and demonstrates the expected **failure before implementing the missing behavior**. Add narrower unit/contract tests as needed; verify that deliberate violation/negative controls actually fail. Do not count unmatched steps, forced skips, fabricated results, or code text inspection as executable acceptance.
5. **Minimal implementation / green:** Make the smallest approved change that passes the behavior scenario and relevant unit tests; preserve controls, side-effect permissions and existing workflows. Re-run the full original test suite. Do not turn each spec sentence into a redundant Gherkin scenario.
6. **Changed independent verification and human merge:** Different verifier reproduces positive/negative cases, source revision, install, lint, typecheck, build, original tests, real BDD execution if selected, and required governance/security/formal checks. Record blocked and skipped honestly. Owner alone merges; deployment remains separately gated. Retrospectively correct specs through a new approved spec PR if real behavior differs.

**Compact scenario-review checklist (not a test result):** Who experiences the outcome? What observable action triggers it? Which business rule/invariant? What contrasting example could disprove our assumption? What must the system refuse or leave unknown? What existing test already covers this? What source/license/authority permits the fixture? Which requirement ID and eventual executable test prove this *same* outcome? Does adding Cucumber improve communication or verification rather than count?

**Decision outcome per scope:** `ADOPT CUCUMBER`, `BDD DISCOVERY ONLY`, `EXISTING TESTS SUFFICIENT`, or `BLOCKED: SPEC / AUTHORIZATION / ENVIRONMENT`. A documented `EXISTING TESTS SUFFICIENT` is a valid successful triage result. Do not enforce a universal package install or claim this draft guide is already the default policy on main.

Official BDD workflow: https://cucumber.io/docs/bdd/ (Discovery → Formulation → Automation). Official Gherkin reference: https://cucumber.io/docs/gherkin/reference/ .

## Proposed governance upgrade: separate human approvals at every transition (not yet enforced)

**Owner instruction dated 2026-10-29:** Owner requests explicit approval at *each* BDD/SDD/TDD/implementation handoff, not merely at spec merge or final PR merge. This is a **proposed requirement** for the canonical `KyPython/ai-governance` policy, `AGENTS.governance.md`, `roles.yml` and its reusable verdict workflow. This **document does not itself change the live governance gate**, grant approval for an individual project, or constitute the Kiro-authored spec needed before executable policy code changes.

### State transitions and minimum approvable evidence

Each checkpoint has a named **human owner decision** with `APPROVE / REJECT / REQUEST_CHANGES / DEFER`; absence, ambiguity, expired/stale decision or missing evidence means **HOLD**. An approval authorizes the *next* specified phase only, within the recorded repo/issue/spec/revision/scope. Approval of one phase does not automatically approve later phases or a cost-bearing action.

| Gate | Prior state → permitted next state | Artifact the owner must approve | Prohibited until gate passes |
| --- | --- | --- | --- |
| **G0 — start discovery** | Identified need → BDD discovery | Source-backed issue, repo/scope, actors, problem, permitted research/fixtures, no-go boundaries | Broad or external discovery outside approved scope; implementation |
| **G1 — discovery acceptance** | Discovery → SDD spec authoring | Owner-reviewed behavior inventory: real actor/outcome, rules, concrete positive/adverse/ambiguous examples, exclusions, unresolved questions and source links | Authoring an authoritative spec from disputed assumptions |
| **G2 — SDD acceptance** | Kiro spec-only PR → BDD formulation | Ky-reviewed and **merged** spec with exact EARS requirement IDs, design/tasks, ownership, contracts and traceability; accepted base revision/merge SHA | Code/step-definition changes or unapproved alteration of requirement sentences |
| **G3 — BDD formulation acceptance** | Agreed spec → TDD/ATDD red | Owner-reviewed Gherkin (or equally precise executable acceptance examples), scenarios mapped to requirement IDs, fixtures, expected fail/abstain/error behavior, proof they are not redundant | Writing executable test changes outside the approved scenario scope; production edits |
| **G4 — RED acceptance** | Authorized test-only PR and genuine red-run evidence → production implementation | Source revision, test-only diff, actual command/log/run ID, precise intended failing assertions, independent validation that RED is caused by the missing behavior (not missing dependency, broken environment or intentionally disabled tests), with no weakening existing checks | Production edits, silent change of test expectations, fabricated RED receipt |
| **G5 — GREEN/implementation acceptance** | Implementation candidate → independent changed verification | Implementation diff, trace to approved spec and RED evidence, observed GREEN on same scenario, baseline suites and side-effect boundaries; owner authorizes independent review of this candidate | Self-attested completion, final PR merge, deployment |
| **G6 — verification acceptance** | Independent reviewer evidence → owner merge decision | Reviewer identity distinct from coder, independent changed verification and negative controls, full suite/CI, security and formal gates, exact head SHA and postconditions | Merge, deploy or claim verified outcome without owner approval, required checks and independent evidence |

**Existing owner gates stay additional**: `ai-governance / verdict` required, Ky alone merges, deployment requires its own separate authorization and exact-revision checks, and LamportLogic `AI_MONETIZATION_GATE` must return `ALLOW` for *each* mutation target. Paid inference, public sharing, secrets, production effects, and disclosure of private content each need their existing explicit authority; these stage approvals do not silently confer it.

### Security, provenance and enforcement design requirements for Kiro

1. **Strong trusted owner identity, not an author field:** `roles.yml` explicitly warns that agent writes using the linked `KyPython` token look like owner writes. Thus a PR comment, YAML checkbox, Gherkin `@approved` tag, commit author, GitHub label, or bot-supplied JSON alone is **not adequate proof of Ky's human decision**. Kiro must specify an independently verifiable approval channel/artifact with authentication and trustworthy issuer, or the gate must block with `UNVERIFIABLE_APPROVER`; it must not accept self-declared signatures or agent-controlled approval receipts. If no trustworthy owner proof is available, stop instead of emulating Ky.
2. **Bind to exact immutable inputs:** Store stage, scope, source revision or digest, issue and approved spec merge SHA, approved scenario/fixture digest, decision, timestamp, approver authority, and referenced evidence. The trusted verifier must check their origin and integrity; revised requirements, test scenarios, target scope, unauthorized effects or a changed implementation after G5 invalidate impacted downstream approvals. No inheritance across repositories or unrelated issues. Revocation and supersession must be effective and auditable.
3. **Fail closed and distinguish statuses:** Required stage missing, malformed, untrusted, revoked, stale, or inconsistent → HOLD; an unavailable approval service must not default to approve. Report `PENDING / BLOCKED / REJECTED / SUPERSEDED / VERIFIED` accurately. `G4` RED means expected assertion failure specifically attributable to the unmet requirement, *not* a generally failing CI job. `G5` GREEN without independent review cannot satisfy G6. Skipped CI does not pass.
4. **Enforcement must work before implementation begins:** A final PR check alone cannot prevent an agent starting code after G3 without G4. Specify guard checks at agent task dispatch / writable workspace handoff / pre-mutation hook, plus blocking final CI for unauthorized phase artifacts and PR merges; describe any surfaces where enforcement is impossible rather than claiming full prevention. Require explicit per-file mutation authority if a stronger repo gate exists. No protection-relaxing changes.
5. **Role separation:** Kiro/authorized spec-author prepares SDD, coder writes accepted failing tests and minimum implementation, a different agent independently verifies, and **only Ky authorizes each transition**. Agents may present recommendations but cannot approve/merge their own work or count automation checks as human judgment. Permission decisions are not delegated to a model.
6. **No blanket friction/false tests:** For documentation-only, mechanical or no-material-behavior changes, Kiro must specify a **trusted owner-approved applicability decision** (`FULL`, `LIMITED`, or `NOT_APPLICABLE`), with source rationale, scope and retention of existing security/merge gates. Agents cannot grant themselves a waiver by changing labels, folder names or wording. For emergency security fixes, explicit separately defined owner break-glass process with independent evidence; never a silent bypass.
7. **Adversarial verification before activation:** Positive control: every gate approved and exact evidence matches. Negative controls: missing G0/G1/G3/G4/G5/G6; forged owner comment from token-authenticated agent; swapped spec SHA; modified scenarios after G3; false RED from setup failure; stale approval replay; revoked approval; wrong repo/issue; same coder/reviewer; skipped required CI; agent-declared N/A; bypass via docs/lockfile exemption or branch rename. All unauthorized transitions must fail closed. Show the pre-mutation enforcement point and the final verdict separately.
8. **Rollout and migration:** Adopt incrementally through the existing spec-only PR and subsequent policy-code PR(s), first on one justified pilot. Version the approval schema; document treatment of open/in-flight PRs (do not retroactively fabricate approvals), rollback without a self-approved escape, signing/issuer trust and secrets boundaries. Only owner-controlled merges activate policy; avoid introducing a gate that deadlocks authorized Kiro spec creation.

**Acceptance criterion for actual governance rollout:** prove via authenticated origin and intentionally forged evidence that *the actor allowed to author/test/code cannot also manufacture the owner approval that lets them advance*. If that cannot be demonstrated, describe approvals as human process obligations only and **do not claim the workflow programmatically enforces them**.

### Status at authorship

No new `AGENTS.governance.md`, `roles.yml`, validator, reusable workflow, Cucumber dependencies, feature files, or code modified by this section. **G0–G6 are proposed requirements, not functioning GitHub status checks.** Owner's request to strengthen governance is explicit, but does not bypass the existing Kiro spec-first, code/CI and human-merge boundaries. This draft PR must remain separate from the Kiro-authored spec PR and any eventual governance implementation PR.

## Per-repository decision (before editing)

1. Inspect that repository's `AGENTS.md`, required approvals, branch rules, existing issue/spec, test scripts, lockfile, runtime version, CI job, and any mutation or monetization gate.
2. Find **one real behavior contract that current tests cannot communicate or exercise clearly**, plus a negative control. If existing tests already express it well, record "no adoption" and retain them.
3. Choose only the stack-matched maintained implementation:
   - JavaScript / TypeScript: official `@cucumber/cucumber` as a **development** dependency when compatible with the repo's Node version. Cucumber-JS v13 requires Node 22, 24, or 26; confirm against current official release before pinning.
   - Python using pytest fixtures: `pytest-bdd` as a test dependency. Use `behave` only where the project deliberately does not follow pytest fixture conventions.
   - Other languages: evaluate their official or maintained equivalents. Do not inject a JavaScript runner into Python, Kotlin, Go, C#, or Rust repositories.
4. Freeze an observable `Given/When/Then` acceptance contract, then independently implement real step definitions, using the existing *production* execution path and deterministic offline fixtures.
5. Require one example that passes because the behavior is correct, and one falsifying negative example that fails for a deliberately wrong implementation. A fake runner, skipped scenario, empty `Then`, mocked success flag, or string-search-only "assertion" does not count.
6. Wire a true failing-on-error command into the repo's ordinary tests / CI, preserve the original suites and provider/secret boundaries, and verify dependency lock/engine compatibility.
7. Report **actual** install, lint, typecheck, test, build, CI and governance checks separately. Missing, skipped, blocked and unexecuted are not green.

## First implementation qualification — no automatic pilot selection

Read-only examination of the current tests found that the initially proposed Claim Checker abstention example is **already asserted** in `KyPython/claim-checker/tests/worker.test.js` (ungrounded decisive verdict becomes `UNVERIFIABLE`, and absent/faulty evidence is handled by the existing worker harness). Adding the same example under Cucumber would increase maintenance without clear new evidence. Its current spec is marked draft; CI may skip under `FREE_CI_ENABLED`. **Do not install Cucumber there until a different real cross-boundary acceptance gap is established and the spec is approved.**

`KyPython/effectproof` already carries `commit-ack-lost-idempotent.yaml` and `commit-ack-lost-duplicate.yaml` fault scenarios and Jest tests. BDD discovery could improve cross-role agreement, but converting those scenarios to Gherkin without a demonstrated missing user-observable contract is duplication. Its `node >=18` package engine is also below the runtime required by current Cucumber-JS versions; first make a deliberate, tested Node compatibility decision if adoption eventually earns its place.

`KyLamportLogic/ky-cloud-control-plane` has rich Python unittest, OPA and TLA+ coverage. A stakeholder-readable acceptance example such as *owner-authorized effect receives no conclusive receipt and must remain unconfirmed* may be valuable **only if** it tests a behavior distinct from its existing verification. Prefer `pytest-bdd` only if a reviewed pytest transition/fixture strategy is justified; its current controller suite is `unittest`. Do not replace OPA/TLA+ with Gherkin.

**Pilot selection gate:** choose exactly one of the above or another owner-controlled application after comparing source evidence, existing tests and requirement coverage. Require a documented untested/poorly communicated observable behavior and a positive+negative reproduction plan. Then follow the spec-first role boundaries. Until that evidence exists, **workflow documentation is the only implemented change in this PR**.

## Subsequent candidates, not automatic installation

| Repo / family | Reason to evaluate | Boundary before implementation |
| --- | --- | --- |
| `KyPython/effectproof` | Authorization and evidence for state-changing effects | Existing Kiro spec and ordinary tests first |
| `KyLamportLogic/ky-cloud-control-plane` | Authorized dispatch, deduplication, reconciliation | Do not replace unit, OPA or TLA+; local trust rules |
| `KyLamportLogic/LamportLogic` | One selected app journey or verified external effect | `AI_MONETIZATION_GATE` must ALLOW every repo-relative target; no monorepo-wide dependency by default |
| `KyLamportLogic/buildlogic-governance` / `KyPython/ai-governance` | Genuine guard outcomes in existing harness | Never weaken protected verdict/workflows/roles |
| `KyPython/site-forecast-app` / `KyPython/openmrs-ddi-knowledge-base` | Domain-facing Python outcomes | Inspect existing pytest and dataset rights first |
| `KyPython/oss-integration-checks` | Synthetic offline validation outcomes | Preserve adversarial controls and strict evidence separation |
| `KyPython/openmrs-esm-chartsearchai` | Application user-flow tests | Respect existing upstream integration/testing conventions |

**Deliberate non-targets:** mirrored upstream libraries/forks (promptfoo, JupyterLab, axe-core, pa11y, pa11y-ci, deepeval, pytest, OpenFn, upstream OpenMRS chart), educational and intentionally incomplete repair exercises, the Visit Taniti static WGU coursework prototype without a genuine executable boundary, a profile repository, and the external Alignerr task repository. Reconsider a specific one only with independent utility and permission. This list describes *present judgment*, not blanket permanent exclusion. The full 34-repository inventory is in issue #238.

## Authoritative implementation gates

- Follow `AGENTS.governance.md` and repo-specific instructions. **Spec first:** Kiro writes spec-only PRs, Ky may act as owner, and coders implement only approved, already-merged requirements. Never use the connected user's GitHub identity to impersonate the authorized spec author or to satisfy an authorship gate.
- Every code PR names the issue and an approved spec on the base branch, and cites exact criterion IDs in real tests.
- Branch + PR only; no agent merges, deploys or self-approves. Any structural file must have the required existing systems-thinking contract.
- For `KyLamportLogic/LamportLogic`, execute `pnpm ai:mutation:check --scope <catalog-scope> --target <repo-relative-path>` on **each** target and act only on `ALLOW`. A chat instruction is not an ALLOW result.
- Keep Human Skill Retention and the Human Rebuild learner-workspace human-write boundary. Generated answers and tests are AI exposure, not evidence of unaided learner capability.
- No cross-repo mass dependency update, no remote/paid provider evaluations, and no public publication are authorized by this documentation PR.

## Follow-through

1. Run behavior discovery on one justified capability, capture the accepted rules and counterexamples, and have Kiro/owner produce an approved spec linked to #238. If no authorized spec channel exists, leave the work blocked and report the precise blocker.
2. Only if a real acceptance gap warrants the runner, implement and independently verify **one** pilot on its own code branch/PR, including failing negative control and ordinary CI.
3. Decide repo-by-repo whether the pilot creates evidence or comprehension value; avoid redundant adapters and test-count inflation.
4. Record actual PRs, CI, remaining gaps and owner merge decisions in #238. Do not claim `Cucumber rolled out everywhere` from documentation alone.
