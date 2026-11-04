# Requirements: ARFBench eval wrapper

Spec ID: ARF · Issue: #250 · Status: proposed; Ky approves by merging this spec-only PR

## Introduction

Datadog's ARFBench (750 multiple-choice QA pairs from 63 production
incidents, Apache 2.0) runs through our eval harness as an inspect_ai task,
so a real vendor benchmark exercises the same scoring path as our suites.

## Requirements

### Requirement 1: Benchmark wrapper (ARF-1)

**User Story:** As Ky, I want ARFBench runnable in our harness, so that
vendor incidents score our reliability work.

#### Acceptance Criteria

1. ARF-1.1 WHEN the wrapper loads THEN it SHALL expose the ARFBench QA
   pairs as an inspect_ai task.
2. ARF-1.2 WHEN the wrapper tests run THEN scoring SHALL complete over the
   bundled dataset without fetching the network.
