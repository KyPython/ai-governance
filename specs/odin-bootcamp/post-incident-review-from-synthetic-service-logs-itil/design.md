# Design: Post-Incident Review from Synthetic Service Logs (ITIL)

Spec ID: PIR

## Overview

This design describes, from the observed recovered source only, how the later deliverable (a claim-verification script plus a completed PIR) is intended to be built against the pinned synthetic fixtures. No source is executed, repaired, or promoted in this session (baselineExecuted = false).

Baseline (current) behavior — OBSERVED:
- Three synthetic fixtures: `fixtures/lb-access.log` (JSONL load-balancer records), `fixtures/application.log` (JSONL application records), `fixtures/service-events.csv`.
- `scripts/summarize_logs.py` (stdlib) parses load-balancer JSONL records with fields `timestamp`, `request_id`, `method`, `path`, `status`, `response_ms`, `upstream`; raises `ValueError("missing fields")` on missing keys; prints neutral aggregates (records count, status_counts, first/last timestamp, min/max response_ms). It is explicitly NOT the claim-verification script.
- `templates/post-incident-review.md` is a blank PIR template: executive summary, customer impact, evidence-backed timeline table, trigger vs root cause, contributing factors, response assessment, corrective-actions table, claim-verification section.
- `tests/test_summarize_logs.py` covers only parse-ok, missing-fields-raises, summary self-consistency.
- The starter contains no diagnosis, answer key, final window, impact total, root cause, corrective decision, or completed verification.

Intended corrected behavior (to build LATER):
- A separate claim-verification script that re-derives each timeline timestamp from a cited log record and recomputes each impact figure, exiting non-zero on any uncitable entry or mismatched figure, computing in UTC.
- A completed PIR authored by the human analyst, trigger and root cause separated, uncertainty preserved.

Exact boundary of the change: add a claim-verification script and complete the PIR template; do NOT modify `summarize_logs.py` behavior or the fixtures.

## Architecture

The recovered source is a stdlib-only Python project: three synthetic fixtures, a neutral summarizer, a blank PIR template, and summarizer tests. The deliverable ADDS a separate claim-verification script and completes the PIR; the summarizer and fixtures are untouched.

- `scripts/summarize_logs.py` (PRESERVED) — the neutral aggregate reporter; stays a reporter and is explicitly NOT the verifier.
- `scripts/verify_claims.py` (NEW, to build LATER) — the separate claim-verification script that re-derives each timeline timestamp from a cited log record and recomputes each impact figure, exiting non-zero on any uncitable entry or mismatched figure, computing in UTC.
- `templates/post-incident-review.md` (COMPLETED LATER) — the blank PIR template filled by the human analyst, with trigger and root cause separated and uncertainty preserved.
- `fixtures/lb-access.log`, `fixtures/application.log`, `fixtures/service-events.csv` (PRESERVED, read-only) — the only evidence sources.
- `tests/test_summarize_logs.py` (PRESERVED; new verifier tests added LATER) — summarizer coverage stays; verifier gets its own tests.

Baseline vs intended vs boundary: baseline only summarizes aggregates and has no verifier or completed PIR; intended adds a separate verifier that enforces citable timeline entries and reconciled impact figures in UTC, plus a human-authored PIR. The exact boundary is a new verifier script and a completed PIR template; `summarize_logs.py` and the fixtures are not modified.

## Components and Interfaces

Interfaces described in prose from the observed source; no source code copied.

- `scripts/summarize_logs.py` — parses load-balancer JSONL records (fields `timestamp`, `request_id`, `method`, `path`, `status`, `response_ms`, `upstream`), raises `ValueError("missing fields")` on missing keys, and prints neutral aggregates (records count, status_counts, first/last timestamp, min/max response_ms). Remains a reporter.
- `scripts/verify_claims.py` (deliverable) — reads a completed PIR plus the fixtures; for each timeline entry, cites the backing log record and re-derives its timestamp; for each impact figure, recomputes it from the fixtures; exits non-zero on any uncitable entry or mismatched figure; computes in UTC.
- PIR template sections — executive summary, customer impact, evidence-backed timeline table, trigger vs root cause, contributing factors, response assessment, corrective-actions table, claim-verification section; human-authored judgment fields.

## Data Models

Shapes described in prose; fixture/template contents are not reproduced.

- Load-balancer access record (JSONL): fields `timestamp`, `request_id`, `method`, `path`, `status`, `response_ms`, `upstream`.
- Application log record (JSONL): application event records (parsed by the verifier for citation/impact as needed).
- Service-events record (CSV): service event rows in `service-events.csv`.
- Summarizer output: aggregate fields — records count, status_counts, first/last timestamp, min/max response_ms.
- PIR document: a timeline table (entry → cited log record(s), timestamp, content), impact figures (e.g., affected request count, error-window duration), distinct trigger and root-cause fields, contributing factors, corrective-actions table, and a claim-verification section.

## Correctness Properties

### Property 1: Fixture-and-UTC grounding
**Validates: Requirements 1.1, 1.2, 5.1, 5.2** (aliases PIR-1, PIR-5)
All derivations read only the three pinned fixtures and compute in UTC; no external/network source and no local-timezone conversion. — observable check: the verifier references only the three fixture paths and orders/compares timestamps in UTC (RUN LATER).

### Property 2: Citable timeline and impact
**Validates: Requirements 3.1, 3.2, 4.1, 4.2** (aliases PIR-3, PIR-4)
Every timeline entry maps to a cited log record and every impact figure recomputes from the fixtures; unreconciled claims fail verification. — observable check: `verify_claims.py` exits non-zero on any uncitable entry or mismatched figure (RUN LATER).

### Property 3: Trigger ≠ root cause with uncertainty
**Validates: Requirements 2.1, 2.2** (alias PIR-2)
Trigger and root cause are distinct fields; unresolved causation is a labeled HOLD, not an assertion. — observable check: the PIR trigger-vs-root-cause section holds two distinct entries and marks unresolved points HOLD (RUN LATER).

### Property 4: Summarizer stays neutral
**Validates: Requirements 6.1, 6.2** (alias PIR-6)
`summarize_logs.py` remains an aggregate reporter and is not the verifier. — observable check: deliverable verifier is a separate script; summarizer output unchanged (RUN LATER).

### Property 5: Human authorship, bounded no-answer-key, honest status
**Validates: Requirements 7.1, 7.2, 8.1, 8.2, 8.3, 9.1, 9.2** (aliases PIR-7, PIR-8, PIR-9)
Human judgment fields are human-authored; any AI reference is labeled. The public spec and the UNWORKED starter contain no answer key; the separate private disclosed guided reference / Notion cues may contain an AI-proposed reference, and final human judgment remains distinct from any such reference. Evidence gaps are HOLDs. — observable check: file/language review confirms the public spec and unworked starter carry no answer key, human-judgment fields are human-authored, and any AI-proposed reference is labeled (RUN LATER).

## Error Handling

- Missing fields: `summarize_logs.py` raises `ValueError("missing fields")` on a record missing required keys; this behavior is preserved unchanged.
- Uncitable timeline entry: the verifier reports a failure (non-zero exit) when a timeline entry cannot be cited to a log record (Requirement 3.2 / PIR-3).
- Mismatched impact figure: the verifier exits non-zero when a recomputed figure does not match the stated figure (Requirement 4.2 / PIR-4).
- Unresolved causation: the PIR marks the unresolved point as a HOLD rather than asserting a root cause (Requirement 2.2 / PIR-2).
- Honest status: no root cause is stated as settled fact, no passing baseline is claimed, and no unaided mastery is claimed; evidence gaps are HOLDs (Requirement 9.1, 9.2 / PIR-9).

## Testing Strategy

Outputs below are **expectations to verify LATER** against the reviewed pinned source in **disposable copies**. Nothing was executed in this session (baselineExecuted = false); these are expectations to verify LATER, not results.

| Command (literal) | Expected RED (pre-work) | Expected GREEN (post-work) | Requirements |
| --- | --- | --- | --- |
| `python -m unittest discover -s tests -v` | Starter summarizer tests pass; proves parsing only, not any PIR claim | Still pass; summarizer unchanged | 6.1, 6.2 (PIR-6) |
| `python scripts/summarize_logs.py fixtures/lb-access.log` | Prints neutral aggregates; no diagnosis | Unchanged aggregates | 6.1 (PIR-6) |
| `python scripts/verify_claims.py <completed-PIR>` (deliverable, not yet present) | Fails/absent: no verifier and no completed PIR exist yet | Exits 0 only when every timeline entry is log-citable and every impact figure reconciles in UTC | 3.1, 4.1, 5.1 (PIR-3, PIR-4, PIR-5) |

HOLD: All coding and source promotion are **HELD** until the canonical spec PR is merged by **@KyPython** into `ai-governance/main` with green required checks. Authorship provenance is the author session `sess_6ccf95b7-8bbe-4225-8682-6f74410eb9cd`; the final combined 54-file reviewed-HEAD Kiro merge receipt comes from the ORIGINAL final-review session `sess_ef9c3844-0570-409c-baa6-7cc73d898476`, not the author session alone. No PR number, PASS, result, settled root cause, or human-mastery claim is asserted here. A clearly labeled AI-proposed causal/PIR/owner reference may be disclosed in the separate private guided reference; final judgment remains human-authored.

Reuse-first note: Reuse existing registration/Python profiles, the reviewed generatedFiles recipe, and existing registry/publisher/learning-map/paired-GHA-artifact/Morning owners and the existing Notion row. Do not create new controllers, world queues, or ledgers.
