# Design — Lambda Handler API Gateway Event-Shape Regression (Local Tests)

<!-- ODIN_ROW_ID:3f08621e-0a7a-8155-9019-c1739de4151c -->
Relates to #12.
Relates to #18.

> **Spec-only.** This design describes *what the synthetic starter environment must look
> like* so a later Codex/Cursor handoff can build it. It intentionally stops short of the
> diagnosis, the handler fix, and any answer. See `requirements.md` R-700.

## 1. Purpose and framing

The task class (issue #18 title) is a **Lambda handler that regresses on an API Gateway
event shape**, caught by **local tests**. The design here does **not** solve that; it
specifies a reproducible bench on which KyJahn can observe the failure and perform the
diagnosis and fix by hand.

The design distinguishes evidence states exactly as `requirements.md` §1 does. Anything
marked **[UNKNOWN]** is a prerequisite for KyJahn, not a decision made here.

## 2. Prerequisites that gate the design (do not guess)

| ID | Prerequisite | Why the design can't proceed without it |
|---|---|---|
| U-1 | Exact approved Goal (issue #18 blank) | Defines done; scopes the fixture delta |
| U-2 | The specific event-shape delta | Determines fixtures (R-200) and the oracle assertion (R-300) |
| U-3 | Root cause / fix | Reserved to KyJahn; not designed here |
| U-4 | Runtime/language/layout | Determines manifest, test runner, paths (R-500) |
| U-5 | TaskRecorder tool/session | Determines the no-AI recording boundary (R-620) |

**Design rule:** every concrete choice below is presented as a *shape* with an explicit
placeholder where U-1..U-5 must land. The handoff MUST confirm these with KyJahn before
authoring files.

## 3. Target structure (shape, not final paths)

A self-contained subtree, exact root TBD pending U-4. Illustrative layout:

```
<handoff-root>/            # location & language per U-4 (confirm with KyJahn)
  README.md                # how to run + the STOP-HERE boundary (R-700.4)
  <manifest + lockfile>    # pinned deps (NFR-1, R-500.2)
  <handler-stub>           # starter stub, failing body is a marked TODO (R-500.1)
  fixtures/
    apigw-<shapeA>.json    # labeled event fixture (R-200)
    apigw-<shapeB>.json    # contrasting shape (R-200.2)
  tests/ (or oracle/)
    <failing-oracle>       # asserts observable behavior, fails unpatched (R-300)
  verify.<ext | script>    # one deterministic verdict command (R-400)
```

> The `<shapeA>/<shapeB>` names and field-level content are deliberately placeholders:
> the real delta is U-2 (KyJahn's diagnosis input), not something this spec may invent.

## 4. Component design

### 4.1 Event fixtures (R-200)
- Checked-in JSON representing the API Gateway event(s) under test. Candidate shapes to
  *consider* once U-2 is known include REST/`v1` vs HTTP-API `v2.0` payloads, presence vs
  absence of a field (e.g. a path/query/header/body/`requestContext` member), encoding
  (base64 body flag), or single- vs multi-value headers. **[INFERENCE]** — these are the
  usual event-shape failure modes; the actual one is **[UNKNOWN]** until KyJahn confirms.
- Each fixture is labeled by shape (filename + sidecar/comment) so the pass/fail contrast
  is visible without reading handler code (R-200.2).
- Synthetic/sanitized values only; no real ARNs, account IDs, tokens (R-200.3).

### 4.2 Handler stub (R-500.1)
- Minimal handler with the correct signature for the chosen runtime (U-4) that **exhibits
  the failing behavior** and leaves the substantive logic as a clearly marked `TODO`.
- The stub is *scaffolding*: it must be runnable by the oracle and must fail, but it must
  not contain the correct event-shape handling. It encodes the problem, never the answer.

### 4.3 Failing oracle (R-300)
- Loads a fixture, invokes the handler, asserts the **observable response/effect** that a
  correct handler would produce for that shape.
- Fails (non-zero) against the stub; would pass once KyJahn's fix is applied — with no
  other change.
- Asserts behavior/contract, never source text (R-300.2); carries a legible failure
  message naming input shape, expected, actual (R-300.4).
- Contains no corrective logic, expected diff, or root-cause hint (R-300.3).

### 4.4 Verification harness (R-400)
- A single deterministic command (`verify.*`) that runs the oracle(s) and prints a clear
  verdict + exit code. Offline, no AWS creds, no network (R-100.1, NFR-2).
- It is the proof mechanism for KyJahn's eventual fix but holds no fix itself (R-400.2).

### 4.5 README with the STOP line (R-700.4)
- Documents: one-command setup, one-command verify, what the failing output means, and a
  prominent **"STOP HERE — human diagnosis begins"** section mapping to R-700. The human
  (KyJahn) resumes at diagnosis with no AI during TaskRecorder (R-620).

## 5. Determinism design (R-100)
- Pin all dependency versions; commit the lockfile (NFR-1).
- No wall-clock, RNG, locale, or map-order dependence in fixtures/oracle; if any seed is
  needed it is fixed and documented (R-100.2).
- Two consecutive clean runs yield identical verdicts (acceptance for R-100.2).

## 6. The STOP line — how it is enforced (R-700)

The boundary is the central design constraint. Enforcement is *observable*:

1. **Out-of-the-box failure.** On the delivered, unmodified environment the verification
   harness MUST FAIL. A passing out-of-the-box run means the fix leaked → the handoff is
   rejected (R-700.1).
2. **No answer artifacts.** No file named/acting as a solution, patch, fix, or answer key;
   no commented-out correct logic; no prose stating the root cause or corrective change
   (R-700.2).
3. **No human-work capture.** The environment records none of KyJahn's diagnosis,
   decisions, or final verification (R-700.3, R-620.1).
4. **Documented handoff point.** README's STOP-HERE section marks exactly where the human
   takes over (R-700.4).

A reviewer checklist (see `tasks.md` T-700) makes each of the four points a yes/no gate.

## 7. Governance & delivery design (R-600)
- This spec change is docs-only under `specs/`. **[VERIFIED CURRENT OBSERVATION]:** per the
  `policy` job in `.github/workflows/governance.yml`, `specs/` is **not** a structural path
  (structural = `packages/`, `.github/workflows/`, `scripts/validate*`, `docs/quality|architecture/`,
  `apps/tools/skeleton-base/`, or AGENTS/CLAUDE/.cursorrules/SPEC/empire-spec files), so **no
  `SYSTEMS_THINKING_CONTRACT` is required** for the spec PR. If KyJahn later places the handoff
  under a structural path, the handoff PR must add a contract covering it (**[INFERENCE]** from
  the same policy rule).
- Delivery is branch + PR; agents never merge/deploy; KyJahn merges (R-600.1).
- PR body carries `ODIN_ROW_ID:3f08621e-0a7a-8155-9019-c1739de4151c`, `Relates to #18`,
  `Relates to #12`; Conventional-Commit title (R-600.2/.3). The orchestrator publishes.
- The later handoff ships its oracle/tests with behavior (governance Rule 3) and must pass
  `quality` + `policy` + `secret-scan` → `verdict` (**[VERIFIED CURRENT OBSERVATION]**).

## 8. Risks & tradeoffs
- **R-A: Fix leakage.** The scaffolding could accidentally encode the answer. *Mitigation:*
  R-700 out-of-the-box-failure gate + reviewer checklist.
- **R-B: Over-specification.** Designing fixtures before U-2 is confirmed would invent
  KyJahn's diagnosis. *Mitigation:* placeholders + prerequisite gate (§2).
- **R-C: Non-determinism** hiding or faking the failure. *Mitigation:* §5 + double-run
  acceptance.
- **R-D: Wrong runtime assumption** (U-4). *Mitigation:* confirm language/layout before
  authoring; nothing in this spec hard-codes a runtime.

## 9. Open questions for KyJahn
All of U-1..U-5 (`requirements.md` §2). None may be resolved by inference before the
handoff authors files.
