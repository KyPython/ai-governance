# Tasks — Flaky Time-Dependent Test Stabilization via Clock Injection

1. **Create synthetic Python time-sensitive module and behavior contract**
   - Assigned coder: **Codex**
   - Reviewer: **Cursor**

2. **Seed direct system-clock/local-time coupling and a flaky starter test**
   - Assigned coder: **Codex**
   - Reviewer: **Cursor**
   - Keep the eventual injected-clock design absent.

3. **Add safe reproduction and multi-TZ scaffolding**
   - Assigned coder: **Codex**
   - Reviewer: **Cursor**
   - Make time/TZ sensitivity demonstrable without waiting for real time; do not include final fixed-timestamp assertions.

4. **No-solution-leak review**
   - Assigned coder: **Cursor**
   - Reviewer: **Codex**
   - Confirm there is no clock injection, final boundary suite, diagnosis note, or ready-to-paste answer.

5. **Package the starter for recording**
   - Assigned coder: **Codex**
   - Reviewer: **Cursor**
   - Leave the project in the deliberately time-dependent starting state.
