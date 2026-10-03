# Requirements: <feature title>

Spec ID: <PREFIX> · Issue: #<n> · Status: draft | approved by Ky on <date>
Author: <Kiro session / human>. Coders implement these sentences; they do not edit them to fit the code.

## Introduction

<Problem, who it is for, and what is out of scope.>

## Requirements

### Requirement 1: <name> (<PREFIX>-1)

**User Story:** As a <role>, I want <capability>, so that <benefit>.

#### Acceptance Criteria

1. <PREFIX>-1.1 WHEN <trigger> THEN the system SHALL <observable response>.
2. <PREFIX>-1.2 IF <unwanted condition> THEN the system SHALL <safe response>.
3. <PREFIX>-1.3 WHILE <state> the system SHALL <behavior>.

<!-- EARS patterns: ubiquitous ("The system SHALL ..."), event-driven (WHEN/THEN), unwanted (IF/THEN),
     state-driven (WHILE), optional feature (WHERE). Each criterion gets a stable ID <PREFIX>-<n>.<m>.
     Tests cite the IDs they verify in the test name or a comment, e.g. it("<PREFIX>-1.1 ...") or # <PREFIX>-1.1 -->
