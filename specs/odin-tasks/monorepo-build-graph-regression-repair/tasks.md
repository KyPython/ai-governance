# Tasks — Monorepo Build-Graph Regression Repair

1. **Create synthetic pnpm/Turborepo workspace**
   - Assigned coder: **Codex**
   - Reviewer: **Cursor**
   - Add affected service, shared dependency, and one unrelated workspace check.

2. **Seed the transitive build-order regression**
   - Assigned coder: **Codex**
   - Reviewer: **Cursor**
   - Shared dependency must require its own build output while the starter service path fails to establish the needed build relationship.

3. **Seed the stale package-identity configuration**
   - Assigned coder: **Codex**
   - Reviewer: **Cursor**
   - Place the obsolete name in a realistic build/container/config surface without writing the repair.

4. **Add deterministic reproduction scaffolding**
   - Assigned coder: **Codex**
   - Reviewer: **Cursor**
   - Document dependency installation and the single failing service build command.

5. **No-solution-leak review and handoff**
   - Assigned coder: **Cursor**
   - Reviewer: **Codex**
   - Confirm neither final correction nor completed verification note is present; leave the failing starter ready for recording.
