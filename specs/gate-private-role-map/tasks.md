# Tasks: Read the role map while ai-governance is private

Spec ID: GRM

One coder per task, each in its own PR, reviewed by a different agent. No task edits `specs/`.
Stop on any failed check and report the command and output.

- [ ] 1. Replace the raw-URL read in `governance.yml` with the authenticated contents-API request, its constants, and the token choice (GRM-1.1, GRM-1.2, GRM-1.3). Keep `ROLES_FILE` for tests.
- [ ] 2. Make failures fail closed with the GRM-2.2 message, with no fallback and no token in output (GRM-2.1 to GRM-2.4).
- [ ] 3. Declare the optional `AI_GOVERNANCE_READ_TOKEN` `workflow_call` secret and pass it to the policy step (GRM-3.1).
- [ ] 4. Add the GRM-4.1 tests with a local HTTP stub, and replace the line-252 raw-URL assertion (GRM-4.2). Run `python3 -m pytest -q`; record the pass count and any failure that also fails on `8da4ed4`.
- [ ] 5. Update `scripts/sweep.sh` reporting and the caller template `templates/ai-governance.yml` (GRM-3.2, GRM-3.3).
- [ ] 6. Show GRM-1.4 in CI: on the PR for tasks 1 to 3, `ai-governance / policy` loads the role map with no added secret. Then, after Ky's HOLD 2 for one KyPython caller, show that caller's policy job loads it.
