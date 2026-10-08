# Requirements Document

Spec: SSRF URL Allowlist Validator Bypass Fix · Spec ID: SSRF · Status: proposed (spec-only); @KyPython approves by merging this spec-only PR.

## Goal

As an application security-minded software engineer, review a synthetic Python URL validator that uses string-prefix matching to restrict outbound fetches, demonstrate the bypasses it allows, replace it with parsed-URL host and IP-range checks, and verify with a table-driven test suite that every listed bypass is rejected while legitimate allowlisted URLs still pass.

Task Factory row: https://app.notion.com/p/3f08621e0a7a81f5b437e25bc0e45e8d

Goal SHA256: ea6c029ccf9c7646bc09b930b74cfa70e9e768b16e3df60c8ada0f253a9d2cd1
Note: the value above is the SHA256 of UTF-8(verbatim Goal + one trailing LF).

## Introduction

This spec governs user-authorized guided INTERNAL Bootcamp, fully-disclosed AI-assisted advance preparation for the task above. It is **NOT** paid Odin approval and **NOT** a claim of unaided human ability. No source is executed, repaired, promoted, merged, or deployed by this spec. The later deliverable is a parsed-URL validator plus a table-driven test suite for the synthetic `synthetic_fetch` package. This is an OFFLINE request-plan exercise: no network I/O, DNS resolution, or live sockets.

### Source identity and admission

Recovery identity (VERIFIED CURRENT OBSERVATION):
- cloudRecoveryTaskId: `task_e_6ac6cf5247a883229257638c900f0d8c`
- diffSha256: `df0f9fbb91b7426040956b99212b85c0b4784d0ba56d003b6de63f086871af47`
- extractedRoot: `/Users/ky/Library/Caches/TaskWorkWorldRecovery/extracted/task_e_6ac6cf5247a883229257638c900f0d8c`
- starterSubdirectory: `specs/odin-tasks/ssrf-url-allowlist-validator/starter`
- starterFileCount: 8
- dependencyShape: Python + pytest 8.3.5 / setuptools 75.8.0
- baselineExecuted: **false**
- sourcePromoted: **false**

The parent session confirmed the Goal SHA256 matches UTF-8(verbatim Goal + one LF), that the extractedRoot and starterSubdirectory exist, and that a sample of file-byte digests matched the inventory below (authentic, unaltered, unworked recovered source). This spec binds that recovery digest and the inventory below.

sourceFileDigests inventory (reference only — paths + mode + sha256, NOT contents):

| path | mode | sha256 |
| --- | --- | --- |
| specs/odin-tasks/ssrf-url-allowlist-validator/starter/.gitignore | 100644 | 2a3c9aea88b4fca6caf1aa452ebbc04daeb288ff4ab6a8d212f56e12f95cc607 |
| specs/odin-tasks/ssrf-url-allowlist-validator/starter/README.md | 100644 | abadb61396ef00ed3f9769a01ac5681df874947b51b96e5fe7beacd2086c27fc |
| specs/odin-tasks/ssrf-url-allowlist-validator/starter/fixtures/allowlist.json | 100644 | 0cd5c74f306fd84b1ce9b78ee0790d72afedd242f667a2fc2d867e469d10378a |
| specs/odin-tasks/ssrf-url-allowlist-validator/starter/pyproject.toml | 100644 | 7f665a64469059a8c3a6d2f0ae0edc6fdfb050ebfc43541daf784819146bade9 |
| specs/odin-tasks/ssrf-url-allowlist-validator/starter/src/synthetic_fetch/__init__.py | 100644 | ed9917a925c3fb99b7e21df843970def6f30464fa4e1d823497a65ad1d8a9319 |
| specs/odin-tasks/ssrf-url-allowlist-validator/starter/src/synthetic_fetch/validator.py | 100644 | 9894275eed352a87eb72891a12a34a599575070f804aff94e57b831e95a1d112 |
| specs/odin-tasks/ssrf-url-allowlist-validator/starter/tests/conftest.py | 100644 | cf0ddb28625918326658ee3a6b45aa32a6b43c05c3e74639b70a5d23de40da9a |
| specs/odin-tasks/ssrf-url-allowlist-validator/starter/tests/test_validator.py | 100644 | 9912a37252636a5315fb7303c2fe268fc71598c0d180726947cb4ac6318953f7 |

(8 tracked file digests, all Git mode 100644, consistent with starterFileCount = 8.)

Preserved paid-state (EXACTLY as given — unchanged by this spec): Stage: Candidate · Fit Gate: HOLD · Approved Goal: (empty) · Approval ID: (empty) · Approved Pay: (empty).

The preserved Candidate/HOLD/empty state is the Odin state and is not changed here. The actual future technical-prep gates are: real Kiro final review, a @KyPython merged-to-main spec, and the bound internal admission. Human/Recorder/paid gates are separate and remain pending. Separate FUTURE human decisions — recording, execution, capture, privacy, audio/narration, transfer — are distinct from this technical preparation.

Post-merge requirement: AFTER @KyPython merges this spec, and BEFORE any internal admission/registration or cloud promotion, the private Ky-owned unworked starter must be published and its full 40-character commit SHA plus per-file byte and mode verification against the inventory above confirmed. No starter SHA is invented here.

Native Kiro session references: authorship provenance is the author session `sess_6ccf95b7-8bbe-4225-8682-6f74410eb9cd`; the final combined 54-file reviewed-HEAD Kiro merge receipt comes from the ORIGINAL final-review session `sess_ef9c3844-0570-409c-baa6-7cc73d898476`, not the author session alone.

## Glossary

- **synthetic_fetch**: the synthetic Python package under audit.
- **is_allowed_url(url, allowed_origins)**: the current allow decision; returns `any(url.startswith(origin) ...)` — a vulnerable string-PREFIX match.
- **build_request_plan**: raises `UrlNotAllowedError` if not allowed, else returns `RequestPlan(method="GET", url=url)`; no network I/O.
- **Allowlist**: `fixtures/allowlist.json` `allowed_origins = ["https://catalog.example.test","https://images.example.test"]`.
- **Normalization policy**: the single proposed rule for case and default-port handling (see Requirement 4).
- **RUN LATER**: an observable check to execute after merge in a disposable copy; nothing is executed in this spec.

## Requirements

### Requirement 1: Parsed-URL host comparison replaces prefix match (SSRF-1)

**User Story:** As a security engineer, I want allow decisions based on parsed scheme and exact host, so that prefix tricks cannot bypass the allowlist.

#### Acceptance Criteria

1. SSRF-1.1 WHEN deciding whether a URL is allowed THE validator SHALL parse the URL (urllib.parse) and compare scheme and exact host (and port where present) against the allowlist, instead of `url.startswith(origin)`. (Source: current vulnerable prefix match.)
2. SSRF-1.2 THE validator MUST NOT use string-prefix matching for the allow decision. (Acceptance RUN LATER: table-driven tests show prefix-only matches no longer pass.)

### Requirement 2: Reject suffix-extension host bypass (SSRF-2)

**User Story:** As a security engineer, I want hosts that merely extend an allowlisted host rejected.

#### Acceptance Criteria

1. SSRF-2.1 WHEN a URL host extends an allowlisted host as a prefix (e.g., `https://catalog.example.test.attacker.example.test/...`) THE validator SHALL reject it. (Source: prefix-match bypass class, synthetic `.example.test`.)
2. SSRF-2.2 WHEN the suffix-extension row runs THE validator SHALL return not-allowed. (Acceptance RUN LATER.)

### Requirement 3: Reject userinfo/credential bypass (SSRF-3)

**User Story:** As a security engineer, I want the real host used, not userinfo.

#### Acceptance Criteria

1. SSRF-3.1 WHEN a URL embeds an allowlisted string in userinfo (e.g., `https://catalog.example.test@evil.example.test/...`) THE validator SHALL reject it based on the real host (`evil.example.test`). (Source: prefix-match bypass class.)
2. SSRF-3.2 WHEN the userinfo row runs THE validator SHALL return not-allowed. (Acceptance RUN LATER.)

### Requirement 4: One consistent normalization policy for case/port/subdomain/scheme (SSRF-4)

**User Story:** As a security engineer, I want a single explicit normalization policy, so that case and default-port handling is consistent rather than contradictory.

#### Acceptance Criteria

1. SSRF-4.1 WHEN comparing a URL against the allowlist THE validator SHALL compare scheme and host case-insensitively (ASCII-lowercased). (Source: steering — one consistent policy.)
2. SSRF-4.2 WHEN comparing ports THE validator SHALL fill the scheme default port (443 for `https`) so an explicit default port equals an omitted one. (Source: steering.)
3. SSRF-4.3 IF a URL adds a subdomain, changes scheme, or uses a non-default port not in the allowlist THEN the validator SHALL reject it. (Acceptance RUN LATER: case-only and explicit-vs-default-port equivalents treated consistently; added-subdomain/different-scheme/non-default-port rows rejected.)

### Requirement 5: Reject raw-IP and private/loopback literals (SSRF-5)

**User Story:** As a security engineer, I want raw-IP and private/loopback literals rejected.

#### Acceptance Criteria

1. SSRF-5.1 WHEN a URL host is a raw IP literal or a private/loopback address THE validator SHALL reject it via IP-range/literal checks. (Source: task boundary.)
2. SSRF-5.2 WHEN raw-IP and private/loopback rows run THE validator SHALL return not-allowed. (Acceptance RUN LATER.)

### Requirement 6: Preserve legitimate allowlisted URLs (SSRF-6)

**User Story:** As a security engineer, I want exactly-matching allowlisted URLs to keep working.

#### Acceptance Criteria

1. SSRF-6.1 WHEN a URL exactly matches a configured allowlisted origin (under the normalization policy) THE validator SHALL allow it and `build_request_plan` SHALL return `RequestPlan(method="GET", url=url)`. (Source: allowlist + build_request_plan; baseline tests cover 3 allowed + 1 unrelated.)
2. SSRF-6.2 WHEN legitimate rows run THE validator SHALL allow them and build a GET plan. (Acceptance RUN LATER.) Depends on SSRF-1.

### Requirement 7: Table-driven coverage (SSRF-7)

**User Story:** As a security engineer, I want one table row per case, so that coverage is explicit.

#### Acceptance Criteria

1. SSRF-7.1 WHEN verifying the fix THE test suite SHALL be table-driven with one row per listed bypass class and one row per legitimate URL. (Source: Goal.)
2. SSRF-7.2 WHEN the suite runs THE run SHALL reject every bypass row and allow every legitimate row. (Acceptance RUN LATER: `python -m pytest`.) Depends on SSRF-1..SSRF-6.

### Requirement 8: Offline only (SSRF-8)

**User Story:** As a security engineer, I want the exercise fully offline.

#### Acceptance Criteria

1. SSRF-8.1 THE exercise MUST NOT perform network I/O, DNS resolution, or open live sockets. (Source: validator does no network I/O; task boundary.)
2. SSRF-8.2 WHEN validator/tests are inspected THEN no socket/DNS calls SHALL appear. (Acceptance RUN LATER.)

### Requirement 9: No overclaim of production SSRF protection (SSRF-9)

**User Story:** As KyJahn, I want out-of-scope limits stated honestly.

#### Acceptance Criteria

1. SSRF-9.1 THE spec and deliverable MUST NOT claim production SSRF protection, DNS-rebinding defense, or redirect-chain coverage from these local string tests. (Source: task boundary.)
2. SSRF-9.2 THE README/notes SHALL state these out-of-scope limits. (Acceptance RUN LATER.)
