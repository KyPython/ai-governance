# Tasks — Async Side-Effect Idempotency Hardening

1. **Create the synthetic asynchronous worker service**
   - Assigned coder: **Codex**
   - Reviewer: **Cursor**
   - Use fabricated jobs and local-only adapters; no credentials or hosted dependencies.

2. **Seed deterministic duplicate delivery and observable effects**
   - Assigned coder: **Codex**
   - Reviewer: **Cursor**
   - Replaying one stable job must visibly record the effect twice in the untouched starter.

3. **Add ordinary-path fixtures and tests**
   - Assigned coder: **Codex**
   - Reviewer: **Cursor**
   - Cover single deliveries and distinct jobs while withholding the decisive duplicate-replay assertion.

4. **Document setup and baseline reproduction**
   - Assigned coder: **Codex**
   - Reviewer: **Cursor**
   - Include short commands and neutral expected baseline output, not diagnosis or repair guidance.

5. **No-solution-leak review**
   - Assigned coder: **Cursor**
   - Reviewer: **Codex**
   - Confirm the final mechanism, decisive regression test, one-effect replay proof, and answer key are absent.

6. **Package the starter for recording**
   - Assigned coder: **Codex**
   - Reviewer: **Cursor**
   - Leave diagnosis, engineering decisions, implementation, verification, and narration to the human.
