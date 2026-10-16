# Trial report — Approval Before Dispatch

## Verification status

- **Offline fixture execution:** completed, **20/20 passed**.
- **Unauthorized simulated dispatches:** **0 across 18 blocked cases**.
- **Authorized simulated dispatches:** **2 across 2 allowed cases**.
- **Supplemental unit tests:** **5/5 passed** (including negative canary assertions that reject false success).
- **Native Inspect AI execution:** **NOT RUN**. Package `inspect-ai` was not installed in this environment; the package registry was unreachable (DNS/network failure), so native framework integration was not exercised here.
- **Actual agent/model execution:** **NOT RUN**. Only the local reference policy and its inert transport were exercised.
- **Cloud or scheduled eval:** **NOT CONFIGURED**.

## What was demonstrated

An in-memory implementation validated a trusted preflight, authorized human approver, approval validity/revocation, scoped message digest, policy revision, workflow identity and replay checks prior to recording a *simulated* dispatch. Eighteen deliberately unauthorized cases produced zero simulated dispatches. Two exact authorized cases each recorded a simulated dispatch.

The scoring function compares an independently specified expected outcome with **recorded dispatch events**, rather than relying solely on textual statements of compliance.

## Recommendation

**KEEP the 20-case dataset/scorer as a small reusable starter; HOLD cloud scheduling and production compliance claims.**

The next meaningful verification is to install `inspect-ai` in a network-enabled environment and run:

```bash
inspect eval approval_eval.py --model none --log-dir ./logs
```

Then attach the runner to an actual **sandboxed** dispatch policy with trustworthy approvals and external-effect instrumentation. Inspect's own log should be reviewed for all 20 cases, and negative canary checks repeated there. A production-readiness claim requires tests of the real agent/tool boundary (including bypass paths, concurrent dispatch, revocation races, retries), not only a self-authored reference gate.

## Source references

Inspect official documentation: https://inspect.aisi.org.uk/tasks.html ; https://inspect.aisi.org.uk/solvers.html ; https://inspect.aisi.org.uk/custom-scorers.html ; https://inspect.aisi.org.uk/models.html
