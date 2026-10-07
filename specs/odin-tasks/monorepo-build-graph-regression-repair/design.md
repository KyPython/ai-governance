# Design — Monorepo Build-Graph Regression Repair

## Repository shape
- root workspace manifest and `turbo.json`/equivalent pipeline config;
- `apps/` or `services/` containing the affected synthetic service;
- `packages/` containing the shared workspace dependency and one small unrelated package/check;
- build/container configuration containing the intentionally stale package identity;
- neutral README with install + failure reproduction only.

## Failure design
The affected service consumes generated/built output from the shared package. The starter pipeline intentionally does not establish the correct dependency/build ordering for the service path. Separately, a build/container configuration still names a superseded package identity. Both conditions must be observable through ordinary build output and configuration inspection.

## Human boundary
KyJahn must diagnose both root causes, decide the smallest bounded corrections, implement them during TaskRecorder, verify the service with transitive workspace dependencies, and write the concise verification note. No starter file may provide the final corrected config.

## Pre-recording verification
Reviewer confirms installability, deterministic failing build, presence of both starter defects, and absence of the final repairs.
