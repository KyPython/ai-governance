# Requirements: governed repo bootstrapper

Spec ID: KYNEW · Issue: #247 · Status: proposed; Ky approves by merging this spec-only PR

## Introduction

`scripts/ky-new-repo` creates a repository with the governance bundle and
protection from day one. This spec pins its offline contract: argument
validation, shared-checkout refusal, and a dry-run plan that executes
nothing. Live creation (gh repo create, clone, protect) is exercised by use,
not by automated tests.

## Requirements

### Requirement 1: Argument validation (KYNEW-1)

**User Story:** As Ky, I want bad invocations rejected before anything runs,
so that a typo never creates a stray repo.

#### Acceptance Criteria

1. KYNEW-1.1 WHEN the repo name is missing, invalid, or given twice THEN the
   script SHALL exit 2 with an error.
2. KYNEW-1.2 WHEN --ci names anything but node, python, or none THEN the
   script SHALL exit 2 with an error.
3. KYNEW-1.3 WHEN run inside the shared checkout THEN the script SHALL refuse
   with an error and SHALL exit 2.
4. KYNEW-1.4 WHEN passed an unknown flag THEN the script SHALL exit 2 with an
   error.

### Requirement 2: Offline dry run (KYNEW-2)

**User Story:** As Ky, I want a fully offline plan preview, so that the
bootstrap is reviewable before anything executes.

#### Acceptance Criteria

1. KYNEW-2.1 WHEN --dry-run is passed THEN the script SHALL print the full
   plan, SHALL execute nothing, and SHALL exit 0.
2. KYNEW-2.2 WHEN --dry-run targets an org THEN the plan SHALL include
   ruleset verification; WHEN it targets a user THEN the plan SHALL include
   the protect step.
