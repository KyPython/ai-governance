# Requirements Document

Spec: Post-Incident Review from Synthetic Service Logs (ITIL) · Spec ID: PIR · Status: proposed (spec-only); @KyPython approves by merging this spec-only PR.

## Goal

As an IT service management analyst, analyze synthetic application and load-balancer logs from a service outage to build an evidence-backed incident timeline, distinguish the trigger from the underlying root cause, and write a post-incident review with impact, timeline, contributing factors, and corrective actions, verified by re-checking every timeline entry and impact figure against the logs with a script.

Task Factory row: https://app.notion.com/p/3f08621e0a7a817bb25efaa3bfc84919

Goal SHA256: 3399c3c85692abf3d9342646a03e76f63b71901a4a94052e2b9c43678016120f
Note: the value above is the SHA256 of UTF-8(verbatim Goal + one trailing LF).

## Introduction

This spec governs user-authorized guided INTERNAL Bootcamp, fully-disclosed AI-assisted advance preparation for the task above. It is **NOT** paid Odin approval and **NOT** a claim of unaided human ability. No source is executed, repaired, promoted, merged, or deployed by this spec. The later deliverable is a claim-verification script plus a completed post-incident review (PIR) built against the pinned synthetic fixtures.

### Source identity and admission

Recovery identity (VERIFIED CURRENT OBSERVATION):
- cloudRecoveryTaskId: `task_e_6ac6d27c3a808322a45b771b98bc97a7`
- diffSha256: `0034e1c015bd9b614efa30828346d3751f3a3a11b3436a4c67dbd7831f243f56`
- extractedRoot: `<private recovery cache>/extracted/task_e_6ac6d27c3a808322a45b771b98bc97a7`
- starterSubdirectory: `bootcamp/incident-review`
- starterFileCount: 7
- dependencyShape: Python standard library
- baselineExecuted: **false**
- sourcePromoted: **false**

The parent session confirmed the Goal SHA256 matches UTF-8(verbatim Goal + one LF), that the extractedRoot and starterSubdirectory exist, and that a sample of file-byte digests matched the inventory below (authentic, unaltered, unworked recovered source). This spec binds that recovery digest and the inventory below.

sourceFileDigests inventory (reference only — paths + mode + sha256, NOT contents):

| path | mode | sha256 |
| --- | --- | --- |
| bootcamp/incident-review/README.md | 100644 | ce4830f8c8d89c29083326cafa84d82747318bd1ba9c53b242434849791a89cb |
| bootcamp/incident-review/fixtures/application.log | 100644 | fec6150a0456e668348d37a6c5b0ea37f07d39010a9406f20d54cad0a1bfe82e |
| bootcamp/incident-review/fixtures/lb-access.log | 100644 | 39186677535f03dff32f828dabb5023c82add23655958cd45166d529e14f2059 |
| bootcamp/incident-review/fixtures/service-events.csv | 100644 | 9cc5388ad71e481f2c865eeed4a9dfba6de2b7d9dd08fe7d463df1b9ee73bb21 |
| bootcamp/incident-review/scripts/summarize_logs.py | 100644 | c9c24ae7de2663161b25f2edd989634266f0ffa08130ec28fcb4dd37b196d517 |
| bootcamp/incident-review/templates/post-incident-review.md | 100644 | ed9694f60a4e8bc48bedc27619a882333950be9f72b6ab2a39fca2971a5d1e6c |
| bootcamp/incident-review/tests/test_summarize_logs.py | 100644 | 75e87055b46c035d18ef7da41b7637c55681a3aeb814692537ebf73207a55163 |

(7 tracked file digests, all Git mode 100644, consistent with starterFileCount = 7.)

Preserved paid-state (EXACTLY as given — unchanged by this spec): Stage: Candidate · Fit Gate: HOLD · Approved Goal: (empty) · Approval ID: (empty) · Approved Pay: (empty).

The preserved Candidate/HOLD/empty paid-approval state is the Odin state and is not changed here. The actual future technical-prep gates are: real Kiro final review, a @KyPython merged-to-main spec, and the bound internal admission. Human/Recorder/paid gates are separate and remain pending. Separate FUTURE human decisions — recording, execution, capture, privacy, audio/narration, transfer — are distinct from this technical preparation.

Post-merge requirement: AFTER @KyPython merges this spec, and BEFORE any internal admission/registration or cloud promotion, the private Ky-owned unworked starter must be published and its full 40-character commit SHA plus per-file byte and mode verification against the inventory above confirmed. No starter SHA is invented here.

Native Kiro session references: Authorship provenance is author session `sess_6ccf95b7-8bbe-4225-8682-6f74410eb9cd` (historical); the original final-review session `sess_ef9c3844-0570-409c-baa6-7cc73d898476` is retained as historical provenance only. Internal admission follows the ACTUAL latest committed-head Kiro PASS capture/receipt referenced by the canonical PR provenance markers — not an exclusive `sess_ef9c3844...` receipt — and the current correction-review execution is session `sess_ef2ac960-554a-4517-8662-aa42a8afd1e9`.

## Glossary

- **PIR**: Post-Incident Review — the ITIL deliverable with executive summary, customer impact, evidence-backed timeline, trigger vs root cause, contributing factors, response assessment, corrective actions, and a claim-verification section.
- **Trigger**: the immediate event that set off the outage.
- **Root cause**: the underlying condition that allowed the trigger to cause impact (a HUMAN analytical judgment).
- **Verifier**: the later claim-verification script (NOT `summarize_logs.py`) that re-checks timeline entries and impact figures against the logs.
- **Fixtures**: the three synthetic logs (`lb-access.log` JSONL, `application.log` JSONL, `service-events.csv`).
- **RUN LATER**: an observable check to execute after merge in a disposable copy; nothing is executed in this spec.

## Requirements

### Requirement 1: Evidence source restriction (PIR-1)

**User Story:** As an ITSM analyst, I want the timeline and impact figures derived only from the synthetic fixtures, so that every claim is grounded in observable evidence.

#### Acceptance Criteria

1. PIR-1.1 WHEN the analyst builds the incident timeline and impact figures THE process SHALL use only `fixtures/lb-access.log`, `fixtures/application.log`, and `fixtures/service-events.csv`. (Source: README frames an ITIL PIR over exactly these three synthetic fixtures.)
2. PIR-1.2 THE process SHALL NOT reference any external or network data source. (Acceptance RUN LATER: the verifier reads only those fixture paths.)

### Requirement 2: Trigger separated from root cause (PIR-2)

**User Story:** As an ITSM analyst, I want the immediate trigger and underlying root cause recorded separately with uncertainty preserved, so that causation is not overstated.

#### Acceptance Criteria

1. PIR-2.1 WHERE the review discusses causation THE PIR SHALL record the immediate trigger and the underlying root cause as distinct, separately labeled items. (Source: task boundary.)
2. PIR-2.2 IF the logs do not settle causation THEN the PIR SHALL mark the unresolved point as a HOLD rather than asserting it. (Acceptance RUN LATER: the trigger-vs-root-cause section contains two distinct entries; the root cause is a HUMAN judgment, not AI-authored.)

### Requirement 3: Every timeline entry is log-citable (PIR-3)

**User Story:** As an ITSM analyst, I want each timeline entry traceable to a log record, so that the timeline is verifiable.

#### Acceptance Criteria

1. PIR-3.1 WHEN a timeline entry is added THE verifier SHALL cite the specific log record(s) backing that entry's timestamp and content. (Source: Goal.)
2. PIR-3.2 IF a timeline entry cannot be cited to a log record THEN the verifier SHALL report it as a failure. (Acceptance RUN LATER: verifier re-derives each timestamp from a log line.)

### Requirement 4: Every impact figure is log-citable (PIR-4)

**User Story:** As an ITSM analyst, I want each impact figure recomputed from the logs, so that no figure is fabricated.

#### Acceptance Criteria

1. PIR-4.1 WHEN an impact figure (e.g., affected request count, error-window duration) is stated THE verifier SHALL recompute that figure from the fixtures. (Source: Goal.)
2. PIR-4.2 IF a recomputed figure does not match the stated figure THEN the verifier SHALL exit non-zero. (Acceptance RUN LATER.)

### Requirement 5: UTC timestamp handling (PIR-5)

**User Story:** As an ITSM analyst, I want all timestamps treated as UTC, so that ordering and durations are consistent.

#### Acceptance Criteria

1. PIR-5.1 WHILE parsing and comparing log timestamps THE process SHALL treat all timestamps as UTC. (Source: task boundary.)
2. PIR-5.2 THE process SHALL NOT apply local-timezone conversion. (Acceptance RUN LATER: timeline ordering/durations computed in UTC.)

### Requirement 6: Starter summarizer is not the verifier (PIR-6)

**User Story:** As an ITSM analyst, I want the provided summarizer kept as a neutral reporter, so that the claim-verification work is a separate, honest deliverable.

#### Acceptance Criteria

1. PIR-6.1 THE provided `scripts/summarize_logs.py` SHALL remain a neutral aggregate reporter (records count, status_counts, first/last timestamp, min/max response_ms). (Source: README states it is explicitly NOT the claim-verification script; it parses load-balancer JSONL fields timestamp/request_id/method/path/status/response_ms/upstream and raises `ValueError("missing fields")` on missing keys.)
2. PIR-6.2 THE process SHALL NOT treat `summarize_logs.py` as the claim-verification script. (Acceptance RUN LATER: the deliverable verifier is a separate script; summarizer behavior unchanged.)

### Requirement 7: Human-owned judgments; AI reference labeled (PIR-7)

**User Story:** As KyJahn, I want human judgment preserved and any AI-proposed reference clearly labeled, so that authorship is not misattributed.

#### Acceptance Criteria

1. PIR-7.1 THE review MAY include a clearly labeled AI-proposed causal/PIR/owner reference grounded in the synthetic logs. (Source: steering permits a disclosed AI-proposed reference.)
2. PIR-7.2 THE review MUST NOT present AI-generated text as the human analyst's final causal judgment, contributing-factor assessment, or corrective-action ownership. (Acceptance RUN LATER: PIR records human authorship for those fields; AI reference labeled as a proposal, not final judgment.)

### Requirement 8: No answer key in the public spec or unworked starter (PIR-8)

**User Story:** As a reviewer, I want the public spec and the UNWORKED starter free of a solution, so that the human diagnosis during preparation is genuine — while a separate private disclosed guided reference may still exist off-screen.

#### Acceptance Criteria

1. PIR-8.1 THE public spec and the pre-recording UNWORKED starter MUST NOT contain a diagnosis, answer key, final impacted window, impact total, settled root cause, corrective decision, or completed verification output. (Source: README states the starter contains none of these — they are human analyst work.)
2. PIR-8.2 THE restriction in PIR-8.1 applies ONLY to the public spec and the unworked starter; it does NOT apply to the separate private disclosed guided reference or Notion cues, which may hold AI-proposed references. Final human judgments remain distinct from any such reference. (Source: steering.)
3. PIR-8.3 WHEN recorder-visible public files and the unworked starter are reviewed THEN no answer-key content SHALL be present. (Acceptance RUN LATER: file review.)

### Requirement 9: No settled-fact / mastery claims (PIR-9)

**User Story:** As KyJahn, I want honest status language, so that nothing is overclaimed.

#### Acceptance Criteria

1. PIR-9.1 THE process MUST NOT state a root cause as settled fact, claim a passing baseline, or claim unaided human mastery from this preparation. (Source: honesty rules; baselineExecuted = false.)
2. PIR-9.2 WHERE evidence is incomplete THE artifacts SHALL state a HOLD. (Acceptance RUN LATER: language audit.)
