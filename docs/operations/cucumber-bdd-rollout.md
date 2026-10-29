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

## Proposed pilot: Claim Checker (pending spec acceptance)

**Repository:** `KyPython/claim-checker`. It already uses Node's test runner, Playwright and offline fixtures and has an extensive draft requirements spec at `specs/claim-checker/requirements.md`. Do **not** start a code PR merely because that draft exists. First resolve its owner-approved spec state and its issue. The current CI `FREE_CI_ENABLED` guard can skip tests; a skipped workflow is not acceptance.

Candidate behavior to specify and *only then* automate (subject to source spec and acceptance IDs):

> Given a submitted factual claim with no qualifying, same-proposition source evidence  
> When the genuine offline verdict path completes with the specified response fixture  
> Then the user receives `UNVERIFIABLE` and an actionable settle-it note, rather than a fabricated decisive verdict.

Compare the new scenario with the existing worker tests and evaluation harness. If this outcome is already sufficiently covered and readable, **do not duplicate it just to use Cucumber**. Check separately whether a scenario genuinely needs a browser; prefer no browser for service-level behavior. No live Puter, Gemini, OpenRouter or other provider calls, new credentials, paid usage, or output claims.

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

1. Kiro/owner produces approved spec(s) linked to #238. If no authorized spec channel exists, leave the work blocked and report the precise blocker.
2. Implement and independently verify **one** pilot on its own code branch/PR, including failing negative control and ordinary CI.
3. Decide repo-by-repo whether the pilot creates evidence or comprehension value; avoid redundant adapters and test-count inflation.
4. Record actual PRs, CI, remaining gaps and owner merge decisions in #238. Do not claim `Cucumber rolled out everywhere` from documentation alone.
