# Tasks: OpenMRS O3-6113 merge with upstream activeVisit rename

Spec ID: OAV · Issue: #217

Each task is one bounded unit. An agent other than the one that produced commit `961389cf`
reviews it. No task edits files under `specs/`. Stop at any HOLD, UNKNOWN that blocks a
criterion, or failed check, and report the exact command and output.

- [ ] 1. Recheck the base (OAV-6.1). Run `git ls-remote https://github.com/openmrs/openmrs-esm-patient-chart refs/heads/main` and confirm the fork branch is still `bf7dccd7`. If `main` has moved past `0039b3f1` or the fork branch changed, stop: the merge must be redone against the new base and this task list rerun.
- [ ] 2. Review `961389cf` against the requirements (OAV-1.1, OAV-1.2, OAV-1.3, OAV-2.1, OAV-3.1). Read the merged `patient-chart.resources.ts`. Record, per criterion, the line that satisfies it or the gap. Confirm with `grep` that no `isValidatingVisitContext`, `setVisitContext`, or store field `visitContext` remains in the app's source or tests.
- [ ] 3. Run the requirement tests (OAV-3.1 to OAV-3.5, OAV-5.1, OAV-5.2). In `packages/esm-patient-chart-app`, run `npx vitest run src/patient-chart/patient-chart.resources.test.ts src/patient-chart/patient-chart.component.test.tsx`. Compare the count of `expect(` calls and test names in both files against `bf7dccd7`; neither may drop, and no `.skip`, `.only`, or `.todo` may be added.
- [ ] 4. Run the regression suite (OAV-4.1). From the repo root, run `yarn verify` (turbo lint, typescript, and test across packages). For any failure, rerun the same command on a clean checkout of `origin/main` and record whether it fails there too.
- [ ] 5. Check the PR diff scope (OAV-6.1). Run `git diff --stat origin/main 961389cf`. It may list only the five O3-6113 files and `useDeleteVisit.tsx`.
- [ ] 6. Record evidence (OAV-6.2). Fill the traceability table below with each command, its exit code, the SHA, and the date. Label every result "local".
- [ ] 7. HOLD 1 and HOLD 2 (OAV-6.3). Ky validates this spec and authorizes the push. Do not push before both.
- [ ] 8. Push, only after task 7 (OAV-6.3). Run `git push fork fix/O3-6113-unavailable-patient` without `--force` and with hooks enabled. Then check that `gh pr view 3798 -R openmrs/openmrs-esm-patient-chart --json mergeable` no longer reports `CONFLICTING`.
- [ ] 9. HOLD 3 (OAV-6.3). Ky decides whether to post the drafted reply on PR #3798, and posts it.

Rollback before task 8: do not push; to discard the candidate, reset the local branch to `bf7dccd7` (the reflog keeps `961389cf`). Rollback after task 8: push a revert commit on the fork branch, not a force-push, and tell the maintainer on the PR.

## Traceability

| Criterion | Test or check | Candidate result (local, `961389cf`, 2026-11-10) |
|---|---|---|
| OAV-1.1 | Task 2 read; resources tests "launches the latest visit context after a previous launch resolves", "records the visit the workspace group was relaunched with" | Pass (vitest) |
| OAV-1.2 | Task 2 read; resources-test `groupPropsFor` assertions use `activeVisit` | Pass (vitest) |
| OAV-1.3 | Task 2 grep; `tsc --noEmit -p .` | `tsc` exit 0; grep not yet recorded by a reviewer |
| OAV-2.1 | Task 2 read of the returned state | Not covered by a test; reviewer read required |
| OAV-3.1 | "preserves the patient-load error for an unavailable patient"; "does not launch or store a retained patient when the patient request has errored" | Pass |
| OAV-3.2 | "preserves missing patient data when loading completes without an error" | Pass |
| OAV-3.3 | "clears a cached patient and suppresses visit launches until the patient request recovers"; component "removes the chart when a cached patient becomes unavailable" | Pass |
| OAV-3.4 | "does not launch a queued visit or publish its context after a pending launch resolves while unavailable" | Pass |
| OAV-3.5 | "does not launch the active-visit group until the store patient identity is restored on recovery"; "reconciles the recovered visit after an invalidated launch may have changed the framework group" | Pass |
| OAV-4.1 | Whole-app vitest; task 4 `yarn verify` | App: 268 passed, 1 skipped (also skipped on `main`). `yarn verify`: not run |
| OAV-5.1 | Task 3 | Pass (vitest); 9 renamed lines across two files |
| OAV-5.2 | Task 3 counts | `expect(` count in resources test: 63 before and after; no skips added |
| OAV-6.1 | Task 5 | 6 files, +629/-18 |
| OAV-6.2 | Task 6 | Pending |
| OAV-6.3 | Tasks 7 to 9 | Not pushed; no comment posted |
