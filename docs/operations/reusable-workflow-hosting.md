# Reusable workflow hosting: stay vs migrate

Status: scoped, awaiting Ky's decision. No code changes in this doc.

## The wrinkle

The reusable `accessibility.reusable.yml` and `diff-hygiene.reusable.yml`
workflows are GitHub-specific shared CI, but they live in
`KyLamportLogic/buildlogic-governance` (the public runtime toolkit) instead of
`KyPython/ai-governance` (the CI enforcement repo). The split happened because
the toolkit repo predates the gate repo (Aug 28 vs Oct 3, 2026) and the
reusable workflows were built alongside the toolkit's own a11y spec (#13).

## Current consumers (pinned to `6aa4b7d`)

| Consumer file | Branch / PR |
| --- | --- |
| `KyPython/visit-taniti` `.github/workflows/accessibility.yml` | `ci/accessibility-level-a` (PR #2) |
| `KyLamportLogic/ky-cloud-control-plane` `.github/workflows/accessibility.yml` | `ci/accessibility-level-a` (PR #2) |
| `KyLamportLogic/aws-career-sandbox` `.github/workflows/accessibility.yml` | main |
| `KyLamportLogic/human-rebuild-bootcamp` `.github/workflows/accessibility.yml` | main |

## Option A: stay (recommended default)

Keep the reusable workflows in buildlogic-governance. Cost: shared workflows
live in two repos; the toolkit repo carries GitHub-only files. Benefit: zero
migration, pins keep working, PR #13's spec history stays with the code.

## Option B: migrate to ai-governance

Move both reusable workflows (plus their spec history reference) into
`KyPython/ai-governance/.github/workflows/`, then re-pin all four consumers
to the new SHA in one wave:

1. Copy workflows to ai-governance via a PR; merge; record the merge SHA.
2. Update the 4 consumer callers (`uses:` + `governance-ref`) to the new
   repo + SHA, one PR per repo (2 are already open PR branches; 2 need new
   branches off main).
3. Keep the old files in buildlogic-governance with a deprecation notice
   until no caller references them (verify with a fleet-wide grep), then
   remove.
4. Update this doc and both READMEs to record the final home.

Benefit: every shared workflow lives in one repo. Cost: a 5-PR migration
wave plus a deprecation tail; org-side PRs wait on the billing fix.

## Decision

Ky picks A or B. If B, the migration itself follows the normal workflow:
spec-only PR first if behavior changes (a pure move needs no spec), then
code PRs per repo. Only Ky merges.
