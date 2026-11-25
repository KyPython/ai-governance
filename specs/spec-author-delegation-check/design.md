<!-- KIRO-AUTHORED SPEC — HUMAN ADOPTION/MERGE PENDING. Not an owner approval. Drafted 2026-11-25; model ID not exposed.
Issue: #238 · Source: KyPython/ai-governance@593f62f · Completion: no completion contract; not gate-verified. -->

# Design: Spec-author delegation check

Status: proposed; supports SAD-1 to SAD-6. This design edits nothing. Every change to a protected path is a proposed future task (SAD-5.4).

## Current behavior (verified)

1. The policy job fetches the role map from `ROLES_URL`, which points at `KyPython/ai-governance` `main`, and fails closed if it cannot (GATE-3.4, GATE-3.5; `governance.yml` about lines 586 and 609 to 671).
2. For a pull request that changes a spec path, it requires the opener and the author and committer of every commit to match an identity in the `spec-author` role. A web-flow committer is checked by author only (GATE-3.1, GATE-3.2).
3. For a pull request in `KyPython/ai-governance` that changes `roles.yml`, it requires the owner identity (GATE-3.3; about lines 979 to 984).
4. Its pass messages say identities are "self-declared, not verified".

## Gap

Step 2 answers "is this identity a spec author". It does not answer "did the owner ask this identity to write this spec". For `kiro-agent[bot]` and `KyPython` that is acceptable today, because both are standing. It is not enough for an additional identity that the owner enrolls for one purpose.

## Proposed behavior

Add one check to the role gate, after the existing GATE-3.1 check passes:

```
for each spec folder F touched by the PR:
    for each identity I on the PR (opener, commit authors, committers except web-flow committers):
        if I is the owner or designated standing:   continue      (SAD-1.2)
        record = delegations on Base matching (I, this repository, issue, F)   (SAD-2.1, SAD-2.2)
        if no record:                               fail NO_DELEGATION
        if record.revoked:                          fail DELEGATION_REVOKED
        if record.expires <= now:                   fail DELEGATION_EXPIRED
```

Other named reasons come from comparing which field differs. Any read, parse or schema error fails with `DELEGATION_UNREADABLE`. Records are read from `main` only, so a record added by the PR under review is not in the set (SAD-2.5).

The "issue" that the pull request is for comes from the PR body's existing `Relates to #N` or `Closes #N` reference, which the policy job already parses (GATE-1.1). A pull request with no issue reference matches no record. The spec folder comes from the changed paths under the spec paths read from `roles.yml`.

## The delegation record

A record is data with these fields. The format and file name are UNKNOWN until Ky decides.

| Field | Meaning |
| --- | --- |
| `identity` | The exact enrolled identity string. No wildcard or pattern |
| `repository` | `owner/name` of the repository whose PR is checked |
| `issue` | Issue number that records the request |
| `spec_folders` | Exact folder names or paths the identity may change |
| `expires` | Required. A date-time. The maximum lifetime is UNKNOWN |
| `revoked` | `false` or `true`. Revocation is a merged edit that sets it, or removes the record |
| `note` | Free text for the owner. Not read by the check |

Designation (standing or delegation-required) is a per-identity field in the owner-controlled role map or the delegation file. An identity with no designation is treated as delegation-required (SAD-1.4).

## Where the record lives (alternatives)

| Option | For | Against |
| --- | --- | --- |
| New owner-only file on `main`, for example `delegations.yml`, protected by the same owner-only rule as `roles.yml` | One purpose per file. The role map schema stays as it is, so GATE-3.4 validation does not change. Delegations have a different churn rate than roles | A new protected file needs a CODEOWNERS line. That is a protected change |
| A `delegations:` block inside `roles.yml` | One file, and the owner-only rule already covers it | Mixes durable roles with short-lived grants. Changes the schema that GATE-3.4 validates |
| Records as issue comments or labels | Easy to write | Forgeable by any agent that uses Ky's token. Rejected by SAD-4.1 |
| Records in a PR body | Visible in review | Editable by the PR's author. Rejected by SAD-2.1 |

This design proposes the first option as the default. It is a proposed implementation constraint. The choice is Ky's.

## What a delegation proves, and what it does not

The record is read from `main`, and only the owner identity may change it (SAD-2.4). So the check proves "an owner-identity merge put this record on `main` before this PR existed".

It does not prove that the human Ky made that merge. An agent using Ky's token appears as `KyPython`, and git author fields are self-declared (AGENTS rule 2, "Limit"; `roles.yml` header). Until B1 is demonstrated, the report says "recorded on the base branch by an owner-identity merge" and nothing stronger (SAD-4.3).

B1 is demonstrated only when an owner-only signing step on a channel agents do not control produces a signature that a trusted verifier checks against the exact subject, and forged, replayed, expired and revoked cases each fail for the right reason (see the B1 criteria in `specs/engineering-stage-enforcement/design.md`, Amendment R1). Nothing in this spec shows that.

## Failure behavior

| Failure | Result |
| --- | --- |
| Delegation file missing, unparseable or missing a field | Fail, `DELEGATION_UNREADABLE` |
| Check did not run or returned nothing | Verdict is not PASS (SAD-3.3) |
| `roles.yml` unreadable | Existing GATE-3.4 behavior, fail |
| Record and PR disagree on any field | Fail with the named reason |
| Delegation and spec change in one PR | Fail, `DELEGATION_IN_SAME_PR` |

## Rollout and rollback

1. Ky reviews and merges this spec.
2. Ky requests the protected change as a separate, exact task. A coder and a distinct reviewer implement it test-first (T2, T3). The change lands on a branch and a PR, passes `ai-governance / verdict` on the exact head SHA, and Ky merges it.
3. The new check applies to every repo that uses the shared workflow only after Ky bumps the pinned SHA there (SAD-5.6). Repos on an older pin keep today's behavior.
4. Rollback is Ky's revert of the merge. Because the role map and delegation file are read from `main`, a revert of the data takes effect on the next run, and a revert of the workflow returns to the old pin's behavior.

Existing behavior stays intact because the new check runs only for identities that are not the owner or standing (SAD-1.2, SAD-5.1).

## Alternatives considered

| Option | Result |
| --- | --- |
| Do nothing and rely on Ky's review | Works today for a single trusted identity. It leaves "recognized" and "delegated" as the same thing, which is the gap the owner named |
| Require a delegation for every identity including Kiro | Strongest, and it changes the flow that works today. Left as an owner decision (SAD-5.2) |
| Check a signed token from the AIV vault broker | Strong in principle. The broker is for agent credentials during a task, and an owner-signed delegation channel (B1) is not demonstrated. Not available as the delegation source today |
| Pattern or wildcard identities | Rejected. Git author fields are self-declared (SAD-5.5) |

## Dependencies on other work

- ESE Amendment R1 (ESE-15.6, ESE-17) defines the policy intent this spec implements.
- The continuity spec Revision R1 (CONT-05-R1, CONT-13) defines enrollment of candidates. SAD does not choose candidates.
- The AIV spec supplies agent identity records. SAD does not change them.
- B1 is a prerequisite for any claim stronger than SAD-4.3.
