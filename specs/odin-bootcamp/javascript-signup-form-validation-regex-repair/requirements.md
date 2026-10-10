# Requirements Document

> INTERNAL guided Bootcamp PREPARATION under an explicit user world-preparation exception. This is NOT externally approved Odin, paid acceptance is UNVERIFIED, and it is NOT recording-ready. Spec documents only — no implementation, no execution, no publication in this Kiro session.

## Introduction

This spec covers the JavaScript Signup Form Validation Regex Repair world. It documents, as read-only static evidence, a synthetic static signup form whose JavaScript validation rejects valid email addresses and accepts malformed phone numbers, and it defines the future repair and verification work that will happen only AFTER an actual Kiro review PASS and Ky's human merge of the new canonical 18-record spec PR to `main`.

This Kiro session executes none of the implementation. It writes documentation only.

### Record identity

Task Factory row: https://app.notion.com/p/3f08621e0a7a810cb2cdf1b3baad13ef

- Verified Goal+LF hash (SHA256 of exact UTF-8 Goal + one trailing LF): `8e3d20cc6a4e9709daf061cfd0a50c7be1f043e996801105eeac4518d96f10ab`
- Candidate (NOT approved) older no-LF hash: `435cbbe7b1508d9fbedaafb82621969bb856b324a32b11104e4f2f262ab3b329` — a recovery-map CANDIDATE only. It is NOT the approved Goal hash and MUST NOT be treated as current or approved.
- Provenance: actual author execution is local Kiro session `sess_74e2d316-c006-4a6b-883f-4809655cbd2b`.
- Current inventory FILE-BYTES SHA256 (`inventoryFileSha256`): `e2a1fb9e82bbbee7ed6bb76829247ffaa739f42de8e7f8f557a2db94c0695924` — SHA256 of the inventory file bytes.
- Current canonical semantic inventory SHA256 (`inventorySha256`): `8143891ad28dfac36b3dcc20217790c3d045659186416edc87d71e71e2519306` — SHA256 over all 18 records, sorted keys, compact JSON separators, UTF-8, `ensure_ascii=False`. Both hashes describe the SAME unchanged 18-record inventory; neither is old or superseded.

### Confirmed read-only source identity

- `extractedRoot`: `<private recovery cache>/extracted/task_e_6ac6d5f886fc8322ae0ceab6e191f68b`
- `starterSubdirectory`: `specs/odin-tasks/javascript-signup-form-validation-regex-repair/starter`
- `cloudRecoveryTaskId`: `task_e_6ac6d5f886fc8322ae0ceab6e191f68b`
- `cloudStatusAtRead`: `ready`
- `diffSha256`: `89720c3ef31690572cb134fe568704153a2b9019c7981cf0ad364626c2da0e2d`
- `starterFileCount`: 10
- `legacyRecoveryIssue`: https://github.com/KyPython/ai-governance/issues/182 — a RETIRED historical alias (closed wrong-lane duplicate; history only), NOT the current owner.

The confirmed recovered UNWORKED source MUST be reused. Do NOT invent a future repo or source commit and do NOT propose a duplicate new build. Do not copy raw source bytes into the docs.

### External human record fields (preserved as recorded facts, do not alter)

- Stage: Candidate (recorded fact; internal guided Bootcamp preparation only, not an externally approved Odin build)
- Fit Gate: HOLD (recorded fact)
- Approval ID: (empty)
- Approved Goal: (empty — never fabricate an approved Goal)
- Pay / attempt / human fields: (empty)
- Source: recovered PRIVATE cache (NOT a published GitHub starter). There is no source commit and no current Build Issue for this row. Closed wrong-lane alias issues are history, not canonical builds.

### Internal preparation gates

The explicit-user world-preparation exception PERMITS off-screen coding, testing, source publication, and registration DESPITE the recorded Candidate stage, the Fit Gate HOLD, and the blank external Approval ID / Approved Goal. Those recorded paid/HOLD properties are preserved as facts and are NOT prerequisites for internal preparation.

The actual future internal-prep gates are:
1. an actual Kiro review PASS;
2. Ky's human merge of this NEW canonical 18-record spec PR to `main`;
3. bound internal admission.

Actual Recorder/human capture and paid-acceptance gates remain PENDING. Paid acceptance is UNVERIFIED (neither eligible nor ineligible). No AI during actual capture.

### Verbatim Goal

As a front-end developer, fix a synthetic static signup form whose JavaScript validation rejects valid email addresses and accepts malformed phone numbers, correct the validation rules and their anchoring, and verify with a Node test table of valid and invalid inputs plus a manual check of the form in the browser.

## Requirements

### Evidence states

#### VERIFIED CURRENT OBSERVATION (static source review only — baseline NOT executed)
- `src/validation.js` defines `emailPattern = /^[\w.-]+@[\w.-]+\.[A-Za-z]{2,4}$/`, which caps the TLD length at 2–4 characters.
- `src/validation.js` defines an UNANCHORED `phonePattern = /\d{3}-\d{3}-\d{4}/` (no `^`/`$`), so it matches substrings inside malformed input.
- Ordinary fixture tests in `test/validation.test.js` / `fixtures/validation-cases.json` omit the decisive valid-email and malformed-phone cases.
- Contract `docs/validation-contract.md`: email requires a non-empty local part allowing letters/digits/dot/underscore/hyphen/plus, exactly one `@`, a domain, and an alphabetic TLD of >=2 letters (the contract itself defines the alphabetic TLD >=2 rule); phone is accepted as any three-digits hyphen three-digits hyphen four-digits group (format example `555-123-4567`, which is only an example and not the sole literal); input is checked AS ENTERED with NO TRIM.
- Toolchain: Node built-ins, NO npm packages. `package.json` has `type=module`, `scripts.test = node --test`, `scripts.start = node server.js`, `engines.node >= 20`. `server.js` uses `import.meta.dirname`, so the real floor is Node 20.11+. Public Node 22.22.0 satisfies it. (README's generic "20+" is too broad.)
- `dependencyShape`: Node built-ins + static server.

#### INTENDED behavior
- Email validation accepts addresses meeting the contract, including alphabetic TLDs longer than 4 characters, and `+` in the local part. The contract already defines alphabetic TLD >=2, so long-TLD acceptance is contract-defined, not a human judgment call.
- Phone validation accepts any contract-format number (three digits, hyphen, three digits, hyphen, four digits; example `555-123-4567`) only when anchored, and rejects anything with leading/trailing extra characters.
- Verification uses a Node `--test` table of valid and invalid inputs PLUS a SEPARATE manual browser check at `localhost:4173`.

#### VERIFIED failures (static only)
- STATIC DEFECT (email): the `{2,4}` TLD cap rejects valid addresses whose TLD exceeds 4 letters.
- STATIC DEFECT (phone): the unanchored `phonePattern` admits malformed phone numbers via substring match.
- These are static source observations; the baseline suite has NOT been executed.

#### UNKNOWNS requiring reproduction after admission
- Actual baseline `node --test` pass/fail counts and exit code.
- Exact set of currently-passing vs currently-missing cases.
- Whether the manual browser check surfaces behavior beyond the automated table.
- These are source-level EXPECTATIONS until executed after admission; nothing has been run.

#### PROPOSED implementation constraints
- MUST keep Node-built-ins-only; MUST NOT add npm packages.
- MUST anchor the phone pattern and MUST honor NO-TRIM / as-entered checking.
- MUST correct the email TLD rule to the contract (alphabetic, >=2) without introducing trim normalization.

### Human-boundary subsection
- Formative, consequential, and authorship judgments stay human.
- No AI during actual capture.
- External paid acceptance is UNVERIFIED (neither eligible nor ineligible).
- Manual capture and all human gates (recorded Fit Gate HOLD, admission, approval) are PENDING.
- Baseline counts and exit/output contracts are source-level EXPECTATIONS until executed after admission; nothing has been run.

### Numbered requirements

#### REQ-1 — Email TLD rule correction
- Subject: email validation pattern.
- The repair MUST accept contract-valid emails including alphabetic TLDs longer than four letters and MUST NOT cap the TLD at `{2,4}`. Long-TLD acceptance is defined by the contract (alphabetic >=2), not a judgment call.
- EARS: WHEN a contract-valid email is validated, THE validator SHALL return valid.
- Rationale/source: `docs/validation-contract.md`; static observation of `emailPattern`.
- Acceptance evidence 1.1: Node `--test` table rows for long-TLD valid emails (to be executed after admission).
- Prerequisite: internal admission (not Fit Gate release or paid approval).

#### REQ-2 — Phone anchoring correction
- Subject: phone validation pattern.
- The phone pattern MUST be anchored (`^...$`) and MUST reject any input containing extra leading/trailing characters; it MUST accept any contract-format number (three digits, hyphen, three digits, hyphen, four digits; example `555-123-4567`).
- EARS: WHEN a malformed phone with surrounding characters is validated, THE validator SHALL return invalid.
- Rationale/source: contract; static observation of unanchored `phonePattern`.
- Acceptance evidence 2.1: Node `--test` negative rows (post-admission).
- Prerequisite: REQ-1 context; internal admission.

#### REQ-3 — No-trim / as-entered semantics
- Subject: input normalization.
- The validator MUST check input AS ENTERED and MUST NOT introduce trim/whitespace normalization.
- EARS: WHEN input has leading/trailing whitespace, THE validator SHALL evaluate it as entered per contract.
- Rationale/source: contract explicit NO TRIM.
- Acceptance evidence 3.1: table rows asserting as-entered behavior (post-admission).

#### REQ-4 — Deterministic Node test table
- Subject: automated verification.
- Verification SHALL use `node --test` with a table of valid and invalid inputs covering the decisive email and phone cases.
- EARS: WHEN the test table runs after admission, THE suite SHALL exercise the long-TLD and malformed-phone cases.
- Rationale/source: Goal; `scripts.test`.
- Acceptance evidence 4.1: executed suite output (post-admission; EXPECTATION only now).

#### REQ-5 — Toolchain floor
- Subject: runtime.
- Documentation SHALL state the real Node floor (20.11+ due to `import.meta.dirname`) and MUST NOT rely on the broader README "20+".
- EARS: WHEN the toolchain is documented, THE floor SHALL be stated as Node 20.11+.
- Rationale/source: static observation of `server.js`.
- Acceptance evidence 5.1: design toolchain section.

#### REQ-6 — Separate manual browser check
- Subject: human verification.
- A manual browser check at `localhost:4173` SHALL be recorded SEPARATELY from the automated Node evidence.
- EARS: WHEN automated evidence is produced, THE manual browser check SHALL remain a distinct human step.
- Rationale/source: Goal.
- Acceptance evidence 6.1: human capture notes (pending).

## Glossary

- **AS ENTERED / NO TRIM**: input is validated exactly as typed, with no leading/trailing whitespace stripping, per `docs/validation-contract.md`.
- **TLD**: top-level domain; the contract requires it to be alphabetic and at least 2 letters, with no upper cap.
- **Baseline**: the recovered unworked source suite as it exists before any repair; not executed in this session.
- **Internal admission**: the bound internal preparation gate permitting off-screen work after Kiro review PASS and Ky's main merge.
- **Fit Gate HOLD**: a recorded external human property on the Task Factory row, preserved as a fact; not a prerequisite for internal preparation.
- **Guided worked reference**: a disposable guided solution kept separate from the ordinary baseline.
