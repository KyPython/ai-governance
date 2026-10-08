# Design Document

> INTERNAL guided Bootcamp PREPARATION under an explicit user world-preparation exception. NOT externally approved Odin, paid acceptance UNVERIFIED, NOT recording-ready. Spec only. This Kiro session executes none of the implementation.

## Overview

Repair the recovered, unworked synthetic signup-form validation source so email validation accepts contract-valid long-TLD addresses and phone validation is anchored to the contract format, then verify with a Node test table plus a separate manual browser check. All implementation is future work gated behind an actual Kiro review PASS and Ky's main merge of the new canonical 18-record spec PR.

## Architecture

- Confirmed read-only source identity (reuse the UNWORKED recovered source; do not re-create):
  - `extractedRoot`: `<private recovery cache>/extracted/task_e_6ac6d5f886fc8322ae0ceab6e191f68b`
  - `starterSubdirectory`: `specs/odin-tasks/javascript-signup-form-validation-regex-repair/starter`
  - `cloudRecoveryTaskId`: `task_e_6ac6d5f886fc8322ae0ceab6e191f68b` (`cloudStatusAtRead`: ready)
  - `diffSha256`: `89720c3ef31690572cb134fe568704153a2b9019c7981cf0ad364626c2da0e2d`
  - `starterFileCount`: 10
  - `legacyRecoveryIssue`: https://github.com/KyPython/ai-governance/issues/182 (retired historical alias; closed wrong-lane duplicate; history only)
- Starter files (read-only; do NOT copy raw source bytes into docs): `README.md`, `docs/validation-contract.md`, `fixtures/validation-cases.json`, `index.html`, `package.json`, `server.js`, `src/app.js`, `src/validation.js`, `styles.css`, `test/validation.test.js`.
- Behavior contract (`docs/validation-contract.md`): email requires a non-empty local part (letters/digits/dot/underscore/hyphen/plus), exactly one `@`, a domain, and an alphabetic TLD >=2 letters (contract-defined); phone is any three-digits hyphen three-digits hyphen four-digits group (format example `555-123-4567`, not the sole literal); input checked AS ENTERED, NO TRIM.

## Components and Interfaces

- `src/validation.js`: exports the email and phone validators. The repair targets `emailPattern` (remove the `{2,4}` TLD cap so an alphabetic TLD >=2 with NO upper cap is accepted, AND include a LITERAL plus `+` in the local-part character class, which the current source local-part class omits) and `phonePattern` (anchor end-to-end with `^...$`). No trim/normalization is introduced; input is evaluated as entered.
- `src/app.js` / `index.html`: static form wiring consumed by the manual browser check.
- `server.js`: static server entrypoint (`node server.js`) serving `localhost:4173`; uses `import.meta.dirname` (Node 20.11+ floor).
- `test/validation.test.js`: Node `--test` table extended with decisive cases.

## Data Models

- Validation fixture (`fixtures/validation-cases.json`): a single JSON object with two arrays, `email` and `phone`. Each element is `{ "value": <string>, "valid": <boolean> }`. `test/validation.test.js` iterates `cases.email` and `cases.phone`, reading `example.value` and `example.valid` and asserting the validator result equals `example.valid`, as entered.
- Phone fixture contract (literal): any three-digits hyphen three-digits hyphen four-digits group; `555-123-4567` is the format example and a valid case, while `5551234567` and `555.123.4567` are invalid per the fixture. Checked AS ENTERED / NO TRIM.
- Email contract shape: local-part charset + single `@` + domain + alphabetic TLD (>=2, no upper bound).
- Phone contract shape: `\d{3}-\d{3}-\d{4}` anchored end to end.

## Correctness Properties

### Property 1: Any contract-valid email, including alphabetic TLDs longer than 4 letters and `+` in the local part, validates as valid.
**Validates: Requirements 1.1**
### Property 2: Any phone input with surrounding characters validates as invalid; only an anchored contract-format number validates as valid.
**Validates: Requirements 2.1**
### Property 3: No trim/normalization is introduced; input is evaluated as entered.
**Validates: Requirements 3.1**

## Error Handling

- Malformed inputs return invalid without throwing.
- The static server failure modes (port in use, missing file) are outside the validation repair scope and are not modified.

## Testing Strategy

- Automated: `node --test` table extended with an INDEPENDENT plus-address case (a local part containing a literal `+` with an otherwise already-accepted TLD) AND an INDEPENDENT long-TLD case (alphabetic TLD longer than 4 letters, WITHOUT a `+`), plus the malformed-phone (surrounding characters) rows; deterministic replay. Each decisive behavior is covered by its own case so removing only the TLD cap cannot satisfy the plus-address case. Retain alphabetic TLD >=2 with no upper cap, phone end-to-end anchoring, and NO-TRIM/as-entered. This restates the contract (`docs/validation-contract.md`); it does NOT add broader email/IANA policy or claim a human selected it.
- Manual: browser check at `localhost:4173` via `node server.js`, recorded as a SEPARATE human evidence step.
- No package install is required (Node built-ins only), so NO offline npm adapter is needed for this world.
- Meaningful strengthened tests MUST FAIL for the intended behavior BEFORE the smallest production repair and PASS after. The strengthened tests and the production repair MUST occur in a DISPOSABLE worked-reference copy — NEVER the published unworked starter, the original pinned input, or the Recorder-captured workspace before capture. Ordinary baseline runs are kept SEPARATE from any disposable guided worked reference, and source preservation MUST be VERIFIED. Published guided steps come from observed steps; on-camera edits and verification are HUMAN/manual only, with no AI during capture.
- The exact final case matrix is read from the exact Goal and the actual `fixtures/validation-cases.json` during review; long-TLD acceptance itself is contract-defined, not a judgment call. Execution RESULTS remain unobserved until a later authorized run.

## Human boundaries

- No AI during actual capture; formative/consequential/authorship decisions stay human.
- Paid acceptance UNVERIFIED (neither eligible nor ineligible). Only the EXTERNAL paid/HOLD release is NOT a prerequisite for internal preparation. The required FUTURE INTERNAL gates REMAIN: an actual Kiro review PASS, Ky's merge of the NEW canonical spec PR to `main`, and bound internal admission. Recorded external fields (Stage=Candidate, Fit Gate=HOLD, blank Approval ID/Approved Goal/pay) and the pending actual Recorder/human-capture and pay gates are preserved as facts.
