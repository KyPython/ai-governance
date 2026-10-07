# Tasks — Vacuous Test Suite Audit

1. **Create the synthetic project skeleton**
   - Assigned coder: **Codex**
   - Reviewer: **Cursor**
   - Build the neutral Python package, behavior document, pytest configuration, and baseline run instructions.

2. **Seed one bounded behavioral mismatch and weak passing coverage**
   - Assigned coder: **Codex**
   - Reviewer: **Cursor**
   - Ensure the implementation violates the written contract while the starter tests still pass.
   - Do not create the final strengthened assertions or corrective patch.

3. **Add deterministic setup and baseline verification**
   - Assigned coder: **Codex**
   - Reviewer: **Cursor**
   - Provide a short local command/script that proves the initial suite is green from the defective starting state.

4. **Perform no-solution-leak review**
   - Assigned coder: **Cursor**
   - Reviewer: **Codex**
   - Confirm recorder-visible files contain no diagnosis, answer key, strengthened final test, or completed fix.

5. **Package for human recording**
   - Assigned coder: **Codex**
   - Reviewer: **Cursor**
   - Leave the repository in the defective, weak-test starting state and document only setup/baseline commands.
