# Design: OpenMRS O3-6113 merge with upstream activeVisit rename

Spec ID: OAV · Issue: #217

## Sources and pins

Current pins (re-pinned 2026-11-11): base `326be2f9`, candidate `6a3a033f`, PR head `bf7dccd7`. The
lines below record the original 2026-11-10 pins and evidence for `961389cf`; that evidence must be
rerun for `6a3a033f` before HOLD 2.

- Upstream repository: `openmrs/openmrs-esm-patient-chart`, `main` at `0039b3f1` (checked with `git ls-remote` on 2026-11-10).
- PR head: `bf7dccd7` on `KyPython/openmrs-esm-patient-chart` `fix/O3-6113-unavailable-patient`.
- Breaking upstream change: `c329ff88`, O3-6032 / PR #3781, 2026-11-06.
- Framework pin in `yarn.lock`: `@openmrs/esm-framework@npm:11.0.1-pre.5951`.
- Contracts on `main`: `PatientChartStore` in `packages/esm-patient-common-lib/src/store/patient-chart-store.ts` (fields `patientUuid`, `patient`, `activeVisit`; setters `setPatient`, `setActiveVisit`); `PatientWorkspaceGroupProps` in `packages/esm-patient-common-lib/src/workspaces.ts` (field `activeVisit`). `PatientWorkspaceWindowProps` keeps a separate `visitContext` window prop.

## Verified current state (2026-11-10)

- `git merge-tree` of `origin/main` with `bf7dccd7` reports one conflicted file, `packages/esm-patient-chart-app/src/patient-chart/patient-chart.resources.ts`, with three hunks: the workspace-group initialization guard, the returned state object, and its `useMemo` dependency array.
- `patient-chart.resources.test.ts` merges without a textual conflict. After the merge, 5 of its PR-only tests fail with `ReferenceError: setVisitContext is not defined` or expect `visitContext` in launch props.
- `patient-chart.component.test.tsx` exists only on the PR branch (added by `747a11aa`). Vitest passes it, but `tsc --noEmit` reports TS2353 at line 89 because its store mock sets `visitContext`, which no longer exists on `PatientChartStore`.
- Commit `747a11aa` states the PR stops "coercing a missing patient to {}". The PR tests assert `patient` is `undefined` for an errored request and `null` for settled missing data.

## Resolution decisions

| Hunk or surface | Chosen | Alternative rejected | Reason | Requirement |
|---|---|---|---|---|
| Group-launch guard | Keep the PR's early return (`isPatientUnavailable \|\| !patient \|\| storePatientUuid !== patient.id`, which clears latest group props); use upstream's `isValidatingStoredVisit` in the following condition | Take upstream's condition alone | Upstream's version drops the unavailable-patient guard | OAV-1.1, OAV-3.3 |
| Returned `patient` | Uncoerced `patient` | Upstream's `patient ?? {}` | `747a11aa` removed the coercion on purpose and the PR tests assert null/undefined | OAV-3.1, OAV-3.2 |
| Returned visit key | Key `visitContext`, value `storedActiveVisit` | Rename the key to `activeVisit` | Upstream keeps `visitContext` because extensions in other apps read the slot state | OAV-2.1 |
| Returned `error` | Keep | Drop (upstream has none) | The component branches on it to render the unavailable state | OAV-3.1 |
| Dependency array | `[patient, patientUuid, storedActiveVisit, isLoadingPatient, error, setPatient]` | Either side alone | Must list every value the memo reads after the rename | OAV-1.1, OAV-3.1 |
| PR-only tests | Rename `setVisitContext` to `setActiveVisit` and the store-mock and launch-prop keys to `activeVisit` | Delete or skip the failing tests | Same mechanical rename `c329ff88` applied to upstream tests; assertions stay | OAV-5.1, OAV-5.2 |
| `useDeleteVisit.tsx` import | Keep the pre-commit hook's Prettier reformat | Commit with `--no-verify` to drop it | Ky's decision 2026-11-10; the hook would reapply it on any normal commit | OAV-6.1 |

## State and lifecycle

The merge does not change the PR's state machine; it renames the identifiers the state machine
reads. The hook's states stay: loading, available, unavailable (error, or settled with no
patient), and recovering. Transitions into unavailable clear the latest group props and block
launches. A launch that resolves while the patient is still unavailable cannot launch a queued
visit or publish a visit uuid. If the patient recovers before that launch resolves, recovery
waits for the store's `patientUuid` to match the patient before launching, then reconciles the
framework group.

## Evidence boundaries

Local checks on the candidate commit `961389cf`, run in `packages/esm-patient-chart-app`:
- `vitest run` on the two PR test files: 23 passed.
- `vitest run` on the whole app: 37 files, 268 passed, 1 skipped. The skipped test, `visit-form.test.tsx:439`, is also `it.skip` on `main`.
- `tsc --noEmit -p .`: exit 0. `eslint --max-warnings=0` and `prettier --check` on the three changed files: exit 0.
- `git diff --stat origin/main 961389cf`: 6 files, +629/-18 (the 5 O3-6113 files plus `useDeleteVisit.tsx`).

These are local author-run checks. They are not maintainer CI. The PR's upstream workflows need
maintainer approval to run.

## Unknowns

- Repo-wide `yarn verify` was not run by the author. An independent review run on 2026-11-10 exited 0 (70 of 70 tasks, 0 cached).
- Playwright e2e has not been run.
- Whether maintainers object to the `useDeleteVisit.tsx` import reformat is unknown.
- Whether upstream `main` moves again before a push is unknown; the review task rechecks it.

## Human gates

- HOLD 1: Ky validates and merges this spec-only PR. An agent review or a green check is not that validation.
- HOLD 2: Ky separately authorizes the push of the reviewed commit to the fork branch.
- HOLD 3: Ky decides whether to post the drafted reply to Bodeayman, and posts it.
