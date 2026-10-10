# Design: SSRF URL Allowlist Validator Bypass Fix

Spec ID: SSRF

## Overview

This design describes, from the observed recovered source only, how the later deliverable (a parsed-URL validator plus a table-driven test suite) is intended to be built against the pinned synthetic `synthetic_fetch` package. No source is executed, repaired, or promoted in this session (baselineExecuted = false).

Baseline (current) behavior — OBSERVED:
- `validator.py`: `is_allowed_url(url, allowed_origins)` returns `any(url.startswith(origin) for origin in allowed_origins)` — a string-PREFIX match (the vulnerable core).
- `build_request_plan` raises `UrlNotAllowedError` if not allowed, else returns `RequestPlan(method="GET", url=url)`. No network I/O (explicit).
- `fixtures/allowlist.json` `allowed_origins = ["https://catalog.example.test","https://images.example.test"]`.
- Baseline `tests/test_validator.py` covers only: 3 configured destinations allowed, one unrelated rejected, allowed builds a GET plan.

Intended corrected behavior (to build LATER):
- Replace prefix matching with parsed scheme + exact host (and port) comparison, plus IP-range/literal checks to reject raw-IP and private/loopback literals; preserve `build_request_plan` for legitimate URLs.

Proposed guided normalization policy (one consistent rule — GUIDEDREFERENCE, AI proposal for Ky's PR review): scheme and host compared case-insensitively (ASCII-lowercased); host must equal a normalized allowlisted hostname exactly (no added subdomain, no suffix extension, no userinfo); port compared after filling the scheme default port (443 for `https`) so explicit `:443` equals an omitted port; any non-default port rejected unless explicitly allowlisted. This avoids a contradictory "reject case-only yet also normalize" rule.

Bypass classes to enumerate (synthetic `.example.test` only): suffix-extension host, userinfo/credential, added subdomain prefix, scheme/case/port variations, non-host prefixes, and raw-IP / private-loopback literals.

Exact boundary of the change: rewrite the allow decision in `validator.py` and add a table-driven test suite; all synthetic hosts remain `.example.test`; no network I/O, DNS, or sockets; no change to the GET-plan contract for legitimate URLs.

## Architecture

The recovered source is an editable Python package `synthetic_fetch` (Python + pytest 8.3.5 / setuptools 75.8.0). The change is confined to the validator module plus added tests; no new modules, controllers, or ledgers.

- `src/synthetic_fetch/validator.py` (CHANGE BOUNDARY) — holds `is_allowed_url` (the vulnerable prefix matcher being replaced) and `build_request_plan` (preserved for legitimate URLs). The parsed scheme/host/port decision and IP-range/literal checks replace the prefix logic here.
- `src/synthetic_fetch/__init__.py` (PRESERVED) — package surface.
- `fixtures/allowlist.json` (PRESERVED, read-only) — the two allowlisted origins the decision is evaluated against.
- `tests/test_validator.py` (EXTENDED LATER) — baseline allow/reject/GET-plan coverage.
- `tests/conftest.py` (PRESERVED/EXTENDED) — pytest fixtures.
- `pyproject.toml`, `README.md`, `.gitignore` (PRESERVED; README notes extended with out-of-scope limits).

Baseline vs intended vs boundary: baseline decides allow via `url.startswith(origin)`, which accepts suffix-extension and userinfo bypasses; intended decides via parsed scheme + exact normalized host (+ port) and IP-range/literal rejection. The exact boundary is the allow decision inside `validator.py` plus a new table-driven suite; the `RequestPlan` GET contract for legitimate URLs is untouched; the exercise is OFFLINE (no network/DNS/sockets).

## Components and Interfaces

Interfaces described in prose from the observed source; no source code copied.

- `is_allowed_url(url, allowed_origins)` — currently returns `any(url.startswith(origin) ...)`. Intended: parse the URL (urllib.parse), compare scheme and exact host (and port, after default-port filling) against the normalized allowlist, and apply IP-range/literal checks; returns allowed/not-allowed with no prefix matching.
- `build_request_plan(url, ...)` — raises `UrlNotAllowedError` when not allowed; otherwise returns `RequestPlan(method="GET", url=url)`. Preserved unchanged for legitimate URLs; performs no network I/O.
- `UrlNotAllowedError` — the error raised for a rejected URL.
- Allowlist source — `fixtures/allowlist.json` providing `allowed_origins` (two `https://*.example.test` origins).
- Table-driven test interface — one row per bypass class and one row per legitimate URL, asserting rejected/allowed outcomes.

## Data Models

Shapes described in prose; fixture contents are not reproduced.

- Allowlist: `allowed_origins` is a JSON array of origin strings (`https://catalog.example.test`, `https://images.example.test`).
- `RequestPlan`: fields `method` (fixed `"GET"`) and `url` (the allowed URL).
- Normalized comparison key (intended): scheme (ASCII-lowercased) + host (ASCII-lowercased) + effective port (explicit port, or the scheme default 443 for `https`).
- Test table row (intended): a case label/class, an input URL, and the expected allow/reject outcome, grouped into bypass rows (suffix-extension, userinfo, added-subdomain, scheme/case/port, non-host prefix, raw-IP/private-loopback) and legitimate rows.

## Correctness Properties

### Property 1: Parsed host decision, no prefix
**Validates: Requirements 1.1, 1.2** (alias SSRF-1)
The allow decision uses parsed scheme + exact normalized host (+ port), never prefix matching. — observable check: table rows show prefix-only matches fail (RUN LATER).

### Property 2: Suffix-extension and userinfo bypasses rejected
**Validates: Requirements 2.1, 2.2, 3.1, 3.2, 3.3** (aliases SSRF-2, SSRF-3)
Hosts extending an allowlisted host, or embedding it in userinfo, are rejected on the real host; userinfo is forbidden even on otherwise allowlisted hosts. — observable check: suffix-extension and userinfo rows return not-allowed (RUN LATER).

### Property 3: Consistent normalization
**Validates: Requirements 4.1, 4.2, 4.3** (alias SSRF-4)
Case-insensitive scheme/host and default-port filling applied uniformly; added-subdomain/different-scheme/non-default-port rejected. — observable check: case-only and explicit-vs-default-port equivalents treated consistently (RUN LATER).

### Property 4: IP-range rejection
**Validates: Requirements 5.1, 5.2** (alias SSRF-5)
Raw-IP literals and private/loopback addresses are rejected by IP-range/literal checks. — observable check: raw-IP and private/loopback rows return not-allowed (RUN LATER).

### Property 5: Legitimate URLs preserved, table-driven, offline, honest
**Validates: Requirements 6.1, 6.2, 7.1, 7.2, 8.1, 8.2, 9.1, 9.2** (aliases SSRF-6, SSRF-7, SSRF-8, SSRF-9)
Exactly-matching allowlisted URLs still build a GET plan; verification is table-driven; no network/DNS/sockets; no production-SSRF overclaim. — observable check: legitimate rows pass; `python -m pytest` green; no socket/DNS calls; out-of-scope limits stated (RUN LATER).

## Error Handling

- Rejected URL: `build_request_plan` raises `UrlNotAllowedError`; the table-driven suite asserts rejection for every bypass row rather than a silent allow.
- Unparseable / malformed URL: treated as not-allowed under the parsed-host decision (no prefix fallback), consistent with the single normalization policy.
- Offline constraint: no network I/O, DNS resolution, or sockets are opened; a rejection is a pure parsing/comparison outcome, never a network error (Requirement 8.1 / SSRF-8).
- Honest scope: rejection here is local string/parse analysis only; it is not production SSRF protection, DNS-rebinding defense, or redirect-chain coverage (Requirement 9.1 / SSRF-9).

## Testing Strategy

Outputs below are **expectations to verify LATER** in **disposable copies**. Nothing was executed in this session (baselineExecuted = false); these are expectations to verify LATER, not results.

| Command (literal) | Expected RED (pre-fix) | Expected GREEN (post-fix) | Requirements |
| --- | --- | --- | --- |
| `python -m pytest -q tests/test_validator.py` | Baseline suite passes but only covers 3 allowed + 1 unrelated; no bypass coverage | Still passes | 6.1, 6.2 (SSRF-6) |
| `python -m pytest -q` (new table-driven bypass suite) | Fails/absent: prefix match accepts suffix-extension/userinfo/etc.; no bypass tests exist yet | All bypass rows rejected, all legitimate rows allowed; suite green | 1.1–7.2 (SSRF-1..SSRF-7) |
| manual: `is_allowed_url("https://catalog.example.test.attacker.example.test/x", origins)` | Returns True (bypass) under prefix match | Returns False under parsed-host match | 1.1, 2.1 (SSRF-1, SSRF-2) |
| manual: `is_allowed_url("https://catalog.example.test@evil.example.test/x", origins)` | Returns True (bypass) under prefix match | Returns False (real host evil.example.test) | 3.1 (SSRF-3) |

HOLD: All coding and source promotion are **HELD** until the canonical spec PR is merged by **@KyPython** into `ai-governance/main` with green required checks. Authorship provenance is author session `sess_6ccf95b7-8bbe-4225-8682-6f74410eb9cd` (historical); the original final-review session `sess_ef9c3844-0570-409c-baa6-7cc73d898476` is retained as historical provenance only. Internal admission follows the ACTUAL latest committed-head Kiro PASS capture/receipt referenced by the canonical PR provenance markers — not an exclusive `sess_ef9c3844...` receipt — and the current correction-review execution is session `sess_ef2ac960-554a-4517-8662-aa42a8afd1e9`. No PR number, PASS, result, or human-mastery claim is asserted here. The exact bypass list and host/IP/normalization rules are AI-proposed GUIDEDREFERENCE for Ky's PR review, not decisions already made.

Reuse-first note: Reuse existing registration/Python profiles, the reviewed generatedFiles recipe, and existing registry/publisher/learning-map/paired-GHA-artifact/Morning owners and the existing Notion row. Do not create new controllers, world queues, or ledgers.
